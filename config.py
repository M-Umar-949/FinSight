# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama Settings
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    # API Keys for Market Data
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
    YAHOO_FINANCE_API_KEY = os.getenv('YAHOO_FINANCE_API_KEY', '')
    
    # Cache Settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', 7200))  # 2 hours
    
    # News Sources
    NEWS_SOURCES = [
        'https://www.coindesk.com',
        'https://finance.yahoo.com',
        'https://cointelegraph.com',
        'https://www.reuters.com',
        'https://www.bloomberg.com'
    ]
    
    # Rate Limiting
    REQUEST_DELAY = 1  # seconds between requests
    
    # Analysis Settings
    MAX_NEWS_ARTICLES = int(os.getenv('MAX_NEWS_ARTICLES', 8))
    MAX_SYMBOLS_ANALYZED = int(os.getenv('MAX_SYMBOLS_ANALYZED', 3))
    
    # Market Indicators to track
    MARKET_INDICATORS = [
        '^VIX',      # Volatility Index
        '^GSPC',     # S&P 500
        '^DJI',      # Dow Jones
        '^IXIC',     # NASDAQ
        '^RUT'       # Russell 2000
    ]
    
    # LLM Analysis Settings
    ANALYSIS_TEMPERATURE = float(os.getenv('ANALYSIS_TEMPERATURE', 0.3))
    ANALYSIS_MAX_TOKENS = int(os.getenv('ANALYSIS_MAX_TOKENS', 2048))
    
    # Data Quality Settings
    MIN_NEWS_ARTICLES = 2  # Minimum articles needed for analysis
    PRICE_DATA_TIMEOUT = 10  # seconds timeout for price data
    NEWS_FETCH_TIMEOUT = 15  # seconds timeout for news fetching