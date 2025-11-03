"""
Data Cleaner - Automated preprocessing untuk tweets IndoPopBase
Untuk MLOps Pipeline - No user input required
"""

import pandas as pd
import re
import os
from datetime import datetime
import warnings
import glob
warnings.filterwarnings('ignore')

class TweetDataCleaner:
    def __init__(self, input_path, output_dir='data/processed'):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_text(self, text):
        """Clean tweet text"""
        if pd.isna(text):
            return ""
        
        # Convert to string
        text = str(text)
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove HTML entities
        text = re.sub(r'&\w+;', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_features(self, df):
        """Extract additional features from tweets"""
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Extract time features
        df['hour'] = df['date'].dt.hour
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_name'] = df['date'].dt.day_name()
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Text features
        df['text_length'] = df['content'].apply(lambda x: len(str(x)))
        df['word_count'] = df['content'].apply(lambda x: len(str(x).split()))
        
        # Count mentions
        df['mention_count'] = df['content'].apply(
            lambda x: len(re.findall(r'@\w+', str(x)))
        )
        
        # Count hashtags
        df['hashtag_count'] = df['content'].apply(
            lambda x: len(re.findall(r'#\w+', str(x)))
        )
        
        # Extract hashtags
        df['hashtags'] = df['content'].apply(
            lambda x: re.findall(r'#\w+', str(x))
        )
        
        # Calculate total engagement
        engagement_cols = ['likes', 'retweets', 'replies']
        for col in engagement_cols:
            if col not in df.columns:
                df[col] = 0
        
        df['total_engagement'] = df['likes'] + df['retweets'] + df['replies']
        
        # Engagement rate (normalized by total engagement)
        max_engagement = df['total_engagement'].max()
        if max_engagement > 0:
            df['engagement_score'] = df['total_engagement'] / max_engagement
        else:
            df['engagement_score'] = 0
        
        return df
    
    def clean_dataset(self):
        """Main cleaning function"""
        print("="*70)
        print("🧹 DATA CLEANING PROCESS")
        print("="*70)
        
        # Read data
        print(f"\n📂 Reading data from: {self.input_path}")
        try:
            df = pd.read_csv(self.input_path)
            print(f"✅ Loaded {len(df)} rows")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
        
        # Show original columns
        print(f"\n📋 Original columns: {list(df.columns)}")
        
        # Remove duplicates
        original_len = len(df)
        df = df.drop_duplicates(subset=['content'] if 'content' in df.columns else None)
        print(f"\n🔄 Removed {original_len - len(df)} duplicates")
        
        # Remove rows with missing content
        if 'content' in df.columns:
            df = df.dropna(subset=['content'])
            print(f"✅ Removed rows with missing content")
        
        # Clean text
        if 'content' in df.columns:
            print("\n🧼 Cleaning text...")
            df['content_clean'] = df['content'].apply(self.clean_text)
            
            # Remove empty cleaned texts
            df = df[df['content_clean'].str.len() > 0]
            print(f"✅ Cleaned {len(df)} tweets")
        
        # Extract features
        print("\n📊 Extracting features...")
        df = self.extract_features(df)
        print("✅ Features extracted")
        
        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date', ascending=False)
        
        # Save cleaned data
        output_path = os.path.join(
            self.output_dir, 
            f"cleaned_{os.path.basename(self.input_path)}"
        )
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n💾 Saved cleaned data to: {output_path}")
        
        # Print summary
        self.print_summary(df)
        
        return df
    
    def print_summary(self, df):
        """Print data summary"""
        print("\n" + "="*70)
        print("📊 DATA SUMMARY")
        print("="*70)
        
        print(f"\n📈 Total Records: {len(df)}")
        
        if 'date' in df.columns:
            print(f"📅 Date Range: {df['date'].min()} to {df['date'].max()}")
        
        if 'total_engagement' in df.columns:
            print(f"\n💙 Engagement Statistics:")
            print(f"   Total Engagement: {df['total_engagement'].sum():,.0f}")
            print(f"   Average per Tweet: {df['total_engagement'].mean():.2f}")
            print(f"   Median: {df['total_engagement'].median():.2f}")
            print(f"   Max: {df['total_engagement'].max():,.0f}")
        
        if 'text_length' in df.columns:
            print(f"\n📝 Text Statistics:")
            print(f"   Avg Length: {df['text_length'].mean():.0f} characters")
            print(f"   Avg Words: {df['word_count'].mean():.1f} words")
        
        if 'hashtag_count' in df.columns:
            print(f"\n#️⃣ Hashtag Usage:")
            print(f"   Total Hashtags: {df['hashtag_count'].sum():.0f}")
            print(f"   Avg per Tweet: {df['hashtag_count'].mean():.2f}")
        
        print("\n" + "="*70)


def find_newest_dataset(data_dir='data/raw'):
    """
    Find the newest complete dataset (account with all 3 file types)
    Returns: (account_name, date_str, file_dict) or None
    """
    print(f"🔍 Scanning {data_dir} for complete datasets...")
    
    # Find all CSV files
    all_files = glob.glob(os.path.join(data_dir, '*.csv'))
    
    if not all_files:
        print(f"❌ No CSV files found in {data_dir}")
        return None
    
    # Parse filenames: [account]_[type]_[YYYYMMDD]_[HHMMSS].csv
    datasets = {}  # {(account, date): {type: filepath}}
    
    for filepath in all_files:
        basename = os.path.basename(filepath)
        parts = basename.replace('.csv', '').split('_')
        
        # Expected format: account_type_date_time
        # e.g., barengwarga_all_quotes_20251013_141157.csv
        if len(parts) >= 4:
            # Handle compound account names (e.g., "indo_pop_base")
            # and compound types (e.g., "all_quotes", "original_tweets")
            
            # Find the date (8 digits)
            date_idx = None
            for i, part in enumerate(parts):
                if len(part) == 8 and part.isdigit():
                    date_idx = i
                    break
            
            if date_idx is None or date_idx < 2:
                continue
            
            # Everything before date is account + type
            account_type_parts = parts[:date_idx]
            date_str = parts[date_idx]
            
            # Last part of account_type should be the type indicator
            # Types: "all_quotes", "all_replies", "original_tweets"
            if len(account_type_parts) >= 2:
                # Check if ends with known type patterns
                type_str = '_'.join(account_type_parts[-2:])  # e.g., "all_quotes"
                
                # Identify the type
                if 'quotes' in type_str:
                    tweet_type = 'quotes'
                elif 'replies' in type_str:
                    tweet_type = 'replies'
                elif 'original' in type_str or 'tweets' in type_str:
                    tweet_type = 'original'
                else:
                    continue
                
                # Account name is everything before the type
                if tweet_type in ['quotes', 'replies']:
                    # For "all_quotes" or "all_replies", remove last 2 parts
                    account_parts = account_type_parts[:-2]
                else:
                    # For "original_tweets", remove last 2 parts
                    account_parts = account_type_parts[:-2]
                
                if not account_parts:
                    continue
                    
                account_name = '_'.join(account_parts)
                
                # Store in datasets dict
                key = (account_name, date_str)
                if key not in datasets:
                    datasets[key] = {}
                datasets[key][tweet_type] = filepath
    
    if not datasets:
        print("❌ No valid datasets found")
        return None
    
    # Find complete datasets (with all 3 types)
    complete_datasets = []
    for (account, date), files in datasets.items():
        if len(files) == 3 and all(t in files for t in ['quotes', 'replies', 'original']):
            complete_datasets.append((account, date, files))
    
    if not complete_datasets:
        print("⚠️ No complete datasets found (need quotes, replies, and original_tweets)")
        print("\n📋 Available datasets:")
        for (account, date), files in sorted(datasets.items(), key=lambda x: x[0][1], reverse=True):
            print(f"   {account} ({date}): {list(files.keys())}")
        return None
    
    # Sort by date (newest first)
    complete_datasets.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n✅ Found {len(complete_datasets)} complete dataset(s):")
    for account, date, files in complete_datasets:
        print(f"   - {account} ({date}): {len(files)} files")
    
    # Return the newest complete dataset
    newest = complete_datasets[0]
    print(f"\n🎯 Selected: {newest[0]} ({newest[1]})")
    
    return newest


def process_dataset_group(data_dir='data/raw'):
    """
    Automatically find and process the newest complete dataset
    """
    print("="*70)
    print("📦 AUTOMATED DATASET PROCESSING")
    print("="*70)
    
    # Find newest complete dataset
    result = find_newest_dataset(data_dir)
    
    if result is None:
        return None
    
    account_name, date_str, files = result
    
    print(f"\n📂 Processing files:")
    for tweet_type, filepath in files.items():
        print(f"   - {tweet_type}: {os.path.basename(filepath)}")
    
    # Process each file
    all_dfs = []
    for tweet_type, filepath in sorted(files.items()):
        print(f"\n\n{'='*70}")
        print(f"Processing: {tweet_type.upper()}")
        print(f"File: {os.path.basename(filepath)}")
        print('='*70)
        
        cleaner = TweetDataCleaner(filepath)
        df = cleaner.clean_dataset()
        
        if df is not None:
            # Add tweet type column
            df['tweet_type'] = tweet_type
            all_dfs.append(df)
    
    # Combine all dataframes with LEFT JOIN logic
    if all_dfs:
        print("\n\n" + "="*70)
        print("📦 COMBINING ALL TWEET TYPES (LEFT JOIN)")
        print("="*70)
        print("💡 Enriching original tweets with their quotes & replies")
        
        # Separate dataframes by type
        original_df = None
        quotes_df = None
        replies_df = None
        
        for df in all_dfs:
            tweet_type = df['tweet_type'].iloc[0] if len(df) > 0 else None
            if tweet_type == 'original':
                original_df = df.copy()
            elif tweet_type == 'quotes':
                quotes_df = df.copy()
            elif tweet_type == 'replies':
                replies_df = df.copy()
        
        if original_df is None:
            print("❌ No original tweets found!")
            return None
        
        print(f"📊 Left table (original tweets): {len(original_df):,} records")
        
        # Prepare quotes and replies for joining
        engagement_tweets = []
        
        if quotes_df is not None:
            print(f"📊 Quotes found: {len(quotes_df):,} records")
            quotes_df['engagement_type'] = 'quote'
            quotes_df['parent_url'] = quotes_df['quote_of']
            engagement_tweets.append(quotes_df)
        
        if replies_df is not None:
            print(f"📊 Replies found: {len(replies_df):,} records")
            replies_df['engagement_type'] = 'reply'
            replies_df['parent_url'] = replies_df['reply_of']
            engagement_tweets.append(replies_df)
        
        if not engagement_tweets:
            print("⚠️ No quotes or replies found, using original tweets only")
            combined_df = original_df
        else:
            # Combine quotes and replies
            all_engagements = pd.concat(engagement_tweets, ignore_index=True)
            print(f"\n📊 Total engagement tweets: {len(all_engagements):,}")
            
            # LEFT JOIN: Keep all original tweets, add engagement data
            # Group engagement tweets by parent URL
            print("\n🔗 Performing LEFT JOIN (original tweets + engagements)...")
            
            # Create a column for joining in original_df
            original_df['join_key'] = original_df['tweet_url']
            all_engagements['join_key'] = all_engagements['parent_url']
            
            # Perform LEFT JOIN
            combined_df = original_df.merge(
                all_engagements,
                on='join_key',
                how='left',
                suffixes=('_original', '_engagement')
            )
            
            # Count matches
            matched_originals = combined_df['content_engagement'].notna().sum()
            unique_originals_with_engagement = combined_df[combined_df['content_engagement'].notna()]['content_original'].nunique()
            
            print(f"✅ Join completed!")
            print(f"   - Total rows (original + engagements): {len(combined_df):,}")
            print(f"   - Original tweets with engagement: {unique_originals_with_engagement:,} / {len(original_df):,}")
            print(f"   - Total engagement responses: {matched_originals:,}")
            print(f"   - Original tweets without engagement: {len(original_df) - unique_originals_with_engagement:,}")
            
            # Calculate engagement stats per original tweet
            engagement_stats = combined_df[combined_df['content_engagement'].notna()].groupby('content_original').agg({
                'content_engagement': 'count',
                'engagement_type': lambda x: x.value_counts().to_dict()
            }).reset_index()
            
            if len(engagement_stats) > 0:
                print(f"\n📈 Engagement Distribution:")
                avg_engagement = engagement_stats['content_engagement'].mean()
                max_engagement = engagement_stats['content_engagement'].max()
                print(f"   - Avg engagements per original tweet: {avg_engagement:.1f}")
                print(f"   - Max engagements on single tweet: {max_engagement:.0f}")
        
        # Remove duplicates based on original content and engagement content combination
        original_len = len(combined_df)
        # Keep duplicates if they're different engagements on same original tweet
        if 'content_engagement' in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset=['content_original', 'content_engagement'])
        else:
            combined_df = combined_df.drop_duplicates(subset=['content'])
        print(f"\n🔄 Removed {original_len - len(combined_df)} duplicates")
        
        # Save combined dataset
        output_dir = 'data/processed'
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f'{account_name}_all_tweets_cleaned_{date_str}.csv'
        output_path = os.path.join(output_dir, output_filename)
        combined_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\n💾 Saved combined dataset to: {output_path}")
        print(f"📊 Total records: {len(combined_df)}")
        
        # Print breakdown by type
        print(f"\n📋 Breakdown by type:")
        for tweet_type in ['original', 'quotes', 'replies']:
            count = len(combined_df[combined_df['tweet_type'] == tweet_type])
            if count > 0:
                print(f"   - {tweet_type}: {count:,} tweets")
        
        # Print join statistics
        if 'content_parent' in combined_df.columns:
            print(f"\n🔗 Join Statistics:")
            print(f"   - Total tweets (quotes + replies): {len(combined_df):,}")
            print(f"   - With parent tweet context: {combined_df['content_parent'].notna().sum():,}")
            print(f"   - Without parent context: {combined_df['content_parent'].isna().sum():,}")
        
        return combined_df
    
    return None


def main():
    """Main execution - automated for MLOps pipeline"""
    print("="*70)
    print("🚀 TWEET DATA CLEANER - Automated MLOps Pipeline")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    DATA_DIR = 'data/raw'
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ Directory '{DATA_DIR}' not found!")
        print(f"💡 Please ensure your data files are in '{DATA_DIR}' folder")
        return
    
    # Process the newest complete dataset
    result = process_dataset_group(DATA_DIR)
    
    if result is not None:
        print("\n" + "="*70)
        print("✅ DATA CLEANING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"📁 Processed files saved to: data/processed/")
        print(f"📊 Total tweets processed: {len(result):,}")
    else:
        print("\n" + "="*70)
        print("❌ DATA CLEANING FAILED")
        print("="*70)
        print("💡 Check error messages above for details")
    
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()