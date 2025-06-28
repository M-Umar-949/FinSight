# tools/cache.py
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
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
            self.collection.create_index([("created_at", 1)], expireAfterSeconds=self.config.CACHE_TTL)
            
            logger.info("✅ MongoDB cache connection established")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def _generate_query_hash(self, query: str, intent: str) -> str:
        """Generate a unique hash for the query and intent combination"""
        # Normalize the query (lowercase, strip whitespace)
        normalized_query = query.lower().strip()
        # Create hash from query + intent
        hash_input = f"{normalized_query}:{intent}"
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    
    def get_cached_response(self, query: str, intent: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response for a query"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return None
        
        try:
            query_hash = self._generate_query_hash(query, intent)
            
            # Find cached response
            cached_doc = self.collection.find_one({"query_hash": query_hash})
            
            if cached_doc:
                # Check if cache is still valid
                created_at = cached_doc.get('created_at')
                if created_at:
                    age = datetime.utcnow() - created_at
                    if age.total_seconds() < self.config.CACHE_TTL:
                        logger.info(f"✅ Cache hit for query: {query[:50]}...")
                        return cached_doc.get('response')
                    else:
                        # Cache expired, remove it
                        self.collection.delete_one({"query_hash": query_hash})
                        logger.info(f"🗑️ Expired cache removed for query: {query[:50]}...")
            
            logger.info(f"❌ Cache miss for query: {query[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
            return None
    
    def cache_response(self, query: str, intent: str, response: Dict[str, Any]) -> bool:
        """Cache a response for future use"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return False
        
        try:
            query_hash = self._generate_query_hash(query, intent)
            
            # Prepare cache document
            cache_doc = {
                "query_hash": query_hash,
                "original_query": query,
                "intent": intent,
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