# llm/ollama_client.py
import requests
import json
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
from .prompts import (
    PRICE_MOVEMENT_ANALYSIS_PROMPT,
    COMPANY_NEWS_ANALYSIS_PROMPT,
    REGULATORY_NEWS_ANALYSIS_PROMPT,
    VIDEO_ANALYSIS_PROMPT,
    CONTEXT_ENHANCED_GENERAL_PROMPT,
    NEWS_SENTIMENT_ANALYSIS_PROMPT,
    TECHNICAL_ANALYSIS_PROMPT,
    FUNDAMENTAL_ANALYSIS_PROMPT,
    CRYPTO_PRICE_ANALYSIS_PROMPT,
    MARKET_SENTIMENT_PROMPT
)

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.base_url = f"http://{self.host}"
    
    def generate(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """Generate response using Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower for more factual responses
                "top_p": 0.9,
                "num_ctx": 4096
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Ollama request failed: {str(e)}"}
    
    def detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        system_prompt = """You are a fintech query classifier. Classify the user's query into one of these categories:
        - price_movement: Questions about price changes, drops, rises, market movements, stock prices, crypto prices
        - company_news: Questions about earnings, announcements, corporate events, IPO, company performance, business news
        - regulatory_news: Questions about regulations, compliance, legal changes, SEC, CFTC, government policy, regulatory updates
        - video_analysis: Requests for video analysis, YouTube links, transcriptions, video content analysis
        - general_query: Greetings, general questions, help requests, capabilities questions, non-financial queries
        
        Respond with only the category name."""
        
        result = self.generate(query, system_prompt)
        if "error" in result:
            return "general_query"  # fallback to general query
        
        return result.get("response", "general_query").strip().lower()
    
    def handle_general_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general queries, greetings, and help requests with context"""
        # Check for greetings and basic interactions
        greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]
        help_words = ["help", "what can you do", "capabilities", "features", "how to use"]
        
        query_lower = query.lower()
        
        # Greeting responses
        if any(greeting in query_lower for greeting in greetings):
            response = """Hello! I'm FinSight, your AI-powered financial analysis assistant. 

I can help you with:
📊 **Price Movement Analysis** - Analyze stock/crypto price changes and market movements
🏢 **Company News Analysis** - Corporate events, earnings, and business developments  
⚖️ **Regulatory News Analysis** - Government policies, compliance, and regulations
🎥 **Video Analysis** - Video content analysis and transcription

Just ask me anything about financial markets, companies, regulations, or video content!"""
            
            return {
                "response": response,
                "intent": "general_query",
                "query_type": "greeting"
            }
        
        # Help responses
        elif any(help_word in query_lower for help_word in help_words):
            response = """I'm FinSight, your comprehensive financial analysis AI assistant!

**What I can do:**

📊 **Price Movement Analysis**
- "Why is AAPL stock dropping today?"
- "What's happening with Tesla TSLA price movement?"
- "Bitcoin BTC price analysis and market sentiment"

🏢 **Company News Analysis**
- "Apple AAPL earnings announcement analysis"
- "Tesla TSLA new product launch"
- "Microsoft MSFT acquisition news"

⚖️ **Regulatory News Analysis**
- "SEC new regulations for crypto"
- "CFTC trading rules update"
- "Federal Reserve policy changes"

🎥 **Video Analysis**
- "Analyze this YouTube video about market trends"
- "Video analysis of earnings call"
- "YouTube content about crypto regulations"

**Features:**
- Real-time market data and news
- AI-powered sentiment analysis
- Comprehensive financial insights
- Multi-source data aggregation
- Context-aware conversations

Just ask me anything about finance, and I'll provide detailed analysis with market context!"""
            
            return {
                "response": response,
                "intent": "general_query",
                "query_type": "help"
            }
        
        # General financial questions with context
        else:
            # Format context information
            conversation_history = self._format_conversation_history(context.get("conversation_history", []) if context else [])
            cached_data = self._format_cached_data(context.get("cached_market_data", {}) if context else {})
            
            # Use context-enhanced prompt
            system_prompt = CONTEXT_ENHANCED_GENERAL_PROMPT.format(
                query=query,
                conversation_history=conversation_history,
                cached_data=cached_data
            )
            
            result = self.generate(query, system_prompt)
            if "error" in result:
                return {
                    "response": "I'm here to help with financial analysis! You can ask me about price movements, company news, regulations, or video content. What would you like to know?",
                    "intent": "general_query",
                    "query_type": "general"
                }
            
            return {
                "response": result.get("response", "I'm here to help with financial analysis! What would you like to know?"),
                "intent": "general_query",
                "query_type": "general"
            }
    
    def analyze_price_movement(self, query: str, market_data: Dict[str, Any], news_articles: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive price movement analysis using LLM with context"""
        # Format market data for analysis
        market_summary = self._format_market_data(market_data)
        news_summary = self._format_news_articles(news_articles)
        
        # Format context information
        conversation_history = self._format_conversation_history(context.get("conversation_history", []) if context else [])
        cached_data = self._format_cached_data(context.get("cached_market_data", {}) if context else {})
        
        # Generate comprehensive analysis
        analysis_prompt = PRICE_MOVEMENT_ANALYSIS_PROMPT.format(
            query=query,
            market_data=market_summary,
            news_articles=news_summary,
            conversation_history=conversation_history,
            cached_data=cached_data
        )
        
        result = self.generate(analysis_prompt)
        if "error" in result:
            return {"error": "Analysis failed", "details": result["error"]}
        
        # Extract key insights using structured analysis
        insights = self._extract_key_insights(result.get("response", ""))
        
        return {
            "analysis": result.get("response", "Analysis unavailable"),
            "insights": insights,
            "market_data": market_data,
            "news_count": len(news_articles),
            "symbols_analyzed": market_data.get("extracted_symbols", []),
            "context_used": bool(context)
        }
    
    def analyze_company_news(self, query: str, news_articles: List[Dict[str, Any]], market_data: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze company news and corporate events with context"""
        news_summary = self._format_news_articles(news_articles)
        market_summary = self._format_market_data(market_data) if market_data else "No market data available"
        
        # Format context information
        conversation_history = self._format_conversation_history(context.get("conversation_history", []) if context else [])
        cached_data = self._format_cached_data(context.get("cached_market_data", {}) if context else {})
        
        analysis_prompt = COMPANY_NEWS_ANALYSIS_PROMPT.format(
            query=query,
            news_articles=news_summary,
            market_data=market_summary,
            conversation_history=conversation_history,
            cached_data=cached_data
        )
        
        result = self.generate(analysis_prompt)
        if "error" in result:
            return {"error": "Company news analysis failed", "details": result["error"]}
        
        # Extract key insights
        insights = self._extract_key_insights(result.get("response", ""))
        
        return {
            "analysis": result.get("response", "Analysis unavailable"),
            "insights": insights,
            "news_count": len(news_articles),
            "market_data": market_data,
            "context_used": bool(context)
        }
    
    def analyze_regulatory_news(self, query: str, news_articles: List[Dict[str, Any]], market_data: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze regulatory news and compliance developments with context"""
        news_summary = self._format_news_articles(news_articles)
        market_summary = self._format_market_data(market_data) if market_data else "No market data available"
        
        # Format context information
        conversation_history = self._format_conversation_history(context.get("conversation_history", []) if context else [])
        cached_data = self._format_cached_data(context.get("cached_market_data", {}) if context else {})
        
        analysis_prompt = REGULATORY_NEWS_ANALYSIS_PROMPT.format(
            query=query,
            news_articles=news_summary,
            market_data=market_summary,
            conversation_history=conversation_history,
            cached_data=cached_data
        )
        
        result = self.generate(analysis_prompt)
        if "error" in result:
            return {"error": "Regulatory news analysis failed", "details": result["error"]}
        
        # Extract key insights
        insights = self._extract_key_insights(result.get("response", ""))
        
        return {
            "analysis": result.get("response", "Analysis unavailable"),
            "insights": insights,
            "news_count": len(news_articles),
            "market_data": market_data,
            "context_used": bool(context)
        }
    
    def analyze_video_content(self, query: str, video_content: str, market_context: str = "", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze video content and transcriptions with context"""
        # Format context information
        conversation_history = self._format_conversation_history(context.get("conversation_history", []) if context else [])
        cached_data = self._format_cached_data(context.get("cached_market_data", {}) if context else {})
        
        analysis_prompt = VIDEO_ANALYSIS_PROMPT.format(
            query=query,
            video_content=video_content,
            market_context=market_context,
            conversation_history=conversation_history,
            cached_data=cached_data
        )
        
        result = self.generate(analysis_prompt)
        if "error" in result:
            return {"error": "Video analysis failed", "details": result["error"]}
        
        # Extract key insights
        insights = self._extract_key_insights(result.get("response", ""))
        
        return {
            "analysis": result.get("response", "Analysis unavailable"),
            "insights": insights,
            "content_length": len(video_content),
            "context_used": bool(context)
        }
    
    def analyze_news_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles"""
        formatted_articles = self._format_news_articles(articles)
        
        sentiment_prompt = NEWS_SENTIMENT_ANALYSIS_PROMPT.format(
            articles=formatted_articles
        )
        
        result = self.generate(sentiment_prompt)
        if "error" in result:
            return {"error": "Sentiment analysis failed"}
        
        return {
            "sentiment_analysis": result.get("response", "Analysis unavailable"),
            "article_count": len(articles)
        }
    
    def analyze_technical_factors(self, price_data: Dict[str, Any], market_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical factors affecting price movements"""
        technical_prompt = TECHNICAL_ANALYSIS_PROMPT.format(
            price_data=json.dumps(price_data, indent=2),
            market_indicators=json.dumps(market_indicators, indent=2)
        )
        
        result = self.generate(technical_prompt)
        if "error" in result:
            return {"error": "Technical analysis failed"}
        
        return {
            "technical_analysis": result.get("response", "Analysis unavailable"),
            "indicators_analyzed": list(market_indicators.keys())
        }
    
    def analyze_fundamental_factors(self, news_context: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamental factors affecting price movements"""
        fundamental_prompt = FUNDAMENTAL_ANALYSIS_PROMPT.format(
            news_context=news_context,
            market_data=json.dumps(market_data, indent=2)
        )
        
        result = self.generate(fundamental_prompt)
        if "error" in result:
            return {"error": "Fundamental analysis failed"}
        
        return {
            "fundamental_analysis": result.get("response", "Analysis unavailable")
        }
    
    def analyze_crypto_movement(self, market_data: Dict[str, Any], news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Specialized analysis for cryptocurrency price movements"""
        crypto_prompt = CRYPTO_PRICE_ANALYSIS_PROMPT.format(
            market_data=json.dumps(market_data, indent=2),
            news_articles=self._format_news_articles(news_articles)
        )
        
        result = self.generate(crypto_prompt)
        if "error" in result:
            return {"error": "Crypto analysis failed"}
        
        return {
            "crypto_analysis": result.get("response", "Analysis unavailable"),
            "news_count": len(news_articles)
        }
    
    def analyze_market_sentiment(self, market_indicators: Dict[str, Any], news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall market sentiment"""
        sentiment_prompt = MARKET_SENTIMENT_PROMPT.format(
            market_indicators=json.dumps(market_indicators, indent=2),
            news_articles=self._format_news_articles(news_articles)
        )
        
        result = self.generate(sentiment_prompt)
        if "error" in result:
            return {"error": "Market sentiment analysis failed"}
        
        return {
            "market_sentiment": result.get("response", "Analysis unavailable"),
            "indicators_analyzed": list(market_indicators.keys())
        }
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """Format market data for LLM analysis"""
        formatted = []
        
        if "price_data" in market_data:
            formatted.append("PRICE DATA:")
            for symbol, data in market_data["price_data"].items():
                if "error" not in data:
                    formatted.append(f"  {symbol}: ${data.get('price', 'N/A')} ({data.get('change_percent', 'N/A')})")
        
        if "market_indicators" in market_data:
            formatted.append("MARKET INDICATORS:")
            indicators = market_data["market_indicators"]
            if "vix" in indicators:
                formatted.append(f"  VIX: {indicators['vix'].get('value', 'N/A')}")
            if "sp500" in indicators:
                formatted.append(f"  S&P 500: {indicators['sp500'].get('value', 'N/A')} ({indicators['sp500'].get('change_percent', 'N/A')})")
        
        return "\n".join(formatted)
    
    def _format_news_articles(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles for LLM analysis"""
        formatted = []
        for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles
            formatted.append(f"{i}. {article.get('title', 'No title')}")
            formatted.append(f"   Summary: {article.get('summary', 'No summary')}")
            formatted.append(f"   Source: {article.get('source', 'Unknown')}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _extract_key_insights(self, analysis: str) -> Dict[str, Any]:
        """Extract key insights from analysis text"""
        insights = {
            "sentiment": "neutral",
            "key_drivers": [],
            "risk_factors": [],
            "watch_levels": []
        }
        
        # Use LLM to extract structured insights
        extraction_prompt = f"""Extract key insights from this analysis and return as JSON:
        {analysis}
        
        Return JSON with:
        {{
            "sentiment": "bullish/bearish/neutral",
            "key_drivers": ["driver1", "driver2"],
            "risk_factors": ["risk1", "risk2"],
            "watch_levels": ["level1", "level2"]
        }}"""
        
        result = self.generate(extraction_prompt)
        if "error" not in result:
            try:
                extracted = json.loads(result.get("response", "{}"))
                insights.update(extracted)
            except json.JSONDecodeError:
                pass
        
        return insights
    
    def summarize_content(self, content: str, query_context: str = "") -> str:
        """Summarize content based on user query"""
        system_prompt = f"""You are a financial news summarizer. 
        Summarize the following content focusing on key financial information.
        User asked: {query_context}
        
        Provide a concise summary highlighting:
        - Key facts and figures
        - Main causes or reasons
        - Market impact
        - Important dates or deadlines"""
        
        result = self.generate(content, system_prompt)
        if "error" in result:
            return "Summary unavailable"
        
        return result.get("response", "Summary unavailable")
    
    def extract_entities(self, text: str) -> Dict[str, list]:
        """Extract financial entities from text"""
        system_prompt = """Extract financial entities from the text and return as JSON format:
        {
            "companies": ["company names"],
            "cryptocurrencies": ["crypto names/symbols"], 
            "people": ["person names"],
            "amounts": ["monetary amounts"],
            "dates": ["dates mentioned"]
        }
        
        Return only valid JSON."""
        
        result = self.generate(text, system_prompt)
        if "error" in result:
            return {}
        
        try:
            return json.loads(result.get("response", "{}"))
        except json.JSONDecodeError:
            return {}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of financial text"""
        system_prompt = """Analyze the sentiment of this financial text. Return JSON format:
        {
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }
        
        Return only valid JSON."""
        
        result = self.generate(text, system_prompt)
        if "error" in result:
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "Analysis failed"}
        
        try:
            return json.loads(result.get("response", "{}"))
        except json.JSONDecodeError:
            return {"sentiment": "neutral", "confidence": 0.5, "reasoning": "Parse error"}
    
    def health_check(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            models = response.json().get("models", [])
            return any(model["name"] == self.model for model in models)
        except:
            return False
    
    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for LLM context"""
        if not history:
            return "No previous conversation context available."
        
        formatted = []
        for turn in history[-3:]:  # Last 3 turns
            formatted.append(f"Previous Q: {turn.get('user_query', 'N/A')}")
            formatted.append(f"Intent: {turn.get('intent', 'N/A')}")
            formatted.append(f"Response: {turn.get('response_summary', 'N/A')}")
            formatted.append("")
        
        return "\n".join(formatted) if formatted else "No previous conversation context available."
    
    def _format_cached_data(self, cached_data: Dict[str, Any]) -> str:
        """Format cached market data for LLM context"""
        if not cached_data:
            return "No cached market data available."
        
        formatted = []
        for symbol, data in cached_data.items():
            if isinstance(data, dict) and "data" in data:
                market_data = data["data"]
                formatted.append(f"Cached data for {symbol}:")
                if "price_data" in market_data:
                    for sym, price_info in market_data["price_data"].items():
                        if "error" not in price_info:
                            formatted.append(f"  {sym}: ${price_info.get('price', 'N/A')} ({price_info.get('change_percent', 'N/A')})")
                formatted.append("")
        
        return "\n".join(formatted) if formatted else "No cached market data available."