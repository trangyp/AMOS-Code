"""AMOS SDK Client.

Synchronous and asynchronous clients for AMOS Brain API.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import aiohttp
import requests

from .exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import AmoslResult, DecideResult, QueryRecord, Stats, ThinkResult

DEFAULT_BASE_URL = "https://neurosyncai.tech"


@dataclass
class ClientConfig:
    """Client configuration."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    timeout: int = 30
    retries: int = 3


class Client:
    """Synchronous AMOS Brain API client.

    Usage:
        client = Client(api_key="your_key")
        result = client.think("Analyze this situation")
    """

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.config = ClientConfig(api_key=api_key, base_url=base_url)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"AMOS-SDK-Python/{__import__('amos_sdk').__version__}",
            }
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request with error handling."""
        url = f"{self.config.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.config.timeout, **kwargs)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}")
            elif response.status_code >= 400:
                raise ValidationError(f"Request error: {response.text}")

            return response.json()

        except requests.exceptions.Timeout:
            raise ServerError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise ServerError("Connection error")

    def think(self, query: str, domain: str = "general") -> ThinkResult:
        """Send a think request to AMOS Brain.

        Args:
            query: The question or problem to analyze
            domain: Knowledge domain (general, software, security, etc.)

        Returns:
            ThinkResult with content, reasoning, and confidence
        """
        data = {"query": query, "domain": domain}
        response = self._request("POST", "/think", json=data)

        return ThinkResult(
            content=response.get("content", ""),
            reasoning=response.get("reasoning", []),
            confidence=response.get("confidence", 0.0),
            law_compliant=response.get("law_compliant", False),
            domain=response.get("domain", domain),
        )

    def decide(self, question: str, options: list[str]) -> DecideResult:
        """Request a decision from AMOS Brain.

        Args:
            question: The decision to be made
            options: List of possible options

        Returns:
            DecideResult with recommendation and risk assessment
        """
        data = {"question": question, "options": options}
        response = self._request("POST", "/decide", json=data)

        return DecideResult(
            approved=response.get("approved", False),
            risk_level=response.get("risk_level", "unknown"),
            reasoning=response.get("reasoning", ""),
            decision_id=response.get("decision_id", ""),
        )

    def validate(self, action: str) -> bool:
        """Validate an action against AMOS global laws.

        Args:
            action: The action description to validate

        Returns:
            True if valid, False otherwise
        """
        data = {"action": action}
        response = self._request("POST", "/validate", json=data)
        return response.get("valid", False)

    def amosl_compile(self, source: str) -> AmoslResult:
        """Compile AMOSL source code.

        Args:
            source: AMOSL source code string

        Returns:
            AmoslResult with compilation results and IR statistics
        """
        data = {"source": source}
        response = self._request("POST", "/amosl/compile", json=data)

        return AmoslResult(
            success=response.get("success", False),
            invariants_valid=response.get("invariants_valid", False),
            violations=response.get("invariant_violations", []),
            ir_stats=response.get("ir", {}),
        )

    def get_history(self, limit: int = 100) -> list[QueryRecord]:
        """Get query history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of QueryRecord objects
        """
        response = self._request("GET", f"/api/history?limit={limit}")

        records = []
        for item in response.get("history", []):
            records.append(
                QueryRecord(
                    id=item.get("id", 0),
                    endpoint=item.get("endpoint", ""),
                    query=item.get("query", ""),
                    domain=item.get("domain", ""),
                    confidence=item.get("confidence", ""),
                    law_compliant=item.get("law_compliant", False),
                    processing_time_ms=item.get("processing_time_ms", 0),
                    created_at=item.get("created_at", ""),
                )
            )
        return records

    def get_stats(self, days: int = 7) -> Stats:
        """Get usage statistics.

        Args:
            days: Number of days to include in statistics

        Returns:
            Stats object with usage metrics
        """
        response = self._request("GET", f"/api/stats?days={days}")
        data = response.get("stats", {})

        return Stats(
            total_requests=data.get("total_requests", 0),
            avg_response_time_ms=data.get("avg_response_time_ms", 0.0),
            success_rate_percent=data.get("success_rate_percent", 0.0),
            period_days=data.get("period_days", days),
        )

    def health_check(self) -> bool:
        """Check API health status.

        Returns:
            True if API is healthy
        """
        try:
            response = self._request("GET", "/health")
            return response.get("status") == "healthy"
        except Exception:
            return False

    def close(self):
        """Close the client session."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class AsyncClient:
    """Asynchronous AMOS Brain API client.

    Usage:
        async with AsyncClient(api_key="your_key") as client:
            result = await client.think("Analyze this")
    """

    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL):
        self.config = ClientConfig(api_key=api_key, base_url=base_url)
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": f"AMOS-SDK-Python/{__import__('amos_sdk').__version__}",
                }
            )
        return self._session

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make async HTTP request."""
        session = await self._get_session()
        url = f"{self.config.base_url}{endpoint}"

        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 500:
                    raise ServerError(f"Server error: {response.status}")
                elif response.status >= 400:
                    text = await response.text()
                    raise ValidationError(f"Request error: {text}")

                return await response.json()

        except aiohttp.ClientTimeout:
            raise ServerError("Request timeout")
        except aiohttp.ClientError as e:
            raise ServerError(f"Connection error: {e}")

    async def think(self, query: str, domain: str = "general") -> ThinkResult:
        """Async think request."""
        data = {"query": query, "domain": domain}
        response = await self._request("POST", "/think", json=data)

        return ThinkResult(
            content=response.get("content", ""),
            reasoning=response.get("reasoning", []),
            confidence=response.get("confidence", 0.0),
            law_compliant=response.get("law_compliant", False),
            domain=response.get("domain", domain),
        )

    async def decide(self, question: str, options: list[str]) -> DecideResult:
        """Async decide request."""
        data = {"question": question, "options": options}
        response = await self._request("POST", "/decide", json=data)

        return DecideResult(
            approved=response.get("approved", False),
            risk_level=response.get("risk_level", "unknown"),
            reasoning=response.get("reasoning", ""),
            decision_id=response.get("decision_id", ""),
        )

    async def get_history(self, limit: int = 100) -> list[QueryRecord]:
        """Async get history."""
        response = await self._request("GET", f"/api/history?limit={limit}")

        records = []
        for item in response.get("history", []):
            records.append(
                QueryRecord(
                    id=item.get("id", 0),
                    endpoint=item.get("endpoint", ""),
                    query=item.get("query", ""),
                    domain=item.get("domain", ""),
                    confidence=item.get("confidence", ""),
                    law_compliant=item.get("law_compliant", False),
                    processing_time_ms=item.get("processing_time_ms", 0),
                    created_at=item.get("created_at", ""),
                )
            )
        return records

    async def get_stats(self, days: int = 7) -> Stats:
        """Async get stats."""
        response = await self._request("GET", f"/api/stats?days={days}")
        data = response.get("stats", {})

        return Stats(
            total_requests=data.get("total_requests", 0),
            avg_response_time_ms=data.get("avg_response_time_ms", 0.0),
            success_rate_percent=data.get("success_rate_percent", 0.0),
            period_days=data.get("period_days", days),
        )

    async def close(self):
        """Close async session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
