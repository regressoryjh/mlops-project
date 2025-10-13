"""
Twitter Scraper for @IndoPopBase
Menggunakan snscrape (free, no rate limit)

Install requirements:
pip install snscrape pandas tqdm

Note: snscrape might have issues, alternative: tweety-ns, twscrape
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import json
import os

class TwitterScraper:
    def __init__(self, username):
        self.username = username.replace('@', '')
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def scrape_user_tweets(self, max_tweets=1000, since_date=None):
        """
        Scrape tweets dari akun tertentu
        
        Args:
            max_tweets: Maksimal jumlah tweets yang akan di-scrape
            since_date: Tanggal mulai (format: 'YYYY-MM-DD')
        """
        print(f"🔍 Scraping tweets from @{self.username}...")
        
        tweets_list = []
        query = f"from:{self.username}"
        
        if since_date:
            query += f" since:{since_date}"
        
        try:
            for i, tweet in enumerate(tqdm(
                sntwitter.TwitterSearchScraper(query).get_items(),
                total=max_tweets,
                desc="Fetching tweets"
            )):
                if i >= max_tweets:
                    break
                
                tweet_data = {
                    'tweet_id': tweet.id,
                    'date': tweet.date,
                    'username': tweet.user.username,
                    'display_name': tweet.user.displayname,
                    'tweet_url': tweet.url,
                    'content': tweet.rawContent,
                    'reply_count': tweet.replyCount,
                    'retweet_count': tweet.retweetCount,
                    'like_count': tweet.likeCount,
                    'quote_count': tweet.quoteCount,
                    'view_count': tweet.viewCount if hasattr(tweet, 'viewCount') else None,
                    'lang': tweet.lang,
                    'hashtags': tweet.hashtags if tweet.hashtags else [],
                    'mentioned_users': [user.username for user in tweet.mentionedUsers] if tweet.mentionedUsers else [],
                    'is_reply': tweet.inReplyToTweetId is not None,
                    'is_retweet': tweet.retweetedTweet is not None,
                }
                
                tweets_list.append(tweet_data)
        
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Tip: snscrape mungkin tidak stabil. Coba alternative: tweety-ns atau twscrape")
        
        df = pd.DataFrame(tweets_list)
        
        if not df.empty:
            # Save to CSV
            filename = f"{self.data_dir}/{self.username}_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Saved {len(df)} tweets to {filename}")
            
            # Print summary
            self._print_summary(df)
        
        return df
    
    def scrape_mentions(self, max_tweets=1000, since_date=None):
        """
        Scrape tweets yang mention @username
        """
        print(f"🔍 Scraping mentions of @{self.username}...")
        
        tweets_list = []
        query = f"@{self.username}"
        
        if since_date:
            query += f" since:{since_date}"
        
        try:
            for i, tweet in enumerate(tqdm(
                sntwitter.TwitterSearchScraper(query).get_items(),
                total=max_tweets,
                desc="Fetching mentions"
            )):
                if i >= max_tweets:
                    break
                
                # Skip tweets dari akun sendiri
                if tweet.user.username.lower() == self.username.lower():
                    continue
                
                tweet_data = {
                    'tweet_id': tweet.id,
                    'date': tweet.date,
                    'username': tweet.user.username,
                    'display_name': tweet.user.displayname,
                    'tweet_url': tweet.url,
                    'content': tweet.rawContent,
                    'reply_count': tweet.replyCount,
                    'retweet_count': tweet.retweetCount,
                    'like_count': tweet.likeCount,
                    'quote_count': tweet.quoteCount,
                    'view_count': tweet.viewCount if hasattr(tweet, 'viewCount') else None,
                    'lang': tweet.lang,
                    'hashtags': tweet.hashtags if tweet.hashtags else [],
                    'is_reply_to_target': self.username.lower() in [user.username.lower() for user in tweet.mentionedUsers] if tweet.mentionedUsers else False,
                }
                
                tweets_list.append(tweet_data)
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        df = pd.DataFrame(tweets_list)
        
        if not df.empty:
            filename = f"{self.data_dir}/{self.username}_mentions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Saved {len(df)} mentions to {filename}")
            
            self._print_summary(df)
        
        return df
    
    def _print_summary(self, df):
        """Print summary statistik"""
        print("\n📊 Summary Statistics:")
        print(f"Total tweets: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"\nEngagement Stats:")
        print(f"  Total likes: {df['like_count'].sum():,}")
        print(f"  Total retweets: {df['retweet_count'].sum():,}")
        print(f"  Total replies: {df['reply_count'].sum():,}")
        print(f"  Avg likes per tweet: {df['like_count'].mean():.2f}")
        print(f"  Avg retweets per tweet: {df['retweet_count'].mean():.2f}")
        print(f"\nTop 5 Most Engaged Tweets:")
        df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
        top_tweets = df.nlargest(5, 'total_engagement')[['date', 'content', 'total_engagement', 'tweet_url']]
        for idx, row in top_tweets.iterrows():
            print(f"\n  {row['date'].strftime('%Y-%m-%d')} | Engagement: {row['total_engagement']:,}")
            print(f"  {row['content'][:100]}...")
            print(f"  {row['tweet_url']}")


# ============================================
# ALTERNATIVE METHOD: Using tweety-ns
# (Lebih stabil daripada snscrape)
# ============================================

"""
Install tweety-ns:
pip install tweety-ns

Usage:
"""

class TwitterScraperTweety:
    def __init__(self, username):
        """
        Alternative scraper using tweety-ns
        Lebih stabil dan aktif maintenance
        """
        try:
            from tweety import Twitter
            self.app = Twitter("session")
            self.username = username.replace('@', '')
            self.data_dir = 'data'
            os.makedirs(self.data_dir, exist_ok=True)
        except ImportError:
            print("❌ tweety-ns not installed. Run: pip install tweety-ns")
    
    def scrape_user_tweets(self, max_tweets=1000):
        """Scrape tweets using tweety-ns"""
        from tweety import Twitter
        
        print(f"🔍 Scraping tweets from @{self.username} using tweety-ns...")
        
        app = Twitter("session")
        tweets_list = []
        
        try:
            user = app.get_user(self.username)
            tweets = user.get_tweets(total=max_tweets)
            
            for tweet in tqdm(tweets, desc="Processing tweets"):
                tweet_data = {
                    'tweet_id': tweet.id,
                    'date': tweet.created_at,
                    'username': tweet.author.username,
                    'display_name': tweet.author.name,
                    'tweet_url': f"https://twitter.com/{tweet.author.username}/status/{tweet.id}",
                    'content': tweet.text,
                    'reply_count': tweet.reply_count,
                    'retweet_count': tweet.retweet_count,
                    'like_count': tweet.favorite_count,
                    'quote_count': tweet.quote_count,
                    'view_count': tweet.view_count if hasattr(tweet, 'view_count') else None,
                    'lang': tweet.language,
                    'is_reply': tweet.is_reply,
                    'is_retweet': tweet.is_retweet,
                }
                
                tweets_list.append(tweet_data)
            
            df = pd.DataFrame(tweets_list)
            
            if not df.empty:
                filename = f"{self.data_dir}/{self.username}_tweets_tweety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                print(f"✅ Saved {len(df)} tweets to {filename}")
            
            return df
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Configuration
    TARGET_USERNAME = "IndoPopBase"
    MAX_TWEETS = 500  # Adjust sesuai kebutuhan
    SINCE_DATE = "2024-01-01"  # Scrape tweets sejak tanggal ini
    
    print("="*60)
    print("🐦 Twitter Scraper for @IndoPopBase")
    print("="*60)
    
    # Method 1: Using snscrape (might be unstable)
    print("\n📌 Method 1: Using snscrape")
    print("-" * 60)
    
    try:
        scraper = TwitterScraper(TARGET_USERNAME)
        
        # Scrape tweets dari akun
        print("\n1️⃣ Scraping account tweets...")
        df_tweets = scraper.scrape_user_tweets(
            max_tweets=MAX_TWEETS,
            since_date=SINCE_DATE
        )
        
        # Scrape mentions
        print("\n2️⃣ Scraping mentions...")
        df_mentions = scraper.scrape_mentions(
            max_tweets=MAX_TWEETS,
            since_date=SINCE_DATE
        )
        
    except Exception as e:
        print(f"❌ snscrape failed: {e}")
        print("\n💡 Trying alternative method...")
    
    # Method 2: Using tweety-ns (recommended)
    print("\n\n📌 Method 2: Using tweety-ns (RECOMMENDED)")
    print("-" * 60)
    
    try:
        scraper_tweety = TwitterScraperTweety(TARGET_USERNAME)
        df_tweets_tweety = scraper_tweety.scrape_user_tweets(max_tweets=MAX_TWEETS)
    except Exception as e:
        print(f"❌ tweety-ns failed: {e}")
    
    print("\n" + "="*60)
    print("✅ Scraping completed!")
    print("📁 Check the 'data/' folder for CSV files")
    print("="*60)
    
    # Tips
    print("\n💡 Tips:")
    print("1. snscrape sering tidak stabil, gunakan tweety-ns sebagai alternative")
    print("2. Untuk scraping besar, bagi menjadi beberapa batch")
    print("3. Jangan scrape terlalu agresif untuk menghindari IP block")
    print("4. Data disimpan di folder 'data/' dengan timestamp")