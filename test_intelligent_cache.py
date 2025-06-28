#!/usr/bin/env python3
"""
Test script for FinSight Intelligent Caching System
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import FinSight

async def test_intelligent_caching():
    """Test the intelligent caching functionality"""
    print("🧠 Testing FinSight Intelligent Caching System")
    print("=" * 60)
    
    finsight = FinSight()
    
    # Test similar queries that should match semantically
    test_queries = [
        "can you tell me about the weather in pakistan today",
        "weather condition in pakistan",
        "what's the weather like in pakistan",
        "pakistan weather forecast",
        "how is the weather in pakistan today"
    ]
    
    print("🌤️ Testing Weather Queries (should match semantically)")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}: '{query}'")
        print("-" * 30)
        
        result = await finsight.process_query(query)
        print(f"Intent: {result.get('intent', 'unknown')}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            response = result.get('response', 'No response')
            print(f"Response: {response[:100]}...")
    
    print("\n" + "=" * 60)
    print("📊 Cache Statistics After Weather Tests:")
    stats = finsight.cache.get_cache_stats()
    if "error" not in stats:
        print(f"Total entries: {stats['total_entries']}")
        print(f"Intent distribution: {stats['intent_distribution']}")
    else:
        print(f"Cache error: {stats['error']}")
    
    print("\n" + "=" * 60)
    print("🏢 Testing Company Queries (should match semantically)")
    print("-" * 50)
    
    company_queries = [
        "what is the price of AAPL stock",
        "AAPL stock price today",
        "how much is Apple stock worth",
        "Apple share price",
        "AAPL current value"
    ]
    
    for i, query in enumerate(company_queries, 1):
        print(f"\n📝 Query {i}: '{query}'")
        print("-" * 30)
        
        result = await finsight.process_query(query)
        print(f"Intent: {result.get('intent', 'unknown')}")
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            if result.get('intent') == 'price_movement':
                analysis = result.get('analysis', 'No analysis')
                print(f"Analysis: {analysis[:100]}...")
            else:
                response = result.get('response', 'No response')
                print(f"Response: {response[:100]}...")
    
    print("\n" + "=" * 60)
    print("📊 Final Cache Statistics:")
    stats = finsight.cache.get_cache_stats()
    if "error" not in stats:
        print(f"Total entries: {stats['total_entries']}")
        print(f"Intent distribution: {stats['intent_distribution']}")
    else:
        print(f"Cache error: {stats['error']}")
    
    # Cleanup
    finsight.cleanup()
    print("\n✅ Intelligent cache test completed!")

if __name__ == "__main__":
    asyncio.run(test_intelligent_caching()) 