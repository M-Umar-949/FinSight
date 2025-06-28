# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama Settings
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    # MongoDB Settings
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'finsight')
    MONGODB_CACHE_COLLECTION = os.getenv('MONGODB_CACHE_COLLECTION', 'query_cache')
    
    # API Keys for Market Data
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    ENABLE_MARKET_DATA = os.getenv('ENABLE_MARKET_DATA', 'true').lower() == 'true'
    MAX_NEWS_ARTICLES = int(os.getenv('MAX_NEWS_ARTICLES', 5))
    
    # Cache Settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5 minutes
    
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
    MAX_SYMBOLS_ANALYZED = int(os.getenv('MAX_SYMBOLS_ANALYZED', 3))
    ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'
    
    # Market Indicators to track
    MARKET_INDICATORS = [
        'VIX', 'SPY', 'QQQ', 'IWM', 'TLT', 'GLD', 'USO', 'UUP'
    ]
    
    # LLM Analysis Settings
    ANALYSIS_TEMPERATURE = float(os.getenv('ANALYSIS_TEMPERATURE', 0.3))
    ANALYSIS_MAX_TOKENS = int(os.getenv('ANALYSIS_MAX_TOKENS', 2048))
    
    # Data Quality Settings
    MIN_NEWS_ARTICLES = 2  # Minimum articles needed for analysis
    PRICE_DATA_TIMEOUT = 10  # seconds timeout for price data
    NEWS_FETCH_TIMEOUT = 15  # seconds timeout for news fetching
    
    # Context Management Settings
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 10))
    CONTEXT_TTL = int(os.getenv('CONTEXT_TTL', 3600))  # 1 hour
    CACHE_MARKET_DATA = os.getenv('CACHE_MARKET_DATA', 'true').lower() == 'true'
    ENABLE_CONTEXT_ANALYSIS = os.getenv('ENABLE_CONTEXT_ANALYSIS', 'true').lower() == 'true'
    
    # Video Transcription Settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY', '')
    ENABLE_VIDEO_TRANSCRIPTION = os.getenv('ENABLE_VIDEO_TRANSCRIPTION', 'true').lower() == 'true'
    MAX_TRANSCRIPT_LENGTH = int(os.getenv('MAX_TRANSCRIPT_LENGTH', 5000))  # words
    TRANSCRIPTION_TIMEOUT = int(os.getenv('TRANSCRIPTION_TIMEOUT', 300))  # 5 minutes