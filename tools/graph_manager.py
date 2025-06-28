# tools/graph_manager.py
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from neo4j import GraphDatabase
from config import Config
from llm.ollama_client import OllamaClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphManager:
    def __init__(self):
        self.config = Config()
        self.driver = None
        self.llm = OllamaClient()
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.config.NEO4J_URI,
                auth=(self.config.NEO4J_USER, self.config.NEO4J_PASSWORD)
            )
            # Test the connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Neo4j connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Neo4j connection failed: {e}")
            self.driver = None
    
    def extract_entities_with_llm(self, text: str) -> Dict[str, List[str]]:
        """Use LLM to extract entities from text"""
        prompt = f"""
        Extract entities from the following text and categorize them. Return ONLY a JSON object with this structure:
        {{
            "companies": ["list of company names"],
            "cryptocurrencies": ["list of crypto names"],
            "indices": ["list of market indices"],
            "currencies": ["list of currencies"],
            "regulators": ["list of regulatory bodies"],
            "locations": ["list of countries/cities"],
            "topics": ["list of financial topics/themes"]
        }}

        Text to analyze:
        {text[:2000]}

        Rules:
        - Only include relevant entities
        - Use exact names as they appear
        - If a category is empty, use empty array []
        - Return ONLY the JSON, no other text
        """
        
        try:
            response = self.llm.generate(prompt)
            
            if "error" in response:
                logger.error(f"LLM error: {response['error']}")
                return self._fallback_entity_extraction(text)
            
            # Extract JSON from response
            content = response.get('response', '').strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                logger.info(f"✅ LLM extracted entities: {sum(len(v) for v in entities.values())} total")
                return entities
            else:
                logger.warning("⚠️ No JSON found in LLM response")
                return self._fallback_entity_extraction(text)
                
        except Exception as e:
            logger.error(f"Error in LLM entity extraction: {e}")
            return self._fallback_entity_extraction(text)
    
    def extract_relationships_with_llm(self, text: str, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Use LLM to extract relationships between entities"""
        # Flatten entities for context
        all_entities = []
        for category, entity_list in entities.items():
            all_entities.extend(entity_list)
        
        if len(all_entities) < 2:
            return []
        
        prompt = f"""
        Extract relationships between entities from the following text. Return ONLY a JSON array with this structure:
        [
            {{
                "source": "entity name",
                "target": "entity name", 
                "relationship": "relationship type",
                "description": "brief description"
            }}
        ]

        Entities found: {all_entities[:20]}

        Text to analyze:
        {text[:1500]}

        Relationship types to look for:
        - CAUSES: one entity causes/leads to another
        - AFFECTS: one entity affects/influences another
        - REGULATES: regulatory body regulates entity
        - LOCATED_IN: entity is located in place
        - COMPETES_WITH: entities compete with each other
        - PART_OF: entity is part of larger entity
        - SIMILAR_TO: entities are similar/comparable

        Rules:
        - Only include relationships where both entities are in the entities list
        - Use exact entity names as provided
        - Return ONLY the JSON array, no other text
        """
        
        try:
            response = self.llm.generate(prompt)
            
            if "error" in response:
                logger.error(f"LLM error: {response['error']}")
                return []
            
            content = response.get('response', '').strip()
            
            # Try to find JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                relationships = json.loads(json_match.group())
                logger.info(f"✅ LLM extracted relationships: {len(relationships)} total")
                return relationships
            else:
                logger.warning("⚠️ No JSON array found in LLM response")
                return []
                
        except Exception as e:
            logger.error(f"Error in LLM relationship extraction: {e}")
            return []
    
    def _fallback_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback entity extraction using regex patterns"""
        entities = {
            'companies': [],
            'cryptocurrencies': [],
            'indices': [],
            'currencies': [],
            'regulators': [],
            'locations': [],
            'topics': []
        }
        
        # Basic patterns for fallback
        patterns = {
            'companies': r'\b[A-Z]{2,5}\b',  # Stock tickers
            'cryptocurrencies': r'\b(Bitcoin|BTC|Ethereum|ETH)\b',
            'indices': r'\b(S&P 500|NASDAQ|Dow Jones)\b',
            'currencies': r'\b(USD|EUR|GBP|JPY)\b',
            'regulators': r'\b(SEC|CFTC|Federal Reserve|Fed)\b',
            'locations': r'\b(USA|China|Japan|UK|India|Europe|Asia)\b'
        }
        
        for category, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities[category] = list(set(matches))
        
        return entities
    
    def create_graph_from_response(self, query: str, response: Dict[str, Any]) -> bool:
        """Create Neo4j graph from LLM response using LLM for entity/relationship extraction"""
        if not self.driver:
            logger.warning("⚠️ Neo4j not connected, skipping graph creation")
            return False
        
        try:
            # Extract text content from response
            text_content = self._extract_text_from_response(response)
            if not text_content:
                logger.warning("⚠️ No text content found in response")
                return False
            
            # Use LLM to extract entities and relationships
            entities = self.extract_entities_with_llm(text_content)
            relationships = self.extract_relationships_with_llm(text_content, entities)
            
            # Create graph in Neo4j
            with self.driver.session() as session:
                # Create query node
                query_id = self._create_query_node(session, query, response)
                
                # Create entity nodes
                entity_nodes = self._create_entity_nodes(session, entities, query_id)
                
                # Create relationship edges
                self._create_relationship_edges(session, relationships, entity_nodes, query_id)
                
                # Create analysis summary
                self._create_analysis_summary(session, response, query_id)
            
            total_entities = sum(len(entity_list) for entity_list in entities.values())
            logger.info(f"✅ Graph created successfully: {total_entities} entities, {len(relationships)} relationships")
            return True
            
        except Exception as e:
            logger.error(f"Error creating graph: {e}")
            return False
    
    def _extract_text_from_response(self, response: Dict[str, Any]) -> str:
        """Extract text content from response"""
        text_parts = []
        
        # Extract from analysis
        if 'analysis' in response:
            analysis = response['analysis']
            if isinstance(analysis, str):
                text_parts.append(analysis)
            elif isinstance(analysis, dict):
                text_parts.append(str(analysis))
        
        # Extract from transcript
        if 'transcript' in response and 'text' in response['transcript']:
            text_parts.append(response['transcript']['text'])
        
        # Extract from key insights
        if 'key_insights' in response:
            insights = response['key_insights']
            if isinstance(insights, dict):
                if 'key_points' in insights:
                    text_parts.extend(insights['key_points'])
        
        # Extract from additional insights
        if 'additional_insights' in response:
            additional = response['additional_insights']
            if isinstance(additional, dict):
                text_parts.append(str(additional))
        
        return ' '.join(text_parts)
    
    def _create_query_node(self, session, query: str, response: Dict[str, Any]) -> str:
        """Create query node in Neo4j"""
        intent = response.get('intent', 'unknown')
        timestamp = response.get('timestamp', datetime.now().isoformat())
        
        cypher = """
        CREATE (q:Query {
            id: randomUUID(),
            text: $query_text,
            intent: $intent,
            timestamp: datetime($timestamp),
            created_at: datetime()
        })
        RETURN q.id as query_id
        """
        
        result = session.run(cypher, query_text=query, intent=intent, timestamp=timestamp)
        return result.single()['query_id']
    
    def _create_entity_nodes(self, session, entities: Dict[str, List[str]], query_id: str) -> Dict[str, str]:
        """Create entity nodes and connect to query"""
        entity_nodes = {}
        
        for category, entity_list in entities.items():
            for entity in entity_list:
                if entity and len(entity) > 1:  # Skip empty or single character entities
                    # Create entity node
                    cypher = """
                    MERGE (e:Entity {
                        name: $entity_name,
                        category: $category
                    })
                    ON CREATE SET e.created_at = datetime()
                    ON MATCH SET e.last_seen = datetime()
                    RETURN e.name as entity_name
                    """
                    
                    result = session.run(cypher, entity_name=entity, category=category)
                    entity_name = result.single()['entity_name']
                    entity_nodes[entity] = entity_name
                    
                    # Connect to query
                    cypher = """
                    MATCH (q:Query {id: $query_id})
                    MATCH (e:Entity {name: $entity_name})
                    MERGE (q)-[:MENTIONS]->(e)
                    """
                    
                    session.run(cypher, query_id=query_id, entity_name=entity_name)
        
        return entity_nodes
    
    def _create_relationship_edges(self, session, relationships: List[Dict[str, Any]], 
                                 entity_nodes: Dict[str, str], query_id: str):
        """Create relationship edges between entities"""
        for rel in relationships:
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('relationship', 'RELATES_TO')
            description = rel.get('description', '')
            
            # Only create if both entities exist
            if source in entity_nodes and target in entity_nodes:
                cypher = """
                MATCH (s:Entity {name: $source_name})
                MATCH (t:Entity {name: $target_name})
                MERGE (s)-[r:RELATES_TO {
                    type: $rel_type,
                    description: $description,
                    created_at: datetime()
                }]->(t)
                """
                
                session.run(cypher, source_name=source, target_name=target, 
                          rel_type=rel_type, description=description)
    
    def _create_analysis_summary(self, session, response: Dict[str, Any], query_id: str):
        """Create analysis summary node"""
        summary_data = {
            'intent': response.get('intent', 'unknown'),
            'has_market_data': 'market_data' in response,
            'has_transcript': 'transcript' in response,
            'has_sentiment': 'key_insights' in response and 'sentiment' in response['key_insights'],
            'word_count': response.get('transcript', {}).get('word_count', 0),
            'symbols_found': len(response.get('market_data', {}).get('symbols_found', [])),
            'news_count': response.get('market_data', {}).get('news_count', 0)
        }
        
        cypher = """
        MATCH (q:Query {id: $query_id})
        CREATE (a:Analysis {
            intent: $intent,
            has_market_data: $has_market_data,
            has_transcript: $has_transcript,
            has_sentiment: $has_sentiment,
            word_count: $word_count,
            symbols_found: $symbols_found,
            news_count: $news_count,
            created_at: datetime()
        })
        CREATE (q)-[:HAS_ANALYSIS]->(a)
        """
        
        session.run(cypher, query_id=query_id, **summary_data)
    
    def search_entities(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for entities in the graph"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                cypher = """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($search_term)
                RETURN e.name as name, e.category as category, e.created_at as created_at
                ORDER BY e.created_at DESC
                LIMIT 20
                """
                
                result = session.run(cypher, search_term=search_term)
                entities = [{"name": record["name"], "category": record["category"], 
                           "created_at": record["created_at"]} for record in result]
                
                return entities
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get Neo4j graph statistics"""
        if not self.driver:
            return {"error": "Neo4j not connected"}
        
        try:
            with self.driver.session() as session:
                # Get node counts
                node_stats = session.run("""
                MATCH (n)
                RETURN labels(n) as labels, count(n) as count
                """)
                
                # Get relationship counts
                rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                """)
                
                # Get recent queries
                recent_queries = session.run("""
                MATCH (q:Query)
                RETURN q.text as query, q.intent as intent, q.timestamp as timestamp
                ORDER BY q.timestamp DESC
                LIMIT 10
                """)
                
                return {
                    "node_counts": {record["labels"][0]: record["count"] for record in node_stats},
                    "relationship_counts": {record["type"]: record["count"] for record in rel_stats},
                    "recent_queries": [{"query": record["query"], "intent": record["intent"], 
                                       "timestamp": record["timestamp"]} for record in recent_queries]
                }
                
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {"error": str(e)}
    
    def clear_graph(self) -> bool:
        """Clear all data from Neo4j"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("🗑️ Neo4j graph cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("🔌 Neo4j connection closed")