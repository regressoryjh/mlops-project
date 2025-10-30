"""
Simple Sentiment Analyzer untuk Indonesian Text
Menggunakan TextBlob untuk cepat (no heavy models)

Install:
pip install textblob textblob-id pandas tqdm

Untuk production: bisa ganti ke IndoBERT
"""

import pandas as pd
import os
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Try import advanced models, fallback to simple
try:
    from textblob import TextBlob
    USE_TEXTBLOB = True
except:
    USE_TEXTBLOB = False
    print("⚠️ TextBlob not installed, using keyword-based sentiment")


class SimpleSentimentAnalyzer:
    """Simple keyword-based sentiment analyzer"""
    
    def __init__(self):
        # Indonesian positive & negative words
        self.positive_words = [
            'bagus', 'hebat', 'keren', 'mantap', 'love', 'suka', 'senang', 
            'bahagia', 'sukses', 'terbaik', 'sempurna', 'luar biasa',
            'amazing', 'good', 'great', 'excellent', 'wonderful', 'best',
            'cantik', 'ganteng', 'talented', 'legend', 'icon', 'queen', 'king'
        ]
        
        self.negative_words = [
            'buruk', 'jelek', 'payah', 'mengecewakan', 'hate', 'benci', 'sedih',
            'gagal', 'terburuk', 'awful', 'bad', 'terrible', 'worst', 'boring',
            'sampah', 'norak', 'cringe', 'flop', 'overrated'
        ]
    
    def analyze(self, text):
        """Analyze sentiment of text"""
        if pd.isna(text):
            return 'neutral', 0.0
        
        text = str(text).lower()
        
        # Count positive and negative words
        pos_count = sum(1 for word in self.positive_words if word in text)
        neg_count = sum(1 for word in self.negative_words if word in text)
        
        # Calculate score
        total = pos_count + neg_count
        if total == 0:
            return 'neutral', 0.0
        
        score = (pos_count - neg_count) / total
        
        # Classify sentiment
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return sentiment, score


class TextBlobSentimentAnalyzer:
    """TextBlob-based sentiment analyzer"""
    
    def analyze(self, text):
        """Analyze sentiment using TextBlob"""
        if pd.isna(text):
            return 'neutral', 0.0
        
        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity
            
            # Classify based on polarity
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return sentiment, polarity
        
        except:
            # Fallback to simple analyzer
            simple = SimpleSentimentAnalyzer()
            return simple.analyze(text)


class SentimentProcessor:
    """Process sentiment for entire dataset"""
    
    def __init__(self, use_textblob=True):
        if use_textblob and USE_TEXTBLOB:
            self.analyzer = TextBlobSentimentAnalyzer()
            print("✅ Using TextBlob analyzer")
        else:
            self.analyzer = SimpleSentimentAnalyzer()
            print("✅ Using Simple keyword-based analyzer")
    
    def process_file(self, input_path, output_path=None):
        """Process sentiment for all tweets in file"""
        print("="*70)
        print("🎭 SENTIMENT ANALYSIS")
        print("="*70)
        
        # Read data
        print(f"\n📂 Reading: {input_path}")
        try:
            df = pd.read_csv(input_path)
            print(f"✅ Loaded {len(df)} tweets")
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        
        # Determine text column
        text_col = 'content_clean' if 'content_clean' in df.columns else 'content'
        
        if text_col not in df.columns:
            print(f"❌ No text column found")
            return None
        
        # Analyze sentiment
        print(f"\n🔍 Analyzing sentiment...")
        sentiments = []
        scores = []
        
        for text in tqdm(df[text_col], desc="Processing"):
            sentiment, score = self.analyzer.analyze(text)
            sentiments.append(sentiment)
            scores.append(score)
        
        df['sentiment'] = sentiments
        df['sentiment_score'] = scores
        
        # Print summary
        self.print_summary(df)
        
        # Save results
        if output_path is None:
            output_path = input_path.replace('.csv', '_with_sentiment.csv')
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n💾 Saved to: {output_path}")
        
        return df
    
    def print_summary(self, df):
        """Print sentiment summary"""
        print("\n" + "="*70)
        print("📊 SENTIMENT SUMMARY")
        print("="*70)
        
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        print(f"\n🎭 Sentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total) * 100
            emoji = {
                'positive': '😊',
                'negative': '😢',
                'neutral': '😐'
            }.get(sentiment, '❓')
            
            print(f"   {emoji} {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        if 'total_engagement' in df.columns:
            print(f"\n💙 Engagement by Sentiment:")
            engagement_by_sentiment = df.groupby('sentiment')['total_engagement'].agg(['mean', 'sum'])
            for sentiment, row in engagement_by_sentiment.iterrows():
                emoji = {
                    'positive': '😊',
                    'negative': '😢',
                    'neutral': '😐'
                }.get(sentiment, '❓')
                print(f"   {emoji} {sentiment.capitalize()}:")
                print(f"      Avg: {row['mean']:.2f}")
                print(f"      Total: {row['sum']:,.0f}")
        
        print("\n" + "="*70)


def main():
    """Main execution"""
    print("="*70)
    print("🎭 SENTIMENT ANALYZER - IndoPopBase Analytics")
    print("="*70)
    
    # Auto-detect processed files
    processed_dir = 'data/processed'
    
    if os.path.exists(processed_dir):
        csv_files = [f for f in os.listdir(processed_dir) 
                     if f.endswith('.csv') and 'sentiment' not in f]
        
        if csv_files:
            print(f"\n📁 Found {len(csv_files)} file(s) to process:")
            for i, file in enumerate(csv_files, 1):
                print(f"   {i}. {file}")
            
            choice = input("\nEnter file number (or 'all' for all files): ").strip()
            
            processor = SentimentProcessor()
            
            if choice.lower() == 'all':
                for file in csv_files:
                    file_path = os.path.join(processed_dir, file)
                    processor.process_file(file_path)
                    print("\n")
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(csv_files):
                        file_path = os.path.join(processed_dir, csv_files[idx])
                        processor.process_file(file_path)
                    else:
                        print("❌ Invalid number")
                except:
                    print("❌ Invalid input")
        else:
            print("\n❌ No processed CSV files found")
            print("💡 Run data_cleaner.py first")
    else:
        print(f"\n❌ Directory '{processed_dir}' not found")
        print("💡 Run data_cleaner.py first")
    
    print("\n✅ Sentiment analysis completed!")


if __name__ == "__main__":
    main()
