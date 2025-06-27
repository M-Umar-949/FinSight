# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Ollama Settings
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    # Cache Settings
    CACHE_TTL = int(os.getenv('CACHE_TTL', 7200))  # 2 hours
    
    # News Sources
    NEWS_SOURCES = [
        'https://www.coindesk.com',
        'https://finance.yahoo.com',
        'https://cointelegraph.com'
    ]
    
    # Rate Limiting
    REQUEST_DELAY = 1  # seconds between requests