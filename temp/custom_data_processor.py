"""
Custom Data Processor untuk IndoPopBase Data
Khusus untuk format CSV yang sudah ada

Run: python process_indopopbase_data.py
"""

import pandas as pd
import re
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class IndoPopBaseProcessor:
    def __init__(self):
        self.raw_dir = 'data/raw'
        self.processed_dir = 'data/processed'
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def load_all_data(self):
        """Load and combine all CSV files"""
        print("="*70)
        print("📂 LOADING DATA")
        print("="*70)
        
        files = {
            'original': 'indopopbase_original_tweets_20251010_183930.csv',
            'replies': 'indopopbase_all_replies_20251010_183930.csv',
            'quotes': 'indopopbase_all_quotes_20251010_183930.csv'
        }
        
        dataframes = {}
        
        for key, filename in files.items():
            filepath = os.path.join(self.raw_dir, filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                print(f"✅ Loaded {key}: {len(df)} rows")
                dataframes[key] = df
            else:
                print(f"⚠️  File not found: {filename}")
        
        return dataframes
    
    def clean_text(self, text):
        """Clean tweet text"""
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove HTML entities
        text = re.sub(r'&\w+;', '', text)
        text = re.sub(r'â€™', "'", text)
        text = re.sub(r'â€œ', '"', text)
        text = re.sub(r'â€', '"', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def process_dataframe(self, df, data_type):
        """Process a single dataframe"""
        print(f"\n🔄 Processing {data_type}...")
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Clean content
        if 'content' in df.columns:
            df['content_clean'] = df['content'].apply(self.clean_text)
        
        # Extract time features
        df['hour'] = df['date'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_name'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month
        df['date_only'] = df['date'].dt.date
        
        # Text features
        if 'content' in df.columns:
            df['text_length'] = df['content'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
            df['word_count'] = df['content'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
            
            # Count mentions
            df['mention_count'] = df['content'].apply(
                lambda x: len(re.findall(r'@\w+', str(x))) if pd.notna(x) else 0
            )
            
            # Count hashtags
            df['hashtag_count'] = df['content'].apply(
                lambda x: len(re.findall(r'#\w+', str(x))) if pd.notna(x) else 0
            )
        
        # Ensure engagement columns exist
        engagement_cols = ['like_count', 'retweet_count', 'reply_count']
        for col in engagement_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = df[col].fillna(0).astype(int)
        
        # Calculate total engagement (if not exists)
        if 'total_engagement' not in df.columns:
            df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
        
        # Add data type
        df['data_type'] = data_type
        
        return df
    
    def analyze_sentiment(self, df):
        """Simple sentiment analysis"""
        print("\n🎭 Analyzing sentiment...")
        
        positive_words = [
            'bagus', 'hebat', 'keren', 'mantap', 'love', 'suka', 'senang',
            'amazing', 'good', 'great', 'excellent', 'beautiful', 'excited',
            'comeback', 'serving', 'mother', 'queen', 'icon', 'ended'
        ]
        
        negative_words = [
            'hate', 'corny', 'bs', 'bad', 'worst', 'boring', 'disappointed',
            'benci', 'jelek', 'buruk', 'payah'
        ]
        
        def get_sentiment(text):
            if pd.isna(text):
                return 'neutral', 0.0
            
            text = str(text).lower()
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            total = pos_count + neg_count
            if total == 0:
                return 'neutral', 0.0
            
            score = (pos_count - neg_count) / total
            
            if score > 0.2:
                return 'positive', score
            elif score < -0.2:
                return 'negative', score
            else:
                return 'neutral', score
        
        sentiments = []
        scores = []
        
        for text in df['content_clean']:
            sentiment, score = get_sentiment(text)
            sentiments.append(sentiment)
            scores.append(score)
        
        df['sentiment'] = sentiments
        df['sentiment_score'] = scores
        
        return df
    
    def generate_summary(self, df):
        """Generate data summary"""
        print("\n" + "="*70)
        print("📊 DATA SUMMARY")
        print("="*70)
        
        print(f"\n📈 Total Records: {len(df)}")
        print(f"📅 Date Range: {df['date'].min()} to {df['date'].max()}")
        
        # Data types breakdown
        if 'data_type' in df.columns:
            print(f"\n📋 Data Types:")
            type_counts = df['data_type'].value_counts()
            for dtype, count in type_counts.items():
                print(f"   {dtype}: {count}")
        
        # Engagement stats
        print(f"\n💙 Engagement Statistics:")
        print(f"   Total Likes: {df['like_count'].sum():,}")
        print(f"   Total Retweets: {df['retweet_count'].sum():,}")
        print(f"   Total Replies: {df['reply_count'].sum():,}")
        print(f"   Total Engagement: {df['total_engagement'].sum():,}")
        print(f"   Average Engagement: {df['total_engagement'].mean():.2f}")
        
        # Sentiment breakdown
        if 'sentiment' in df.columns:
            print(f"\n🎭 Sentiment Distribution:")
            sentiment_counts = df['sentiment'].value_counts()
            for sentiment, count in sentiment_counts.items():
                pct = (count / len(df)) * 100
                emoji = {'positive': '😊', 'negative': '😢', 'neutral': '😐'}.get(sentiment, '❓')
                print(f"   {emoji} {sentiment.capitalize()}: {count} ({pct:.1f}%)")
        
        # Top engaging tweets
        print(f"\n🏆 Top 5 Most Engaged:")
        top_5 = df.nlargest(5, 'total_engagement')[['date', 'username', 'content', 'total_engagement']]
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            print(f"\n   {i}. {row['username']} - {row['total_engagement']:,} engagement")
            print(f"      {row['content'][:80]}...")
        
        print("\n" + "="*70)
    
    def save_processed_data(self, df):
        """Save processed data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save complete dataset
        output_file = os.path.join(self.processed_dir, f'all_data_processed_{timestamp}.csv')
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n💾 Saved: {output_file}")
        
        # Save by type
        if 'data_type' in df.columns:
            for dtype in df['data_type'].unique():
                type_df = df[df['data_type'] == dtype]
                type_file = os.path.join(self.processed_dir, f'{dtype}_processed_{timestamp}.csv')
                type_df.to_csv(type_file, index=False, encoding='utf-8')
                print(f"💾 Saved: {type_file}")
        
        return output_file
    
    def run_complete_pipeline(self):
        """Run complete processing pipeline"""
        print("="*70)
        print("🚀 INDOPOPBASE DATA PROCESSOR")
        print("="*70)
        
        # Step 1: Load data
        dataframes = self.load_all_data()
        
        if not dataframes:
            print("\n❌ No data files found!")
            return None
        
        # Step 2: Process each dataframe
        processed_dfs = []
        
        if 'original' in dataframes:
            df = self.process_dataframe(dataframes['original'], 'original_tweet')
            processed_dfs.append(df)
        
        if 'replies' in dataframes:
            df = self.process_dataframe(dataframes['replies'], 'reply')
            processed_dfs.append(df)
        
        if 'quotes' in dataframes:
            df = self.process_dataframe(dataframes['quotes'], 'quote')
            processed_dfs.append(df)
        
        # Step 3: Combine all data
        print("\n📦 Combining all datasets...")
        combined_df = pd.concat(processed_dfs, ignore_index=True)
        print(f"✅ Combined: {len(combined_df)} total records")
        
        # Step 4: Remove duplicates
        original_len = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['tweet_url'])
        print(f"🔄 Removed {original_len - len(combined_df)} duplicates")
        
        # Step 5: Sentiment analysis
        combined_df = self.analyze_sentiment(combined_df)
        
        # Step 6: Generate summary
        self.generate_summary(combined_df)
        
        # Step 7: Save processed data
        output_file = self.save_processed_data(combined_df)
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETED!")
        print("="*70)
        print(f"\n📁 Output file: {output_file}")
        print(f"📊 Total records: {len(combined_df)}")
        print("\n🎯 Next steps:")
        print("   1. Run dashboard: streamlit run dashboard.py")
        print("   2. Or use Docker: docker-compose up")
        
        return combined_df


def main():
    processor = IndoPopBaseProcessor()
    df = processor.run_complete_pipeline()
    
    if df is not None:
        print("\n✅ Data ready for dashboard!")
        print("🚀 Run: streamlit run dashboard.py")


if __name__ == "__main__":
    main()
