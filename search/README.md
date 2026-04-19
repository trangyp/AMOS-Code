# Search & Discovery

Full-text search for AMOS Equation System with Elasticsearch.

## Features

- **Full-Text Search**: Search across name, formula, description
- **Fuzzy Matching**: Typo-tolerant search with AUTO fuzziness
- **Faceted Search**: Filter by tags, category, author, verification status
- **Auto-Complete**: Suggestions as you type
- **Similar Equations**: Find related equations using More Like This
- **Synonym Support**: "derivative" matches "differentiate"
- **Highlighting**: Marked search terms in results

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 AMOS Search Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   User Query  →  Elasticsearch  →  Results + Facets      │
│      ↓              ↓                    ↓              │
│   Suggest API   Index (3 shards)      Aggregations       │
│                                                         │
│   Index Fields:                                         │
│   • name (boost 3x)                                    │
│   • formula (boost 2x)                                  │
│   • description                                         │
│   • tags (keyword)                                      │
│   • category (keyword)                                  │
│   • author (keyword)                                    │
│   • verified (boolean)                                  │
│   • difficulty (integer)                                │
│   • suggest (completion)                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from search.engine import EquationSearchEngine

# Initialize
search = EquationSearchEngine("http://localhost:9200")
await search.initialize()

# Index an equation
await search.index_equation({
    "id": "123",
    "name": "Quadratic Formula",
    "formula": "x = (-b ± √(b² - 4ac)) / 2a",
    "description": "Solutions to quadratic equation ax² + bx + c = 0",
    "tags": ["algebra", "quadratic", "roots"],
    "author": "Mathematician",
})

# Search
results = await search.search(
    query="quadratic",
    filters={"tags": ["algebra"]},
    sort_by="relevance"
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search/` | POST | Main search with filters |
| `/search/` | GET | Browser-friendly search |
| `/search/suggest` | GET | Auto-complete |
| `/search/similar/{id}` | GET | Similar equations |
| `/search/facets/tags` | GET | Popular tags |
| `/search/admin/health` | GET | ES health status |

### Search Examples

```bash
# Basic search
curl "http://localhost:8000/search/?q=derivative"

# Filtered search
curl "http://localhost:8000/search/?q=formula&tags=algebra&verified=true"

# Auto-complete
curl "http://localhost:8000/search/suggest?q=quad"

# Similar equations
curl "http://localhost:8000/search/similar/123"

# POST search with body
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "integration",
    "tags": ["calculus"],
    "sort_by": "usage",
    "page": 1,
    "per_page": 20
  }'
```

## Sort Options

| Option | Description |
|--------|-------------|
| `relevance` | Best match (default) |
| `newest` | Recently created |
| `oldest` | Oldest first |
| `name_asc` | Name A-Z |
| `name_desc` | Name Z-A |
| `usage` | Most used |
| `difficulty` | Easiest first |

## Facets

Search response includes aggregation counts:

```json
{
  "facets": {
    "tags": {
      "algebra": 42,
      "calculus": 38,
      "geometry": 15
    },
    "categories": {
      "basic": 25,
      "advanced": 18
    },
    "authors": {
      "Newton": 10,
      "Euler": 8
    }
  }
}
```

## Synonyms

Configured synonyms for better discovery:
- derivative ↔ differentiate ↔ d/dx
- integral ↔ integration ↔ ∫
- quadratic ↔ second-degree

## Index Sync

Keep search index synchronized with database:

```python
from search.engine import IndexSync

sync = IndexSync(search_engine)

# On equation creation
await sync.on_equation_created(equation_dict)

# On equation update
await sync.on_equation_updated(equation_dict)

# On equation deletion
await sync.on_equation_deleted(equation_id)
```

## Deployment

### AWS OpenSearch

```bash
# Deploy with Terraform
cd terraform
terraform apply -target=aws_opensearch_domain.amos_search

# Output endpoint
terraform output elasticsearch_endpoint
```

### Local Development

```bash
# Start Elasticsearch with Docker
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.0

# Verify
curl http://localhost:9200/_cluster/health
```

## Performance

- Index sharding: 3 shards for parallelism
- Replicas: 1 replica for failover
- Caching: ES query cache for repeated searches
- Pagination: Deep pagination with `search_after`

## Monitoring

```bash
# Index stats
curl http://localhost:9200/equations/_stats

# Query performance
curl http://localhost:9200/_nodes/stats/indices/search

# Health check
python -c "from search.engine import EquationSearchEngine; import asyncio; s = EquationSearchEngine(); print(asyncio.run(s.health_check()))"
```

---

*Find any equation, instantly*
