# 🚀 FinSight - Fintech Intelligence Agent

An intelligent, agentic web-based pipeline for fintech news and analysis with modular tool architecture.

## 🎯 Features

### 🎯 Four Core Analysis Categories

1. **Price Movement Analysis** 📈
   - Real-time market data fetching
   - Technical and fundamental analysis
   - Price trend identification
   - Support/resistance levels
   - Market sentiment integration

2. **Company News Analysis** 📰
   - Latest company news aggregation
   - Earnings reports and financial updates
   - Corporate announcements
   - Market impact assessment
   - Sentiment analysis

3. **Regulatory News Analysis** ⚖️
   - Regulatory updates and policy changes
   - Compliance news
   - Government announcements
   - Industry regulation impact
   - Legal framework analysis

4. **Video Analysis** 🎥
   - **Video transcription** using multiple APIs (YouTube, AssemblyAI, OpenAI)
   - YouTube video metadata extraction
   - Transcript analysis and summarization
   - Key points extraction
   - Sentiment analysis of video content
   - Market context integration

### 🔧 Additional Features

- **Context-Aware Conversations** 💬
  - Maintains conversation history
  - Caches market data for efficiency
  - Context-aware analysis and responses

- **General Query Handling** 🤖
  - Greetings and help commands
  - General financial questions
  - Domain-specific assistance

- **Multi-API Integration** 🔌
  - Alpha Vantage for market data
  - YouTube Data API for video info
  - AssemblyAI for transcription
  - OpenAI Whisper for audio processing
  - News APIs for content aggregation

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FinSight
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the required model
   ollama pull llama3.2:latest
   ```

4. **Environment setup**
   ```bash
   # Create .env file
   echo "OLLAMA_HOST=localhost:11434" > .env
   echo "OLLAMA_MODEL=llama3.2:latest" >> .env
   ```

## 🚀 Usage

### Web Interface
```bash
streamlit run frontend/app.py
```

### CLI Interface
```bash
python main.py
```

### Test Intent Detection
```bash
python test_intent.py
```

## 📁 Project Structure

```
FinSight/
├── main.py                 # Main application logic
├── config.py              # Configuration settings
├── frontend/
│   └── app.py             # Streamlit web interface
├── llm/
│   ├── __init__.py
│   ├── ollama_client.py   # LLM integration
│   └── prompts.py         # LLM prompts
├── tools/
│   ├── __init__.py
│   ├── scraper.py         # News scraping (placeholder)
│   ├── sentiment.py       # Sentiment analysis (placeholder)
│   ├── summarizer.py      # Content summarization (placeholder)
│   └── video_transcriber.py # Video transcription (placeholder)
├── data/
│   ├── __init__.py
│   └── cache.py           # Caching layer
└── requirements.txt       # Dependencies
```

## 🔧 Tool Architecture

### Current Placeholder Tools
- **NewsScraper**: Web scraping for financial news
- **SentimentAnalyzer**: Market sentiment analysis
- **ContentSummarizer**: Article and video summarization
- **VideoTranscriber**: YouTube video transcription

### Tool Integration Pattern
```python
# Example tool usage
from tools import NewsScraper, SentimentAnalyzer

scraper = NewsScraper()
sentiment = SentimentAnalyzer()

# Scrape news
articles = await scraper.scrape_news("Bitcoin price")

# Analyze sentiment
sentiment_result = sentiment.analyze_text_sentiment(articles[0]['content'])
```

## 🎯 Intent Detection Examples

| Query | Detected Intent | Tools Needed |
|-------|----------------|--------------|
| "Why is BTC dropping?" | `price_movement` | price_analyzer, market_data |
| "Latest SEC regulations" | `regulatory_news` | news_scraper, regulatory_db |
| "AAPL earnings impact" | `company_event` | earnings_analyzer, news_scraper |
| "Analyze this YouTube video" | `video_transcription` | youtube_extractor, transcription_service |
| "Market sentiment today" | `market_sentiment` | sentiment_analyzer, social_media_scraper |

## 🔮 Next Steps

### Immediate Implementation Priorities
1. **News Scraping**: Implement actual web scraping for CoinDesk, Bloomberg, etc.
2. **Video Transcription**: Integrate Whisper or similar for YouTube transcription
3. **Database Integration**: Add MongoDB for data storage
4. **Caching Layer**: Implement timestamp-based caching
5. **Neo4j Integration**: Knowledge graph for entities and relationships

### Advanced Features
- **Real-time Data**: Live market data integration
- **Advanced Analytics**: Technical and fundamental analysis
- **API Endpoints**: RESTful API for external integrations
- **User Authentication**: Multi-user support
- **Advanced UI**: Real-time updates, charts, and dashboards

## 🧪 Testing

Run the intent detection test:
```bash
python test_intent.py
```

This will test various query types and verify intent classification accuracy.

## 📝 Environment Variables

Create a `.env` file with:
```env
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.2:latest
CACHE_TTL=7200
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of a hiring assignment for fintech intelligence development.

---

**🚀 Ready to revolutionize fintech analysis with intelligent, modular tools!**
