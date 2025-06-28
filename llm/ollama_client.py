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
    GENERAL_QUERY_PROMPT,
    NEWS_SENTIMENT_ANALYSIS_PROMPT
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
    
    def handle_general_query(self, query: str, context: dict = None) -> dict:
        """Handle general queries, greetings, and help requests"""
        try:
            # Use the prompt template from prompts.py
            prompt = GENERAL_QUERY_PROMPT.format(query=query)
            
            # Get response from Ollama
            response = self._get_ollama_response(prompt)
            
            return {
                "response": response,
                "intent": "general_query",
                "query_type": "general"
            }
        except Exception as e:
            return {"error": f"General query handling failed: {str(e)}"}
    
    def analyze_price_movement(self, query: str, market_data: dict, news_articles: list, context: dict = None) -> dict:
        """Analyze price movement with comprehensive data"""
        try:
            # Format market data for prompt
            market_context = self._format_market_data_for_prompt(market_data, news_articles)
            news_context = self._format_news_articles(news_articles)
            
            # Use the prompt template from prompts.py
            prompt = PRICE_MOVEMENT_ANALYSIS_PROMPT.format(
                query=query,
                market_data=market_context,
                news_articles=news_context
            )
            
            # Get response from Ollama
            response = self._get_ollama_response(prompt)
            
            return {
                "analysis": response,
                "market_data": market_data,
                "news_articles": news_articles
            }
        except Exception as e:
            return {"error": f"Price movement analysis failed: {str(e)}"}
    
    def analyze_company_news(self, query: str, news_articles: list, market_data: dict, context: dict = None) -> dict:
        """Analyze company news with comprehensive data"""
        try:
            # Format news data for prompt
            news_context = self._format_news_data_for_prompt(news_articles, market_data)
            market_context = self._format_market_data(market_data) if market_data else "No market data available"
            
            # Use the prompt template from prompts.py
            prompt = COMPANY_NEWS_ANALYSIS_PROMPT.format(
                query=query,
                news_articles=news_context,
                market_data=market_context
            )
            
            # Get response from Ollama
            response = self._get_ollama_response(prompt)
            
            return {
                "analysis": response,
                "news_articles": news_articles,
                "market_data": market_data
            }
        except Exception as e:
            return {"error": f"Company news analysis failed: {str(e)}"}
    
    def analyze_regulatory_news(self, query: str, news_articles: list, market_data: dict, context: dict = None) -> dict:
        """Analyze regulatory news with comprehensive data"""
        try:
            # Format news data for prompt
            news_context = self._format_news_data_for_prompt(news_articles, market_data)
            market_context = self._format_market_data(market_data) if market_data else "No market data available"
            
            # Use the prompt template from prompts.py
            prompt = REGULATORY_NEWS_ANALYSIS_PROMPT.format(
                query=query,
                news_articles=news_context,
                market_data=market_context
            )
            
            # Get response from Ollama
            response = self._get_ollama_response(prompt)
            
            return {
                "analysis": response,
                "news_articles": news_articles,
                "market_data": market_data
            }
        except Exception as e:
            return {"error": f"Regulatory news analysis failed: {str(e)}"}
    
    def analyze_video_content(self, query: str, video_content: str, market_context: str, context: dict = None) -> dict:
        """Analyze video content with market context"""
        try:
            # Use the prompt template from prompts.py
            prompt = VIDEO_ANALYSIS_PROMPT.format(
                query=query,
                video_content=video_content,
                market_context=market_context
            )
            
            # Get response from Ollama
            response = self._get_ollama_response(prompt)
            
            return {
                "analysis": response,
                "video_content": video_content,
                "market_context": market_context
            }
        except Exception as e:
            return {"error": f"Video analysis failed: {str(e)}"}
    
    def analyze_news_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles"""
        try:
            formatted_articles = self._format_news_articles(articles)
            
            # Use the prompt template from prompts.py
            prompt = NEWS_SENTIMENT_ANALYSIS_PROMPT.format(articles=formatted_articles)
            
            response = self._get_ollama_response(prompt)
            
            return {
                "sentiment_analysis": response,
                "article_count": len(articles)
            }
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def _format_market_data_for_prompt(self, market_data: dict, news_articles: list) -> str:
        """Format market data for prompt"""
        formatted = []
        
        if market_data and "error" not in market_data:
            # Add price data
            if market_data.get("price_data"):
                formatted.append("📊 Price Data:")
                for symbol, data in market_data["price_data"].items():
                    formatted.append(f"  {symbol}: ${data.get('price', 'N/A')} ({data.get('change_percent', 'N/A')}%)")
            
            # Add market indicators
            if market_data.get("market_indicators"):
                formatted.append("📈 Market Indicators:")
                for indicator, value in market_data["market_indicators"].items():
                    formatted.append(f"  {indicator}: {value}")
        
        # Add news summary
        if news_articles:
            formatted.append("📰 Recent News:")
            for i, article in enumerate(news_articles[:3], 1):
                formatted.append(f"  {i}. {article.get('title', 'No title')}")
        
        return "\n".join(formatted) if formatted else "No market data available"
    
    def _format_news_data_for_prompt(self, news_articles: list, market_data: dict) -> str:
        """Format news data for prompt"""
        formatted = []
        
        if news_articles:
            formatted.append("📰 News Articles:")
            for i, article in enumerate(news_articles, 1):
                formatted.append(f"  {i}. {article.get('title', 'No title')}")
                if article.get('description'):
                    formatted.append(f"     {article.get('description', '')[:100]}...")
                formatted.append("")
        
        return "\n".join(formatted) if formatted else "No news articles available"
    
    def _format_market_data(self, market_data: dict) -> str:
        """Format market data for display"""
        if not market_data or "error" in market_data:
            return "No market data available"
        
        formatted = []
        if market_data.get("price_data"):
            formatted.append("📊 Market Data:")
            for symbol, data in market_data["price_data"].items():
                formatted.append(f"  {symbol}: ${data.get('price', 'N/A')} ({data.get('change_percent', 'N/A')}%)")
        
        return "\n".join(formatted) if formatted else "No market data available"
    
    def _format_news_articles(self, articles: List[Dict[str, Any]]) -> str:
        """Format news articles for prompt"""
        if not articles:
            return "No news articles available"
        
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append(f"{i}. {article.get('title', 'No title')}")
            if article.get('description'):
                formatted.append(f"   {article.get('description', '')[:150]}...")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _get_ollama_response(self, prompt: str) -> str:
        """Get response from Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"