"""AMOS Equation System - Neo4j Graph Database.

Graph database for equation relationships and knowledge graph:
- Equation dependency relationships
- Concept hierarchies
- Mathematical knowledge graph
- Path finding between concepts
- Recommendation engine

Author: AMOS Data Engineering Team
Version: 2.0.0
"""

from dataclasses import dataclass
from typing import Any

from neo4j import AsyncGraphDatabase


@dataclass
class GraphEquation:
    """Equation node in graph."""

    id: str
    name: str
    formula: str
    category: str
    difficulty: int


@dataclass
class Relationship:
    """Relationship between equations/concepts."""

    source_id: str
    target_id: str
    rel_type: str  # DERIVES_FROM, RELATED_TO, PREREQUISITE_FOR, etc.
    properties: Dict[str, Any]


@dataclass
class ConceptPath:
    """Path through the knowledge graph."""

    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    length: int


class EquationGraph:
    """Neo4j graph database client for equation relationships."""

    def __init__(
        self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"
    ):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) -> None:
        """Close database connection."""
        await self.driver.close()

    async def create_equation_node(self, equation: GraphEquation) -> None:
        """Create or update equation node."""
        query = """
        MERGE (e:Equation {id: $id})
        SET e.name = $name,
            e.formula = $formula,
            e.category = $category,
            e.difficulty = $difficulty,
            e.updated_at = datetime()
        RETURN e
        """

        async with self.driver.session() as session:
            await session.run(
                query,
                {
                    "id": equation.id,
                    "name": equation.name,
                    "formula": equation.formula,
                    "category": equation.category,
                    "difficulty": equation.difficulty,
                },
            )

    async def create_concept_node(self, concept_id: str, name: str, concept_type: str) -> None:
        """Create mathematical concept node."""
        query = """
        MERGE (c:Concept {id: $id})
        SET c.name = $name,
            c.type = $type,
            c.updated_at = datetime()
        RETURN c
        """

        async with self.driver.session() as session:
            await session.run(
                query,
                {
                    "id": concept_id,
                    "name": name,
                    "type": concept_type,
                },
            )

    async def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: dict = None,
    ) -> None:
        """Create relationship between nodes."""
        props = properties or {}

        query = f"""
        MATCH (a) WHERE a.id = $source_id
        MATCH (b) WHERE b.id = $target_id
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $properties,
            r.created_at = datetime()
        RETURN r
        """

        async with self.driver.session() as session:
            await session.run(
                query,
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "properties": props,
                },
            )

    async def get_related_equations(
        self,
        equation_id: str,
        rel_type: str = None,
        depth: int = 1,
    ) -> list[dict[str, Any]]:
        """Get equations related to given equation."""
        if rel_type:
            query = (
                """
            MATCH (e:Equation {id: $id})-[r:%s]-(related:Equation)
            RETURN related, r, type(r) as rel_type
            LIMIT 50
            """
                % rel_type
            )
        else:
            query = (
                """
            MATCH path = (e:Equation {id: $id})-[r*1..%d]-(related:Equation)
            WHERE e <> related
            RETURN related, relationships(path) as rels, length(path) as distance
            ORDER BY distance
            LIMIT 50
            """
                % depth
            )

        async with self.driver.session() as session:
            result = await session.run(query, {"id": equation_id})
            records = await result.data()

            equations = []
            for record in records:
                eq = {
                    "id": record["related"]["id"],
                    "name": record["related"]["name"],
                    "formula": record["related"]["formula"],
                    "category": record["related"]["category"],
                    "difficulty": record["related"]["difficulty"],
                }
                if "distance" in record:
                    eq["distance"] = record["distance"]
                equations.append(eq)

            return equations

    async def find_learning_path(
        self,
        start_concept: str,
        end_concept: str,
        max_depth: int = 5,
    ) -> Optional[ConceptPath]:
        """Find learning path between concepts using shortest path."""
        query = (
            """
        MATCH path = shortestPath(
            (start:Concept {id: $start})-[:PREREQUISITE_FOR|RELATED_TO*1..%d]-(end:Concept {id: $end})
        )
        RETURN path, length(path) as path_length
        """
            % max_depth
        )

        async with self.driver.session() as session:
            result = await session.run(
                query,
                {
                    "start": start_concept,
                    "end": end_concept,
                },
            )
            record = await result.single()

            if not record:
                return None

            path = record["path"]
            nodes = [
                {"id": n["id"], "name": n["name"], "type": n.get("type", "equation")}
                for n in path.nodes
            ]
            relationships = [{"type": r.type, "properties": dict(r)} for r in path.relationships]

            return ConceptPath(
                nodes=nodes,
                relationships=relationships,
                length=record["path_length"],
            )

    async def get_prerequisites(self, equation_id: str) -> list[dict[str, Any]]:
        """Get prerequisite equations/concepts."""
        query = """
        MATCH (prereq)-[:PREREQUISITE_FOR]->(e:Equation {id: $id})
        RETURN prereq
        ORDER BY prereq.difficulty
        """

        async with self.driver.session() as session:
            result = await session.run(query, {"id": equation_id})
            records = await result.data()

            return [
                {
                    "id": r["prereq"]["id"],
                    "name": r["prereq"]["name"],
                    "type": r["prereq"].get("type", "equation"),
                }
                for r in records
            ]

    async def get_derivatives(self, equation_id: str) -> list[dict[str, Any]]:
        """Get equations derived from this equation."""
        query = """
        MATCH (e:Equation {id: $id})-[:DERIVES_FROM]->(derived:Equation)
        RETURN derived
        """

        async with self.driver.session() as session:
            result = await session.run(query, {"id": equation_id})
            records = await result.data()

            return [
                {
                    "id": r["derived"]["id"],
                    "name": r["derived"]["name"],
                    "formula": r["derived"]["formula"],
                }
                for r in records
            ]

    async def recommend_for_user(
        self,
        user_id: str,
        known_equations: List[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Recommend equations based on known equations (collaborative filtering)."""
        query = """
        MATCH (u:User {id: $user_id})-[:KNOWS]->(known:Equation)
        WHERE known.id IN $known_ids
        MATCH (known)-[:RELATED_TO|PREREQUISITE_FOR]-(candidate:Equation)
        WHERE NOT (u)-[:KNOWS]->(candidate)
        RETURN candidate, count(*) as relevance
        ORDER BY relevance DESC, candidate.difficulty ASC
        LIMIT $limit
        """

        async with self.driver.session() as session:
            result = await session.run(
                query,
                {
                    "user_id": user_id,
                    "known_ids": known_equations,
                    "limit": limit,
                },
            )
            records = await result.data()

            return [
                {
                    "id": r["candidate"]["id"],
                    "name": r["candidate"]["name"],
                    "formula": r["candidate"]["formula"],
                    "relevance": r["relevance"],
                }
                for r in records
            ]

    async def search_concepts(self, query_text: str, limit: int = 20) -> list[dict[str, Any]]:
        """Full-text search on concepts and equations."""
        query = """
        CALL db.index.fulltext.queryNodes('conceptSearch', $query) YIELD node, score
        RETURN node, score
        ORDER BY score DESC
        LIMIT $limit
        """

        async with self.driver.session() as session:
            try:
                result = await session.run(query, {"query": query_text, "limit": limit})
                records = await result.data()

                return [
                    {
                        "id": r["node"]["id"],
                        "name": r["node"]["name"],
                        "type": r["node"].get("type", "unknown"),
                        "score": r["score"],
                    }
                    for r in records
                ]
            except Exception:
                # Fallback if fulltext index not available
                fallback_query = """
                MATCH (n)
                WHERE n.name CONTAINS $query OR n.id CONTAINS $query
                RETURN n as node, 1.0 as score
                LIMIT $limit
                """
                result = await session.run(fallback_query, {"query": query_text, "limit": limit})
                records = await result.data()
                return [
                    {
                        "id": r["node"]["id"],
                        "name": r["node"]["name"],
                        "type": r["node"].get("type", "unknown"),
                        "score": r["score"],
                    }
                    for r in records
                ]

    async def get_knowledge_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        queries = {
            "equations": "MATCH (e:Equation) RETURN count(e) as count",
            "concepts": "MATCH (c:Concept) RETURN count(c) as count",
            "relationships": "MATCH ()-[r]->() RETURN count(r) as count",
            "categories": "MATCH (e:Equation) RETURN count(DISTINCT e.category) as count",
        }

        stats = {}
        async with self.driver.session() as session:
            for key, query in queries.items():
                result = await session.run(query)
                record = await result.single()
                stats[key] = record["count"]

        return stats

    async def create_indexes(self) -> None:
        """Create indexes for performance."""
        indexes = [
            "CREATE INDEX equation_id IF NOT EXISTS FOR (e:Equation) ON (e.id)",
            "CREATE INDEX equation_category IF NOT EXISTS FOR (e:Equation) ON (e.category)",
            "CREATE INDEX concept_id IF NOT EXISTS FOR (c:Concept) ON (c.id)",
        ]

        async with self.driver.session() as session:
            for index_query in indexes:
                try:
                    await session.run(index_query)
                except Exception:
                    pass  # Index may already exist

    async def delete_equation(self, equation_id: str) -> None:
        """Delete equation node and its relationships."""
        query = """
        MATCH (e:Equation {id: $id})
        DETACH DELETE e
        """

        async with self.driver.session() as session:
            await session.run(query, {"id": equation_id})

    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as health")
                record = await result.single()
                return {
                    "status": "healthy",
                    "connected": record["health"] == 1,
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Graph analytics
class GraphAnalytics:
    """Analytics on the knowledge graph."""

    def __init__(self, graph: EquationGraph):
        self.graph = graph

    async def get_central_equations(self, limit: int = 10) -> list[dict[str, Any]]:
        """Find most central equations by relationship count (degree centrality)."""
        query = """
        MATCH (e:Equation)-[r]-()
        RETURN e.id as id, e.name as name, count(r) as degree
        ORDER BY degree DESC
        LIMIT $limit
        """

        async with self.graph.driver.session() as session:
            result = await session.run(query, {"limit": limit})
            records = await result.data()
            return [{"id": r["id"], "name": r["name"], "connections": r["degree"]} for r in records]

    async def get_communities(self) -> list[dict[str, Any]]:
        """Detect equation communities using Louvain (if available)."""
        query = """
        CALL gds.louvain.stream('equation-graph')
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).id as equation_id,
               gds.util.asNode(nodeId).name as name,
               communityId
        ORDER BY communityId
        """

        try:
            async with self.graph.driver.session() as session:
                result = await session.run(query)
                records = await result.data()

                communities = {}
                for r in records:
                    cid = r["communityId"]
                    if cid not in communities:
                        communities[cid] = []
                    communities[cid].append({"id": r["equation_id"], "name": r["name"]})

                return [{"community_id": k, "members": v} for k, v in communities.items()]
        except Exception:
            return []  # GDS not available

    async def get_difficulty_progression(self) -> list[dict[str, Any]]:
        """Analyze difficulty progression paths."""
        query = """
        MATCH path = (start:Equation)-[:PREREQUISITE_FOR*3..5]->(end:Equation)
        WHERE start.difficulty < end.difficulty
        RETURN start.name as start, end.name as end,
               length(path) as steps,
               [n in nodes(path) | n.difficulty] as difficulties
        ORDER BY steps DESC
        LIMIT 20
        """

        async with self.graph.driver.session() as session:
            result = await session.run(query)
            records = await result.data()
            return [
                {
                    "start": r["start"],
                    "end": r["end"],
                    "steps": r["steps"],
                    "difficulties": r["difficulties"],
                }
                for r in records
            ]
