# AMOS Fast Web Runtime Guide

## Overview

The Fast Web Runtime implements the equation:

```
WebQuery → RankFast → ReadLittle → AnswerEarly → DeepenOnlyIfNeeded
```

This transforms slow document-understanding web crawling into high-precision retrieval under tight budgets.

## Core Problem

**Traditional web crawling is slow:**

```
T_web = T_dns + T_connect + T_download + T_render + T_extract + 
        T_boilerplate_strip + T_chunk + T_rank + T_read + T_verify
```

This is much slower than internal reasoning because:
1. Network latency dominates
2. Too many pages opened
3. Rendering overhead (JS-heavy pages)
4. Boilerplate pollution
5. Full-read behavior without early exit
6. No domain prioritization
7. Verification cost overruns

## The Solution

### Two-Stage Runtime

#### Fast Path (Default)
```
query → search → top 3 → snippet rank → open 1-2 → answer
```

Time target: **< 2 seconds**

#### Deep Path (Auto-escalation)
```
query → search → authoritative shortlist → local compare → verify → answer
```

Time target: **< 5 seconds**

### Source Ranking

```
Rank = Authority × QueryFit × Freshness × StructureQuality - RenderCost - BoilerplateCost
```

Authority tiers:
- **Official** (4): docs.*, api.*, developer.*
- **Authoritative** (3): Established domains (.edu, .gov, major tech)
- **Established** (2): Known publications
- **Unknown** (1): New sources
- **Suspicious** (0): Low trust

### Hard Browsing Budgets

```json
{
  "max_search_queries": 2,
  "max_page_opens": 4,
  "max_deep_reads": 2,
  "max_verification_reads": 2,
  "max_total_time_ms": 5000
}
```

### Early-Sufficiency Gate

Stop when:
```
Confidence ≥ τ_c ∧ SourceQuality ≥ τ_q ∧ CrossCheck ≥ τ_x
```

Defaults:
- τ_c (confidence): 0.85
- τ_q (source quality): 0.70
- τ_x (cross-check): 0.60

### Aggressive Caching

Four-tier cache:
1. **Domain cache**: Per-domain result lists
2. **Page cache**: Full page content
3. **Extract cache**: Strategy-specific extractions
4. **Query cache**: Search result lists

TTL: 1 hour default

## API Usage

### Python SDK

```python
from amos_fast_web_runtime import FastWebRuntime, WebBudgets

# Simple query
result = await web_query("What is quantum computing?")
print(result["answer"])

# With custom budgets
runtime = FastWebRuntime(
    budgets=WebBudgets(
        max_search_queries=3,
        max_page_opens=6,
        max_deep_reads=3,
    )
)

result = await runtime.query(
    "Python asyncio best practices",
    path="auto",  # or "fast" or "deep"
)
```

### REST API

```bash
# POST query with budgets
curl -X POST http://localhost:8000/web/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Rust memory safety",
    "path": "auto",
    "max_search_queries": 2,
    "max_page_opens": 4,
    "confidence_threshold": 0.85
  }'

# Simple GET query
curl "http://localhost:8000/web/query?q=fastapi+async"
```

Response:
```json
{
  "answer": "FastAPI supports async/await for high-performance...",
  "path": "fast_with_fetch",
  "time_ms": 1450,
  "pages_fetched": 1,
  "confidence": 0.88,
  "sources": [
    {
      "url": "https://fastapi.tiangolo.com/async/",
      "title": "Async - FastAPI",
      "source_rank_score": 0.92
    }
  ]
}
```

## Extraction Strategies

1. **SNIPPET_ONLY**: Search snippet (fastest, no fetch)
2. **MAIN_CONTENT**: Article/main extraction (default)
3. **STRUCTURED**: Tables, lists, code blocks
4. **FULL_TEXT**: Complete page text (slowest)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastWebRuntime                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   Search    │→ │ Source Rank  │→ │ Budget Enforcer  │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Cache (Domain | Page | Extract | Query)      │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    Sufficiency Gate (Confidence × Quality × Cross)  │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Content Extractor (Main | Structured | Full) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Fast path latency | < 2s | End-to-end with fetch |
| Deep path latency | < 5s | With verification |
| Cache hit rate | > 70% | Query + page cache |
| Pages per query | < 2 avg | Production telemetry |
| Answer confidence | > 0.80 | Sufficiency gate |

## Integration

### With FastAPI Gateway

```python
from backend.api.web_runtime import router as web_router

app.include_router(web_router)
```

### With Brain/Cascade

```python
# In brain reasoning loop
if requires_external_knowledge(query):
    web_result = await fast_web_runtime.query(query, path="fast")
    context += web_result["answer"]
```

## Configuration

Environment variables:
```bash
WEB_RUNTIME_CACHE_TTL=3600
WEB_RUNTIME_MAX_TIMEOUT=10
WEB_RUNTIME_USER_AGENT="AMOS-FastWeb/1.0"
```

## Dependencies

```bash
pip install httpx beautifulsoup4
```

## Status

✅ **Operational**
- Fast path: < 2s target
- Deep path: < 5s target
- Aggressive caching
- Early sufficiency gates
- Hard browsing budgets
