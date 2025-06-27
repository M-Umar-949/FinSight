# frontend/app.py
import streamlit as st
import asyncio
import sys
import os

# Add parent directory to path to import FinSight
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import FinSight
from tools import NewsScraper, SentimentAnalyzer, ContentSummarizer, VideoTranscriber

# Page configuration
st.set_page_config(
    page_title="FinSight - Fintech Intelligence Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .intent-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .response-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .tool-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize FinSight
@st.cache_resource
def get_finsight():
    return FinSight()

# Initialize tools
@st.cache_resource
def get_tools():
    return {
        'scraper': NewsScraper(),
        'sentiment': SentimentAnalyzer(),
        'summarizer': ContentSummarizer(),
        'transcriber': VideoTranscriber()
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 FinSight</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #666;">Fintech Intelligence Agent</h3>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Tools Status")
        
        finsight = get_finsight()
        tools = get_tools()
        
        # Health check
        if finsight.llm.health_check():
            st.success("✅ Ollama LLM Connected")
        else:
            st.error("❌ Ollama LLM Not Available")
        
        st.markdown("---")
        st.header("📊 Available Tools")
        
        tool_status = {
            "News Scraper": "🟡 Placeholder",
            "Sentiment Analyzer": "🟡 Placeholder", 
            "Content Summarizer": "🟡 Placeholder",
            "Video Transcriber": "🟡 Placeholder"
        }
        
        for tool, status in tool_status.items():
            st.write(f"{tool}: {status}")
        
        st.markdown("---")
        st.header("🎯 Intent Categories")
        intents = [
            "💰 Price Movement",
            "📋 Regulatory News", 
            "🏢 Company Events",
            "📈 Market Sentiment",
            "🎥 Video Transcription",
            "📰 News Summary",
            "📊 Technical Analysis",
            "📋 Fundamental Analysis",
            "₿ Crypto Specific",
            "ℹ️ General Info"
        ]
        
        for intent in intents:
            st.write(f"• {intent}")
    
    # Main content area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 💬 Ask Your Fintech Question")
        
        # Query input
        query = st.text_area(
            "Enter your query here...",
            placeholder="e.g., 'Why is BTC dropping?', 'AAPL earnings impact?', 'Analyze this YouTube video about crypto'",
            height=100
        )
        
        # Process button
        if st.button("🚀 Process Query", type="primary", use_container_width=True):
            if query.strip():
                with st.spinner("Processing your query..."):
                    # Process query asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(finsight.process_query(query))
                    finally:
                        loop.close()
                
                # Display results
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Intent badge
                    intent = result.get('intent', 'unknown')
                    intent_colors = {
                        'price_movement': '#ff6b6b',
                        'regulatory_news': '#4ecdc4', 
                        'company_event': '#45b7d1',
                        'market_sentiment': '#96ceb4',
                        'video_transcription': '#feca57',
                        'news_summary': '#ff9ff3',
                        'technical_analysis': '#54a0ff',
                        'fundamental_analysis': '#5f27cd',
                        'crypto_specific': '#ff9f43',
                        'general_info': '#00d2d3'
                    }
                    
                    color = intent_colors.get(intent, '#666')
                    st.markdown(f"""
                    <div class="intent-badge" style="background-color: {color}; color: white;">
                        🎯 Detected Intent: {intent.replace('_', ' ').title()}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Response
                    st.markdown('<div class="response-box">', unsafe_allow_html=True)
                    
                    if 'response' in result:
                        st.markdown("### 💡 Response")
                        st.write(result['response'])
                    elif 'message' in result:
                        st.markdown("### 💡 Response")
                        st.write(result['message'])
                    
                    # Tools needed
                    if 'tools_needed' in result:
                        st.markdown("### 🔧 Tools That Would Be Used")
                        for tool in result['tools_needed']:
                            st.markdown(f'<div class="tool-info">🛠️ {tool.replace("_", " ").title()}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Query details
                    with st.expander("📋 Query Details"):
                        st.json(result)
            else:
                st.warning("Please enter a query to process.")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Price Movement:**
        - "Why is Bitcoin dropping today?"
        - "What's causing the stock market crash?"
        
        **Regulatory News:**
        - "Latest SEC crypto regulations"
        - "CFTC announcements this week"
        
        **Company Events:**
        - "Apple earnings impact on tech stocks"
        - "Tesla Q4 results analysis"
        
        **Video Analysis:**
        - "Analyze this YouTube video about crypto: https://youtube.com/watch?v=..."
        - "Transcribe and summarize this financial video"
        
        **Market Sentiment:**
        - "Current market sentiment for crypto"
        - "Fear and greed index today"
        
        **Technical Analysis:**
        - "BTC technical analysis chart"
        - "Support and resistance levels for ETH"
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 FinSight - Intelligent Fintech Analysis Platform</p>
        <p>Powered by Ollama LLM and Modular Tool Architecture</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
