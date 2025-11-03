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


def get_newest_dataset(data_dir='data/raw', dataset_prefix='barengwarga'):
    """
    Find the newest dataset based on filename timestamp
    Looks for files matching pattern: {dataset_prefix}_*_YYYYMMDD_*.csv
    """
    print(f"🔍 Looking for {dataset_prefix} datasets in {data_dir}...")
    
    # Find all matching CSV files
    pattern = os.path.join(data_dir, f"{dataset_prefix}_*.csv")
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        print(f"❌ No {dataset_prefix} datasets found in {data_dir}")
        return None
    
    print(f"📁 Found {len(csv_files)} {dataset_prefix} file(s)")
    
    # Extract timestamps from filenames and sort
    files_with_timestamps = []
    for file in csv_files:
        basename = os.path.basename(file)
        # Extract date from filename (format: prefix_type_YYYYMMDD_HHMMSS.csv)
        parts = basename.split('_')
        if len(parts) >= 3:
            try:
                # Try to parse the date part (usually 3rd element)
                date_str = parts[2]
                timestamp = datetime.strptime(date_str, '%Y%m%d')
                files_with_timestamps.append((file, timestamp, basename))
            except:
                # If parsing fails, use file modification time
                mtime = os.path.getmtime(file)
                timestamp = datetime.fromtimestamp(mtime)
                files_with_timestamps.append((file, timestamp, basename))
    
    if not files_with_timestamps:
        print("⚠️ Could not parse timestamps, using first file found")
        return csv_files[0]
    
    # Sort by timestamp (newest first)
    files_with_timestamps.sort(key=lambda x: x[1], reverse=True)
    
    # Print all found files
    print("\n📋 Available datasets (sorted by date):")
    for i, (file, timestamp, basename) in enumerate(files_with_timestamps, 1):
        print(f"   {i}. {basename} ({timestamp.strftime('%Y-%m-%d')})")
    
    # Return the newest file
    newest_file = files_with_timestamps[0][0]
    newest_name = files_with_timestamps[0][2]
    newest_date = files_with_timestamps[0][1]
    
    print(f"\n✅ Selected newest dataset: {newest_name}")
    print(f"   Date: {newest_date.strftime('%Y-%m-%d')}")
    
    return newest_file


def process_dataset_group(data_dir='data/raw', dataset_prefix='barengwarga'):
    """
    Process all files from the newest dataset group
    (original_tweets, quotes, replies)
    """
    print("="*70)
    print(f"📦 PROCESSING {dataset_prefix.upper()} DATASET GROUP")
    print("="*70)
    
    # Find all files matching the dataset prefix with the newest timestamp
    pattern = os.path.join(data_dir, f"{dataset_prefix}_*.csv")
    all_files = glob.glob(pattern)
    
    if not all_files:
        print(f"❌ No {dataset_prefix} datasets found")
        return None
    
    # Group files by timestamp
    grouped_files = {}
    for file in all_files:
        basename = os.path.basename(file)
        parts = basename.split('_')
        if len(parts) >= 3:
            date_str = parts[2]  # YYYYMMDD
            if date_str not in grouped_files:
                grouped_files[date_str] = []
            grouped_files[date_str].append(file)
    
    # Get the newest group
    if not grouped_files:
        print("❌ Could not group files by timestamp")
        return None
    
    newest_date = max(grouped_files.keys())
    newest_group = grouped_files[newest_date]
    
    print(f"\n✅ Found {len(newest_group)} files from {newest_date}:")
    for file in newest_group:
        print(f"   - {os.path.basename(file)}")
    
    # Process each file in the group
    all_dfs = []
    for file in newest_group:
        print(f"\n\n{'='*70}")
        print(f"Processing: {os.path.basename(file)}")
        print('='*70)
        
        cleaner = TweetDataCleaner(file)
        df = cleaner.clean_dataset()
        
        if df is not None:
            all_dfs.append(df)
    
    # Combine all dataframes
    if all_dfs:
        print("\n\n" + "="*70)
        print("📦 COMBINING ALL FILES FROM DATASET")
        print("="*70)
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # Remove duplicates across files
        original_len = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['content'])
        print(f"\n🔄 Removed {original_len - len(combined_df)} duplicates across files")
        
        # Save combined dataset
        output_dir = 'data/processed'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{dataset_prefix}_all_tweets_cleaned.csv')
        combined_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\n💾 Saved combined dataset to: {output_path}")
        print(f"📊 Total records: {len(combined_df)}")
        
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
    DATASET_PREFIX = 'barengwarga'  # Change this if needed
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ Directory '{DATA_DIR}' not found!")
        print(f"💡 Please ensure your data files are in '{DATA_DIR}' folder")
        return
    
    # Process the newest dataset group
    result = process_dataset_group(DATA_DIR, DATASET_PREFIX)
    
    if result is not None:
        print("\n" + "="*70)
        print("✅ DATA CLEANING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"📁 Processed files saved to: data/processed/")
        print(f"📊 Total tweets processed: {len(result)}")
    else:
        print("\n" + "="*70)
        print("❌ DATA CLEANING FAILED")
        print("="*70)
        print("💡 Check error messages above for details")
    
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()