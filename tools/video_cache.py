# tools/video_cache.py
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoCache:
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
            self.collection = self.db[self.config.MONGODB_VIDEO_COLLECTION]
            
            # Create indexes for better performance
            self.collection.create_index([("video_hash", 1)], unique=True)
            self.collection.create_index([("video_url", 1)])
            self.collection.create_index([("created_at", 1)], expireAfterSeconds=self.config.CACHE_TTL)
            
            logger.info("✅ MongoDB video cache connection established")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"⚠️ MongoDB video connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def _generate_video_hash(self, video_url: str) -> str:
        """Generate a unique hash for the video URL"""
        return hashlib.md5(video_url.encode('utf-8')).hexdigest()
    
    def get_cached_video(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached video transcription and analysis"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return None
        
        try:
            video_hash = self._generate_video_hash(video_url)
            
            # Find cached video data
            cached_doc = self.collection.find_one({"video_hash": video_hash})
            
            if cached_doc:
                # Check if cache is still valid
                created_at = cached_doc.get('created_at')
                if created_at:
                    age = datetime.utcnow() - created_at
                    if age.total_seconds() < self.config.CACHE_TTL:
                        logger.info(f"✅ Video cache hit for URL: {video_url[:50]}...")
                        return {
                            "video_info": cached_doc.get('video_info'),
                            "transcript": cached_doc.get('transcript'),
                            "analysis": cached_doc.get('analysis'),
                            "cached_at": created_at
                        }
                    else:
                        # Cache expired, remove it
                        self.collection.delete_one({"video_hash": video_hash})
                        logger.info(f"🗑️ Expired video cache removed for URL: {video_url[:50]}...")
            
            logger.info(f"❌ Video cache miss for URL: {video_url[:50]}...")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached video: {e}")
            return None
    
    def cache_video_data(self, video_url: str, video_info: Dict[str, Any], 
                        transcript: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Cache video transcription and analysis data"""
        if self.collection is None or not self.config.CACHE_ENABLED:
            return False
        
        try:
            video_hash = self._generate_video_hash(video_url)
            
            # Prepare cache document
            cache_doc = {
                "video_hash": video_hash,
                "video_url": video_url,
                "video_info": video_info,
                "transcript": transcript,
                "analysis": analysis,
                "created_at": datetime.utcnow(),
                "cache_ttl": self.config.CACHE_TTL,
                "metadata": {
                    "title": video_info.get('title', 'Unknown'),
                    "channel": video_info.get('channel', 'Unknown'),
                    "duration": video_info.get('duration', 0),
                    "view_count": video_info.get('view_count', 0),
                    "transcript_length": len(transcript.get('text', '')),
                    "word_count": transcript.get('word_count', 0)
                }
            }
            
            # Use upsert to handle duplicate keys
            result = self.collection.update_one(
                {"video_hash": video_hash},
                {"$set": cache_doc},
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"💾 Cached video data for URL: {video_url[:50]}...")
                return True
            else:
                logger.warning(f"⚠️ Failed to cache video data for URL: {video_url[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"Error caching video data: {e}")
            return False
    
    def get_video_stats(self) -> Dict[str, Any]:
        """Get video cache statistics"""
        if self.collection is None:
            return {"error": "Video cache not available"}
        
        try:
            total_videos = self.collection.count_documents({})
            
            # Get total transcript length
            pipeline = [
                {"$group": {
                    "_id": None,
                    "total_transcript_length": {"$sum": "$metadata.transcript_length"},
                    "total_word_count": {"$sum": "$metadata.word_count"},
                    "avg_duration": {"$avg": "$metadata.duration"}
                }}
            ]
            
            stats_result = list(self.collection.aggregate(pipeline))
            stats = stats_result[0] if stats_result else {}
            
            # Get oldest and newest entries
            oldest = self.collection.find_one({}, sort=[("created_at", 1)])
            newest = self.collection.find_one({}, sort=[("created_at", -1)])
            
            # Get top channels
            channel_pipeline = [
                {"$group": {"_id": "$metadata.channel", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            top_channels = list(self.collection.aggregate(channel_pipeline))
            
            return {
                "total_videos": total_videos,
                "total_transcript_length": stats.get("total_transcript_length", 0),
                "total_word_count": stats.get("total_word_count", 0),
                "avg_duration": stats.get("avg_duration", 0),
                "oldest_entry": oldest.get("created_at") if oldest else None,
                "newest_entry": newest.get("created_at") if newest else None,
                "top_channels": top_channels,
                "cache_ttl_seconds": self.config.CACHE_TTL
            }
            
        except Exception as e:
            logger.error(f"Error getting video stats: {e}")
            return {"error": str(e)}
    
    def clear_video_cache(self, older_than_hours: int = 24) -> int:
        """Clear video cache entries older than specified hours"""
        if self.collection is None:
            return 0
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            result = self.collection.delete_many({"created_at": {"$lt": cutoff_time}})
            
            logger.info(f"🗑️ Cleared {result.deleted_count} video cache entries older than {older_than_hours} hours")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing video cache: {e}")
            return 0
    
    def search_videos(self, query: str) -> List[Dict[str, Any]]:
        """Search videos by title, channel, or transcript content"""
        if self.collection is None:
            return []
        
        try:
            # Create text search query
            search_query = {
                "$or": [
                    {"metadata.title": {"$regex": query, "$options": "i"}},
                    {"metadata.channel": {"$regex": query, "$options": "i"}},
                    {"transcript.text": {"$regex": query, "$options": "i"}}
                ]
            }
            
            results = list(self.collection.find(search_query, {
                "video_url": 1,
                "metadata.title": 1,
                "metadata.channel": 1,
                "metadata.duration": 1,
                "created_at": 1,
                "_id": 0
            }).sort("created_at", -1).limit(10))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client is not None:
            self.client.close()
            logger.info("🔌 MongoDB video cache connection closed") 