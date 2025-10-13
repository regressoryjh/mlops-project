"""
SELENIUM SCRAPER WITH COOKIE SESSION
Solves automation problem by saving login cookies!

How it works:
1. First run: Login manually, cookies are saved
2. Next runs: Cookies loaded automatically (NO MANUAL LOGIN!)
3. Perfect for ML pipelines!

Install:
pip install selenium webdriver-manager pandas tqdm

Usage:
python selenium_scraper_cookies.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
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
import random
import pickle
import json

class CookieTwitterScraper:
    def __init__(self, headless=False):
        """
        Initialize scraper with cookie support
        
        Args:
            headless: Run in background
        """
        self.headless = headless
        self.data_dir = 'data'
        self.cookies_dir = 'cookies'
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        self.cookies_file = os.path.join(self.cookies_dir, 'twitter_cookies.pkl')
        self.driver = None
        self.logged_in = False
        
        # Rate limiting
        self.scroll_delay = (2, 4)
    
    def setup_driver(self):
        """Setup Chrome driver"""
        print("🔧 Setting up Chrome driver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
            print("   Running in headless mode")
        else:
            print("   Browser window will be visible")
        
        # Anti-detection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Important for persistent login
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove automation flags
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver ready!")
    
    def save_cookies(self):
        """Save cookies to file"""
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"   💾 Cookies saved to {self.cookies_file}")
    
    def load_cookies(self):
        """Load cookies from file"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                # Navigate to Twitter first
                self.driver.get("https://twitter.com")
                time.sleep(2)
                
                # Load cookies
                for cookie in cookies:
                    # Fix cookie format if needed
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        continue
                
                # Refresh to apply cookies
                self.driver.refresh()
                time.sleep(3)
                
                print("   ✅ Cookies loaded successfully")
                return True
            except Exception as e:
                print(f"   ⚠️ Could not load cookies: {e}")
                return False
        else:
            print("   ℹ️ No saved cookies found")
            return False
    
    def check_logged_in(self):
        """Check if logged in"""
        try:
            # Check URL
            current_url = self.driver.current_url.lower()
            
            # If on home/timeline, likely logged in
            if 'home' in current_url or (current_url == 'https://twitter.com/' or current_url == 'https://x.com/'):
                # Double check by looking for compose button
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')
                    return True
                except:
                    pass
                
                # Or check for timeline
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '[data-testid="primaryColumn"]')
                    return True
                except:
                    pass
            
            return False
        except:
            return False
    
    def login_with_cookies_or_manual(self, account_name="default"):
        """
        Login using cookies OR manual login (one-time setup)
        
        Args:
            account_name: Name for this login session
        
        Returns:
            bool: True if logged in
        """
        print("\n🔐 LOGIN PROCESS")
        print("="*70)
        
        # Update cookies file path with account name
        self.cookies_file = os.path.join(self.cookies_dir, f'twitter_cookies_{account_name}.pkl')
        
        # Try loading existing cookies
        if self.load_cookies():
            print("   🔍 Checking if cookies are valid...")
            
            # Navigate to home to check
            self.driver.get("https://twitter.com/home")
            time.sleep(5)
            
            if self.check_logged_in():
                print("   ✅ Logged in with saved cookies!")
                print("   🎉 NO MANUAL LOGIN NEEDED!")
                self.logged_in = True
                return True
            else:
                print("   ⚠️ Cookies expired or invalid")
        
        # Cookies failed, need manual login
        print("\n" + "="*70)
        print("📱 MANUAL LOGIN REQUIRED (ONE-TIME SETUP)")
        print("="*70)
        print("\n⚠️ This is needed ONLY ONCE!")
        print("   After you login, cookies will be saved.")
        print("   Future runs will login automatically (no manual steps)!")
        print("\n📝 Instructions:")
        print("   1. Browser window will open")
        print("   2. Login to Twitter/X manually")
        print("   3. Complete any verification (captcha, 2FA, etc)")
        print("   4. Wait until you see your Twitter homepage")
        print("   5. Script will auto-detect and save cookies")
        print("\n⏰ You have 120 seconds...")
        print("="*70)
        
        # Navigate to login page
        self.driver.get("https://twitter.com/i/flow/login")
        
        # Wait for manual login
        login_timeout = 120  # 2 minutes
        start_time = time.time()
        
        while (time.time() - start_time) < login_timeout:
            # Check every 5 seconds
            time.sleep(5)
            
            if self.check_logged_in():
                print("\n   ✅ Login detected!")
                print("   💾 Saving cookies for future use...")
                
                # Save cookies
                self.save_cookies()
                
                print("\n   🎉 SUCCESS! Cookies saved!")
                print("   ℹ️ Next time you run this script, it will login automatically!")
                self.logged_in = True
                return True
            
            elapsed = int(time.time() - start_time)
            remaining = login_timeout - elapsed
            print(f"   ⏳ Waiting for login... ({remaining}s remaining)", end='\r')
        
        print("\n   ❌ Login timeout")
        return False
    
    def scrape_tweets(self, username, max_tweets=500, max_scrolls=50):
        """
        Scrape tweets (fully automated after first login!)
        
        Args:
            username: Twitter username
            max_tweets: Target tweets
            max_scrolls: Max scrolls
        """
        username = username.replace('@', '')
        
        print("\n" + "="*70)
        print(f"🔍 SCRAPING @{username}")
        print("="*70)
        
        if not self.logged_in:
            print("⚠️ Not logged in - limited results expected")
        else:
            print("✅ Logged in - full scraping capability!")
        
        try:
            # Navigate to profile
            url = f"https://twitter.com/{username}"
            print(f"\n📍 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Check for login wall
            if "login" in self.driver.current_url.lower():
                print("\n❌ Login required!")
                return pd.DataFrame()
            
            print("✅ Page loaded")
            
            # Scroll and collect
            print(f"\n   📜 Scrolling to collect tweets (target: {max_tweets})...")
            scrolls = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            no_change = 0
            
            while scrolls < max_scrolls:
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(self.scroll_delay[0], self.scroll_delay[1]))
                
                # Count tweets
                current_tweets = len(self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                
                # Check height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    no_change += 1
                    if no_change >= 3:
                        print(f"\n   ✅ Reached end at {current_tweets} tweets")
                        break
                else:
                    no_change = 0
                
                last_height = new_height
                scrolls += 1
                
                if current_tweets >= max_tweets:
                    print(f"\n   ✅ Target reached: {current_tweets} tweets")
                    break
                
                print(f"   Scroll {scrolls}/{max_scrolls} - {current_tweets} tweets", end='\r')
            
            # Extract tweets
            print(f"\n\n   📝 Extracting tweet data...")
            tweets_df = self._extract_tweets(username)
            
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
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _extract_tweets(self, username):
        """Extract tweets"""
        tweets_list = []
        seen_urls = set()
        
        tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        print(f"   Found {len(tweet_elements)} tweet elements")
        
        for tweet_elem in tqdm(tweet_elements, desc="   Processing"):
            try:
                # Text
                try:
                    text_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    text = text_elem.text
                except:
                    text = ""
                
                # Time & URL
                try:
                    time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                    timestamp = time_elem.get_attribute('datetime')
                    tweet_url = time_elem.find_element(By.XPATH, './..').get_attribute('href')
                except:
                    timestamp = None
                    tweet_url = None
                
                if not tweet_url or tweet_url in seen_urls:
                    continue
                seen_urls.add(tweet_url)
                
                # Metrics
                def get_count(testid):
                    try:
                        elem = tweet_elem.find_element(By.CSS_SELECTOR, f'[data-testid="{testid}"]')
                        label = elem.get_attribute('aria-label')
                        if label:
                            import re
                            nums = re.findall(r'\d+', label.replace(',', ''))
                            return int(nums[0]) if nums else 0
                    except:
                        pass
                    return 0
                
                tweet_data = {
                    'date': timestamp,
                    'username': username,
                    'content': text,
                    'reply_count': get_count('reply'),
                    'retweet_count': get_count('retweet'),
                    'like_count': get_count('like'),
                    'tweet_url': tweet_url,
                }
                
                tweets_list.append(tweet_data)
            except:
                continue
        
        df = pd.DataFrame(tweets_list)
        
        if not df.empty:
            df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.sort_values('date', ascending=False)
        
        return df
    
    def _print_summary(self, df):
        """Print summary"""
        if df.empty:
            return
        
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"\n📈 Total: {len(df)} tweets")
        
        if 'date' in df.columns and not df['date'].isna().all():
            print(f"📅 Range: {df['date'].min()} to {df['date'].max()}")
        
        print(f"\n💙 Engagement:")
        print(f"   Likes: {df['like_count'].sum():,} (avg: {df['like_count'].mean():.0f})")
        print(f"   Retweets: {df['retweet_count'].sum():,} (avg: {df['retweet_count'].mean():.0f})")
        print(f"   Replies: {df['reply_count'].sum():,} (avg: {df['reply_count'].mean():.0f})")
        
        print(f"\n🔥 Top 3:")
        for _, row in df.nlargest(3, 'total_engagement').iterrows():
            print(f"   💙{row['like_count']:,} 🔁{row['retweet_count']:,} - {row['content'][:50]}...")
        
        print("="*70)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("🐦 TWITTER SCRAPER WITH COOKIE SESSION")
    print("="*70)
    print("\n✨ Perfect for ML Pipelines!")
    print("   ✅ First run: Login manually (one-time)")
    print("   ✅ Future runs: Fully automated (no manual login!)")
    print("   ✅ Cookies saved for persistent session")
    print()
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    TARGET_USERNAME = "IndoPopBase"
    MAX_TWEETS = 200
    MAX_SCROLLS = 50
    HEADLESS = False  # Set True after first successful login
    
    # Account name (untuk multiple accounts, ubah ini)
    ACCOUNT_NAME = "default"  # e.g., "scraper1", "main_account", etc.
    
    # ========================================
    # Run Scraper
    # ========================================
    
    scraper = CookieTwitterScraper(headless=HEADLESS)
    scraper.setup_driver()
    
    # Login (manual first time, automatic after that)
    login_success = scraper.login_with_cookies_or_manual(account_name=ACCOUNT_NAME)
    
    if login_success:
        print("\n🚀 Starting scrape...")
        
        # Scrape tweets
        df_tweets = scraper.scrape_tweets(
            username=TARGET_USERNAME,
            max_tweets=MAX_TWEETS,
            max_scrolls=MAX_SCROLLS
        )
        
        # You can scrape multiple accounts
        # df_mentions = scraper.scrape_tweets("another_account", max_tweets=100)
        
    else:
        print("\n❌ Login failed - cannot scrape")
    
    scraper.close()
    
    print("\n" + "="*70)
    print("✅ DONE!")
    print("="*70)
    
    if login_success:
        print("\n💡 NEXT RUNS:")
        print("   Just run this script again - NO MANUAL LOGIN needed!")
        print("   Cookies will automatically login for you!")
        print("\n🤖 FOR ML PIPELINE:")
        print("   This script can now run fully automated in:")
        print("   - Cron jobs")
        print("   - Airflow DAGs")
        print("   - GitHub Actions")
        print("   - Docker containers")
        print("   Just make sure to copy the 'cookies/' folder!")
    else:
        print("\n💡 TRY AGAIN:")
        print("   Run script again and complete manual login")
        print("   After successful login, it will be automated forever!")