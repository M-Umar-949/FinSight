# test_intent.py
import asyncio
from main import FinSight

async def test_intent_detection():
    """Test the intent detection functionality"""
    finsight = FinSight()
    
    # Test queries for different intents
    test_queries = [
        "Why is BTC dropping today?",
        "What are the latest SEC crypto regulations?",
        "How did Apple's earnings affect the stock price?",
        "What's the current market sentiment for crypto?",
        "Can you analyze this YouTube video about Bitcoin?",
        "Summarize the latest financial news",
        "Show me the technical analysis for ETH",
        "What are the fundamentals for Tesla stock?",
        "Explain the latest DeFi developments",
        "What is blockchain technology?"
    ]
    
    print("🧪 Testing Intent Detection")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        try:
            result = await finsight.process_query(query)
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                intent = result.get('intent', 'unknown')
                response = result.get('response', result.get('message', 'No response'))
                print(f"   🎯 Intent: {intent}")
                print(f"   💡 Response: {response[:100]}...")
                
                if 'tools_needed' in result:
                    tools = ', '.join(result['tools_needed'])
                    print(f"   🛠️ Tools: {tools}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Intent detection test completed!")

if __name__ == "__main__":
    asyncio.run(test_intent_detection()) 