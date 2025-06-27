# FinSight Four-Category Analysis System

## Overview

FinSight has been streamlined to focus on four core categories, each with integrated sentiment analysis:

1. **📊 Price Movement Analysis** - Stock/crypto price changes and market movements
2. **🏢 Company News Analysis** - Corporate events, earnings, and business developments  
3. **⚖️ Regulatory News Analysis** - Government policies, compliance, and regulations
4. **🎥 Video Analysis** - Video content analysis and transcription

## Key Features

### 🧠 **Integrated Sentiment Analysis**
- **News Sentiment**: Analyzes sentiment of scraped news articles
- **Market Sentiment**: Evaluates broader market mood and indicators
- **Content Sentiment**: Assesses tone and sentiment of video content
- **Unified Insights**: Combines multiple sentiment sources for comprehensive analysis

### 🔍 **Comprehensive Data Collection**
- **Real-time Market Data**: Prices, indicators, and technical data
- **Multi-source News**: Yahoo Finance, Reuters, Bloomberg, and more
- **Symbol Extraction**: Automatic identification of stocks/crypto symbols
- **Market Context**: VIX, S&P 500, and other market indicators

### 🤖 **AI-Powered Analysis**
- **Specialized Prompts**: Category-specific analysis frameworks
- **Structured Insights**: Key drivers, risk factors, and actionable insights
- **Contextual Understanding**: LLM interprets data in query context
- **Multi-layered Analysis**: Technical, fundamental, and sentiment perspectives

## Category Details

### 1. 📊 Price Movement Analysis

**Purpose**: Analyze stock and cryptocurrency price movements with market context

**Capabilities**:
- Real-time price data and technical indicators
- News impact analysis on price movements
- Market sentiment and volatility context
- Risk assessment and key levels to watch
- Actionable insights for investors

**Example Queries**:
- "Why is AAPL stock dropping today?"
- "What's happening with Tesla TSLA price movement?"
- "Bitcoin BTC price analysis and market sentiment"
- "S&P 500 market movement and volatility"

**Output Structure**:
```json
{
  "intent": "price_movement",
  "analysis": "Comprehensive price movement analysis...",
  "key_insights": {
    "sentiment": "bearish",
    "key_drivers": ["earnings miss", "market volatility"],
    "risk_factors": ["Fed policy", "sector rotation"],
    "watch_levels": ["$150 support", "$160 resistance"]
  },
  "market_data": {
    "symbols_found": ["AAPL"],
    "price_data": {...},
    "news_count": 8
  },
  "additional_insights": {
    "news_sentiment": "Negative sentiment in recent news...",
    "market_sentiment": "Overall market sentiment is cautious..."
  }
}
```

### 2. 🏢 Company News Analysis

**Purpose**: Analyze corporate events, earnings, and business developments

**Capabilities**:
- Company event summary and strategic implications
- Financial impact analysis and earnings implications
- Competitive context and market positioning
- Future outlook and key milestones
- Integrated sentiment analysis

**Example Queries**:
- "Apple AAPL earnings announcement analysis"
- "Tesla TSLA new product launch"
- "Microsoft MSFT acquisition news"
- "Amazon AMZN business expansion"

**Output Structure**:
```json
{
  "intent": "company_news",
  "analysis": "Comprehensive company news analysis...",
  "key_insights": {
    "sentiment": "positive",
    "key_drivers": ["strong earnings", "product innovation"],
    "risk_factors": ["competition", "supply chain"],
    "watch_levels": ["earnings date", "product launch"]
  },
  "market_data": {
    "symbols_found": ["AAPL"],
    "news_count": 6
  }
}
```

### 3. ⚖️ Regulatory News Analysis

**Purpose**: Analyze regulatory developments and compliance implications

**Capabilities**:
- Regulatory development summary and policy updates
- Market impact analysis and sector implications
- Compliance requirements and implementation timeline
- Risk assessment and enforcement actions
- Strategic considerations for businesses

**Example Queries**:
- "SEC new regulations for crypto"
- "CFTC trading rules update"
- "Federal Reserve policy changes"
- "EU digital asset regulations"

**Output Structure**:
```json
{
  "intent": "regulatory_news",
  "analysis": "Comprehensive regulatory analysis...",
  "key_insights": {
    "sentiment": "neutral",
    "key_drivers": ["compliance requirements", "market structure"],
    "risk_factors": ["enforcement actions", "implementation costs"],
    "watch_levels": ["compliance deadline", "enforcement date"]
  },
  "market_data": {
    "symbols_found": ["affected companies"],
    "news_count": 5
  }
}
```

### 4. 🎥 Video Analysis

**Purpose**: Analyze video content and extract financial insights

**Capabilities**:
- Video content summary and key points
- Financial analysis and investment insights
- Sentiment analysis of video content
- Credibility assessment and source reliability
- Actionable insights from video content

**Example Queries**:
- "Analyze this YouTube video about market trends"
- "Video analysis of earnings call"
- "YouTube content about crypto regulations"
- "Video about company merger news"

**Output Structure**:
```json
{
  "intent": "video_analysis",
  "analysis": "Comprehensive video content analysis...",
  "key_insights": {
    "sentiment": "bullish",
    "key_drivers": ["expert opinion", "market analysis"],
    "risk_factors": ["bias", "limited data"],
    "watch_levels": ["key dates mentioned"]
  },
  "video_info": {
    "content_length": 1500,
    "content_preview": "Video content preview..."
  }
}
```

## Sentiment Analysis Integration

### How Sentiment Works Across Categories

1. **News Sentiment Analysis**
   - Analyzes sentiment of scraped news articles
   - Identifies bullish/bearish/neutral sentiment
   - Evaluates credibility and source quality
   - Assesses timing and urgency of information

2. **Market Sentiment Analysis**
   - Evaluates broader market indicators (VIX, S&P 500)
   - Analyzes market mood and volatility
   - Identifies sector rotation and flows
   - Assesses institutional vs retail sentiment

3. **Content Sentiment Analysis**
   - Analyzes tone and sentiment of video content
   - Evaluates confidence levels in statements
   - Identifies bias or perspective
   - Assesses expert credibility

### Sentiment Output Structure

```json
{
  "key_insights": {
    "sentiment": "bullish/bearish/neutral",
    "key_drivers": ["driver1", "driver2"],
    "risk_factors": ["risk1", "risk2"],
    "watch_levels": ["level1", "level2"]
  },
  "additional_insights": {
    "news_sentiment": "Detailed news sentiment analysis...",
    "market_sentiment": "Detailed market sentiment analysis..."
  }
}
```

## Configuration

### Environment Variables
```bash
# Required for real price data
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Ollama settings
OLLAMA_HOST=localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Analysis settings
MAX_NEWS_ARTICLES=8
MAX_SYMBOLS_ANALYZED=3
ANALYSIS_TEMPERATURE=0.3
```

### Intent Detection
The system automatically classifies queries into one of the four categories:

```python
# Intent detection examples
"Apple stock price" → price_movement
"Tesla earnings" → company_news  
"SEC regulations" → regulatory_news
"Video analysis" → video_analysis
```

## Usage Examples

### Basic Usage
```python
from main import FinSight

finsight = FinSight()

# Price movement analysis
result = await finsight.process_query("Why is AAPL dropping today?")

# Company news analysis
result = await finsight.process_query("Apple earnings announcement")

# Regulatory news analysis
result = await finsight.process_query("SEC crypto regulations")

# Video analysis
result = await finsight.process_query("Analyze this market video")
```

### Test Scripts
```bash
# Test all four categories
python test_four_categories.py

# Test price movement specifically
python test_price_movement.py

# Interactive CLI
python main.py
```

## Data Flow

### 1. Query Processing
```
User Query → Intent Detection → Category Routing
```

### 2. Data Collection
```
Category Handler → Market Data + News Articles + Video Content
```

### 3. LLM Analysis
```
Raw Data → Specialized Prompts → Structured Analysis
```

### 4. Sentiment Integration
```
Analysis Results → Sentiment Analysis → Unified Insights
```

### 5. Response Compilation
```
All Insights → Structured Response → User Output
```

## Error Handling

### Common Issues
1. **API Rate Limits**: Built-in delays and retry logic
2. **Insufficient Data**: Minimum article requirements
3. **Network Timeouts**: Configurable timeout settings
4. **LLM Failures**: Graceful fallbacks and error messages

### Fallback Behavior
- Unclear queries default to price movement analysis
- Missing data triggers appropriate error messages
- LLM failures provide basic responses

## Performance Optimization

### Caching
- News articles cached for 2 hours
- Price data cached for 5 minutes
- Market indicators cached for 1 hour

### Rate Limiting
- 1-second delay between API calls
- Configurable request delays
- Respectful of API limits

### Parallel Processing
- Concurrent data fetching
- Async/await for optimal performance
- Non-blocking LLM analysis

## Future Enhancements

### Planned Features
1. **Enhanced Video Processing**: YouTube API integration
2. **Social Media Sentiment**: Twitter/Reddit analysis
3. **Real-time Alerts**: Price and news monitoring
4. **Advanced Charting**: Technical pattern recognition

### API Integrations
- **YouTube API**: Video content extraction
- **Twitter API**: Social sentiment analysis
- **Polygon.io**: Enhanced market data
- **NewsAPI**: Additional news sources

## Troubleshooting

### Setup Issues
1. **Ollama not running**: Start with `ollama serve`
2. **Model not found**: Pull with `ollama pull llama3.1:8b`
3. **API key missing**: Set `ALPHA_VANTAGE_API_KEY` in `.env`

### Runtime Issues
1. **Network errors**: Check internet connection
2. **Rate limiting**: Increase delays in config
3. **LLM timeouts**: Reduce model complexity

### Data Quality Issues
1. **No news found**: Check query specificity
2. **Invalid symbols**: Verify symbol format
3. **Stale data**: Check cache settings

## Contributing

### Adding New Categories
1. Add category to intent detection
2. Create specialized prompt
3. Implement analysis method
4. Add handler in main.py
5. Update documentation

### Enhancing Analysis
1. Modify prompts in `prompts.py`
2. Add analysis methods to `OllamaClient`
3. Update handlers in `main.py`
4. Test with various queries

### Testing
1. Run `test_four_categories.py`
2. Test each category thoroughly
3. Verify sentiment integration
4. Check error handling 