# tools/scraper.py
import asyncio
import aiohttp
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from datetime import datetime

class NewsScraper:
    def __init__(self):
        self.sources = {
            'coindesk': 'https://www.coindesk.com',
            'yahoo_finance': 'https://finance.yahoo.com',
            'cointelegraph': 'https://cointelegraph.com',
            'bloomberg': 'https://www.bloomberg.com'
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_yahoo_finance_news(self,query: str, limit=5):
        search_url = f"https://news.search.yahoo.com/search?p={query.replace(' ', '+')}"
        articles = []

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as resp:
                if resp.status != 200:
                    return [{"error": f"Failed to fetch: {resp.status}"}]
                text = await resp.text()

        soup = BeautifulSoup(text, "html.parser")
        for result in soup.find_all("div", class_="NewsArticle")[:limit]:
            title_tag = result.find("h4")
            link_tag = title_tag.find("a") if title_tag else None
            desc_tag = result.find("p")

            if title_tag and link_tag:
                articles.append({
                    "title": title_tag.text.strip(),
                    "link": link_tag["href"],
                    "summary": desc_tag.text.strip() if desc_tag else ""
                })

        return articles
    
    async def scrape_youtube_video(self, video_url: str) -> Dict[str, Any]:
        """Extract YouTube video information and prepare for transcription"""
        # Placeholder implementation
        return {
            "title": "Sample YouTube Video",
            "description": "Video description would be extracted here",
            "duration": "10:30",
            "upload_date": "2024-01-01",
            "channel": "Financial Channel",
            "video_id": "sample_id",
            "transcription_ready": True
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities from text"""
        # Placeholder implementation
        entities = {
            "companies": [],
            "cryptocurrencies": [],
            "people": [],
            "amounts": [],
            "dates": []
        }
        
        # Simple regex patterns for demonstration
        crypto_pattern = r'\b(BTC|ETH|XRP|ADA|DOT|LINK|LTC|BCH|BNB|SOL)\b'
        amount_pattern = r'\$\d+(?:\.\d{2})?'
        
        entities["cryptocurrencies"] = re.findall(crypto_pattern, text.upper())
        entities["amounts"] = re.findall(amount_pattern, text)
        
        return entities
