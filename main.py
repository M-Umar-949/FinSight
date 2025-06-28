import asyncio
from llm.ollama_client import OllamaClient
from config import Config
from tools.scraper import get_comprehensive_market_data
from tools.video_transcriber import VideoTranscriber
from tools.cache import QueryCache
from tools.video_cache import VideoCache
from datetime import datetime
import re
from typing import Dict, Any

class FinSight:
    def __init__(self):
        self.llm = OllamaClient()
        self.config = Config()
        self.video_transcriber = VideoTranscriber()
        self.cache = QueryCache()
        self.video_cache = VideoCache()
    
    async def process_query(self, query: str) -> dict:
        """Process a single query with caching"""
        print(f"🔍 Processing query: {query}")
        
        # Detect intent
        intent = self.llm.detect_intent(query)
        print(f"🎯 Detected intent: {intent}")
        
        # Special handling for video queries - bypass general cache
        if intent == "video_analysis":
            return await self._handle_video_query(query)
        
        # For non-video queries, check general cache first
        cached_response = self.cache.get_cached_response(query, intent)
        if cached_response:
            print("💾 Returning cached response")
            return cached_response
        
        # If not in cache, process normally
        print("🔄 Processing with LLM (cache miss)")
        
        # Route to appropriate handler
        if intent == "price_movement":
            response = await self._handle_price_query(query)
        elif intent == "company_news":
            response = await self._handle_company_news_query(query)
        elif intent == "regulatory_news":
            response = await self._handle_regulatory_news_query(query)
        elif intent == "general_query":
            response = await self._handle_general_query(query)
        else:
            response = {"error": f"Unknown intent: {intent}"}
        
        # Cache the response if successful
        if "error" not in response:
            self.cache.cache_response(query, intent, response)
        
        return response
    
    async def _handle_price_query(self, query: str) -> dict:
        """Enhanced price movement analysis with comprehensive data and LLM insights"""
        print("🔍 Gathering comprehensive market data...")
        
        # Step 1: Get comprehensive market data
        market_data = await get_comprehensive_market_data(query)
        
        if "error" in market_data:
            return {"error": f"Failed to fetch market data: {market_data['error']}"}
        
        # Step 2: Analyze with LLM
        print("🧠 Analyzing with AI...")
        analysis_result = self.llm.analyze_price_movement(
            query=query,
            market_data=market_data,
            news_articles=market_data.get("news_articles", []),
            context=None
        )
        
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}
        
        # Step 3: Additional specialized analysis based on data available
        additional_insights = {}
        
        # News sentiment analysis
        if market_data.get("news_articles"):
            sentiment_analysis = self.llm.analyze_news_sentiment(market_data["news_articles"])
            if "error" not in sentiment_analysis:
                additional_insights["news_sentiment"] = sentiment_analysis["sentiment_analysis"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "price_movement",
            "query": query,
            "analysis": analysis_result["analysis"],
            "market_data": {
                "symbols_found": market_data.get("extracted_symbols", []),
                "price_data": market_data.get("price_data", {}),
                "market_indicators": market_data.get("market_indicators", {}),
                "news_count": len(market_data.get("news_articles", []))
            },
            "additional_insights": additional_insights,
            "timestamp": market_data.get("timestamp")
        }
        
        return response

    async def _handle_company_news_query(self, query: str) -> dict:
        """Enhanced company news analysis with comprehensive data and LLM insights"""
        print("🔍 Gathering company news and market data...")
        
        # Step 1: Get comprehensive market data
        market_data = await get_comprehensive_market_data(query)
        
        if "error" in market_data:
            return {"error": f"Failed to fetch market data: {market_data['error']}"}
        
        # Step 2: Analyze with LLM
        print("🧠 Analyzing company news with AI...")
        analysis_result = self.llm.analyze_company_news(
            query=query,
            news_articles=market_data.get("news_articles", []),
            market_data=market_data,
            context=None
        )
        
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}
        
        # Step 3: Additional sentiment analysis
        additional_insights = {}
        
        # News sentiment analysis
        if market_data.get("news_articles"):
            sentiment_analysis = self.llm.analyze_news_sentiment(market_data["news_articles"])
            if "error" not in sentiment_analysis:
                additional_insights["news_sentiment"] = sentiment_analysis["sentiment_analysis"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "company_news",
            "query": query,
            "analysis": analysis_result["analysis"],
            "market_data": {
                "symbols_found": market_data.get("extracted_symbols", []),
                "price_data": market_data.get("price_data", {}),
                "market_indicators": market_data.get("market_indicators", {}),
                "news_count": len(market_data.get("news_articles", []))
            },
            "additional_insights": additional_insights,
            "timestamp": market_data.get("timestamp")
        }
        
        return response

    async def _handle_regulatory_news_query(self, query: str) -> dict:
        """Enhanced regulatory news analysis with comprehensive data and LLM insights"""
        print("🔍 Gathering regulatory news and market data...")
        
        # Step 1: Get comprehensive market data
        market_data = await get_comprehensive_market_data(query)
        
        if "error" in market_data:
            return {"error": f"Failed to fetch market data: {market_data['error']}"}
        
        # Step 2: Analyze with LLM
        print("🧠 Analyzing regulatory news with AI...")
        analysis_result = self.llm.analyze_regulatory_news(
            query=query,
            news_articles=market_data.get("news_articles", []),
            market_data=market_data,
            context=None
        )
        
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}
        
        # Step 3: Additional sentiment analysis
        additional_insights = {}
        
        # News sentiment analysis
        if market_data.get("news_articles"):
            sentiment_analysis = self.llm.analyze_news_sentiment(market_data["news_articles"])
            if "error" not in sentiment_analysis:
                additional_insights["news_sentiment"] = sentiment_analysis["sentiment_analysis"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "regulatory_news",
            "query": query,
            "analysis": analysis_result["analysis"],
            "market_data": {
                "symbols_found": market_data.get("extracted_symbols", []),
                "price_data": market_data.get("price_data", {}),
                "market_indicators": market_data.get("market_indicators", {}),
                "news_count": len(market_data.get("news_articles", []))
            },
            "additional_insights": additional_insights,
            "timestamp": market_data.get("timestamp")
        }
        
        return response
    
    async def _handle_video_query(self, query: str) -> dict:
        """Enhanced video analysis with caching using YouTube API and Whisper transcription"""
        print("🎥 Analyzing video...")
        
        # Extract YouTube URL from query
        url = self._extract_youtube_url(query)
        
        if not url:
            return {
                "error": "No YouTube URL found. Please provide a YouTube video URL to analyze.",
                "query": query
            }
        
        print(f"🎬 Video URL: {url}")
        
        # Check video cache first (based on URL, not query text)
        cached_video = self.video_cache.get_cached_video(url)
        if cached_video:
            print("💾 Using cached video data (URL-based cache)")
            video_info = cached_video["video_info"]
            transcript = cached_video["transcript"]
            analysis = cached_video["analysis"]
        else:
            print("🔄 Processing video (video cache miss)")
            # Use the new video analysis with transcription
            video_result = await self.video_transcriber.analyze_video(url, query)
            
            if "error" in video_result:
                return {"error": f"Video analysis failed: {video_result['error']}"}
            
            video_info = video_result['video_info']
            transcript = video_result['transcript']
            analysis = video_result['analysis']
            
            # Cache the video data (based on URL)
            print("💾 Caching video data for future use")
            self.video_cache.cache_video_data(url, video_info, transcript, analysis)
        
        # Get market context
        market_data = await get_comprehensive_market_data(query)
        market_context = self._format_market_data(market_data) if "error" not in market_data else "No market data available"
        
        # Analyze with LLM
        print("🧠 Analyzing with AI...")
        analysis_result = self.llm.analyze_video_content(
            query=query,
            video_content=transcript['text'],
            market_context=market_context,
            context=None
        )
        
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}
        
        # Compile response (NOT cached in general cache - only video cache)
        response = {
            "intent": "video_analysis",
            "query": query,
            "video_url": url,
            "video_info": video_info,
            "transcript": transcript,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis,
            "market_context": market_data if "error" not in market_data else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _extract_youtube_url(self, query: str) -> str:
        """Extract YouTube URL from query"""
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[^&\s]+',
            r'https?://youtu\.be/[^&\s]+',
            r'https?://(?:www\.)?youtube\.com/embed/[^&\s]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(0)
        
        return ""
    
    def _format_market_data(self, market_data: dict) -> str:
        """Format market data for video analysis context"""
        if not market_data:
            return "No market data available"
        
        formatted = []
        
        if "extracted_symbols" in market_data and market_data["extracted_symbols"]:
            formatted.append(f"Relevant symbols: {', '.join(market_data['extracted_symbols'])}")
        
        if "market_indicators" in market_data:
            indicators = market_data["market_indicators"]
            if indicators:
                formatted.append("Market indicators:")
                for name, data in indicators.items():
                    formatted.append(f"  {name}: {data.get('value', 'N/A')}")
        
        return "\n".join(formatted) if formatted else "No market data available"
    
    async def _handle_general_query(self, query: str) -> dict:
        """Handle general queries, greetings, and help requests"""
        return self.llm.handle_general_query(query, None)
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'cache'):
            self.cache.close()
        if hasattr(self, 'video_cache'):
            self.video_cache.close()

# CLI Test Interface
async def main():
    finsight = FinSight()
    
    print("🚀 FinSight - Fintech Intelligence Agent")
    print("Type 'quit' to exit\n")
    
    while True:
        query = input("💬 Ask me anything about fintech: ")
        
        if query.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            finsight.cleanup()
            break
        elif query.lower() in ['help', '?']:
            print("🤖 FinSight AI Assistant - Available Commands:")
            print("  • Ask about price movements: 'What's happening with AAPL stock?'")
            print("  • Company news: 'Tell me about Tesla news'")
            print("  • Regulatory updates: 'What are the latest SEC regulations?'")
            print("  • Video analysis: 'Analyze this video: [YouTube URL]'")
            print("  • General questions: 'Hello', 'How are you?'")
            print("  • Cache commands: 'cache stats', 'clear cache', 'video stats', 'clear video cache'")
            print("  • Commands: 'help', 'quit'")
            continue
        elif query.lower() == 'cache stats':
            stats = finsight.cache.get_cache_stats()
            if "error" in stats:
                print(f"❌ Cache Error: {stats['error']}")
            else:
                print("📊 Query Cache Statistics:")
                print(f"  Total entries: {stats['total_entries']}")
                print(f"  Cache TTL: {stats['cache_ttl_seconds']} seconds")
                if stats['intent_distribution']:
                    print("  Intent distribution:")
                    for intent, count in stats['intent_distribution'].items():
                        print(f"    {intent}: {count}")
                if stats['oldest_entry']:
                    print(f"  Oldest entry: {stats['oldest_entry']}")
                if stats['newest_entry']:
                    print(f"  Newest entry: {stats['newest_entry']}")
            continue
        elif query.lower() == 'video stats':
            stats = finsight.video_cache.get_video_stats()
            if "error" in stats:
                print(f"❌ Video Cache Error: {stats['error']}")
            else:
                print("🎥 Video Cache Statistics:")
                print(f"  Total videos: {stats['total_videos']}")
                print(f"  Total transcript length: {stats['total_transcript_length']} characters")
                print(f"  Total word count: {stats['total_word_count']} words")
                print(f"  Average duration: {stats['avg_duration']:.1f} seconds")
                if stats['top_channels']:
                    print("  Top channels:")
                    for channel in stats['top_channels']:
                        print(f"    {channel['_id']}: {channel['count']} videos")
                if stats['oldest_entry']:
                    print(f"  Oldest entry: {stats['oldest_entry']}")
                if stats['newest_entry']:
                    print(f"  Newest entry: {stats['newest_entry']}")
            continue
        elif query.lower() == 'clear cache':
            try:
                hours = input("Enter hours to clear (default 24): ").strip()
                hours = int(hours) if hours.isdigit() else 24
                cleared = finsight.cache.clear_cache(hours)
                print(f"🗑️ Cleared {cleared} query cache entries older than {hours} hours")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
            continue
        elif query.lower() == 'clear video cache':
            try:
                hours = input("Enter hours to clear (default 24): ").strip()
                hours = int(hours) if hours.isdigit() else 24
                cleared = finsight.video_cache.clear_video_cache(hours)
                print(f"🗑️ Cleared {cleared} video cache entries older than {hours} hours")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
            continue
        
        if not query.strip():
            continue
        
        result = await finsight.process_query(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🎯 Intent: {result.get('intent', 'unknown')}")
            
            if result.get('intent') == 'price_movement':
                # Enhanced display for price movement analysis
                print(f"📊 Analysis: {result.get('analysis', 'No analysis available')}")
                
                market_data = result.get('market_data', {})
                if market_data.get('symbols_found'):
                    print(f"📈 Symbols Analyzed: {', '.join(market_data['symbols_found'])}")
                if market_data.get('news_count'):
                    print(f"📰 News Articles: {market_data['news_count']}")
                
                # Show additional insights if available
                additional = result.get('additional_insights', {})
                if additional.get('news_sentiment'):
                    print(f"📰 News Sentiment: {additional['news_sentiment'][:200]}...")
                    
            elif result.get('intent') == 'company_news':
                # Enhanced display for company news analysis
                print(f"🏢 Company Analysis: {result.get('analysis', 'No analysis available')}")
                
                market_data = result.get('market_data', {})
                if market_data.get('symbols_found'):
                    print(f"🏢 Companies: {', '.join(market_data['symbols_found'])}")
                if market_data.get('news_count'):
                    print(f"📰 News Articles: {market_data['news_count']}")
                
                # Show additional insights if available
                additional = result.get('additional_insights', {})
                if additional.get('news_sentiment'):
                    print(f"📰 News Sentiment: {additional['news_sentiment'][:200]}...")
                    
            elif result.get('intent') == 'regulatory_news':
                # Enhanced display for regulatory news analysis
                print(f"⚖️ Regulatory Analysis: {result.get('analysis', 'No analysis available')}")
                
                market_data = result.get('market_data', {})
                if market_data.get('symbols_found'):
                    print(f"🏢 Affected Companies: {', '.join(market_data['symbols_found'])}")
                if market_data.get('news_count'):
                    print(f"📰 News Articles: {market_data['news_count']}")
                
                # Show additional insights if available
                additional = result.get('additional_insights', {})
                if additional.get('news_sentiment'):
                    print(f"📰 News Sentiment: {additional['news_sentiment'][:200]}...")
                    
            elif result.get('intent') == 'video_analysis':
                # Simple display for video analysis
                print(f"🎥 Video Analysis: {result.get('analysis', 'No analysis available')}")
                
                video_info = result.get('video_info', {})
                if video_info:
                    print(f"📹 Title: {video_info.get('title', 'Unknown')}")
                    print(f"📹 Channel: {video_info.get('channel', 'Unknown')}")
                    print(f"📹 Views: {video_info.get('view_count', 'N/A')}")
                
                transcript = result.get('transcript', {})
                if transcript:
                    print(f"📝 Duration Analyzed: {transcript.get('duration_analyzed', 'N/A')}")
                    print(f"📝 Word Count: {transcript.get('word_count', 'N/A')}")
                    print(f"📝 Transcript Preview: {transcript.get('text', '')[:100]}...")
                
                insights = result.get('key_insights', {})
                if insights:
                    sentiment = insights.get('sentiment', {})
                    if sentiment:
                        print(f"📊 Sentiment: {sentiment.get('sentiment', 'neutral')} (confidence: {sentiment.get('confidence', 0):.2f})")
                    
                    key_points = insights.get('key_points', [])
                    if key_points:
                        print(f"🎯 Key Points:")
                        for i, point in enumerate(key_points[:3], 1):
                            print(f"  {i}. {point[:80]}...")
                    
                    topics = insights.get('topics', [])
                    if topics:
                        print(f"📋 Topics: {', '.join(topics)}")
                
                market_context = result.get('market_context')
                if market_context and "error" not in market_context:
                    print(f"🌐 Market Context: Available")
            elif result.get('intent') == 'general_query':
                # Display general query responses
                print(f"💬 {result.get('response', 'No response available')}")
            else:
                print(f"💡 Response: {result.get('response', result.get('message', 'No response'))}")

        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
