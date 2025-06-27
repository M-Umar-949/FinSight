import asyncio
from llm.ollama_client import OllamaClient
from config import Config

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
        elif intent == "regulatory_news":
            return await self._handle_regulatory_query(query)
        elif intent == "company_event":
            return await self._handle_company_query(query)
        elif intent == "market_sentiment":
            return await self._handle_sentiment_query(query)
        elif intent == "video_transcription":
            return await self._handle_video_query(query)
        elif intent == "news_summary":
            return await self._handle_news_query(query)
        elif intent == "technical_analysis":
            return await self._handle_technical_query(query)
        elif intent == "fundamental_analysis":
            return await self._handle_fundamental_query(query)
        elif intent == "crypto_specific":
            return await self._handle_crypto_query(query)
        else:
            return await self._handle_general_query(query)
    
    async def _handle_price_query(self, query: str) -> dict:
        # Placeholder - will implement with scrapers
        return {
            "intent": "price_movement",
            "message": "Price analysis feature coming soon",
            "query": query
        }
    
    async def _handle_regulatory_query(self, query: str) -> dict:
        return {
            "intent": "regulatory_news", 
            "message": "Regulatory news analysis coming soon",
            "query": query
        }
    
    async def _handle_company_query(self, query: str) -> dict:
        return {
            "intent": "company_event",
            "message": "Company event analysis coming soon", 
            "query": query
        }
    
    async def _handle_general_query(self, query: str) -> dict:
        # Basic LLM response for general queries
        response = self.llm.generate(
            query,
            "You are a helpful fintech assistant. Provide accurate, concise financial information."
        )
        
        return {
            "intent": "general_info",
            "response": response.get("response", "Unable to process query"),
            "query": query
        }
    
    async def _handle_sentiment_query(self, query: str) -> dict:
        """Handle market sentiment analysis queries"""
        return {
            "intent": "market_sentiment",
            "message": "Market sentiment analysis feature coming soon. Will analyze fear/greed index, social media sentiment, and market indicators.",
            "query": query,
            "tools_needed": ["sentiment_analyzer", "social_media_scraper", "market_indicators"]
        }
    
    async def _handle_video_query(self, query: str) -> dict:
        """Handle video transcription and analysis queries"""
        return {
            "intent": "video_transcription",
            "message": "Video transcription and analysis feature coming soon. Will extract YouTube videos, transcribe audio, and analyze content.",
            "query": query,
            "tools_needed": ["youtube_extractor", "transcription_service", "content_analyzer"]
        }
    
    async def _handle_news_query(self, query: str) -> dict:
        """Handle news summary and aggregation queries"""
        return {
            "intent": "news_summary",
            "message": "News aggregation and summarization feature coming soon. Will scrape multiple sources and provide AI-powered summaries.",
            "query": query,
            "tools_needed": ["news_scraper", "content_summarizer", "source_aggregator"]
        }
    
    async def _handle_technical_query(self, query: str) -> dict:
        """Handle technical analysis queries"""
        return {
            "intent": "technical_analysis",
            "message": "Technical analysis feature coming soon. Will provide chart analysis, indicators, and pattern recognition.",
            "query": query,
            "tools_needed": ["chart_analyzer", "indicator_calculator", "pattern_recognition"]
        }
    
    async def _handle_fundamental_query(self, query: str) -> dict:
        """Handle fundamental analysis queries"""
        return {
            "intent": "fundamental_analysis",
            "message": "Fundamental analysis feature coming soon. Will analyze financial statements, ratios, and company fundamentals.",
            "query": query,
            "tools_needed": ["financial_data_provider", "ratio_calculator", "statement_analyzer"]
        }
    
    async def _handle_crypto_query(self, query: str) -> dict:
        """Handle cryptocurrency-specific queries"""
        return {
            "intent": "crypto_specific",
            "message": "Cryptocurrency analysis feature coming soon. Will provide DeFi metrics, blockchain analysis, and crypto-specific insights.",
            "query": query,
            "tools_needed": ["crypto_data_provider", "blockchain_analyzer", "defi_metrics"]
        }

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
            print(f"💡 Response: {result.get('response', result.get('message', 'No response'))}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
