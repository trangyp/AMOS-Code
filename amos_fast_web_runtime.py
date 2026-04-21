from __future__ import annotations

from typing import Any, Optional

"""AMOS Fast Web Runtime - High-precision web retrieval under tight budgets.

Implements the equation:
WebQuery → RankFast → ReadLittle → AnswerEarly → DeepenOnlyIfNeeded

Author: AMOS Architecture
Version: 1.0.0
"""

import asyncio
import hashlib
import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ExtractionStrategy(Enum):
    """Content extraction strategies from fastest to most thorough."""

    SNIPPET_ONLY = auto()  # Search snippet only
    MAIN_CONTENT = auto()  # Article/main content extraction
    STRUCTURED = auto()  # Tables, lists, code blocks
    FULL_TEXT = auto()  # Complete page text


class SourceAuthority(Enum):
    """Authority tiers for source ranking."""

    OFFICIAL = 4  # Official docs, primary sources
    AUTHORITATIVE = 3  # Established publications
    ESTABLISHED = 2  # Known blogs, mid-tier sources
    UNKNOWN = 1  # New/unverified sources
    SUSPICIOUS = 0  # Low trust


@dataclass
class WebBudgets:
    """Hard browsing budgets to prevent runaway crawling."""

    max_search_queries: int = 2
    max_page_opens: int = 4
    max_deep_reads: int = 2
    max_verification_reads: int = 2
    max_total_time_ms: float = 5000.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_search_queries": self.max_search_queries,
            "max_page_opens": self.max_page_opens,
            "max_deep_reads": self.max_deep_reads,
            "max_verification_reads": self.max_verification_reads,
            "max_total_time_ms": self.max_total_time_ms,
        }


@dataclass
class SourceRank:
    """Rank = Authority * QueryFit * Freshness * StructureQuality - RenderCost - BoilerplateCost"""

    authority: float = 0.0  # 0-1 based on domain tier
    query_fit: float = 0.0  # 0-1 snippet/heading relevance
    freshness: float = 0.0  # 0-1 recency score
    structure_quality: float = 0.0  # 0-1 structured content ratio
    render_cost: float = 0.0  # 0-1 estimated render overhead
    boilerplate_cost: float = 0.0  # 0-1 estimated noise ratio

    @property
    def score(self) -> float:
        return (
            self.authority * self.query_fit * self.freshness * self.structure_quality
            - self.render_cost
            - self.boilerplate_cost
        )


@dataclass
class WebResult:
    """A web result with extracted content and metadata."""

    url: str
    title: str = ""
    snippet: str = ""
    extracted_content: str = ""
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.SNIPPET_ONLY
    source_rank: SourceRank = field(default_factory=SourceRank)
    fetch_time_ms: float = 0.0
    extract_time_ms: float = 0.0
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))  # noqa: UP017

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet[:500],
            "extracted_content": self.extracted_content[:2000],
            "extraction_strategy": self.extraction_strategy.name,
            "source_rank_score": round(self.source_rank.score, 3),
            "fetch_time_ms": round(self.fetch_time_ms, 1),
            "extract_time_ms": round(self.extract_time_ms, 1),
            "confidence": round(self.confidence, 3),
        }


@dataclass
class SufficiencyGate:
    """Stop when Confidence ≥ τ_c ∧ SourceQuality ≥ τ_q ∧ CrossCheck ≥ τ_x"""

    confidence_threshold: float = 0.85
    source_quality_threshold: float = 0.70
    cross_check_threshold: float = 0.60

    def is_sufficient(self, confidence: float, source_quality: float, cross_check: float) -> bool:
        return (
            confidence >= self.confidence_threshold
            and source_quality >= self.source_quality_threshold
            and cross_check >= self.cross_check_threshold
        )


class WebCache:
    """Aggressive multi-tier caching for web content."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self._domain_cache: dict[str, list[WebResult]] = {}
        self._page_cache: dict[str, WebResult] = {}
        self._extract_cache: dict[str, str] = {}
        self._query_cache: dict[str, list[WebResult]] = {}
        self._timestamps: dict[str, datetime] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def _make_key(self, *parts: str) -> str:
        combined = "|".join(parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]

    def get_query_results(self, query: str) -> list[Optional[WebResult]]:
        key = self._make_key("query", query.lower().strip())
        if key in self._query_cache and not self._is_expired(key):
            logger.debug(f"Cache hit for query: {query[:50]}...")
            return self._query_cache[key]
        return None

    def set_query_results(self, query: str, results: list[WebResult]) -> None:
        key = self._make_key("query", query.lower().strip())
        self._query_cache[key] = results
        self._timestamps[key] = datetime.now(UTC)

    def get_page(self, url: str) -> Optional[WebResult]:
        key = self._make_key("page", url)
        if key in self._page_cache and not self._is_expired(key):
            return self._page_cache[key]
        return None

    def set_page(self, url: str, result: WebResult) -> None:
        key = self._make_key("page", url)
        self._page_cache[key] = result
        self._timestamps[key] = datetime.now(UTC)

    def get_extract(self, url: str, strategy: ExtractionStrategy) -> Optional[str]:
        key = self._make_key("extract", url, strategy.name)
        if key in self._extract_cache and not self._is_expired(key):
            return self._extract_cache[key]
        return None

    def set_extract(self, url: str, strategy: ExtractionStrategy, content: str) -> None:
        key = self._make_key("extract", url, strategy.name)
        self._extract_cache[key] = content
        self._timestamps[key] = datetime.now(UTC)

    def _is_expired(self, key: str) -> bool:
        if key not in self._timestamps:
            return True
        return datetime.now(UTC) - self._timestamps[key] > self._ttl

    def clear(self) -> None:
        self._domain_cache.clear()
        self._page_cache.clear()
        self._extract_cache.clear()
        self._query_cache.clear()
        self._timestamps.clear()


class FastWebRuntime:
    """Fast web runtime: RankFast → ReadLittle → AnswerEarly → DeepenOnlyIfNeeded"""

    def __init__(
        self,
        budgets: Optional[WebBudgets] = None,
        sufficiency: Optional[SufficiencyGate] = None,
        cache: Optional[WebCache] = None,
    ) -> None:
        self.budgets = budgets or WebBudgets()
        self.sufficiency = sufficiency or SufficiencyGate()
        self.cache = cache or WebCache()
        self._authority_domains: set[str] = {
            "docs.python.org",
            "github.com",
            "stackoverflow.com",
            "wikipedia.org",
            "arxiv.org",
            "ietf.org",
            "oracle.com",
            "microsoft.com",
            "google.com",
            "amazon.com",
            "apple.com",
            "mozilla.org",
            "apache.org",
        }
        self._client: httpx.Optional[AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True,
                headers={
                    "User-Agent": "AMOS-FastWeb/1.0 (Research Bot)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                },
            )
        return self._client

    def _rank_source(self, url: str, title: str, snippet: str, query: str) -> SourceRank:
        """Rank = Authority * QueryFit * Freshness * StructureQuality - RenderCost - BoilerplateCost"""
        domain = urlparse(url).netloc.lower()

        # Authority score
        authority = SourceAuthority.UNKNOWN
        if any(auth in domain for auth in ["docs.", "api.", "developer."]):
            authority = SourceAuthority.OFFICIAL
        elif any(d in domain for d in self._authority_domains):
            authority = SourceAuthority.AUTHORITATIVE
        elif domain.endswith((".edu", ".gov")):
            authority = SourceAuthority.AUTHORITATIVE
        authority_score = authority.value / 4.0

        # Query fit: snippet relevance
        query_words = set(query.lower().split())
        snippet_words = set(snippet.lower().split())
        overlap = len(query_words & snippet_words)
        query_fit = min(1.0, overlap / max(1, len(query_words)) * 1.5)

        # Freshness: assume recent if no date indicators
        freshness = 0.8
        date_patterns = [
            r"\b202[0-9]\b",  # Years 2020-2029
            r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}\b",
        ]
        for pattern in date_patterns:
            if re.search(pattern, snippet + title, re.I):
                freshness = 0.95
                break

        # Structure quality: presence of structured indicators
        structure_indicators = ["api", "reference", "guide", "documentation", "tutorial"]
        structure_score = sum(1 for ind in structure_indicators if ind in (title + snippet).lower())
        structure_quality = min(1.0, structure_score / 3.0)

        # Render cost estimation
        render_cost = 0.3 if any(x in url for x in ["youtube", "twitter", "x.com"]) else 0.1

        # Boilerplate cost estimation
        boilerplate_indicators = ["cookie", "privacy", "terms", "subscribe", "newsletter"]
        boilerplate_score = sum(1 for ind in boilerplate_indicators if ind in snippet.lower())
        boilerplate_cost = min(0.5, boilerplate_score * 0.1)

        return SourceRank(
            authority=authority_score,
            query_fit=query_fit,
            freshness=freshness,
            structure_quality=structure_quality,
            render_cost=render_cost,
            boilerplate_cost=boilerplate_cost,
        )

    async def search(
        self,
        query: str,
        num_results: int = 10,
    ) -> list[WebResult]:
        """Search and return ranked results (cache-aware)."""
        # Check cache first
        cached = self.cache.get_query_results(query)
        if cached:
            return cached

        # Use DuckDuckGo lite or similar fast search
        # For production, integrate with actual search API
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"

        try:
            client = await self._get_client()
            start_time = time.time()
            response = await client.get(search_url)
            fetch_time = (time.time() - start_time) * 1000

            results = self._parse_search_results(response.text, query)
            results.sort(key=lambda r: r.source_rank.score, reverse=True)

            # Cache results
            self.cache.set_query_results(query, results)

            logger.info(
                f"Search '{query[:40]}...' returned {len(results)} results in {fetch_time:.0f}ms"
            )
            return results[:num_results]

        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []

    def _parse_search_results(self, html: str, query: str) -> list[WebResult]:
        """Parse search result page."""
        results = []
        soup = BeautifulSoup(html, "html.parser")

        # DuckDuckGo results
        for result in soup.find_all("div", class_="result"):
            try:
                link = result.find("a", class_="result__a")
                if not link:
                    continue

                url = link.get("href", "")
                title = link.get_text(strip=True)

                snippet_elem = result.find("a", class_="result__snippet")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                rank = self._rank_source(url, title, snippet, query)

                results.append(
                    WebResult(
                        url=url,
                        title=title,
                        snippet=snippet,
                        source_rank=rank,
                    )
                )
            except Exception as e:
                logger.debug(f"Failed to parse result: {e}")
                continue

        return results

    async def fetch_page(
        self,
        url: str,
        strategy: ExtractionStrategy = ExtractionStrategy.MAIN_CONTENT,
    ) -> Optional[WebResult]:
        """Fetch and extract content from a page."""
        # Check cache
        cached = self.cache.get_page(url)
        if cached:
            return cached

        # Check extract cache for content-only retrieval
        cached_extract = self.cache.get_extract(url, strategy)

        try:
            client = await self._get_client()
            start_time = time.time()
            response = await client.get(url)
            fetch_time = (time.time() - start_time) * 1000

            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {url}")
                return None

            # Extract content
            extract_start = time.time()
            if cached_extract:
                content = cached_extract
            else:
                content = self._extract_content(response.text, strategy, url)
                self.cache.set_extract(url, strategy, content)

            extract_time = (time.time() - extract_start) * 1000

            # Get title from HTML if not already set
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else ""

            result = WebResult(
                url=url,
                title=title,
                extracted_content=content,
                extraction_strategy=strategy,
                fetch_time_ms=fetch_time,
                extract_time_ms=extract_time,
                confidence=0.8 if content else 0.0,
            )

            self.cache.set_page(url, result)

            logger.debug(
                f"Fetched {url[:60]}... in {fetch_time:.0f}ms, extracted in {extract_time:.0f}ms"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def _extract_content(self, html: str, strategy: ExtractionStrategy, url: str) -> str:
        """Extract content based on strategy."""
        soup = BeautifulSoup(html, "html.parser")

        if strategy == ExtractionStrategy.SNIPPET_ONLY:
            return ""

        if strategy == ExtractionStrategy.MAIN_CONTENT:
            # Remove navigation, ads, footers
            for elem in soup(["nav", "header", "footer", "aside", "script", "style", "noscript"]):
                elem.decompose()

            # Try article/main content first
            for selector in [
                "article",
                "main",
                "[role='main']",
                ".content",
                "#content",
                ".post",
                ".entry",
            ]:
                elem = soup.select_one(selector)
                if elem:
                    return elem.get_text(separator="\n", strip=True)[:8000]

            # Fallback to body
            body = soup.find("body")
            if body:
                return body.get_text(separator="\n", strip=True)[:8000]

            return soup.get_text(separator="\n", strip=True)[:8000]

        if strategy == ExtractionStrategy.STRUCTURED:
            # Extract tables, lists, code blocks
            structured = []
            for table in soup.find_all("table")[:3]:
                structured.append(f"[TABLE]\n{table.get_text(separator=' | ', strip=True)}\n")
            for pre in soup.find_all(["pre", "code"])[:5]:
                structured.append(f"[CODE]\n{pre.get_text(strip=True)}\n")
            for list_elem in soup.find_all(["ul", "ol"])[:3]:
                items = [f"- {li.get_text(strip=True)}" for li in list_elem.find_all("li")]
                structured.append("[LIST]\n" + "\n".join(items) + "\n")
            return "\n".join(structured)[:6000]

        # FULL_TEXT
        return soup.get_text(separator="\n", strip=True)[:10000]

    async def query_fast(
        self,
        query: str,
        answer_callback: Callable[[str, float], Awaitable[None]] = None,
    ) -> dict[str, Any]:
        """Fast path: query → search → top 3 → snippet rank → open 1-2 → answer."""
        start_time = time.time()
        total_time_ms = self.budgets.max_total_time_ms

        # Stage 1: Search (budget: 1 search)
        results = await self.search(query, num_results=3)
        if not results:
            return {"answer": "No results found.", "sources": [], "time_ms": 0}

        # Stage 2: Quick snippet-only answer attempt
        top_snippets = [r.snippet for r in results[:2] if r.snippet]
        if top_snippets and self._snippet_sufficiency(top_snippets, query):
            answer = self._synthesize_from_snippets(top_snippets, results[:2])
            elapsed = (time.time() - start_time) * 1000

            if answer_callback:
                await answer_callback(answer, 0.75)

            return {
                "answer": answer,
                "sources": [r.to_dict() for r in results[:2]],
                "time_ms": round(elapsed, 1),
                "path": "fast_snippet_only",
                "pages_fetched": 0,
            }

        # Stage 3: Fetch top 1-2 pages with MAIN_CONTENT extraction
        pages_fetched = 0
        all_content = []

        for result in results[:2]:
            if pages_fetched >= self.budgets.max_deep_reads:
                break

            # Check time budget
            elapsed = (time.time() - start_time) * 1000
            if elapsed > total_time_ms * 0.7:
                break

            page = await self.fetch_page(result.url, ExtractionStrategy.MAIN_CONTENT)
            if page:
                pages_fetched += 1
                all_content.append((page, result))

                # Early sufficiency check
                if answer_callback and pages_fetched >= 1:
                    partial = self._synthesize_from_content([all_content[0][0]], query)
                    await answer_callback(partial, 0.6)

        # Stage 4: Synthesize answer
        if all_content:
            answer = self._synthesize_from_content([p for p, _ in all_content], query)
            confidence = min(0.9, 0.7 + (pages_fetched * 0.1))
        else:
            answer = self._synthesize_from_snippets(top_snippets, results[:2])
            confidence = 0.6

        elapsed = (time.time() - start_time) * 1000

        if answer_callback:
            await answer_callback(answer, confidence)

        return {
            "answer": answer,
            "sources": [r.to_dict() for _, r in all_content]
            if all_content
            else [r.to_dict() for r in results[:2]],
            "time_ms": round(elapsed, 1),
            "path": "fast_with_fetch" if all_content else "fast_snippet_fallback",
            "pages_fetched": pages_fetched,
            "confidence": round(confidence, 2),
        }

    async def query_deep(
        self,
        query: str,
        answer_callback: Callable[[str, float], Awaitable[None]] = None,
    ) -> dict[str, Any]:
        """Deep path: search authoritative sources with verification."""
        start_time = time.time()

        # Stage 1: Broader search
        results = await self.search(query, num_results=10)

        # Stage 2: Filter to authoritative sources only
        authoritative = [
            r
            for r in results
            if r.source_rank.authority >= SourceAuthority.AUTHORITATIVE.value / 4.0
        ]

        if not authoritative:
            # Fall back to fast path
            return await self.query_fast(query, answer_callback)

        # Stage 3: Fetch authoritative sources
        all_content = []
        for result in authoritative[: self.budgets.max_deep_reads]:
            page = await self.fetch_page(result.url, ExtractionStrategy.MAIN_CONTENT)
            if page:
                all_content.append((page, result))

        # Stage 4: Cross-validation (if budget allows)
        if len(all_content) >= 2 and self.budgets.max_verification_reads > 0:
            verification = self._cross_validate(all_content, query)
        else:
            verification = 0.7

        # Stage 5: Synthesize
        answer = self._synthesize_from_content([p for p, _ in all_content], query)
        confidence = min(0.95, 0.75 + (len(all_content) * 0.05) + (verification * 0.1))

        elapsed = (time.time() - start_time) * 1000

        if answer_callback:
            await answer_callback(answer, confidence)

        return {
            "answer": answer,
            "sources": [r.to_dict() for _, r in all_content],
            "time_ms": round(elapsed, 1),
            "path": "deep_authoritative",
            "pages_fetched": len(all_content),
            "verification_score": round(verification, 2),
            "confidence": round(confidence, 2),
        }

    def _snippet_sufficiency(self, snippets: list[str], query: str) -> bool:
        """Check if snippets alone are sufficient to answer."""
        combined = " ".join(snippets).lower()
        query_terms = set(query.lower().split())

        # Check if all query terms are covered
        coverage = sum(1 for term in query_terms if term in combined)
        coverage_ratio = coverage / max(1, len(query_terms))

        # Check for answer indicators
        answer_indicators = ["is", "are", "was", "were", "means", "refers to", "defined as"]
        has_answer_form = any(ind in combined for ind in answer_indicators)

        return coverage_ratio >= 0.7 and has_answer_form

    def _synthesize_from_snippets(self, snippets: list[str], sources: list[WebResult]) -> str:
        """Create answer from search snippets."""
        if not snippets:
            return "No information available."

        # De-duplicate and clean
        seen = set()
        unique = []
        for s in snippets:
            key = s[:50].lower()
            if key not in seen:
                seen.add(key)
                unique.append(s)

        return " ".join(unique)[:1000]

    def _synthesize_from_content(self, pages: list[WebResult], query: str) -> str:
        """Create answer from page content."""
        if not pages:
            return "No content available."

        # Extract relevant paragraphs
        query_terms = set(query.lower().split())
        relevant_spans = []

        for page in pages:
            paragraphs = page.extracted_content.split("\n")
            for para in paragraphs[:20]:  # Top 20 paragraphs
                para_lower = para.lower()
                score = sum(2 if term in para_lower else 0 for term in query_terms)
                if score > 0:
                    relevant_spans.append((score, para.strip()))

        # Sort by relevance and combine
        relevant_spans.sort(reverse=True)
        top_spans = [span for _, span in relevant_spans[:5]]

        return "\n\n".join(top_spans)[:2000]

    def _cross_validate(
        self,
        content: list[tuple[WebResult, WebResult]],
        query: str,
    ) -> float:
        """Cross-validate content from multiple sources."""
        if len(content) < 2:
            return 0.5

        # Simple agreement scoring
        texts = [p.extracted_content[:500].lower() for p, _ in content]

        # Check for common terms
        all_terms = [set(t.split()) for t in texts]
        if not all_terms:
            return 0.5

        common = all_terms[0]
        for terms in all_terms[1:]:
            common &= terms

        total_unique = set()
        for terms in all_terms:
            total_unique |= terms

        if not total_unique:
            return 0.5

        agreement = len(common) / len(total_unique)
        return min(1.0, agreement * 3)  # Scale up since exact match is rare

    async def query(
        self,
        query: str,
        path: str = "auto",
        answer_callback: Callable[[str, float], Awaitable[None]] = None,
    ) -> dict[str, Any]:
        """Main query entry point. Path: 'fast', 'deep', or 'auto'."""
        if path == "fast":
            return await self.query_fast(query, answer_callback)
        elif path == "deep":
            return await self.query_deep(query, answer_callback)
        else:
            # Auto: try fast first, deepen only if needed
            result = await self.query_fast(query, answer_callback)
            if result.get("confidence", 0) < self.sufficiency.confidence_threshold:
                return await self.query_deep(query, answer_callback)
            return result

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Global instance for convenience
_default_runtime: Optional[FastWebRuntime] = None


def get_fast_web_runtime() -> FastWebRuntime:
    """Get or create global FastWebRuntime instance."""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = FastWebRuntime()
    return _default_runtime


async def web_query(
    query: str,
    path: str = "auto",
    budgets: Optional[WebBudgets] = None,
) -> dict[str, Any]:
    """One-shot web query with automatic cleanup."""
    runtime = FastWebRuntime(budgets=budgets) if budgets else get_fast_web_runtime()
    try:
        return await runtime.query(query, path=path)
    finally:
        if budgets:  # Only close if we created a custom instance
            await runtime.close()


if __name__ == "__main__":
    # Demo
    async def demo() -> None:
        runtime = FastWebRuntime()

        async def on_answer(text: str, conf: float) -> None:
            print(f"\n[Partial answer @ {conf:.0%} confidence]\n{text[:200]}...\n")

        result = await runtime.query(
            "What is the AMOS architecture?",
            path="auto",
            answer_callback=on_answer,
        )

        print("\n" + "=" * 60)
        print(f"Path: {result['path']}")
        print(f"Time: {result['time_ms']:.0f}ms")
        print(f"Pages: {result['pages_fetched']}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print("\nFinal Answer:")
        print(result["answer"][:500])

        await runtime.close()

    asyncio.run(demo())
