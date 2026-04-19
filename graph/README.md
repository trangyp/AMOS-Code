# Knowledge Graph

Neo4j graph database for equation relationships and mathematical knowledge.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 AMOS Knowledge Graph                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Nodes:                                                │
│   • Equation (id, name, formula, category, difficulty) │
│   • Concept (id, name, type)                           │
│                                                         │
│   Relationships:                                        │
│   • DERIVES_FROM (equation → equation)                  │
│   • PREREQUISITE_FOR (concept → equation)               │
│   • RELATED_TO (equation ↔ equation)                    │
│   • USES (equation → concept)                           │
│   • EXAMPLE_OF (equation → concept)                     │
│                                                         │
│   Use Cases:                                            │
│   • Learning paths                                     │
│   • Equation recommendations                            │
│   • Prerequisite checking                              │
│   • Concept exploration                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from graph.neo4j_client import EquationGraph, GraphEquation

# Initialize
graph = EquationGraph("bolt://localhost:7687", "neo4j", "password")

# Create equation node
await graph.create_equation_node(GraphEquation(
    id="quadratic-formula",
    name="Quadratic Formula",
    formula="x = (-b ± √(b² - 4ac)) / 2a",
    category="algebra",
    difficulty=3,
))

# Create concept
await graph.create_concept_node("algebra", "Algebra", "branch")

# Link equation to concept
await graph.create_relationship(
    "quadratic-formula",
    "algebra",
    "EXAMPLE_OF",
)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/equations` | POST | Create equation node |
| `/graph/concepts` | POST | Create concept node |
| `/graph/relationships` | POST | Create relationship |
| `/graph/equations/{id}/related` | GET | Get related equations |
| `/graph/equations/{id}/prerequisites` | GET | Get prerequisites |
| `/graph/equations/{id}/derivatives` | GET | Get derived equations |
| `/graph/path` | GET | Find learning path |
| `/graph/recommendations/{user}` | GET | Get recommendations |
| `/graph/search` | GET | Search graph |
| `/graph/stats` | GET | Graph statistics |
| `/graph/centrality` | GET | Most central equations |

### Examples

```bash
# Create equation
curl -X POST "http://localhost:8000/graph/equations" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "pythagorean-theorem",
    "name": "Pythagorean Theorem",
    "formula": "a² + b² = c²",
    "category": "geometry",
    "difficulty": 2
  }'

# Create relationship
curl -X POST "http://localhost:8000/graph/relationships" \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "pythagorean-theorem",
    "target_id": "euclidean-geometry",
    "rel_type": "EXAMPLE_OF"
  }'

# Find learning path
curl "http://localhost:8000/graph/path?start=algebra&end=calculus&max_depth=5"

# Get recommendations
curl "http://localhost:8000/graph/recommendations/user-123?known=algebra&known=geometry&limit=10"

# Search graph
curl "http://localhost:8000/graph/search?q=derivative&limit=20"
```

## Graph Analytics

### Centrality Analysis

Find most connected equations (hubs of knowledge):

```python
from graph.neo4j_client import GraphAnalytics

analytics = GraphAnalytics(graph)
central = await analytics.get_central_equations(limit=10)
# Returns equations with most connections
```

### Learning Path Analysis

```python
# Find path from basic to advanced
path = await graph.find_learning_path(
    start_concept="linear-equations",
    end_concept="differential-equations",
    max_depth=5,
)
# Returns shortest path through prerequisites
```

### Community Detection

```python
# Find equation clusters
communities = await analytics.get_communities()
# Groups equations by interconnectedness
```

## Deployment

### Docker Compose

```yaml
services:
  neo4j:
    image: neo4j:5.14-community
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
```

### AWS Neptune (Alternative)

```python
from graph.neo4j_client import EquationGraph

# Neptune uses Gremlin, but similar concepts
graph = EquationGraph(
    uri="wss://amos-cluster.cluster-xxx.us-east-1.neptune.amazonaws.com:8182"
)
```

## Data Model

### Equation Node

```cypher
(:Equation {
  id: "quadratic-formula",
  name: "Quadratic Formula",
  formula: "x = (-b ± √(b² - 4ac)) / 2a",
  category: "algebra",
  difficulty: 3,
  created_at: datetime(),
  updated_at: datetime()
})
```

### Concept Node

```cypher
(:Concept {
  id: "algebra",
  name: "Algebra",
  type: "branch",
  created_at: datetime()
})
```

### Relationships

```cypher
// Derivation
(equation1)-[:DERIVES_FROM {method: "algebraic_manipulation"}]->(equation2)

// Prerequisite
(concept)-[:PREREQUISITE_FOR {strength: "required"}]->(equation)

// Related
(equation1)-[:RELATED_TO {similarity: 0.85}]->(equation2)
```

## Query Patterns

### Find Prerequisites Chain

```cypher
MATCH path = (start:Concept {id: "calculus"})-[:PREREQUISITE_FOR*1..5]->(target:Equation)
RETURN path, length(path) as depth
ORDER BY depth
```

### Recommend Based on Knowledge

```cypher
MATCH (u:User {id: $user})-[:KNOWS]->(known:Equation)
MATCH (known)-[:RELATED_TO|PREREQUISITE_FOR]-(candidate:Equation)
WHERE NOT (u)-[:KNOWS]->(candidate)
RETURN candidate, count(*) as relevance
ORDER BY relevance DESC
```

### Shortest Learning Path

```cypher
MATCH path = shortestPath(
  (a:Concept {id: $start})-[:PREREQUISITE_FOR*]-(b:Concept {id: $end})
)
RETURN path
```

## Monitoring

```cypher
// Node counts
MATCH (n) RETURN labels(n), count(n)

// Relationship counts
MATCH ()-[r]->() RETURN type(r), count(r)

// Orphan nodes
MATCH (e:Equation) WHERE NOT (e)-[]-() RETURN e

// Dense nodes
MATCH (e:Equation)-[r]-() 
RETURN e.id, count(r) as degree 
ORDER BY degree DESC LIMIT 10
```

## Integration with Other Systems

### Sync with PostgreSQL

```python
# On equation creation in DB
async def on_equation_created(equation):
    await graph.create_equation_node(GraphEquation(
        id=str(equation.id),
        name=equation.name,
        formula=equation.formula,
        category=equation.category,
        difficulty=equation.difficulty,
    ))
```

### Sync with Kafka Events

```python
@processor.on(EventType.EQUATION_CREATED)
async def index_in_graph(event):
    await graph.create_equation_node(...)

@processor.on(EventType.EQUATION_VERIFIED)
async def mark_verified(event):
    await graph.create_relationship(
        event.aggregate_id,
        "verified-equations",
        "EXAMPLE_OF",
    )
```

---

*Discover the connections in mathematics*
