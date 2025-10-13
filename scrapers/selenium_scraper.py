"""
IMPROVED SELENIUM SCRAPER
Features:
- Optional Twitter login (untuk bypass login wall)
- Flexible search (username, mentions, hashtags)
- Better scrolling strategy
- More robust element detection

Install:
pip install selenium webdriver-manager pandas tqdm

Usage:
python selenium_scraper_improved.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import time
import os
from tqdm import tqdm
import json

class ImprovedSeleniumScraper:
    def __init__(self, headless=True, login_required=False):
        """
        Initialize scraper
        
        Args:
            headless: Run in background (True) or show browser (False)
            login_required: Set True if you want to login to Twitter
        """
        self.headless = headless
        self.login_required = login_required
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        self.driver = None
        self.logged_in = False
    
    def setup_driver(self):
        """Setup Chrome driver with better options"""
        print("🔧 Setting up Chrome driver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
            print("   Running in headless mode")
        else:
            print("   Browser window will be visible")
        
        # Better options for stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver ready!")
    
    def login_twitter(self, username, password):
        """
        Login to Twitter (optional but recommended for better scraping)
        
        Args:
            username: Your Twitter username/email
            password: Your Twitter password
        """
        print("\n🔐 Logging in to Twitter...")
        
        try:
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(3)
            
            # Enter username
            print("   Entering username...")
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Enter password
            print("   Entering password...")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            # Check if logged in
            if "home" in self.driver.current_url or self.driver.current_url == "https://twitter.com/":
                print("✅ Successfully logged in!")
                self.logged_in = True
                return True
            else:
                print("❌ Login failed - check credentials")
                return False
        
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def smart_scroll(self, max_scrolls=50, tweets_target=100):
        """
        Improved scrolling strategy
        
        Args:
            max_scrolls: Maximum scrolls
            tweets_target: Stop when this many unique tweets found
        """
        print(f"   Smart scrolling (target: {tweets_target} tweets, max: {max_scrolls} scrolls)...")
        
        scrolls = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        no_change_count = 0
        prev_tweet_count = 0
        
        while scrolls < max_scrolls:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            
            # Check current tweets
            current_tweets = len(self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            
            # Calculate new height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Check if we have enough tweets
            if current_tweets >= tweets_target:
                print(f"\n   ✅ Target reached: {current_tweets} tweets found")
                break
            
            # Check if page height changed
            if new_height == last_height:
                no_change_count += 1
                if no_change_count >= 3:
                    print(f"\n   ⚠️ Reached end of available tweets at {current_tweets} tweets")
                    break
            else:
                no_change_count = 0
            
            # Check if tweet count increased
            if current_tweets == prev_tweet_count:
                # Try scrolling up a bit then down again (sometimes helps)
                self.driver.execute_script("window.scrollBy(0, -500);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            last_height = new_height
            prev_tweet_count = current_tweets
            scrolls += 1
            
            print(f"   Scroll {scrolls}/{max_scrolls} - Found {current_tweets} tweets", end='\r')
        
        print(f"\n   Completed scrolling - Total tweets visible: {current_tweets}")
        return current_tweets
    
    def scrape_by_username(self, username, max_tweets=500, max_scrolls=50):
        """
        Scrape tweets from a specific username
        
        Args:
            username: Twitter username (without @)
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
        """
        username = username.replace('@', '')
        print(f"\n🔍 Scraping tweets from @{username}...")
        print(f"   Target: {max_tweets} tweets")
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to profile
            url = f"https://twitter.com/{username}"
            print(f"   Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Check for login wall
            if "login" in self.driver.current_url:
                print("⚠️ Twitter requires login. Please set login_required=True")
                return pd.DataFrame()
            
            # Smart scroll
            self.smart_scroll(max_scrolls=max_scrolls, tweets_target=max_tweets)
            
            # Extract tweets
            tweets_df = self._extract_tweets(username, filter_username=username)
            
            if not tweets_df.empty:
                filename = f"{self.data_dir}/{username}_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                tweets_df.to_csv(filename, index=False, encoding='utf-8')
                print(f"\n✅ Saved {len(tweets_df)} tweets to {filename}")
                self._print_summary(tweets_df)
            else:
                print("\n❌ No tweets extracted")
            
            return tweets_df
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return pd.DataFrame()
    
    def scrape_by_mention(self, mention, max_tweets=500, max_scrolls=50):
        """
        Scrape tweets that mention a specific account
        
        Args:
            mention: Account to search for (e.g., "IndoPopBase" or "@IndoPopBase")
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
        """
        mention = mention.replace('@', '')
        query = f"@{mention}"
        
        print(f"\n🔍 Scraping tweets mentioning {query}...")
        print(f"   Target: {max_tweets} tweets")
        
        return self._scrape_by_search(query, max_tweets, max_scrolls, filename_prefix=f"{mention}_mentions")
    
    def scrape_by_hashtag(self, hashtag, max_tweets=500, max_scrolls=50):
        """
        Scrape tweets with a specific hashtag
        
        Args:
            hashtag: Hashtag to search (e.g., "kpop" or "#kpop")
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
        """
        hashtag = hashtag.replace('#', '')
        query = f"#{hashtag}"
        
        print(f"\n🔍 Scraping tweets with {query}...")
        print(f"   Target: {max_tweets} tweets")
        
        return self._scrape_by_search(query, max_tweets, max_scrolls, filename_prefix=f"hashtag_{hashtag}")
    
    def scrape_by_keyword(self, keyword, max_tweets=500, max_scrolls=50):
        """
        Scrape tweets containing specific keyword
        
        Args:
            keyword: Keyword to search
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
        """
        print(f"\n🔍 Scraping tweets with keyword: '{keyword}'...")
        print(f"   Target: {max_tweets} tweets")
        
        return self._scrape_by_search(keyword, max_tweets, max_scrolls, filename_prefix=f"keyword_{keyword.replace(' ', '_')}")
    
    def _scrape_by_search(self, query, max_tweets, max_scrolls, filename_prefix):
        """Internal method for search-based scraping"""
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to search
            from urllib.parse import quote
            search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&f=live"
            print(f"   Navigating to search...")
            self.driver.get(search_url)
            time.sleep(5)
            
            # Check for login wall
            if "login" in self.driver.current_url:
                print("⚠️ Twitter requires login. Please set login_required=True")
                return pd.DataFrame()
            
            # Smart scroll
            self.smart_scroll(max_scrolls=max_scrolls, tweets_target=max_tweets)
            
            # Extract tweets
            tweets_df = self._extract_tweets(query)
            
            if not tweets_df.empty:
                filename = f"{self.data_dir}/{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                tweets_df.to_csv(filename, index=False, encoding='utf-8')
                print(f"\n✅ Saved {len(tweets_df)} tweets to {filename}")
                self._print_summary(tweets_df)
            else:
                print("\n❌ No tweets extracted")
            
            return tweets_df
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return pd.DataFrame()
    
    def _extract_tweets(self, source, filter_username=None):
        """Extract tweet data from current page"""
        print("\n   Extracting tweet data...")
        
        tweets_list = []
        seen_urls = set()
        
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        print(f"   Found {len(tweet_elements)} tweet elements")
        
        if len(tweet_elements) == 0:
            print("   ⚠️ No tweets found. Possible reasons:")
            print("      - Login required (try login_required=True)")
            print("      - Rate limited (wait and try again)")
            print("      - Page structure changed")
            return pd.DataFrame()
        
        for tweet_elem in tqdm(tweet_elements, desc="   Processing"):
            try:
                # Extract username
                try:
                    user_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    user_text = user_elem.text.split('\n')
                    username = user_text[1].replace('@', '') if len(user_text) > 1 else 'unknown'
                except:
                    username = 'unknown'
                
                # Filter if needed
                if filter_username and username.lower() != filter_username.lower():
                    continue
                
                # Extract text
                try:
                    text_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    text = text_elem.text
                except:
                    text = ""
                
                # Extract timestamp and URL
                try:
                    time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                    timestamp = time_elem.get_attribute('datetime')
                    tweet_url = time_elem.find_element(By.XPATH, './..').get_attribute('href')
                except:
                    timestamp = None
                    tweet_url = None
                
                # Skip duplicates
                if not tweet_url or tweet_url in seen_urls:
                    continue
                seen_urls.add(tweet_url)
                
                # Extract engagement metrics
                metrics = self._extract_metrics(tweet_elem)
                
                # Store data
                tweet_data = {
                    'date': timestamp,
                    'username': username,
                    'content': text,
                    'reply_count': metrics['replies'],
                    'retweet_count': metrics['retweets'],
                    'like_count': metrics['likes'],
                    'view_count': metrics['views'],
                    'tweet_url': tweet_url,
                }
                
                tweets_list.append(tweet_data)
            
            except Exception as e:
                continue
        
        df = pd.DataFrame(tweets_list)
        
        if not df.empty:
            df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.sort_values('date', ascending=False)
        
        return df
    
    def _extract_metrics(self, tweet_elem):
        """Extract engagement metrics from tweet element"""
        metrics = {'replies': 0, 'retweets': 0, 'likes': 0, 'views': 0}
        
        # Helper function to extract number
        def extract_number(text):
            if not text:
                return 0
            # Handle K, M notation
            text = text.lower()
            multiplier = 1
            if 'k' in text:
                multiplier = 1000
                text = text.replace('k', '')
            elif 'm' in text:
                multiplier = 1000000
                text = text.replace('m', '')
            try:
                number = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
                return int(float(number) * multiplier) if number else 0
            except:
                return 0
        
        try:
            reply_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
            metrics['replies'] = extract_number(reply_elem.get_attribute('aria-label'))
        except:
            pass
        
        try:
            retweet_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
            metrics['retweets'] = extract_number(retweet_elem.get_attribute('aria-label'))
        except:
            pass
        
        try:
            like_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
            metrics['likes'] = extract_number(like_elem.get_attribute('aria-label'))
        except:
            pass
        
        try:
            # Views are sometimes in analytics button
            analytics = tweet_elem.find_elements(By.CSS_SELECTOR, '[href*="/analytics"]')
            if analytics:
                view_text = analytics[0].get_attribute('aria-label')
                metrics['views'] = extract_number(view_text)
        except:
            pass
        
        return metrics
    
    def _print_summary(self, df):
        """Print summary statistics"""
        if df.empty:
            return
        
        print("\n" + "="*70)
        print("📊 SUMMARY STATISTICS")
        print("="*70)
        
        print(f"\n📈 Total Tweets: {len(df)}")
        if 'date' in df.columns and not df['date'].isna().all():
            print(f"📅 Date Range: {df['date'].min()} to {df['date'].max()}")
        
        print(f"\n💙 Engagement Metrics:")
        print(f"   Total Likes: {df['like_count'].sum():,}")
        print(f"   Total Retweets: {df['retweet_count'].sum():,}")
        print(f"   Total Replies: {df['reply_count'].sum():,}")
        
        if 'view_count' in df.columns:
            print(f"   Total Views: {df['view_count'].sum():,}")
        
        print(f"\n📊 Average per Tweet:")
        print(f"   Avg Likes: {df['like_count'].mean():.1f}")
        print(f"   Avg Retweets: {df['retweet_count'].mean():.1f}")
        print(f"   Avg Engagement: {df['total_engagement'].mean():.1f}")
        
        print(f"\n🔥 Top 5 Most Engaged Tweets:")
        print("-" * 70)
        top = df.nlargest(5, 'total_engagement')
        for _, row in top.iterrows():
            if 'date' in row and pd.notna(row['date']):
                print(f"\n📅 {row['date']}")
            print(f"💙 {row['like_count']:,} | 🔁 {row['retweet_count']:,} | 💬 {row['reply_count']:,}")
            content = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
            print(f"📝 {content}")
            if 'tweet_url' in row:
                print(f"🔗 {row['tweet_url']}")
        
        print("\n" + "="*70)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


# ============================================
# MAIN EXECUTION WITH EXAMPLES
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("🐦 IMPROVED SELENIUM SCRAPER")
    print("="*70)
    print("\n📝 Features:")
    print("   ✓ Scrape by username")
    print("   ✓ Scrape by mentions")
    print("   ✓ Scrape by hashtag")
    print("   ✓ Scrape by keyword")
    print("   ✓ Optional Twitter login")
    print()
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    TARGET_USERNAME = "IndoPopBase"
    MAX_TWEETS = 200  # Increased from 100
    MAX_SCROLLS = 50   # Increased from 20
    HEADLESS = True    # Set False to see browser
    
    # Twitter login (OPTIONAL but recommended for better results)
    USE_LOGIN = False  # Set True to use login
    TWITTER_USERNAME = ""  # Your Twitter username/email
    TWITTER_PASSWORD = ""  # Your Twitter password
    
    # ========================================
    # Initialize Scraper
    # ========================================
    
    scraper = ImprovedSeleniumScraper(headless=HEADLESS, login_required=USE_LOGIN)
    
    # Login if required
    if USE_LOGIN and TWITTER_USERNAME and TWITTER_PASSWORD:
        scraper.setup_driver()
        scraper.login_twitter(TWITTER_USERNAME, TWITTER_PASSWORD)
    
    # ========================================
    # EXAMPLE 1: Scrape Account Tweets
    # ========================================
    
    print("\n" + "="*70)
    print("1️⃣ SCRAPING ACCOUNT TWEETS")
    print("="*70)
    
    df_tweets = scraper.scrape_by_username(
        username=TARGET_USERNAME,
        max_tweets=MAX_TWEETS,
        max_scrolls=MAX_SCROLLS
    )
    
    # ========================================
    # EXAMPLE 2: Scrape Mentions
    # ========================================
    
    print("\n\n" + "="*70)
    print("2️⃣ SCRAPING MENTIONS")
    print("="*70)
    
    df_mentions = scraper.scrape_by_mention(
        mention=TARGET_USERNAME,
        max_tweets=MAX_TWEETS,
        max_scrolls=MAX_SCROLLS
    )
    
    # ========================================
    # EXAMPLE 3: Scrape by Hashtag (BONUS)
    # ========================================
    
    # Uncomment to scrape hashtag
    # print("\n\n" + "="*70)
    # print("3️⃣ SCRAPING HASHTAG #KPOP")
    # print("="*70)
    # 
    # df_hashtag = scraper.scrape_by_hashtag(
    #     hashtag="kpop",
    #     max_tweets=100,
    #     max_scrolls=30
    # )
    
    # ========================================
    # EXAMPLE 4: Scrape by Keyword (BONUS)
    # ========================================
    
    # Uncomment to scrape keyword
    # print("\n\n" + "="*70)
    # print("4️⃣ SCRAPING KEYWORD 'BTS'")
    # print("="*70)
    # 
    # df_keyword = scraper.scrape_by_keyword(
    #     keyword="BTS",
    #     max_tweets=100,
    #     max_scrolls=30
    # )
    
    # ========================================
    # Close Browser
    # ========================================
    
    scraper.close()
    
    # ========================================
    # Final Summary
    # ========================================
    
    print("\n\n" + "="*70)
    print("✅ SCRAPING COMPLETED!")
    print("="*70)
    
    if not df_tweets.empty:
        print(f"\n✓ Account tweets: {len(df_tweets)} tweets")
    if not df_mentions.empty:
        print(f"✓ Mentions: {len(df_mentions)} tweets")
    
    print(f"\n📁 Files saved in: ./data/")
    
    print("\n💡 Tips for better results:")
    print("   1. Set USE_LOGIN=True and add your Twitter credentials")
    print("   2. Increase MAX_SCROLLS for more tweets (e.g., 100)")
    print("   3. Set HEADLESS=False to watch the scraping process")
    print("   4. Wait a few minutes between runs to avoid rate limiting")
    
    print("\n🚀 Happy Scraping!")