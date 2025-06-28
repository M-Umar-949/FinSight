#!/usr/bin/env python3
"""
Simple test for video transcription
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.video_transcriber import VideoTranscriber

async def test_video():
    """Test the simplified video transcription"""
    print("🧪 Testing Simplified Video Transcription")
    print("=" * 50)
    
    transcriber = VideoTranscriber()
    
    # Test URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"🎬 Testing URL: {test_url}")
    print("-" * 30)
    
    # Test the full pipeline
    result = await transcriber.analyze_video(test_url, "What is this video about?")
    
    print("\n📊 Results:")
    print("-" * 30)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Status: {result.get('status', 'unknown')}")
        print(f"✅ Method: {result.get('transcript', {}).get('method', 'unknown')}")
        print(f"✅ Word count: {result.get('transcript', {}).get('word_count', 0)}")
        
        # Show transcript preview
        transcript = result.get('transcript', {}).get('text', '')
        if transcript:
            print(f"\n📝 Transcript preview:")
            print(f"   {transcript[:300]}...")
        
        # Show analysis
        analysis = result.get('analysis', {})
        if analysis:
            print(f"\n🔍 Analysis:")
            print(f"   Topics: {analysis.get('topics', [])}")
            print(f"   Sentiment: {analysis.get('sentiment', {}).get('sentiment', 'unknown')}")
            
            key_points = analysis.get('key_points', [])
            if key_points:
                print(f"   Key points:")
                for i, point in enumerate(key_points[:3], 1):
                    print(f"     {i}. {point[:100]}...")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_video()) 