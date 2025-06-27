from typing import Dict, Any, Optional, List
import re
import json
import asyncio
from datetime import datetime
import aiohttp
import subprocess
import tempfile
import os
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
    
    def download_audio_segment(self, video_id: str, duration_seconds: int = 120) -> str:
        """Download first 2 minutes of audio from YouTube video"""
        try:
            # Create temporary file for audio
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Use yt-dlp with simpler options to avoid ffmpeg issues
            cmd = [
                'yt-dlp',
                '-f', 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '--max-downloads', '1',
                '--no-playlist',
                '--no-warnings',
                '-o', temp_path,
                f'https://www.youtube.com/watch?v={video_id}'
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                print(f"✅ Audio downloaded successfully: {temp_path}")
                return temp_path
            else:
                print(f"❌ Download failed: {result.stderr}")
                
                # Try alternative approach without audio extraction
                print("🔄 Trying alternative download method...")
                alt_cmd = [
                    'yt-dlp',
                    '-f', 'worstaudio',  # Use worst quality to avoid codec issues
                    '--no-playlist',
                    '--no-warnings',
                    '-o', temp_path,
                    f'https://www.youtube.com/watch?v={video_id}'
                ]
                
                alt_result = subprocess.run(alt_cmd, capture_output=True, text=True, timeout=120)
                if alt_result.returncode == 0 and os.path.exists(temp_path):
                    print(f"✅ Alternative download successful: {temp_path}")
                    return temp_path
                else:
                    print(f"❌ Alternative download also failed: {alt_result.stderr}")
                    return ""
                
        except subprocess.TimeoutExpired:
            print("❌ Download timed out")
            return ""
        except Exception as e:
            print(f"❌ Error downloading audio: {str(e)}")
            return ""
    
    def transcribe_with_whisper(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio using local Whisper"""
        try:
            print(f"🎤 Starting Whisper transcription of: {audio_file_path}")
            
            # Check if file exists and has content
            if not os.path.exists(audio_file_path):
                return {"error": "Audio file not found"}
            
            file_size = os.path.getsize(audio_file_path)
            if file_size == 0:
                return {"error": "Audio file is empty"}
            
            print(f"📁 Audio file size: {file_size} bytes")
            
            # Use whisper command line tool with simpler options
            cmd = [
                'whisper',
                audio_file_path,
                '--model', 'tiny',  # Use tiny model for faster processing
                '--language', 'en',
                '--output_format', 'txt',
                '--verbose', 'False'
            ]
            
            print(f"Running Whisper command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                # Read the transcript file
                transcript_file = audio_file_path.replace('.mp3', '.txt')
                if os.path.exists(transcript_file):
                    with open(transcript_file, 'r') as f:
                        transcript = f.read().strip()
                    
                    print(f"✅ Transcription successful: {len(transcript)} characters")
                    
                    # Clean up files
                    try:
                        os.unlink(audio_file_path)
                        os.unlink(transcript_file)
                    except:
                        pass  # Don't fail if cleanup fails
                    
                    return {
                        "transcript": transcript,
                        "word_count": len(transcript.split()),
                        "status": "success"
                    }
                else:
                    return {"error": "Transcript file not created"}
            
            print(f"❌ Whisper transcription failed: {result.stderr}")
            return {"error": f"Transcription failed: {result.stderr}"}
            
        except subprocess.TimeoutExpired:
            print("❌ Whisper transcription timed out")
            return {"error": "Transcription timed out"}
        except Exception as e:
            print(f"❌ Error in Whisper transcription: {str(e)}")
            return {"error": f"Transcription error: {str(e)}"}
    
    async def analyze_video(self, url: str, query: str) -> Dict[str, Any]:
        """Main method to analyze video with transcription"""
        print(f"🎥 Analyzing video: {url}")
        
        # Step 1: Extract video ID and get info
        video_id = self.extract_youtube_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        video_info = await self.get_youtube_video_info(video_id)
        if "error" in video_info:
            return {"error": f"Failed to get video info: {video_info['error']}"}
        
        # Step 2: Download audio segment (first 2 minutes)
        print("📥 Downloading audio segment...")
        audio_file = self.download_audio_segment(video_id, duration_seconds=120)
        
        # Step 3: Transcribe with Whisper
        transcript_result = None
        if audio_file:
            print("🎤 Transcribing with Whisper...")
            transcript_result = self.transcribe_with_whisper(audio_file)
        else:
            print("⚠️ Audio download failed, using fallback analysis")
        
        # Step 4: Handle transcription result or fallback
        if transcript_result and "error" not in transcript_result:
            transcript = transcript_result["transcript"]
            key_points = self.extract_key_points(transcript)
            sentiment = self.analyze_sentiment(transcript)
            topics = self._detect_topics(transcript)
            word_count = transcript_result["word_count"]
            duration_analyzed = "2 minutes"
        else:
            # Fallback: Generate simulated transcript based on video info
            print("🔄 Using fallback simulated analysis...")
            fallback_transcript = self._generate_fallback_transcript(video_info, query)
            transcript = fallback_transcript["transcript"]
            key_points = fallback_transcript["key_points"]
            sentiment = fallback_transcript["sentiment"]
            topics = fallback_transcript["topics"]
            word_count = fallback_transcript["word_count"]
            duration_analyzed = "simulated"
        
        # Step 5: Compile result
        result = {
            "video_info": video_info,
            "transcript": {
                "text": transcript,
                "word_count": word_count,
                "duration_analyzed": duration_analyzed,
                "method": "whisper" if transcript_result and "error" not in transcript_result else "fallback"
            },
            "analysis": {
                "key_points": key_points,
                "sentiment": sentiment,
                "topics": topics
            },
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        return result
    
    def _generate_fallback_transcript(self, video_info: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate fallback transcript when real transcription fails"""
        title = video_info.get("title", "Unknown Video")
        channel = video_info.get("channel", "Unknown Channel")
        
        # Generate context-aware transcript based on video info and query
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['earnings', 'quarter', 'financial']):
            transcript = f"Welcome to {channel}. Today we're discussing {title}. This appears to be an earnings call or financial analysis video. Key topics typically covered in such content include quarterly performance, revenue growth, profit margins, and future outlook. The analysis would focus on financial metrics, market performance, and strategic initiatives."
            topics = ['earnings_analysis', 'financial_performance']
        elif any(word in query_lower for word in ['crypto', 'bitcoin', 'ethereum']):
            transcript = f"Welcome to {channel}. Today we're analyzing {title}. This cryptocurrency analysis would typically cover market trends, price movements, technical indicators, and fundamental factors affecting digital assets. Key discussion points include market sentiment, trading volumes, and regulatory developments."
            topics = ['cryptocurrency', 'market_analysis']
        elif any(word in query_lower for word in ['stock', 'market', 'trading']):
            transcript = f"Welcome to {channel}. Today we're covering {title}. This stock market analysis would typically discuss price movements, technical analysis, fundamental factors, and market sentiment. Key points include support and resistance levels, trading volumes, and market trends."
            topics = ['stock_market', 'technical_analysis']
        else:
            transcript = f"Welcome to {channel}. Today we're discussing {title}. This financial analysis video would typically cover market trends, investment opportunities, and economic factors. The content would include analysis of key financial indicators, market sentiment, and strategic insights for investors."
            topics = ['general_finance', 'market_analysis']
        
        key_points = [
            "Market analysis and trends discussed in the video",
            "Key financial indicators and metrics analyzed",
            "Investment opportunities and recommendations presented",
            "Risk factors and market considerations highlighted"
        ]
        
        sentiment = {
            "sentiment": "neutral",
            "confidence": 0.5,
            "positive_indicators": 2,
            "negative_indicators": 1
        }
        
        return {
            "transcript": transcript,
            "key_points": key_points,
            "sentiment": sentiment,
            "topics": topics,
            "word_count": len(transcript.split())
        }
    
    def _detect_topics(self, transcript: str) -> list:
        """Detect topics from transcript"""
        topics = []
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ['earnings', 'quarter', 'financial', 'profit', 'revenue']):
            topics.append('earnings_analysis')
        if any(word in transcript_lower for word in ['crypto', 'bitcoin', 'ethereum', 'blockchain']):
            topics.append('cryptocurrency')
        if any(word in transcript_lower for word in ['stock', 'market', 'trading', 'investment']):
            topics.append('stock_market')
        if any(word in transcript_lower for word in ['company', 'business', 'corporate']):
            topics.append('company_news')
        if any(word in transcript_lower for word in ['economy', 'economic', 'fed', 'federal']):
            topics.append('economic_analysis')
        
        return topics if topics else ['general_finance'] 