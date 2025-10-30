"""
Engagement Analyzer - Analyze tweet engagement patterns

Jalankan: python engagement_analyzer.py
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import json


class EngagementAnalyzer:
    """Analyze engagement metrics"""
    
    def __init__(self, df):
        self.df = df
        self.results = {}
    
    def calculate_basic_metrics(self):
        """Calculate basic engagement metrics"""
        print("\n📊 Calculating basic metrics...")
        
        self.results['basic_metrics'] = {
            'total_tweets': len(self.df),
            'total_likes': int(self.df['likes'].sum()) if 'likes' in self.df.columns else 0,
            'total_retweets': int(self.df['retweets'].sum()) if 'retweets' in self.df.columns else 0,
            'total_replies': int(self.df['replies'].sum()) if 'replies' in self.df.columns else 0,
            'total_engagement': int(self.df['total_engagement'].sum()) if 'total_engagement' in self.df.columns else 0,
            'avg_engagement_per_tweet': float(self.df['total_engagement'].mean()) if 'total_engagement' in self.df.columns else 0,
            'median_engagement': float(self.df['total_engagement'].median()) if 'total_engagement' in self.df.columns else 0,
            'max_engagement': int(self.df['total_engagement'].max()) if 'total_engagement' in self.df.columns else 0,
        }
        
        return self.results['basic_metrics']
    
    def analyze_best_times(self):
        """Find best times to post"""
        print("\n⏰ Analyzing best posting times...")
        
        if 'hour' not in self.df.columns or 'total_engagement' not in self.df.columns:
            return None
        
        # Best hours
        hourly_engagement = self.df.groupby('hour')['total_engagement'].agg(['mean', 'count', 'sum'])
        hourly_engagement = hourly_engagement.sort_values('mean', ascending=False)
        
        best_hours = []
        for hour, row in hourly_engagement.head(5).iterrows():
            best_hours.append({
                'hour': int(hour),
                'avg_engagement': float(row['mean']),
                'tweet_count': int(row['count']),
                'total_engagement': int(row['sum'])
            })
        
        # Best days
        if 'day_name' in self.df.columns:
            daily_engagement = self.df.groupby('day_name')['total_engagement'].agg(['mean', 'count', 'sum'])
            daily_engagement = daily_engagement.sort_values('mean', ascending=False)
            
            best_days = []
            for day, row in daily_engagement.head(5).iterrows():
                best_days.append({
                    'day': str(day),
                    'avg_engagement': float(row['mean']),
                    'tweet_count': int(row['count']),
                    'total_engagement': int(row['sum'])
                })
        else:
            best_days = []
        
        self.results['best_times'] = {
            'best_hours': best_hours,
            'best_days': best_days
        }
        
        return self.results['best_times']
    
    def analyze_content_performance(self):
        """Analyze content performance"""
        print("\n📝 Analyzing content performance...")
        
        results = {}
        
        # Text length analysis
        if 'text_length' in self.df.columns and 'total_engagement' in self.df.columns:
            # Bin text lengths
            self.df['length_category'] = pd.cut(
                self.df['text_length'], 
                bins=[0, 50, 100, 150, 200, 1000],
                labels=['Very Short', 'Short', 'Medium', 'Long', 'Very Long']
            )
            
            length_engagement = self.df.groupby('length_category')['total_engagement'].agg(['mean', 'count'])
            
            results['by_length'] = []
            for cat, row in length_engagement.iterrows():
                results['by_length'].append({
                    'category': str(cat),
                    'avg_engagement': float(row['mean']),
                    'count': int(row['count'])
                })
        
        # Hashtag analysis
        if 'hashtag_count' in self.df.columns:
            # Group by hashtag count
            hashtag_engagement = self.df.groupby('hashtag_count')['total_engagement'].agg(['mean', 'count'])
            hashtag_engagement = hashtag_engagement.sort_values('mean', ascending=False)
            
            results['by_hashtag_count'] = []
            for count, row in hashtag_engagement.head(10).iterrows():
                results['by_hashtag_count'].append({
                    'hashtag_count': int(count),
                    'avg_engagement': float(row['mean']),
                    'tweet_count': int(row['count'])
                })
        
        # Mention analysis
        if 'mention_count' in self.df.columns:
            mention_engagement = self.df.groupby('mention_count')['total_engagement'].agg(['mean', 'count'])
            mention_engagement = mention_engagement.sort_values('mean', ascending=False)
            
            results['by_mention_count'] = []
            for count, row in mention_engagement.head(10).iterrows():
                results['by_mention_count'].append({
                    'mention_count': int(count),
                    'avg_engagement': float(row['mean']),
                    'tweet_count': int(row['count'])
                })
        
        self.results['content_performance'] = results
        return results
    
    def get_top_tweets(self, n=10):
        """Get top performing tweets"""
        print(f"\n🏆 Finding top {n} tweets...")
        
        if 'total_engagement' not in self.df.columns:
            return []
        
        top_tweets = self.df.nlargest(n, 'total_engagement')
        
        results = []
        for _, tweet in top_tweets.iterrows():
            result = {
                'date': str(tweet['date']) if 'date' in tweet else '',
                'content': str(tweet['content'])[:200] if 'content' in tweet else '',
                'likes': int(tweet['likes']) if 'likes' in tweet else 0,
                'retweets': int(tweet['retweets']) if 'retweets' in tweet else 0,
                'replies': int(tweet['replies']) if 'replies' in tweet else 0,
                'total_engagement': int(tweet['total_engagement']),
            }
            
            if 'sentiment' in tweet:
                result['sentiment'] = str(tweet['sentiment'])
            
            if 'url' in tweet:
                result['url'] = str(tweet['url'])
            
            results.append(result)
        
        self.results['top_tweets'] = results
        return results
    
    def analyze_trends(self):
        """Analyze engagement trends over time"""
        print("\n📈 Analyzing trends...")
        
        if 'date' not in self.df.columns or 'total_engagement' not in self.df.columns:
            return None
        
        # Daily trends
        self.df['date_only'] = pd.to_datetime(self.df['date']).dt.date
        daily_stats = self.df.groupby('date_only').agg({
            'total_engagement': ['sum', 'mean', 'count']
        }).reset_index()
        
        daily_stats.columns = ['date', 'total_engagement', 'avg_engagement', 'tweet_count']
        
        trends = []
        for _, row in daily_stats.iterrows():
            trends.append({
                'date': str(row['date']),
                'total_engagement': int(row['total_engagement']),
                'avg_engagement': float(row['avg_engagement']),
                'tweet_count': int(row['tweet_count'])
            })
        
        self.results['trends'] = {
            'daily': trends
        }
        
        return self.results['trends']
    
    def generate_report(self):
        """Generate complete analysis report"""
        print("\n" + "="*70)
        print("📊 GENERATING ENGAGEMENT REPORT")
        print("="*70)
        
        # Run all analyses
        self.calculate_basic_metrics()
        self.analyze_best_times()
        self.analyze_content_performance()
        self.get_top_tweets()
        self.analyze_trends()
        
        return self.results
    
    def print_report(self):
        """Print human-readable report"""
        print("\n" + "="*70)
        print("📊 ENGAGEMENT ANALYSIS REPORT")
        print("="*70)
        
        # Basic Metrics
        if 'basic_metrics' in self.results:
            metrics = self.results['basic_metrics']
            print("\n📈 BASIC METRICS:")
            print(f"   Total Tweets: {metrics['total_tweets']:,}")
            print(f"   Total Engagement: {metrics['total_engagement']:,}")
            print(f"   Average Engagement: {metrics['avg_engagement_per_tweet']:.2f}")
            print(f"   Median Engagement: {metrics['median_engagement']:.2f}")
            print(f"   Max Engagement: {metrics['max_engagement']:,}")
        
        # Best Times
        if 'best_times' in self.results:
            times = self.results['best_times']
            
            if times.get('best_hours'):
                print("\n⏰ BEST HOURS TO POST:")
                for hour_data in times['best_hours'][:3]:
                    hour = hour_data['hour']
                    avg = hour_data['avg_engagement']
                    print(f"   {hour:02d}:00 - Avg engagement: {avg:.2f}")
            
            if times.get('best_days'):
                print("\n📅 BEST DAYS TO POST:")
                for day_data in times['best_days'][:3]:
                    day = day_data['day']
                    avg = day_data['avg_engagement']
                    print(f"   {day} - Avg engagement: {avg:.2f}")
        
        # Top Tweets
        if 'top_tweets' in self.results:
            print("\n🏆 TOP 5 TWEETS:")
            for i, tweet in enumerate(self.results['top_tweets'][:5], 1):
                print(f"\n   {i}. Engagement: {tweet['total_engagement']:,}")
                print(f"      💙 {tweet['likes']} | 🔁 {tweet['retweets']} | 💬 {tweet['replies']}")
                print(f"      📝 {tweet['content'][:100]}...")
                if 'sentiment' in tweet:
                    print(f"      😊 Sentiment: {tweet['sentiment']}")
        
        print("\n" + "="*70)
    
    def save_report(self, output_path):
        """Save report to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Report saved to: {output_path}")


def main():
    """Main execution"""
    print("="*70)
    print("📊 ENGAGEMENT ANALYZER - IndoPopBase Analytics")
    print("="*70)
    
    # Find processed files with sentiment
    processed_dir = 'data/processed'
    
    if os.path.exists(processed_dir):
        csv_files = [f for f in os.listdir(processed_dir) 
                     if f.endswith('.csv') and 'sentiment' in f]
        
        if csv_files:
            print(f"\n📁 Found {len(csv_files)} file(s):")
            for i, file in enumerate(csv_files, 1):
                print(f"   {i}. {file}")
            
            choice = input("\nEnter file number: ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(csv_files):
                    file_path = os.path.join(processed_dir, csv_files[idx])
                    
                    # Load data
                    print(f"\n📂 Loading: {csv_files[idx]}")
                    df = pd.read_csv(file_path)
                    print(f"✅ Loaded {len(df)} tweets")
                    
                    # Analyze
                    analyzer = EngagementAnalyzer(df)
                    analyzer.generate_report()
                    analyzer.print_report()
                    
                    # Save report
                    report_path = file_path.replace('.csv', '_engagement_report.json')
                    analyzer.save_report(report_path)
                    
                else:
                    print("❌ Invalid number")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("\n❌ No processed files with sentiment found")
            print("💡 Run sentiment_analyzer.py first")
    else:
        print(f"\n❌ Directory '{processed_dir}' not found")
    
    print("\n✅ Engagement analysis completed!")


if __name__ == "__main__":
    main()