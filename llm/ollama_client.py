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
        
        Respond with only the category name."""
        
        result = self.generate(query, system_prompt)
        if "error" in result:
            return "price_movement"  # fallback to most common intent
        
        return result.get("response", "price_movement").strip().lower()
    
    def analyze_price_movement(self, query: str, market_data: Dict[str, Any], news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive price movement analysis using LLM"""
        # Format market data for analysis
        market_summary = self._format_market_data(market_data)
        news_summary = self._format_news_articles(news_articles)
        
        # Generate comprehensive analysis
        analysis_prompt = PRICE_MOVEMENT_ANALYSIS_PROMPT.format(
            query=query,
            market_data=market_summary,
            news_articles=news_summary
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
            "symbols_analyzed": market_data.get("extracted_symbols", [])
        }
    
    def analyze_company_news(self, query: str, news_articles: List[Dict[str, Any]], market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze company news and corporate events"""
        news_summary = self._format_news_articles(news_articles)
        market_summary = self._format_market_data(market_data) if market_data else "No market data available"
        
        analysis_prompt = COMPANY_NEWS_ANALYSIS_PROMPT.format(
            query=query,
            news_articles=news_summary,
            market_data=market_summary
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
            "market_data": market_data
        }
    
    def analyze_regulatory_news(self, query: str, news_articles: List[Dict[str, Any]], market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze regulatory news and compliance developments"""
        news_summary = self._format_news_articles(news_articles)
        market_summary = self._format_market_data(market_data) if market_data else "No market data available"
        
        analysis_prompt = REGULATORY_NEWS_ANALYSIS_PROMPT.format(
            query=query,
            news_articles=news_summary,
            market_data=market_summary
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
            "market_data": market_data
        }
    
    def analyze_video_content(self, query: str, video_content: str, market_context: str = "") -> Dict[str, Any]:
        """Analyze video content and transcriptions"""
        analysis_prompt = VIDEO_ANALYSIS_PROMPT.format(
            query=query,
            video_content=video_content,
            market_context=market_context
        )
        
        result = self.generate(analysis_prompt)
        if "error" in result:
            return {"error": "Video analysis failed", "details": result["error"]}
        
        # Extract key insights
        insights = self._extract_key_insights(result.get("response", ""))
        
        return {
            "analysis": result.get("response", "Analysis unavailable"),
            "insights": insights,
            "content_length": len(video_content)
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