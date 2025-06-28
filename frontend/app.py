# frontend/app.py
import streamlit as st
import asyncio
import sys
import os
import json

# Add parent directory to path to import FinSight
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import FinSight

# Page configuration
st.set_page_config(
    page_title="FinSight - AI Financial Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for minimal, clean design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    .response-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.25rem;
    }
    .stMarkdown {
        line-height: 1.6;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1f77b4;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .stMarkdown code {
        background-color: #f1f3f4;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .stMarkdown pre {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        overflow-x: auto;
    }
    .cache-info {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Initialize FinSight
@st.cache_resource
def get_finsight():
    return FinSight()

def format_intent_badge(intent: str) -> str:
    """Format intent with color coding"""
    colors = {
        'price_movement': '#ff6b6b',
        'company_news': '#4ecdc4',
        'regulatory_news': '#45b7d1',
        'video_analysis': '#feca57',
        'general_query': '#00d2d3'
    }
    color = colors.get(intent, '#666')
    return f'<span class="intent-badge" style="background-color: {color}; color: white;">🎯 {intent.replace("_", " ").title()}</span>'

def display_metrics(result: dict):
    """Display key metrics from the result"""
    if 'market_data' in result and result['market_data']:
        market_data = result['market_data']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            symbols = market_data.get('symbols_found', [])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(symbols)}</div>
                <div class="metric-label">Symbols Found</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            news_count = market_data.get('news_count', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{news_count}</div>
                <div class="metric-label">News Articles</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if 'transcript' in result and result['transcript']:
                word_count = result['transcript'].get('word_count', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{word_count}</div>
                    <div class="metric-label">Words Transcribed</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">-</div>
                    <div class="metric-label">Video Analysis</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if 'timestamp' in result:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">✓</div>
                    <div class="metric-label">Analysis Complete</div>
                </div>
                """, unsafe_allow_html=True)

def display_response(result: dict):
    """Display the main response content"""
    st.markdown('<div class="response-container">', unsafe_allow_html=True)
    
    # Display intent badge
    intent = result.get('intent', 'unknown')
    st.markdown(format_intent_badge(intent), unsafe_allow_html=True)
    
    # Display main analysis
    if 'analysis' in result:
        st.markdown("### 📊 Analysis")
        # Handle markdown content properly
        analysis = result['analysis']
        if isinstance(analysis, str):
            st.markdown(analysis)
        else:
            st.json(analysis)
    
    # Display additional insights
    if 'additional_insights' in result and result['additional_insights']:
        st.markdown("### 🔍 Additional Insights")
        insights = result['additional_insights']
        if 'news_sentiment' in insights:
            st.markdown("#### 📰 News Sentiment")
            st.markdown(insights['news_sentiment'])
    
    # Display key insights for video analysis
    if 'key_insights' in result and result['key_insights']:
        st.markdown("### 🎯 Key Insights")
        key_insights = result['key_insights']
        if 'key_points' in key_insights:
            st.markdown("#### Key Points:")
            for i, point in enumerate(key_insights['key_points'], 1):
                st.markdown(f"{i}. {point}")
        
        if 'sentiment' in key_insights:
            sentiment = key_insights['sentiment']
            st.markdown(f"#### Sentiment: **{sentiment.get('sentiment', 'Unknown').title()}**")
    
    # Display transcript for video analysis
    if 'transcript' in result and result['transcript']:
        with st.expander("📝 Video Transcript"):
            transcript = result['transcript']
            if 'text' in transcript:
                st.markdown(transcript['text'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 FinSight</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Financial Intelligence Platform</p>', unsafe_allow_html=True)
    
    # Sidebar for status and info
    with st.sidebar:
        st.header("🔧 System Status")
        
        finsight = get_finsight()
        
        # Health check
        if finsight.llm.health_check():
            st.success("✅ LLM Connected")
        else:
            st.error("❌ LLM Not Available")
        
        st.markdown("---")
        st.header("📊 Cache Status")
        
        # Cache stats
        try:
            cache_stats = finsight.cache.get_cache_stats()
            if "error" not in cache_stats:
                st.metric("Query Cache", f"{cache_stats.get('total_entries', 0)} entries")
            
            video_stats = finsight.video_cache.get_video_stats()
            if "error" not in video_stats:
                st.metric("Video Cache", f"{video_stats.get('total_videos', 0)} videos")
        except:
            st.info("Cache stats unavailable")
        
        st.markdown("---")
        st.header("💡 Supported Queries")
        st.markdown("""
        • **Price Analysis**: "Why is BTC dropping?"
        • **Company News**: "AAPL earnings impact"
        • **Regulatory**: "Latest SEC crypto rules"
        • **Video Analysis**: "Analyze this video: [URL]"
        • **General**: "Hello", "Help"
        """)
    
    # Main content
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    
    # Query input
    query = st.text_area(
        "💬 Ask your financial question:",
        placeholder="e.g., 'Why is Bitcoin dropping today?', 'Analyze this video: https://youtube.com/watch?v=...', 'What's the latest on AAPL earnings?'",
        height=100,
        key="query_input"
    )
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process query
    if process_button and query.strip():
        with st.spinner("🔍 Analyzing your query..."):
            try:
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
                    # Display metrics
                    display_metrics(result)
                    
                    # Display main response
                    display_response(result)
                    
                    # Show cache info if available
                    if 'cached' in result and result['cached']:
                        st.markdown('<p class="cache-info">💾 Response served from cache</p>', unsafe_allow_html=True)
                    
                    # Show raw data in expander
                    with st.expander("🔍 Raw Response Data"):
                        st.json(result)
                        
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")
    
    elif process_button and not query.strip():
        st.warning("⚠️ Please enter a query to analyze.")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        **Price Movement Analysis:**
        - "Why is Bitcoin dropping today?"
        - "What's causing the stock market crash?"
        - "Why is AAPL stock up?"
        
        **Company News:**
        - "Apple earnings impact on tech stocks"
        - "Tesla Q4 results analysis"
        - "Microsoft latest announcements"
        
        **Regulatory News:**
        - "Latest SEC crypto regulations"
        - "CFTC announcements this week"
        - "New banking regulations"
        
        **Video Analysis:**
        - "Analyze this YouTube video about crypto: https://youtube.com/watch?v=..."
        - "Transcribe and summarize this financial video"
        
        **General Queries:**
        - "Hello, how can you help me?"
        - "What can you analyze?"
        - "Help me understand market trends"
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🚀 FinSight - Powered by Ollama LLM & Advanced Financial Analysis</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
