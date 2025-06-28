import aiohttp
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Any
import re
from datetime import datetime, timedelta
from config import Config
import asyncio

# Initialize config
config = Config()

async def fetch_yahoo_finance_news(query: str, limit=None):
    """Enhanced Yahoo Finance news scraper with better data extraction"""
    if limit is None:
        limit = config.MAX_NEWS_ARTICLES
        
    search_url = f"https://news.search.yahoo.com/search?p={query.replace(' ', '+')}"
    articles = []

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, timeout=config.NEWS_FETCH_TIMEOUT) as resp:
                if resp.status != 200:
                    return [{"error": f"Failed to fetch: {resp.status}"}]
                text = await resp.text()

        soup = BeautifulSoup(text, "html.parser")
        news_cards = soup.select("div.NewsArticle") or soup.select("li.js-stream-content")

        for card in news_cards[:limit]:
            title_tag = card.find("h4") or card.find("h3")
            link_tag = title_tag.find("a") if title_tag else None
            desc_tag = card.find("p") or card.find("div", class_="s-desc")
            time_tag = card.find("span", class_="s-time") or card.find("time")

            title = title_tag.text.strip() if title_tag else "No Title"
            link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
            summary = desc_tag.text.strip() if desc_tag else "No summary available."
            timestamp = time_tag.text.strip() if time_tag else "Unknown"

            if link:
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "timestamp": timestamp,
                    "source": "Yahoo Finance"
                })
    except Exception as e:
        return [{"error": f"Scraping failed: {str(e)}"}]

    return articles

async def fetch_stock_price_data(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock price data"""
    api_key = config.ALPHA_VANTAGE_API_KEY
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=config.PRICE_DATA_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    quote = data.get("Global Quote", {})
                    
                    # Check if we got valid data
                    if not quote or "05. price" not in quote:
                        return {"error": f"No price data available for {symbol}"}
                    
                    return {
                        "symbol": symbol,
                        "price": quote.get("05. price", "N/A"),
                        "change": quote.get("09. change", "N/A"),
                        "change_percent": quote.get("10. change percent", "N/A"),
                        "volume": quote.get("06. volume", "N/A"),
                        "high": quote.get("03. high", "N/A"),
                        "low": quote.get("04. low", "N/A"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"API request failed with status {resp.status}"}
    except Exception as e:
        return {"error": f"Failed to fetch price data for {symbol}: {str(e)}"}

async def fetch_market_indicators() -> Dict[str, Any]:
    """Fetch key market indicators"""
    indicators = {}
    
    for symbol in config.MARKET_INDICATORS:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={config.ALPHA_VANTAGE_API_KEY}"
                async with session.get(url, timeout=config.PRICE_DATA_TIMEOUT) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        quote_data = data.get("Global Quote", {})
                        
                        if quote_data and "05. price" in quote_data:
                            indicator_name = symbol.replace("^", "").lower()
                            indicators[indicator_name] = {
                                "value": quote_data.get("05. price", "N/A"),
                                "change": quote_data.get("09. change", "N/A"),
                                "change_percent": quote_data.get("10. change percent", "N/A")
                            }
        except Exception as e:
            print(f"Failed to fetch {symbol}: {str(e)}")
            continue
    
    return indicators

def extract_stock_symbols(text: str) -> List[str]:
    """Extract stock symbols from text using regex patterns"""
    # Common stock symbol patterns
    patterns = [
        r'\b[A-Z]{1,5}\b',  # 1-5 letter symbols
        r'\$[A-Z]{1,5}\b',  # $AAPL format
    ]
    
    symbols = set()
    for pattern in patterns:
        matches = re.findall(pattern, text.upper())
        symbols.update(matches)
    
    # Filter out common words that aren't stock symbols
    common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
    symbols = {s.replace('$', '') for s in symbols if s.replace('$', '') not in common_words}
    
    return list(symbols)[:config.MAX_SYMBOLS_ANALYZED]

async def get_comprehensive_market_data(query: str) -> Dict[str, Any]:
    """Get comprehensive market data including news, prices, and indicators"""
    try:
        # Extract potential stock symbols from query
        symbols = extract_stock_symbols(query)
        
        # Fetch news articles
        news_articles = await fetch_yahoo_finance_news(query, config.MAX_NEWS_ARTICLES)
        
        # Check if we have enough news articles for analysis
        if len([a for a in news_articles if "error" not in a]) < config.MIN_NEWS_ARTICLES:
            return {"error": f"Insufficient news articles found. Need at least {config.MIN_NEWS_ARTICLES}"}
        
        # Fetch market indicators
        market_indicators = await fetch_market_indicators()
        
        # Fetch price data for extracted symbols
        price_data = {}
        for symbol in symbols:
            price_data[symbol] = await fetch_stock_price_data(symbol)
            # Add small delay to respect rate limits
            await asyncio.sleep(config.REQUEST_DELAY)
        
        return {
            "query": query,
            "extracted_symbols": symbols,
            "news_articles": news_articles,
            "market_indicators": market_indicators,
            "price_data": price_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Failed to gather market data: {str(e)}"}
