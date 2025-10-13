"""
ALTERNATIVE TWITTER SCRAPER - FREE & NO RATE LIMIT
Menggunakan multiple methods yang paling reliable

Recommended Order:
1. twscrape (BEST - paling stabil)
2. tweety-ns (GOOD - mudah digunakan)
3. ntscraper (GOOD - lightweight)
4. snscrape (UNSTABLE - sering bermasalah)

Install:
pip install twscrape tweety-ns ntscraper pandas tqdm
"""

import pandas as pd
from datetime import datetime
import os
from tqdm import tqdm
import asyncio

# ============================================
# METHOD 1: TWSCRAPE (RECOMMENDED - PALING STABIL)
# ============================================

class TwscrapeMethod:
    """
    Menggunakan twscrape - Twitter scraper terbaik saat ini
    Kelebihan:
    - Paling stabil
    - Support async
    - Bisa scrape banyak data
    - Aktif maintenance
    
    Setup:
    pip install twscrape
    """
    
    def __init__(self, username):
        self.username = username.replace('@', '')
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def setup_account(self):
        """
        Setup akun Twitter untuk scraping
        PENTING: Anda perlu Twitter account (bisa akun baru/dummy)
        """
        from twscrape import API
        
        api = API()
        
        # Add akun Twitter (gunakan akun dummy/burner account)
        # Format: username, password, email, email_password
        print("⚠️ Setup Twitter Account for Scraping:")
        print("Note: Gunakan akun dummy/burner, bukan akun utama!")
        print("Anda bisa buat akun baru khusus untuk scraping\n")
        
        # Uncomment dan isi dengan credentials akun dummy
        # await api.pool.add_account("username", "password", "email@example.com", "email_password")
        # await api.pool.login_all()
        
        return api
    
    async def scrape_user_tweets(self, max_tweets=1000):
        """Scrape tweets dari user"""
        from twscrape import API
        
        print(f"🔍 Scraping tweets from @{self.username} using twscrape...")
        
        api = API()
        tweets_list = []
        
        try:
            count = 0
            async for tweet in api.user_tweets(self.username, limit=max_tweets):
                tweet_data = {
                    'tweet_id': tweet.id,
                    'date': tweet.date,
                    'username': tweet.user.username,
                    'display_name': tweet.user.displayName,
                    'tweet_url': tweet.url,
                    'content': tweet.rawContent,
                    'reply_count': tweet.replyCount,
                    'retweet_count': tweet.retweetCount,
                    'like_count': tweet.likeCount,
                    'quote_count': tweet.quoteCount,
                    'view_count': tweet.viewCount,
                    'lang': tweet.lang,
                    'is_reply': tweet.inReplyToTweetId is not None,
                    'is_retweet': hasattr(tweet, 'retweetedTweet'),
                }
                
                tweets_list.append(tweet_data)
                count += 1
                
                if count % 100 == 0:
                    print(f"  Scraped {count} tweets...")
            
            df = pd.DataFrame(tweets_list)
            
            if not df.empty:
                filename = f"{self.data_dir}/{self.username}_tweets_twscrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ Saved {len(df)} tweets to {filename}")
                self._print_summary(df)
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()
    
    async def scrape_mentions(self, max_tweets=1000):
        """Scrape mentions"""
        from twscrape import API
        
        print(f"🔍 Scraping mentions of @{self.username}...")
        
        api = API()
        tweets_list = []
        
        try:
            query = f"@{self.username}"
            count = 0
            
            async for tweet in api.search(query, limit=max_tweets):
                # Skip tweets dari akun sendiri
                if tweet.user.username.lower() == self.username.lower():
                    continue
                
                tweet_data = {
                    'tweet_id': tweet.id,
                    'date': tweet.date,
                    'username': tweet.user.username,
                    'display_name': tweet.user.displayName,
                    'tweet_url': tweet.url,
                    'content': tweet.rawContent,
                    'reply_count': tweet.replyCount,
                    'retweet_count': tweet.retweetCount,
                    'like_count': tweet.likeCount,
                    'quote_count': tweet.quoteCount,
                    'view_count': tweet.viewCount,
                    'lang': tweet.lang,
                }
                
                tweets_list.append(tweet_data)
                count += 1
                
                if count % 100 == 0:
                    print(f"  Scraped {count} mentions...")
            
            df = pd.DataFrame(tweets_list)
            
            if not df.empty:
                filename = f"{self.data_dir}/{self.username}_mentions_twscrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ Saved {len(df)} mentions to {filename}")
                self._print_summary(df)
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()
    
    def _print_summary(self, df):
        """Print summary"""
        print("\n📊 Summary Statistics:")
        print(f"Total tweets: {len(df)}")
        if not df.empty:
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"\nEngagement Stats:")
            print(f"  Total likes: {df['like_count'].sum():,}")
            print(f"  Total retweets: {df['retweet_count'].sum():,}")
            print(f"  Total replies: {df['reply_count'].sum():,}")
            print(f"  Avg likes per tweet: {df['like_count'].mean():.2f}")


# ============================================
# METHOD 2: NTSCRAPER (SIMPLE & LIGHTWEIGHT)
# ============================================

class NtscraperMethod:
    """
    Menggunakan ntscraper - Simple dan cepat
    Kelebihan:
    - Tidak perlu login
    - Simple API
    - Cukup stabil
    """
    
    def __init__(self, username):
        self.username = username.replace('@', '')
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def scrape_user_tweets(self, max_tweets=1000):
        """Scrape tweets"""
        from ntscraper import Nitter
        
        print(f"🔍 Scraping tweets from @{self.username} using ntscraper...")
        
        scraper = Nitter(log_level=1, skip_instance_check=False)
        tweets_list = []
        
        try:
            # Get tweets
            tweets = scraper.get_tweets(self.username, mode='user', number=max_tweets)
            
            for tweet in tqdm(tweets['tweets'], desc="Processing tweets"):
                tweet_data = {
                    'tweet_id': None,  # ntscraper tidak provide ID
                    'date': tweet['date'],
                    'username': self.username,
                    'content': tweet['text'],
                    'like_count': tweet['stats']['likes'],
                    'retweet_count': tweet['stats']['retweets'],
                    'reply_count': tweet['stats']['comments'],
                    'quote_count': tweet['stats'].get('quotes', 0),
                    'tweet_url': tweet['link'],
                    'is_reply': 'replying to' in tweet['text'].lower(),
                }
                
                tweets_list.append(tweet_data)
            
            df = pd.DataFrame(tweets_list)
            
            if not df.empty:
                filename = f"{self.data_dir}/{self.username}_tweets_ntscraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ Saved {len(df)} tweets to {filename}")
                self._print_summary(df)
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return pd.DataFrame()
    
    def _print_summary(self, df):
        """Print summary"""
        if not df.empty:
            print("\n📊 Summary Statistics:")
            print(f"Total tweets: {len(df)}")
            print(f"Total likes: {df['like_count'].sum():,}")
            print(f"Total retweets: {df['retweet_count'].sum():,}")
            print(f"Avg engagement: {(df['like_count'] + df['retweet_count']).mean():.2f}")


# ============================================
# METHOD 3: SELENIUM (FALLBACK - SLOW BUT RELIABLE)
# ============================================

class SeleniumMethod:
    """
    Menggunakan Selenium - Browser automation
    Kelebihan:
    - Paling reliable (selama Twitter website masih accessible)
    - Bisa scrape semua data yang visible
    
    Kekurangan:
    - Lambat
    - Perlu browser driver
    
    Install:
    pip install selenium webdriver-manager
    """
    
    def __init__(self, username):
        self.username = username.replace('@', '')
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def scrape_user_tweets(self, max_tweets=100, headless=True):
        """
        Scrape menggunakan Selenium
        Note: Lebih lambat tapi reliable
        """
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import time
        
        print(f"🔍 Scraping tweets from @{self.username} using Selenium...")
        print("⚠️ This method is slower but more reliable")
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        tweets_list = []
        
        try:
            # Navigate to profile
            url = f"https://twitter.com/{self.username}"
            driver.get(url)
            time.sleep(3)
            
            # Scroll dan collect tweets
            last_height = driver.execute_script("return document.body.scrollHeight")
            collected = 0
            
            while collected < max_tweets:
                # Find tweet elements
                tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                for tweet in tweets:
                    if collected >= max_tweets:
                        break
                    
                    try:
                        # Extract data (basic extraction)
                        text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_element.text
                        
                        # Get timestamp
                        time_element = tweet.find_element(By.CSS_SELECTOR, 'time')
                        timestamp = time_element.get_attribute('datetime')
                        
                        tweet_data = {
                            'date': timestamp,
                            'username': self.username,
                            'content': text,
                            'tweet_url': url,
                        }
                        
                        tweets_list.append(tweet_data)
                        collected += 1
                        
                    except Exception as e:
                        continue
                
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if reached bottom
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
                print(f"  Collected {collected} tweets...")
            
            driver.quit()
            
            df = pd.DataFrame(tweets_list)
            
            if not df.empty:
                filename = f"{self.data_dir}/{self.username}_tweets_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"✅ Saved {len(df)} tweets to {filename}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error: {e}")
            driver.quit()
            return pd.DataFrame()


# ============================================
# MAIN EXECUTION
# ============================================

async def main():
    TARGET_USERNAME = "IndoPopBase"
    MAX_TWEETS = 500
    
    print("="*70)
    print("🐦 TWITTER SCRAPER - MULTIPLE METHODS")
    print("="*70)
    
    # Method 1: twscrape (RECOMMENDED - tapi perlu setup account)
    print("\n📌 METHOD 1: twscrape (RECOMMENDED)")
    print("-" * 70)
    print("⚠️ Note: Perlu setup Twitter account dulu (gunakan dummy account)")
    print("Uncomment code di setup_account() untuk menggunakan method ini\n")
    
    # Uncomment jika sudah setup account
    # try:
    #     scraper_tw = TwscrapeMethod(TARGET_USERNAME)
    #     df_tweets = await scraper_tw.scrape_user_tweets(max_tweets=MAX_TWEETS)
    #     df_mentions = await scraper_tw.scrape_mentions(max_tweets=MAX_TWEETS)
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    # Method 2: ntscraper (SIMPLE - tidak perlu login)
    print("\n📌 METHOD 2: ntscraper (SIMPLE & FREE)")
    print("-" * 70)
    
    try:
        scraper_nt = NtscraperMethod(TARGET_USERNAME)
        df_tweets_nt = scraper_nt.scrape_user_tweets(max_tweets=MAX_TWEETS)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: Selenium (FALLBACK - slow but reliable)
    print("\n\n📌 METHOD 3: Selenium (SLOW BUT RELIABLE)")
    print("-" * 70)
    print("⚠️ Use this if other methods fail")
    print("Uncomment to use:\n")
    
    # Uncomment untuk menggunakan Selenium
    # try:
    #     scraper_sel = SeleniumMethod(TARGET_USERNAME)
    #     df_tweets_sel = scraper_sel.scrape_user_tweets(max_tweets=100, headless=True)
    # except Exception as e:
    #     print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Scraping completed!")
    print("📁 Check the 'data/' folder for CSV files")
    print("="*70)
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. BEST: twscrape (perlu setup dummy Twitter account)")
    print("2. GOOD: ntscraper (no login required, tapi terbatas)")
    print("3. FALLBACK: Selenium (slow but always works)")
    print("\n4. Untuk production: Gunakan twscrape dengan multiple accounts")
    print("5. Untuk testing cepat: Gunakan ntscraper")


if __name__ == "__main__":
    # Run async function
    asyncio.run(main())