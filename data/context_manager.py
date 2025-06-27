import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import hashlib

class ContextManager:
    def __init__(self, max_history: int = 10, context_ttl: int = 3600):
        """
        Initialize context manager
        
        Args:
            max_history: Maximum number of conversation turns to keep
            context_ttl: Time to live for context in seconds (1 hour default)
        """
        self.max_history = max_history
        self.context_ttl = context_ttl
        self.conversation_history = deque(maxlen=max_history)
        self.context_cache = {}
        self.last_cleanup = time.time()
        
    def add_conversation_turn(self, user_query: str, response: Dict[str, Any], session_id: str = "default") -> None:
        """Add a conversation turn to history"""
        turn = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_query": user_query,
            "intent": response.get("intent", "unknown"),
            "response_summary": self._extract_response_summary(response),
            "symbols_mentioned": self._extract_symbols(user_query),
            "market_context": self._extract_market_context(response)
        }
        
        self.conversation_history.append(turn)
        self._cleanup_old_contexts()
    
    def get_relevant_context(self, current_query: str, session_id: str = "default") -> Dict[str, Any]:
        """Get relevant context for current query"""
        current_symbols = self._extract_symbols(current_query)
        relevant_history = []
        
        # Find relevant conversation history
        for turn in reversed(self.conversation_history):
            if turn["session_id"] == session_id:
                # Check if symbols match
                if current_symbols and any(symbol in turn["symbols_mentioned"] for symbol in current_symbols):
                    relevant_history.append(turn)
                # Check if intent matches
                elif self._is_similar_intent(current_query, turn["user_query"]):
                    relevant_history.append(turn)
        
        # Get cached market data if available
        cached_market_data = self._get_cached_market_data(current_symbols)
        
        return {
            "conversation_history": relevant_history[:3],  # Limit to 3 most relevant
            "cached_market_data": cached_market_data,
            "session_id": session_id,
            "current_symbols": current_symbols
        }
    
    def cache_market_data(self, symbols: List[str], market_data: Dict[str, Any], ttl: int = None) -> None:
        """Cache market data for symbols"""
        if ttl is None:
            ttl = self.context_ttl
            
        for symbol in symbols:
            cache_key = f"market_data_{symbol.upper()}"
            self.context_cache[cache_key] = {
                "data": market_data,
                "timestamp": time.time(),
                "ttl": ttl
            }
    
    def _extract_response_summary(self, response: Dict[str, Any]) -> str:
        """Extract a summary from the response"""
        if response.get("intent") == "general_query":
            return response.get("response", "")[:200]
        elif response.get("analysis"):
            return response.get("analysis", "")[:200]
        else:
            return str(response)[:200]
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract stock/crypto symbols from text"""
        import re
        patterns = [
            r'\b[A-Z]{1,5}\b',  # 1-5 letter symbols
            r'\$[A-Z]{1,5}\b',  # $AAPL format
        ]
        
        symbols = set()
        for pattern in patterns:
            matches = re.findall(pattern, text.upper())
            symbols.update(matches)
        
        # Filter out common words
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
        symbols = {s.replace('$', '') for s in symbols if s.replace('$', '') not in common_words}
        
        return list(symbols)
    
    def _extract_market_context(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market context from response"""
        market_data = response.get("market_data", {})
        return {
            "symbols": market_data.get("symbols_found", []),
            "news_count": market_data.get("news_count", 0),
            "indicators": market_data.get("market_indicators", {})
        }
    
    def _is_similar_intent(self, query1: str, query2: str) -> bool:
        """Check if two queries have similar intent"""
        # Simple keyword-based similarity
        keywords1 = set(query1.lower().split())
        keywords2 = set(query2.lower().split())
        
        # Check for common financial keywords
        financial_keywords = {'price', 'stock', 'market', 'earnings', 'news', 'analysis', 'crypto', 'bitcoin', 'tesla', 'apple', 'amazon', 'google', 'microsoft'}
        
        common_keywords = keywords1.intersection(keywords2)
        financial_common = common_keywords.intersection(financial_keywords)
        
        return len(financial_common) > 0
    
    def _get_cached_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get cached market data for symbols"""
        cached_data = {}
        current_time = time.time()
        
        for symbol in symbols:
            cache_key = f"market_data_{symbol.upper()}"
            if cache_key in self.context_cache:
                cache_entry = self.context_cache[cache_key]
                if current_time - cache_entry["timestamp"] < cache_entry["ttl"]:
                    cached_data[symbol] = cache_entry["data"]
        
        return cached_data
    
    def _cleanup_old_contexts(self) -> None:
        """Clean up old cached contexts"""
        current_time = time.time()
        
        # Clean up old cache entries
        expired_keys = []
        for key, entry in self.context_cache.items():
            if current_time - entry["timestamp"] > entry["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.context_cache[key]
        
        # Update last cleanup time
        self.last_cleanup = current_time
    
    def get_conversation_summary(self, session_id: str = "default") -> str:
        """Get a summary of the conversation"""
        session_history = [turn for turn in self.conversation_history if turn["session_id"] == session_id]
        
        if not session_history:
            return "No conversation history available."
        
        summary_parts = []
        for turn in session_history[-3:]:  # Last 3 turns
            summary_parts.append(f"User: {turn['user_query']}")
            summary_parts.append(f"Intent: {turn['intent']}")
            summary_parts.append(f"Response: {turn['response_summary']}")
            summary_parts.append("---")
        
        return "\n".join(summary_parts)
    
    def clear_session(self, session_id: str = "default") -> None:
        """Clear conversation history for a session"""
        self.conversation_history = deque(
            [turn for turn in self.conversation_history if turn["session_id"] != session_id],
            maxlen=self.max_history
        )
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            "conversation_history_size": len(self.conversation_history),
            "cache_size": len(self.context_cache),
            "last_cleanup": self.last_cleanup,
            "max_history": self.max_history,
            "context_ttl": self.context_ttl
        } 