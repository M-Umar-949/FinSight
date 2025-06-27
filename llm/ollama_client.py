# llm/ollama_client.py
import requests
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

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
        - price_movement: Questions about price changes, drops, rises, market movements
        - regulatory_news: Questions about regulations, compliance, legal changes, SEC, CFTC
        - company_event: Questions about earnings, announcements, corporate events, IPO
        - market_sentiment: Questions about market mood, investor sentiment, fear/greed
        - video_transcription: Requests for video analysis, YouTube links, transcriptions
        - news_summary: Requests for news summaries, latest updates, breaking news
        - technical_analysis: Questions about charts, indicators, technical patterns
        - fundamental_analysis: Questions about company fundamentals, financials, ratios
        - crypto_specific: Cryptocurrency specific questions, DeFi, NFTs, blockchain
        - general_info: General information requests
        
        Respond with only the category name."""
        
        result = self.generate(query, system_prompt)
        if "error" in result:
            return "general_info"  # fallback
        
        return result.get("response", "general_info").strip().lower()
    
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