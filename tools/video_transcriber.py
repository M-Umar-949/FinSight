from typing import Dict, Any, Optional, List
import re
import json
import asyncio
from datetime import datetime
import aiohttp
from config import Config

class VideoTranscriber:
    def __init__(self):
        self.config = Config()
        # You can add API keys for various services here
        self.youtube_api_key = getattr(self.config, 'YOUTUBE_API_KEY', '')
        self.openai_api_key = getattr(self.config, 'OPENAI_API_KEY', '')
        self.assemblyai_api_key = getattr(self.config, 'ASSEMBLYAI_API_KEY', '')
        
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtu\.be\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_youtube_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get YouTube video information using YouTube Data API"""
        if not self.youtube_api_key:
            return {"error": "YouTube API key not configured"}
        
        url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': video_id,
            'key': self.youtube_api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('items'):
                            video_info = data['items'][0]
                            return {
                                "title": video_info['snippet']['title'],
                                "description": video_info['snippet']['description'],
                                "channel": video_info['snippet']['channelTitle'],
                                "duration": video_info['contentDetails']['duration'],
                                "view_count": video_info['statistics'].get('viewCount', 0),
                                "like_count": video_info['statistics'].get('likeCount', 0),
                                "published_at": video_info['snippet']['publishedAt']
                            }
                        else:
                            return {"error": "Video not found"}
                    else:
                        return {"error": f"YouTube API error: {response.status}"}
        except Exception as e:
            return {"error": f"Failed to fetch YouTube info: {str(e)}"}
    
    async def transcribe_with_assemblyai(self, audio_url: str) -> Dict[str, Any]:
        """Transcribe audio using AssemblyAI API"""
        if not self.assemblyai_api_key:
            return {"error": "AssemblyAI API key not configured"}
        
        headers = {
            "authorization": self.assemblyai_api_key,
            "content-type": "application/json"
        }
        
        # Submit transcription request
        submit_url = "https://api.assemblyai.com/v2/transcript"
        submit_data = {
            "audio_url": audio_url,
            "speaker_labels": True,
            "auto_highlights": True,
            "sentiment_analysis": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Submit transcription
                async with session.post(submit_url, json=submit_data, headers=headers) as response:
                    if response.status == 200:
                        submit_result = await response.json()
                        transcript_id = submit_result['id']
                        
                        # Poll for completion
                        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
                        while True:
                            async with session.get(polling_url, headers=headers) as poll_response:
                                if poll_response.status == 200:
                                    polling_result = await poll_response.json()
                                    if polling_result['status'] == 'completed':
                                        return {
                                            "transcript": polling_result['text'],
                                            "sentiment": polling_result.get('sentiment_analysis_results', []),
                                            "highlights": polling_result.get('auto_highlights_result', {}),
                                            "speakers": polling_result.get('utterances', [])
                                        }
                                    elif polling_result['status'] == 'error':
                                        return {"error": f"Transcription failed: {polling_result.get('error', 'Unknown error')}"}
                                    
                                    await asyncio.sleep(3)  # Wait before polling again
                                else:
                                    return {"error": f"Polling failed: {poll_response.status}"}
                    else:
                        return {"error": f"Submission failed: {response.status}"}
        except Exception as e:
            return {"error": f"AssemblyAI transcription failed: {str(e)}"}
    
    async def transcribe_with_openai(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API"""
        if not self.openai_api_key:
            return {"error": "OpenAI API key not configured"}
        
        # This would require the openai library
        # For now, return a placeholder
        return {"error": "OpenAI transcription not implemented yet"}
    
    def generate_simulated_transcript(self, video_title: str, duration_minutes: int = 10) -> Dict[str, Any]:
        """Generate a simulated transcript for testing purposes"""
        # Create a realistic financial video transcript
        topics = [
            "market analysis", "earnings report", "crypto trends", "stock recommendations",
            "economic indicators", "trading strategies", "company news", "market sentiment"
        ]
        
        topic = topics[hash(video_title) % len(topics)]
        
        # Generate realistic transcript content
        transcript_parts = [
            f"Welcome to today's {topic} discussion. I'm [Host Name] and today we're going to dive deep into the latest developments.",
            f"Let's start with the current market conditions. We're seeing significant volatility in the tech sector, particularly around companies like Apple, Tesla, and Microsoft.",
            f"The key factors driving this movement include earnings expectations, Federal Reserve policy changes, and global economic indicators.",
            f"Looking at the technical analysis, we can see support levels at key price points and resistance levels that traders should watch closely.",
            f"From a fundamental perspective, the underlying business metrics remain strong, but there are some concerns about valuation levels.",
            f"Let's talk about specific recommendations. Based on our analysis, we're maintaining a bullish outlook on technology stocks but with some caution on high-growth names.",
            f"The crypto market is also showing interesting patterns, with Bitcoin and Ethereum leading the charge while altcoins show mixed performance.",
            f"Risk management is crucial in this environment. We recommend maintaining diversified portfolios and setting appropriate stop-loss levels.",
            f"Looking ahead, we expect continued volatility but with opportunities for patient investors who can weather short-term fluctuations.",
            f"That's our analysis for today. Remember to do your own research and consider your risk tolerance before making investment decisions."
        ]
        
        # Add some filler content based on duration
        filler_content = [
            "Now, let me show you some charts that illustrate these points.",
            "The data clearly shows a pattern that we've seen before in similar market conditions.",
            "Investors should pay attention to these key indicators as they often signal important market turns.",
            "Let's take a look at some specific examples from recent market activity.",
            "This analysis is based on comprehensive research and multiple data sources."
        ]
        
        # Calculate how many filler segments to add based on duration
        filler_count = max(0, duration_minutes - 5)
        for i in range(filler_count):
            transcript_parts.append(filler_content[i % len(filler_content)])
        
        full_transcript = " ".join(transcript_parts)
        
        return {
            "transcript": full_transcript,
            "word_count": len(full_transcript.split()),
            "estimated_duration": duration_minutes,
            "topics_detected": [topic],
            "sentiment": "neutral",
            "confidence": 0.85
        }
    
    async def analyze_video_content(self, video_url: str = None, video_title: str = None) -> Dict[str, Any]:
        """Main method to analyze video content"""
        result = {
            "video_info": {},
            "transcript": {},
            "analysis": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract video information
        if video_url and "youtube.com" in video_url:
            video_id = self.extract_youtube_id(video_url)
            if video_id:
                video_info = await self.get_youtube_video_info(video_id)
                result["video_info"] = video_info
                video_title = video_info.get("title", video_title)
        
        # Generate or get transcript
        if video_title:
            # For now, use simulated transcript
            transcript_data = self.generate_simulated_transcript(video_title)
            result["transcript"] = transcript_data
        else:
            result["transcript"] = {"error": "No video title or URL provided"}
        
        return result
    
    def extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points from transcript"""
        # Simple key point extraction
        sentences = transcript.split('. ')
        key_points = []
        
        # Look for sentences with financial keywords
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'growth', 'decline',
            'market', 'stock', 'price', 'investment', 'trading', 'analysis',
            'recommendation', 'buy', 'sell', 'hold', 'target', 'support',
            'resistance', 'trend', 'volatility', 'risk', 'opportunity'
        ]
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in financial_keywords):
                if len(sentence) > 20:  # Avoid very short sentences
                    key_points.append(sentence.strip())
        
        return key_points[:5]  # Return top 5 key points
    
    def analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment of video content"""
        # Simple sentiment analysis
        positive_words = ['bullish', 'positive', 'growth', 'profit', 'gain', 'opportunity', 'strong', 'buy']
        negative_words = ['bearish', 'negative', 'loss', 'decline', 'risk', 'sell', 'weak', 'concern']
        
        transcript_lower = transcript.lower()
        positive_count = sum(1 for word in positive_words if word in transcript_lower)
        negative_count = sum(1 for word in negative_words if word in transcript_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, (positive_count - negative_count) / 10)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, (negative_count - positive_count) / 10)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        } 