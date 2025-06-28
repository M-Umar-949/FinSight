from typing import Dict, Any, Optional, List
import re
import json
import asyncio
from datetime import datetime
import subprocess
import tempfile
import os
from config import Config

class VideoTranscriber:
    def __init__(self):
        self.config = Config()
    
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
    
    def download_and_transcribe(self, video_url: str) -> Dict[str, Any]:
        """Simple download and transcribe using proven commands"""
        try:
            print(f"🎥 Processing video: {video_url}")
            
            # Step 1: Download audio using yt-dlp
            print("📥 Downloading audio...")
            download_cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'mp3',
                video_url
            ]
            
            print(f"Running: {' '.join(download_cmd)}")
            result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                return {"error": f"Download failed: {result.stderr}"}
            
            # Step 2: Find the downloaded file
            # yt-dlp downloads to current directory with video title
            files = [f for f in os.listdir('.') if f.endswith('.mp3')]
            if not files:
                return {"error": "No audio file found after download"}
            
            audio_file = files[0]  # Use the first .mp3 file found
            print(f"✅ Audio downloaded: {audio_file}")
            
            # Step 3: Transcribe with Whisper
            print("🎤 Transcribing with Whisper...")
            whisper_cmd = [
                'whisper',
                audio_file,
                '--model', 'small'
            ]
            
            print(f"Running: {' '.join(whisper_cmd)}")
            whisper_result = subprocess.run(whisper_cmd, capture_output=True, text=True, timeout=300)
            
            if whisper_result.returncode != 0:
                return {"error": f"Transcription failed: {whisper_result.stderr}"}
            
            # Step 4: Read the transcript
            transcript_file = audio_file.replace('.mp3', '.txt')
            if not os.path.exists(transcript_file):
                return {"error": "Transcript file not created"}
            
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript = f.read().strip()
            
            print(f"✅ Transcription successful: {len(transcript)} characters")
            
            # Step 5: Clean up files
            try:
                os.unlink(audio_file)
                os.unlink(transcript_file)
            except:
                pass
            
            return {
                "transcript": transcript,
                "word_count": len(transcript.split()),
                "status": "success"
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Process timed out"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}
    
    def extract_key_points(self, transcript: str) -> List[str]:
        """Extract key points from transcript"""
        sentences = transcript.split('. ')
        key_points = []
        
        financial_keywords = [
            'earnings', 'revenue', 'profit', 'loss', 'growth', 'decline',
            'market', 'stock', 'price', 'investment', 'trading', 'analysis',
            'recommendation', 'buy', 'sell', 'hold', 'target', 'support',
            'resistance', 'trend', 'volatility', 'risk', 'opportunity'
        ]
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in financial_keywords):
                if len(sentence) > 20:
                    key_points.append(sentence.strip())
        
        return key_points[:5]
    
    def analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment of video content"""
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
    
    async def analyze_video(self, url: str, query: str) -> Dict[str, Any]:
        """Main method to analyze video with transcription"""
        print(f"🎥 Analyzing video: {url}")
        
        # Extract video ID for basic info
        video_id = self.extract_youtube_id(url)
        if not video_id:
            return {"error": "Invalid YouTube URL"}
        
        # Download and transcribe
        transcript_result = self.download_and_transcribe(url)
        
        if "error" in transcript_result:
            return {"error": f"Transcription failed: {transcript_result['error']}"}
        
        # Analyze the transcript
        transcript = transcript_result["transcript"]
        key_points = self.extract_key_points(transcript)
        sentiment = self.analyze_sentiment(transcript)
        topics = self._detect_topics(transcript)
        word_count = transcript_result["word_count"]
        
        # Compile result
        result = {
            "video_info": {
                "video_id": video_id,
                "url": url
            },
            "transcript": {
                "text": transcript,
                "word_count": word_count,
                "method": "whisper"
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