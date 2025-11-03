"""
Data Cleaner - Complete preprocessing untuk tweets IndoPopBase
Jalankan: python data_cleaner.py
"""

import pandas as pd
import re
import os
from datetime import datetime
import warnings
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


class MultiFileProcessor:
    """Process multiple CSV files"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
    
    def process_all_files(self):
        """Process all CSV files in data directory"""
        print("="*70)
        print("🔄 PROCESSING ALL DATA FILES")
        print("="*70)
        
        # Find all CSV files
        csv_files = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.csv') and not file.startswith('cleaned_'):
                csv_files.append(os.path.join(self.data_dir, file))
        
        if not csv_files:
            print("\n❌ No CSV files found in data directory")
            return
        
        print(f"\n📁 Found {len(csv_files)} file(s) to process:")
        for file in csv_files:
            print(f"   - {os.path.basename(file)}")
        
        # Process each file
        all_dfs = []
        for file in csv_files:
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
            print("📦 COMBINING ALL DATASETS")
            print("="*70)
            
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Remove duplicates across files
            original_len = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=['content'])
            print(f"\n🔄 Removed {original_len - len(combined_df)} duplicates across files")
            
            # Save combined dataset
            output_path = os.path.join(self.data_dir, 'processed', 'all_tweets_cleaned.csv')
            combined_df.to_csv(output_path, index=False, encoding='utf-8')
            
            print(f"\n💾 Saved combined dataset to: {output_path}")
            print(f"📊 Total records: {len(combined_df)}")
            
            return combined_df
        
        return None


def main():
    """Main execution"""
    print("="*70)
    print("🚀 TWEET DATA CLEANER - IndoPopBase Analytics")
    print("="*70)
    
    # Ask user for input
    print("\nOptions:")
    print("1. Process single file")
    print("2. Process all files in data/ directory")
    
    # choice = input("\nChoose option (1 or 2): ").strip()
    
    # if choice == '1':
    file_path = input("Enter CSV file path: ").strip()
    if os.path.exists(file_path):
        cleaner = TweetDataCleaner(file_path)
        cleaner.clean_dataset()
    else:
        print(f"❌ File not found: {file_path}")
    
    # elif choice == '2':
    #     processor = MultiFileProcessor()
    #     processor.process_all_files()
    
    # else:
    #     print("❌ Invalid choice")
    
    print("\n✅ Data cleaning completed!")
    print("📁 Check the 'data/processed/' folder for cleaned files")


if __name__ == "__main__":
    main()
