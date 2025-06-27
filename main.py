import asyncio
from llm.ollama_client import OllamaClient
from config import Config
from tools.scraper import get_comprehensive_market_data
from tools.video_transcriber import VideoTranscriber
from datetime import datetime
from data.context_manager import ContextManager
import re
from typing import Dict, Any

class FinSight:
    def __init__(self):
        self.llm = OllamaClient()
        self.config = Config()
        self.context_manager = ContextManager(
            max_history=self.config.MAX_CONVERSATION_HISTORY,
            context_ttl=self.config.CONTEXT_TTL
        )
        self.video_transcriber = VideoTranscriber()
    
    async def process_query(self, query: str, session_id: str = "default") -> dict:
        """Main query processing pipeline with context management"""
        print(f"Processing query: {query}")
        
        # Step 1: Health check
        if not self.llm.health_check():
            return {"error": "Ollama service not available"}
        
        # Step 2: Get relevant context
        context = self.context_manager.get_relevant_context(query, session_id)
        print(f"📚 Context found: {len(context.get('conversation_history', []))} relevant turns")
        
        # Step 3: Detect intent
        intent = self.llm.detect_intent(query)
        print(f"Detected intent: {intent}")
        
        # Step 4: Route based on intent
        if intent == "price_movement":
            result = await self._handle_price_query(query, context)
        elif intent == "company_news":
            result = await self._handle_company_query(query, context)
        elif intent == "regulatory_news":
            result = await self._handle_regulatory_query(query, context)
        elif intent == "video_analysis":
            result = await self._handle_video_query(query, context)
        elif intent == "general_query":
            result = self._handle_general_query(query, context)
        else:
            # Fallback to general query for unclear queries
            result = self._handle_general_query(query, context)
        
        # Step 5: Add to conversation history
        if "error" not in result:
            self.context_manager.add_conversation_turn(query, result, session_id)
            
            # Cache market data if available and enabled
            if self.config.CACHE_MARKET_DATA and result.get("market_data"):
                symbols = result["market_data"].get("symbols_found", [])
                if symbols:
                    self.context_manager.cache_market_data(symbols, result["market_data"])
        
        return result
    
    async def _handle_price_query(self, query: str, context: dict) -> dict:
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
            context=context if self.config.ENABLE_CONTEXT_ANALYSIS else None
        )
        
        if "error" in analysis_result:
            return {"error": f"Analysis failed: {analysis_result['error']}"}
        
        # Step 3: Additional specialized analysis based on data available
        additional_insights = {}
        
        # Technical analysis if we have price data
        if market_data.get("price_data"):
            technical_analysis = self.llm.analyze_technical_factors(
                market_data["price_data"],
                market_data.get("market_indicators", {})
            )
            if "error" not in technical_analysis:
                additional_insights["technical_analysis"] = technical_analysis["technical_analysis"]
        
        # News sentiment analysis
        if market_data.get("news_articles"):
            sentiment_analysis = self.llm.analyze_news_sentiment(market_data["news_articles"])
            if "error" not in sentiment_analysis:
                additional_insights["news_sentiment"] = sentiment_analysis["sentiment_analysis"]
        
        # Market sentiment analysis
        if market_data.get("market_indicators"):
            market_sentiment = self.llm.analyze_market_sentiment(
                market_data["market_indicators"],
                market_data.get("news_articles", [])
            )
            if "error" not in market_sentiment:
                additional_insights["market_sentiment"] = market_sentiment["market_sentiment"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "price_movement",
            "query": query,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis_result["insights"],
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

    async def _handle_company_query(self, query: str, context: dict) -> dict:
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
            context=context if self.config.ENABLE_CONTEXT_ANALYSIS else None
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
        
        # Market sentiment analysis
        if market_data.get("market_indicators"):
            market_sentiment = self.llm.analyze_market_sentiment(
                market_data["market_indicators"],
                market_data.get("news_articles", [])
            )
            if "error" not in market_sentiment:
                additional_insights["market_sentiment"] = market_sentiment["market_sentiment"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "company_news",
            "query": query,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis_result["insights"],
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

    async def _handle_regulatory_query(self, query: str, context: dict) -> dict:
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
            context=context if self.config.ENABLE_CONTEXT_ANALYSIS else None
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
        
        # Market sentiment analysis
        if market_data.get("market_indicators"):
            market_sentiment = self.llm.analyze_market_sentiment(
                market_data["market_indicators"],
                market_data.get("news_articles", [])
            )
            if "error" not in market_sentiment:
                additional_insights["market_sentiment"] = market_sentiment["market_sentiment"]
        
        # Step 4: Compile comprehensive response
        response = {
            "intent": "regulatory_news",
            "query": query,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis_result["insights"],
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
    
    async def _handle_video_query(self, query: str, context: dict) -> dict:
        """Enhanced video analysis with transcription and LLM insights"""
        print("🎥 Analyzing video content...")
        
        # Step 1: Extract video information from query
        video_info = self._extract_video_info_from_query(query)
        
        if not video_info:
            return {
                "error": "No video information found. Please provide a YouTube URL or video description.",
                "query": query
            }
        
        # Step 2: Analyze video content
        print("📹 Processing video content...")
        video_analysis = await self.video_transcriber.analyze_video_content(
            video_url=video_info.get("url"),
            video_title=video_info.get("title")
        )
        
        if "error" in video_analysis.get("transcript", {}):
            return {"error": f"Video analysis failed: {video_analysis['transcript']['error']}"}
        
        # Step 3: Extract key insights from transcript
        transcript = video_analysis["transcript"].get("transcript", "")
        if transcript:
            key_points = self.video_transcriber.extract_key_points(transcript)
            sentiment_analysis = self.video_transcriber.analyze_sentiment(transcript)
        else:
            key_points = []
            sentiment_analysis = {"sentiment": "neutral", "confidence": 0.5}
        
        # Step 4: Get market context for analysis
        market_data = await get_comprehensive_market_data(query)
        market_context = self._format_market_data(market_data) if "error" not in market_data else "No market data available"
        
        # Step 5: Analyze with LLM
        print("🧠 Analyzing video content with AI...")
        analysis_result = self.llm.analyze_video_content(
            query=query,
            video_content=transcript,
            market_context=market_context,
            context=context if self.config.ENABLE_CONTEXT_ANALYSIS else None
        )
        
        if "error" in analysis_result:
            return {"error": f"Video analysis failed: {analysis_result['error']}"}
        
        # Step 6: Compile comprehensive response
        response = {
            "intent": "video_analysis",
            "query": query,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis_result["insights"],
            "video_info": {
                "title": video_info.get("title", "Unknown"),
                "url": video_info.get("url", ""),
                "transcript_length": len(transcript),
                "word_count": video_analysis["transcript"].get("word_count", 0),
                "duration": video_analysis["transcript"].get("estimated_duration", 0)
            },
            "transcript_analysis": {
                "key_points": key_points,
                "sentiment": sentiment_analysis,
                "topics": video_analysis["transcript"].get("topics_detected", [])
            },
            "market_context": market_data if "error" not in market_data else None,
            "context_used": analysis_result.get("context_used", False),
            "timestamp": video_analysis.get("timestamp")
        }
        
        return response
    
    def _extract_video_info_from_query(self, query: str) -> Dict[str, Any]:
        """Extract video information from user query"""
        # Look for YouTube URLs
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([^&\s]+)',
            r'https?://youtu\.be/([^&\s]+)',
            r'https?://(?:www\.)?youtube\.com/embed/([^&\s]+)'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, query)
            if match:
                video_id = match.group(1)
                return {
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "type": "youtube",
                    "video_id": video_id
                }
        
        # Look for video-related keywords and extract potential title
        video_keywords = ['video', 'youtube', 'earnings call', 'presentation', 'interview', 'analysis']
        if any(keyword in query.lower() for keyword in video_keywords):
            # Extract potential title from query
            words = query.split()
            title_start = -1
            for i, word in enumerate(words):
                if any(keyword in word.lower() for keyword in ['about', 'on', 'regarding', 'discussing']):
                    title_start = i + 1
                    break
            
            if title_start >= 0 and title_start < len(words):
                title = " ".join(words[title_start:])
                return {
                    "title": title,
                    "type": "description"
                }
        
        # If no specific video info found, use the query as a general description
        return {
            "title": query,
            "type": "general"
        }
    
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
    
    def _handle_general_query(self, query: str, context: dict) -> dict:
        """Handle general queries, greetings, and help requests"""
        return self.llm.handle_general_query(query, context if self.config.ENABLE_CONTEXT_ANALYSIS else None)

# CLI Test Interface
async def main():
    finsight = FinSight()
    
    print("🚀 FinSight - Fintech Intelligence Agent")
    print("Type 'quit' to exit\n")
    
    while True:
        query = input("💬 Ask me anything about fintech: ")
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if query.lower() in ['clear', 'reset']:
            finsight.context_manager.clear_session()
            print("🧹 Conversation history cleared!")
            continue
        
        if query.lower() in ['history', 'context']:
            summary = finsight.context_manager.get_conversation_summary()
            print("📚 Conversation History:")
            print(summary)
            continue
        
        if query.lower() in ['stats', 'status']:
            stats = finsight.context_manager.get_context_stats()
            print("📊 Context Manager Stats:")
            print(f"  Conversation History: {stats['conversation_history_size']} turns")
            print(f"  Cache Size: {stats['cache_size']} entries")
            print(f"  Max History: {stats['max_history']}")
            print(f"  Context TTL: {stats['context_ttl']} seconds")
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
                
                insights = result.get('key_insights', {})
                if insights:
                    print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
                    if insights.get('key_drivers'):
                        print(f"🚀 Key Drivers: {', '.join(insights['key_drivers'])}")
                    if insights.get('risk_factors'):
                        print(f"⚠️ Risk Factors: {', '.join(insights['risk_factors'])}")
                
                market_data = result.get('market_data', {})
                if market_data.get('symbols_found'):
                    print(f"📈 Symbols Analyzed: {', '.join(market_data['symbols_found'])}")
                if market_data.get('news_count'):
                    print(f"📰 News Articles: {market_data['news_count']}")
                
                # Show additional insights if available
                additional = result.get('additional_insights', {})
                if additional.get('technical_analysis'):
                    print(f"📊 Technical Analysis: {additional['technical_analysis'][:200]}...")
                if additional.get('news_sentiment'):
                    print(f"📰 News Sentiment: {additional['news_sentiment'][:200]}...")
                    
            elif result.get('intent') == 'company_news':
                # Enhanced display for company news analysis
                print(f"🏢 Company Analysis: {result.get('analysis', 'No analysis available')}")
                
                insights = result.get('key_insights', {})
                if insights:
                    print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
                    if insights.get('key_drivers'):
                        print(f"🚀 Key Events: {', '.join(insights['key_drivers'])}")
                    if insights.get('risk_factors'):
                        print(f"⚠️ Risk Factors: {', '.join(insights['risk_factors'])}")
                
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
                
                insights = result.get('key_insights', {})
                if insights:
                    print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
                    if insights.get('key_drivers'):
                        print(f"📋 Key Regulations: {', '.join(insights['key_drivers'])}")
                    if insights.get('risk_factors'):
                        print(f"⚠️ Compliance Risks: {', '.join(insights['risk_factors'])}")
                
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
                # Enhanced display for video analysis
                print(f"🎥 Video Analysis: {result.get('analysis', 'No analysis available')}")
                
                insights = result.get('key_insights', {})
                if insights:
                    print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
                    if insights.get('key_drivers'):
                        print(f"🎬 Key Points: {', '.join(insights['key_drivers'])}")
                
                video_info = result.get('video_info', {})
                if video_info:
                    print(f"📹 Title: {video_info.get('title', 'Unknown')}")
                    if video_info.get('url'):
                        print(f"📹 URL: {video_info.get('url')}")
                    print(f"📹 Transcript Length: {video_info.get('transcript_length', 'N/A')} characters")
                    print(f"📹 Word Count: {video_info.get('word_count', 'N/A')} words")
                    print(f"📹 Duration: {video_info.get('duration', 'N/A')} minutes")
                
                transcript_analysis = result.get('transcript_analysis', {})
                if transcript_analysis:
                    if transcript_analysis.get('key_points'):
                        print(f"🎯 Key Points from Transcript:")
                        for i, point in enumerate(transcript_analysis['key_points'][:3], 1):
                            print(f"  {i}. {point[:100]}...")
                    
                    sentiment = transcript_analysis.get('sentiment', {})
                    if sentiment:
                        print(f"📊 Transcript Sentiment: {sentiment.get('sentiment', 'neutral')} (confidence: {sentiment.get('confidence', 0):.2f})")
                    
                    topics = transcript_analysis.get('topics', [])
                    if topics:
                        print(f"📋 Topics: {', '.join(topics)}")
                
                market_context = result.get('market_context')
                if market_context and "error" not in market_context:
                    print(f"🌐 Market Context: Available")
            elif result.get('intent') == 'general_query':
                # Display general query responses
                print(f"💬 {result.get('response', 'No response available')}")
                
                # Show context information if used
                if result.get('context_used'):
                    print(f"📚 Context: Used previous conversation history")
            else:
                print(f"💡 Response: {result.get('response', result.get('message', 'No response'))}")
            
            # Show context information for all responses
            if result.get('context_used'):
                print(f"📚 Context: Used previous conversation history")

        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
