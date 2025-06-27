import asyncio
from llm.ollama_client import OllamaClient
from config import Config
from tools.scraper import get_comprehensive_market_data
from datetime import datetime

class FinSight:
    def __init__(self):
        self.llm = OllamaClient()
        self.config = Config()
    
    async def process_query(self, query: str) -> dict:
        """Main query processing pipeline"""
        print(f"Processing query: {query}")
        
        # Step 1: Health check
        if not self.llm.health_check():
            return {"error": "Ollama service not available"}
        
        # Step 2: Detect intent
        intent = self.llm.detect_intent(query)
        print(f"Detected intent: {intent}")
        
        # Step 3: Route based on intent
        if intent == "price_movement":
            return await self._handle_price_query(query)
        elif intent == "company_news":
            return await self._handle_company_query(query)
        elif intent == "regulatory_news":
            return await self._handle_regulatory_query(query)
        elif intent == "video_analysis":
            return await self._handle_video_query(query)
        else:
            # Fallback to price movement for unclear queries
            return await self._handle_price_query(query)
    
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
            news_articles=market_data.get("news_articles", [])
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

    async def _handle_company_query(self, query: str) -> dict:
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
            market_data=market_data
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

    async def _handle_regulatory_query(self, query: str) -> dict:
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
            market_data=market_data
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
    
    async def _handle_video_query(self, query: str) -> dict:
        """Enhanced video analysis with transcription and LLM insights"""
        print("🎥 Analyzing video content...")
        
        # For now, we'll use a placeholder video content
        # In a real implementation, you would extract video content from YouTube URLs
        video_content = self._extract_video_content_from_query(query)
        
        if not video_content:
            return {
                "error": "No video content found. Please provide a YouTube URL or video description.",
                "query": query
            }
        
        # Step 1: Get market context for the analysis
        market_data = await get_comprehensive_market_data(query)
        market_context = self._format_market_data(market_data) if "error" not in market_data else "No market data available"
        
        # Step 2: Analyze with LLM
        print("🧠 Analyzing video content with AI...")
        analysis_result = self.llm.analyze_video_content(
            query=query,
            video_content=video_content,
            market_context=market_context
        )
        
        if "error" in analysis_result:
            return {"error": f"Video analysis failed: {analysis_result['error']}"}
        
        # Step 3: Compile comprehensive response
        response = {
            "intent": "video_analysis",
            "query": query,
            "analysis": analysis_result["analysis"],
            "key_insights": analysis_result["insights"],
            "video_info": {
                "content_length": analysis_result.get("content_length", 0),
                "content_preview": video_content[:200] + "..." if len(video_content) > 200 else video_content
            },
            "market_context": market_data if "error" not in market_data else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    def _extract_video_content_from_query(self, query: str) -> str:
        """Extract video content from query or provide placeholder content"""
        # This is a placeholder implementation
        # In a real system, you would:
        # 1. Extract YouTube URLs from the query
        # 2. Use YouTube API or web scraping to get video info
        # 3. Use a transcription service to get video content
        
        # For now, return a placeholder based on the query
        if "youtube" in query.lower() or "video" in query.lower():
            return f"Video content analysis for: {query}. This is a placeholder transcription that would be replaced with actual video content in a production system."
        
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
                    print(f"📹 Content Length: {video_info.get('content_length', 'N/A')} characters")
                    print(f"📹 Content Preview: {video_info.get('content_preview', 'No preview available')}")
                
                market_context = result.get('market_context')
                if market_context and "error" not in market_context:
                    print(f"🌐 Market Context: Available")
            else:
                print(f"💡 Response: {result.get('response', result.get('message', 'No response'))}")

        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
