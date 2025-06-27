#!/usr/bin/env python3
"""
Test script for the four core FinSight categories:
1. Price Movement Analysis
2. Company News Analysis  
3. Regulatory News Analysis
4. Video Analysis

Each category includes integrated sentiment analysis.
"""

import asyncio
import json
from main import FinSight

async def test_all_categories():
    """Test all four core categories"""
    finsight = FinSight()
    
    # Test queries for each category
    test_categories = {
        "price_movement": [
            "Why is AAPL stock dropping today?",
            "What's happening with Tesla TSLA price movement?",
            "Bitcoin BTC price analysis and market sentiment",
            "S&P 500 market movement and volatility"
        ],
        "company_news": [
            "Apple AAPL earnings announcement analysis",
            "Tesla TSLA new product launch",
            "Microsoft MSFT acquisition news",
            "Amazon AMZN business expansion"
        ],
        "regulatory_news": [
            "SEC new regulations for crypto",
            "CFTC trading rules update",
            "Federal Reserve policy changes",
            "EU digital asset regulations"
        ],
        "video_analysis": [
            "Analyze this YouTube video about market trends",
            "Video analysis of earnings call",
            "YouTube content about crypto regulations",
            "Video about company merger news"
        ]
    }
    
    print("🚀 FinSight Four-Category Analysis Test Suite")
    print("=" * 70)
    print("Testing: Price Movement | Company News | Regulatory News | Video Analysis")
    print("Each category includes integrated sentiment analysis")
    print("=" * 70)
    
    for category, queries in test_categories.items():
        print(f"\n📊 Testing {category.upper().replace('_', ' ')} Category")
        print("=" * 50)
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            print("-" * 40)
            
            try:
                result = await finsight.process_query(query)
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                    continue
                
                # Display category-specific results
                display_category_results(category, result)
                
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
            
            print("\n" + "-" * 40)

def display_category_results(category: str, result: dict):
    """Display results based on category"""
    print(f"✅ Intent: {result.get('intent', 'unknown')}")
    
    if category == "price_movement":
        display_price_movement_results(result)
    elif category == "company_news":
        display_company_news_results(result)
    elif category == "regulatory_news":
        display_regulatory_news_results(result)
    elif category == "video_analysis":
        display_video_analysis_results(result)

def display_price_movement_results(result: dict):
    """Display price movement analysis results"""
    print(f"📊 Analysis: {result.get('analysis', 'No analysis available')[:300]}...")
    
    insights = result.get('key_insights', {})
    if insights:
        print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
        if insights.get('key_drivers'):
            print(f"🚀 Key Drivers: {', '.join(insights['key_drivers'])}")
        if insights.get('risk_factors'):
            print(f"⚠️ Risk Factors: {', '.join(insights['risk_factors'])}")
    
    market_data = result.get('market_data', {})
    if market_data.get('symbols_found'):
        print(f"📈 Symbols: {', '.join(market_data['symbols_found'])}")
    if market_data.get('news_count'):
        print(f"📰 News: {market_data['news_count']} articles")

def display_company_news_results(result: dict):
    """Display company news analysis results"""
    print(f"🏢 Analysis: {result.get('analysis', 'No analysis available')[:300]}...")
    
    insights = result.get('key_insights', {})
    if insights:
        print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
        if insights.get('key_drivers'):
            print(f"🚀 Key Events: {', '.join(insights['key_drivers'])}")
        if insights.get('risk_factors'):
            print(f"⚠️ Risk Factors: {', '.join(insights['risk_factors'])}")
    
    market_data = result.get('market_data', {})
    if market_data.get('symbols_found'):
        print(f"🏢 Companies: {', '.join(market_data['symbols_found'])}")
    if market_data.get('news_count'):
        print(f"📰 News: {market_data['news_count']} articles")

def display_regulatory_news_results(result: dict):
    """Display regulatory news analysis results"""
    print(f"⚖️ Analysis: {result.get('analysis', 'No analysis available')[:300]}...")
    
    insights = result.get('key_insights', {})
    if insights:
        print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
        if insights.get('key_drivers'):
            print(f"📋 Key Regulations: {', '.join(insights['key_drivers'])}")
        if insights.get('risk_factors'):
            print(f"⚠️ Compliance Risks: {', '.join(insights['risk_factors'])}")
    
    market_data = result.get('market_data', {})
    if market_data.get('symbols_found'):
        print(f"🏢 Affected: {', '.join(market_data['symbols_found'])}")
    if market_data.get('news_count'):
        print(f"📰 News: {market_data['news_count']} articles")

def display_video_analysis_results(result: dict):
    """Display video analysis results"""
    print(f"🎥 Analysis: {result.get('analysis', 'No analysis available')[:300]}...")
    
    insights = result.get('key_insights', {})
    if insights:
        print(f"🎯 Sentiment: {insights.get('sentiment', 'neutral')}")
        if insights.get('key_drivers'):
            print(f"🎬 Key Points: {', '.join(insights['key_drivers'])}")
    
    video_info = result.get('video_info', {})
    if video_info:
        print(f"📹 Content: {video_info.get('content_length', 'N/A')} chars")
        print(f"📹 Preview: {video_info.get('content_preview', 'N/A')[:100]}...")

async def test_sentiment_integration():
    """Test sentiment analysis integration across all categories"""
    finsight = FinSight()
    
    print("\n🧠 Testing Sentiment Analysis Integration")
    print("=" * 50)
    
    # Test queries that should trigger sentiment analysis
    sentiment_tests = [
        ("price_movement", "Why is the market so bearish today?"),
        ("company_news", "What's the sentiment around Apple's latest earnings?"),
        ("regulatory_news", "How are investors reacting to new crypto regulations?"),
        ("video_analysis", "Analyze the sentiment in this market analysis video")
    ]
    
    for category, query in sentiment_tests:
        print(f"\n🔍 {category.replace('_', ' ').title()}: {query}")
        print("-" * 40)
        
        try:
            result = await finsight.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Check for sentiment analysis
            insights = result.get('key_insights', {})
            additional = result.get('additional_insights', {})
            
            print(f"🎯 Main Sentiment: {insights.get('sentiment', 'neutral')}")
            
            if additional.get('news_sentiment'):
                print(f"📰 News Sentiment: {additional['news_sentiment'][:150]}...")
            
            if additional.get('market_sentiment'):
                print(f"🌐 Market Sentiment: {additional['market_sentiment'][:150]}...")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

async def detailed_category_test():
    """Detailed test of one example from each category"""
    finsight = FinSight()
    
    print("\n🔬 Detailed Category Analysis")
    print("=" * 50)
    
    detailed_tests = [
        ("price_movement", "Why is Tesla TSLA stock dropping today?"),
        ("company_news", "Apple AAPL earnings announcement and market impact"),
        ("regulatory_news", "SEC new regulations for cryptocurrency trading"),
        ("video_analysis", "Analyze this YouTube video about market trends")
    ]
    
    for category, query in detailed_tests:
        print(f"\n🎯 {category.replace('_', ' ').title()}: {query}")
        print("=" * 60)
        
        try:
            result = await finsight.process_query(query)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Pretty print the full result
            print("📋 Full Analysis Result:")
            print(json.dumps(result, indent=2, default=str))
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    print("🧪 FinSight Four-Category Analysis Test Suite")
    print("Make sure Ollama is running with llama3.1:8b model")
    print("You may need to set ALPHA_VANTAGE_API_KEY in your .env file for real price data")
    
    # Run comprehensive tests
    asyncio.run(test_all_categories())
    
    # Test sentiment integration
    asyncio.run(test_sentiment_integration())
    
    # Uncomment for detailed analysis
    # asyncio.run(detailed_category_test()) 