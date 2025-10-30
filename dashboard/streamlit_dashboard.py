"""
Streamlit Dashboard - IndoPopBase Analytics

Install:
pip install streamlit plotly wordcloud

Run:
streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="IndoPopBase Analytics",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1DA1F2;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_path):
    """Load data with caching"""
    return pd.read_csv(file_path)


def display_metrics(df):
    """Display key metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Tweets",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        total_engagement = df['total_engagement'].sum() if 'total_engagement' in df.columns else 0
        st.metric(
            label="💙 Total Engagement",
            value=f"{total_engagement:,}",
            delta=None
        )
    
    with col3:
        avg_engagement = df['total_engagement'].mean() if 'total_engagement' in df.columns else 0
        st.metric(
            label="📈 Avg Engagement",
            value=f"{avg_engagement:.1f}",
            delta=None
        )
    
    with col4:
        if 'sentiment' in df.columns:
            positive_pct = (df['sentiment'] == 'positive').sum() / len(df) * 100
            st.metric(
                label="😊 Positive %",
                value=f"{positive_pct:.1f}%",
                delta=None
            )


def plot_sentiment_distribution(df):
    """Plot sentiment distribution pie chart"""
    if 'sentiment' not in df.columns:
        return None
    
    sentiment_counts = df['sentiment'].value_counts()
    
    colors = {
        'positive': '#10B981',
        'negative': '#EF4444',
        'neutral': '#6B7280'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        marker=dict(colors=[colors.get(s, '#6B7280') for s in sentiment_counts.index]),
        hole=0.4,
        textinfo='label+percent',
        textfont_size=14
    )])
    
    fig.update_layout(
        title="Sentiment Distribution",
        height=400,
        showlegend=True
    )
    
    return fig


def plot_engagement_timeline(df):
    """Plot engagement over time"""
    if 'date' not in df.columns or 'total_engagement' not in df.columns:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    df_sorted = df.sort_values('date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=df_sorted['total_engagement'],
        mode='lines+markers',
        name='Engagement',
        line=dict(color='#1DA1F2', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Engagement Timeline",
        xaxis_title="Date",
        yaxis_title="Total Engagement",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_hourly_engagement(df):
    """Plot engagement by hour"""
    if 'hour' not in df.columns or 'total_engagement' not in df.columns:
        return None
    
    hourly_avg = df.groupby('hour')['total_engagement'].mean().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=hourly_avg['hour'],
            y=hourly_avg['total_engagement'],
            marker_color='#1DA1F2',
            text=hourly_avg['total_engagement'].round(1),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Average Engagement by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Average Engagement",
        height=400,
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    
    return fig


def plot_daily_engagement(df):
    """Plot engagement by day of week"""
    if 'day_name' not in df.columns or 'total_engagement' not in df.columns:
        return None
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_avg = df.groupby('day_name')['total_engagement'].mean().reindex(day_order).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=daily_avg['day_name'],
            y=daily_avg['total_engagement'],
            marker_color='#10B981',
            text=daily_avg['total_engagement'].round(1),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Average Engagement by Day",
        xaxis_title="Day of Week",
        yaxis_title="Average Engagement",
        height=400
    )
    
    return fig


def plot_sentiment_over_time(df):
    """Plot sentiment trends over time"""
    if 'date' not in df.columns or 'sentiment' not in df.columns:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.date
    
    sentiment_daily = df.groupby(['date_only', 'sentiment']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    colors = {
        'positive': '#10B981',
        'negative': '#EF4444',
        'neutral': '#6B7280'
    }
    
    for sentiment in sentiment_daily.columns:
        fig.add_trace(go.Scatter(
            x=sentiment_daily.index,
            y=sentiment_daily[sentiment],
            mode='lines+markers',
            name=sentiment.capitalize(),
            line=dict(color=colors.get(sentiment, '#6B7280'), width=2),
            stackgroup='one'
        ))
    
    fig.update_layout(
        title="Sentiment Trends Over Time",
        xaxis_title="Date",
        yaxis_title="Number of Tweets",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def display_top_tweets(df, n=10):
    """Display top performing tweets"""
    if 'total_engagement' not in df.columns:
        st.warning("No engagement data available")
        return
    
    top_tweets = df.nlargest(n, 'total_engagement')
    
    st.subheader(f"🏆 Top {n} Most Engaged Tweets")
    
    for i, (_, tweet) in enumerate(top_tweets.iterrows(), 1):
        with st.expander(f"#{i} - Engagement: {tweet['total_engagement']:,}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Date:** {tweet['date']}")
                st.write(f"**Content:** {tweet['content'][:300]}...")
                
                if 'sentiment' in tweet:
                    sentiment_emoji = {
                        'positive': '😊',
                        'negative': '😢',
                        'neutral': '😐'
                    }
                    st.write(f"**Sentiment:** {sentiment_emoji.get(tweet['sentiment'], '❓')} {tweet['sentiment']}")
            
            with col2:
                if 'likes' in tweet:
                    st.metric("💙 Likes", f"{tweet['likes']:,}")
                if 'retweets' in tweet:
                    st.metric("🔁 Retweets", f"{tweet['retweets']:,}")
                if 'replies' in tweet:
                    st.metric("💬 Replies", f"{tweet['replies']:,}")


def main():
    """Main dashboard"""
    
    # Header
    st.markdown('<p class="main-header">🐦 IndoPopBase Analytics Dashboard</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # File selector
    processed_dir = 'data/processed'
    
    if not os.path.exists(processed_dir):
        st.error(f"❌ Directory '{processed_dir}' not found. Please run data preprocessing first.")
        return
    
    csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    
    if not csv_files:
        st.error("❌ No CSV files found in processed directory.")
        return
    
    selected_file = st.sidebar.selectbox(
        "📂 Select Dataset",
        csv_files
    )
    
    # Load data
    file_path = os.path.join(processed_dir, selected_file)
    
    try:
        df = load_data(file_path)
        st.sidebar.success(f"✅ Loaded {len(df)} tweets")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return
    
    # Date filter
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
            df = df[mask]
    
    # Main content
    st.markdown("---")
    
    # Key Metrics
    st.subheader("📊 Key Metrics")
    display_metrics(df)
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        fig = plot_sentiment_distribution(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = plot_engagement_timeline(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        fig = plot_hourly_engagement(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = plot_daily_engagement(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment Timeline
    st.markdown("---")
    fig = plot_sentiment_over_time(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Tweets
    st.markdown("---")
    display_top_tweets(df, n=10)
    
    # Data Table
    st.markdown("---")
    st.subheader("📋 Raw Data")
    
    if st.checkbox("Show raw data"):
        st.dataframe(df, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"indopopbase_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6B7280; padding: 1rem;'>
            <p>🐦 IndoPopBase Analytics Dashboard</p>
            <p>Built with Streamlit • Data from Twitter</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
