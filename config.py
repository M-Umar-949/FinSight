# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Ollama Settings
        self.OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        
        # MongoDB Settings
        self.MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'finsight')
        self.MONGODB_CACHE_COLLECTION = os.getenv('MONGODB_CACHE_COLLECTION', 'query_cache')
        self.MONGODB_VIDEO_COLLECTION = os.getenv('MONGODB_VIDEO_COLLECTION', 'video_cache')
        
        # API Keys for Market Data
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
        self.ENABLE_MARKET_DATA = os.getenv('ENABLE_MARKET_DATA', 'true').lower() == 'true'
        self.MAX_NEWS_ARTICLES = int(os.getenv('MAX_NEWS_ARTICLES', 5))
        
        # Cache Settings
        self.CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', 86400))  # 24 hours in seconds
        
        # News Sources
        self.NEWS_SOURCES = [
            'https://www.coindesk.com',
            'https://finance.yahoo.com',
            'https://cointelegraph.com',
            'https://www.reuters.com',
            'https://www.bloomberg.com'
        ]
        
        # Rate Limiting
        self.REQUEST_DELAY = 1  # seconds between requests
        
        # Analysis Settings
        self.MAX_SYMBOLS_ANALYZED = int(os.getenv('MAX_SYMBOLS_ANALYZED', 3))
        self.ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'
        
        # Market Indicators to track
        self.MARKET_INDICATORS = [
            'VIX', 'SPY', 'QQQ', 'IWM', 'TLT', 'GLD', 'USO', 'UUP'
        ]
        
        # LLM Analysis Settings
        self.ANALYSIS_TEMPERATURE = float(os.getenv('ANALYSIS_TEMPERATURE', 0.3))
        self.ANALYSIS_MAX_TOKENS = int(os.getenv('ANALYSIS_MAX_TOKENS', 2048))
        
        # Data Quality Settings
        self.MIN_NEWS_ARTICLES = 2  # Minimum articles needed for analysis
        self.PRICE_DATA_TIMEOUT = 10  # seconds timeout for price data
        self.NEWS_FETCH_TIMEOUT = 15  # seconds timeout for news fetching
        
        # Context Management Settings
        self.MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', 10))
        self.CONTEXT_TTL = int(os.getenv('CONTEXT_TTL', 3600))  # 1 hour
        self.CACHE_MARKET_DATA = os.getenv('CACHE_MARKET_DATA', 'true').lower() == 'true'
        self.ENABLE_CONTEXT_ANALYSIS = os.getenv('ENABLE_CONTEXT_ANALYSIS', 'true').lower() == 'true'
        
        # Video Transcription Settings
        self.ENABLE_VIDEO_TRANSCRIPTION = os.getenv('ENABLE_VIDEO_TRANSCRIPTION', 'true').lower() == 'true'
        self.MAX_TRANSCRIPT_LENGTH = int(os.getenv('MAX_TRANSCRIPT_LENGTH', 5000))  # words
        self.TRANSCRIPTION_TIMEOUT = int(os.getenv('TRANSCRIPTION_TIMEOUT', 300))  # 5 minutes
        
        # Neo4j Configuration
        self.NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
        self.NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'umar123*')
        self.NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')