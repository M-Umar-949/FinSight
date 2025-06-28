# tools/cache.py
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryCache:
    def __init__(self):
        self.config = Config()
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
        
        # Common stop words to remove for better matching
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
            'to', 'was', 'will', 'with', 'can', 'you', 'tell', 'me', 'about',
            'what', 'how', 'when', 'where', 'why', 'which', 'who', 'this',
            'these', 'those', 'have', 'had', 'do', 'does', 'did', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'will'
        }
        
        # Common financial terms to normalize
        self.financial_synonyms = {
            'price': ['cost', 'value', 'worth', 'rate'],
            'stock': ['shares', 'equity', 'ticker'],
            'crypto': ['cryptocurrency', 'bitcoin', 'btc', 'digital currency'],
            'market': ['trading', 'exchange', 'financial market'],
            'news': ['update', 'announcement', 'report', 'information'],
            'earnings': ['profit', 'revenue', 'income', 'financial results'],
            'regulation': ['regulatory', 'compliance', 'legal', 'policy'],
            'weather': ['climate', 'temperature', 'forecast', 'conditions']
        }
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.config.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.config.MONGODB_DATABASE]
            self.collection = self.db[self.config.MONGODB_CACHE_COLLECTION]
            
            # Create indexes for better performance
            self.collection.create_index([("query_hash", 1)], unique=True)
            self.collection.create_index([("normalized_keywords", 1)])  # New index for keyword matching
            self.collection.create_index([("created_at", 1)], expireAfterSeconds=self.config.CACHE_TTL)
            
            logger.info("✅ MongoDB cache connection established")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing stop words and standardizing format"""
        # Convert to lowercase and remove extra whitespace
        normalized = query.lower().strip()
        
        # Remove punctuation except for important symbols
        normalized = re.sub(r'[^\w\s$%]', ' ', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove stop words
        words = normalized.split()
        filtered_words = [word for word in words if word not in self.stop_words]
        
        return ' '.join(filtered_words)
    
    def _extract_key_entities(self, query: str) -> Dict[str, Any]:
        """Extract key entities from query for intelligent matching"""
        normalized = self._normalize_query(query)
        words = normalized.split()
        
        entities = {
            'companies': [],
            'locations': [],
            'topics': [],
            'time_periods': [],
            'keywords': [],
            'actions': [],
            'numbers': []
        }
        
        # Enhanced company/ticker detection
        for word in words:
            # Stock tickers (1-5 letters, all caps)
            if word.isupper() and 1 <= len(word) <= 5 and word.isalpha():
                entities['companies'].append(word)
            # Common company names
            elif word.lower() in ['apple', 'tesla', 'microsoft', 'google', 'amazon', 'facebook', 'meta', 'netflix', 'nvidia', 'amd', 'intel']:
                entities['companies'].append(word.lower())
            # Time periods
            elif word in ['today', 'yesterday', 'tomorrow', 'week', 'month', 'year', 'quarter', 'q1', 'q2', 'q3', 'q4']:
                entities['time_periods'].append(word)
            # Locations
            elif word in ['pakistan', 'china', 'usa', 'uk', 'india', 'japan', 'europe', 'asia', 'america']:
                entities['locations'].append(word)
            # Numbers and percentages
            elif re.match(r'^\d+\.?\d*%?$', word):
                entities['numbers'].append(word)
            # Actions
            elif word in ['dropping', 'falling', 'rising', 'up', 'down', 'crash', 'rally', 'surge', 'plunge', 'gain', 'loss']:
                entities['actions'].append(word)
            else:
                entities['keywords'].append(word)
        
        # Enhanced topic extraction with synonyms
        for word in words:
            for topic, synonyms in self.financial_synonyms.items():
                if word in synonyms or word == topic:
                    entities['topics'].append(topic)
                    break
        
        # Add common financial topics
        financial_topics = {
            'earnings': ['earnings', 'profit', 'revenue', 'income', 'quarterly', 'results'],
            'crypto': ['crypto', 'bitcoin', 'btc', 'ethereum', 'eth', 'blockchain', 'digital'],
            'stocks': ['stock', 'shares', 'equity', 'market', 'trading', 'investment'],
            'regulation': ['regulation', 'regulatory', 'sec', 'cftc', 'compliance', 'legal'],
            'economy': ['economy', 'economic', 'gdp', 'inflation', 'interest', 'rates'],
            'forex': ['forex', 'currency', 'dollar', 'euro', 'yen', 'pound']
        }
        
        for topic, keywords in financial_topics.items():
            if any(keyword in words for keyword in keywords):
                entities['topics'].append(topic)
        
        return entities
    
    def _generate_semantic_key(self, query: str, intent: str) -> str:
        """Generate semantic key based on normalized query and key entities"""
        normalized = self._normalize_query(query)
        entities = self._extract_key_entities(query)
        
        # Create semantic key components
        components = [
            intent,
            normalized,
            '|'.join(sorted(entities['companies'])),
            '|'.join(sorted(entities['topics'])),
            '|'.join(sorted(entities['locations']))
        ]
        
        # Join components and create hash
        semantic_string = '::'.join(components)
        return hashlib.md5(semantic_string.encode('utf-8')).hexdigest()
    
    def _generate_query_hash(self, query: str, intent: str) -> str:
        """Generate a unique hash for the query and intent combination"""
        # Use semantic key for intelligent matching
        return self._generate_semantic_key(query, intent)
    
    def get_cached_response(self, query: str, intent: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response for a query with intelligent matching"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return None
        
        try:
            query_hash = self._generate_query_hash(query, intent)
            normalized = self._normalize_query(query)
            entities = self._extract_key_entities(query)
            
            # First try exact hash match
            cached_doc = self.collection.find_one({"query_hash": query_hash})
            
            if cached_doc:
                # Check if cache is still valid
                created_at = cached_doc.get('created_at')
                if created_at:
                    age = datetime.utcnow() - created_at
                    if age.total_seconds() < self.config.CACHE_TTL:
                        logger.info(f"✅ Cache hit (exact match) for query: {query[:50]}...")
                        return cached_doc.get('response')
                    else:
                        # Cache expired, remove it
                        self.collection.delete_one({"query_hash": query_hash})
                        logger.info(f"🗑️ Expired cache removed for query: {query[:50]}...")
            
            # Try semantic matching if no exact match
            logger.info(f"🔍 Attempting semantic matching for: {query[:50]}...")
            logger.info(f"   Entities: {entities}")
            
            # Look for similar queries with same intent and recent cache entries
            similar_queries = self.collection.find({
                "intent": intent,
                "created_at": {"$gte": datetime.utcnow() - timedelta(seconds=self.config.CACHE_TTL)}
            })
            
            best_match = None
            best_score = 0
            match_details = ""
            
            for doc in similar_queries:
                if doc.get('entities'):
                    # Calculate similarity score
                    score = self._calculate_similarity(entities, doc['entities'])
                    
                    if score > best_score and score >= 0.6:  # Lowered threshold to 60%
                        best_score = score
                        best_match = doc
                        match_details = f"Matched with: {doc.get('original_query', 'Unknown')[:50]}..."
            
            if best_match:
                logger.info(f"✅ Cache hit (semantic match, {best_score:.2f}) for query: {query[:50]}...")
                logger.info(f"   {match_details}")
                
                # Add cache hit indicator to response
                response = best_match.get('response', {})
                if isinstance(response, dict):
                    response['cached'] = True
                    response['cache_similarity'] = best_score
                    response['original_query'] = best_match.get('original_query', query)
                
                return response
            
            logger.info(f"❌ Cache miss for query: {query[:50]}...")
            logger.info(f"   No similar queries found with score >= 0.6")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
            return None
    
    def _calculate_similarity(self, entities1: Dict[str, Any], entities2: Dict[str, Any]) -> float:
        """Calculate enhanced similarity between two entity sets"""
        total_score = 0
        max_possible_score = 0
        
        # Weight different entity types
        weights = {
            'companies': 0.4,    # Companies are most important
            'topics': 0.3,       # Topics are very important
            'actions': 0.2,      # Actions (up/down) are important
            'locations': 0.1,    # Locations are less important
            'time_periods': 0.1, # Time periods are less important
            'keywords': 0.05     # General keywords are least important
        }
        
        for entity_type, weight in weights.items():
            set1 = set(entities1.get(entity_type, []))
            set2 = set(entities2.get(entity_type, []))
            
            if set1 or set2:  # Only count if at least one set has entities
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                
                if union > 0:
                    jaccard_similarity = intersection / union
                    total_score += jaccard_similarity * weight
                    max_possible_score += weight
        
        # Bonus for having same number of companies (indicates same focus)
        companies1 = set(entities1.get('companies', []))
        companies2 = set(entities2.get('companies', []))
        if companies1 and companies2 and companies1 == companies2:
            total_score += 0.1  # Bonus for exact company match
            max_possible_score += 0.1
        
        # Bonus for having same topics
        topics1 = set(entities1.get('topics', []))
        topics2 = set(entities2.get('topics', []))
        if topics1 and topics2 and topics1 == topics2:
            total_score += 0.05  # Bonus for exact topic match
            max_possible_score += 0.05
        
        return total_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def cache_response(self, query: str, intent: str, response: Dict[str, Any]) -> bool:
        """Cache a response for future use with intelligent matching"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return False
        
        try:
            query_hash = self._generate_query_hash(query, intent)
            normalized = self._normalize_query(query)
            entities = self._extract_key_entities(query)
            
            # Prepare cache document
            cache_doc = {
                "query_hash": query_hash,
                "original_query": query,
                "normalized_query": normalized,
                "intent": intent,
                "entities": entities,
                "response": response,
                "created_at": datetime.utcnow(),
                "cache_ttl": self.config.CACHE_TTL
            }
            
            # Use upsert to handle duplicate keys
            result = self.collection.update_one(
                {"query_hash": query_hash},
                {"$set": cache_doc},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"💾 Cached response for query: {query[:50]}...")
                return True
            else:
                logger.warning(f"⚠️ Failed to cache response for query: {query[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False
    
    def clear_cache(self, older_than_hours: int = 24) -> int:
        """Clear cache entries older than specified hours"""
        if self.collection is None:
            return 0
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            result = self.collection.delete_many({"created_at": {"$lt": cutoff_time}})
            
            logger.info(f"🗑️ Cleared {result.deleted_count} cache entries older than {older_than_hours} hours")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.collection is None:
            return {"error": "Cache not available"}
        
        try:
            total_docs = self.collection.count_documents({})
            
            # Count by intent
            intent_stats = {}
            pipeline = [
                {"$group": {"_id": "$intent", "count": {"$sum": 1}}}
            ]
            
            for doc in self.collection.aggregate(pipeline):
                intent_stats[doc["_id"]] = doc["count"]
            
            # Get oldest and newest entries
            oldest = self.collection.find_one({}, sort=[("created_at", 1)])
            newest = self.collection.find_one({}, sort=[("created_at", -1)])
            
            return {
                "total_entries": total_docs,
                "intent_distribution": intent_stats,
                "oldest_entry": oldest.get("created_at") if oldest else None,
                "newest_entry": newest.get("created_at") if newest else None,
                "cache_ttl_seconds": self.config.CACHE_TTL
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            logger.info("🔌 MongoDB cache connection closed") 