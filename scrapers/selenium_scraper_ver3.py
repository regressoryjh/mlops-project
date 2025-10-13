"""
ENHANCED TWITTER SCRAPER V3
Fixes:
- Virtual scrolling issue (tweets receding)
- Full text extraction (auto-clicks "Show more")
- Better tweet collection strategy
- Option to scrape without login

Install:
pip install selenium webdriver-manager pandas tqdm

Usage:
python twitter_scraper_v3.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import time
import os
from tqdm import tqdm
import random
import pickle

class EnhancedTwitterScraper:
    def __init__(self, headless=False, use_cookies=True):
        """
        Initialize scraper
        
        Args:
            headless: Run in background
            use_cookies: Try to use saved cookies for login
        """
        self.headless = headless
        self.use_cookies = use_cookies
        self.data_dir = 'data/raw'
        self.cookies_dir = 'cookies'
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        self.cookies_file = None
        self.driver = None
        self.logged_in = False
        
        # Collection strategy: Store tweet IDs as we go to avoid duplicates
        self.collected_tweet_ids = set()
        self.collected_tweets_data = []
    
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
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Better performance
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove automation flags
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver ready!")
    
    def save_cookies(self, account_name="default"):
        """Save cookies to file"""
        self.cookies_file = os.path.join(self.cookies_dir, f'twitter_cookies_{account_name}.pkl')
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'wb') as f:
            pickle.dump(cookies, f)
        print(f"   💾 Cookies saved to {self.cookies_file}")
    
    def load_cookies(self, account_name="default"):
        """Load cookies from file"""
        self.cookies_file = os.path.join(self.cookies_dir, f'twitter_cookies_{account_name}.pkl')
        
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                self.driver.get("https://twitter.com")
                time.sleep(2)
                
                for cookie in cookies:
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        continue
                
                self.driver.refresh()
                time.sleep(3)
                
                print("   ✅ Cookies loaded")
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
            current_url = self.driver.current_url.lower()
            
            if 'home' in current_url or current_url in ['https://twitter.com/', 'https://x.com/']:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, '[data-testid="SideNav_NewTweet_Button"]')
                    return True
                except:
                    pass
                
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
        Login using cookies OR manual login
        
        Args:
            account_name: Name for this login session
        
        Returns:
            bool: True if logged in
        """
        print("\n🔐 LOGIN PROCESS")
        print("="*70)
        
        # Try loading existing cookies
        if self.use_cookies and self.load_cookies(account_name):
            print("   🔍 Checking if cookies are valid...")
            
            self.driver.get("https://twitter.com/home")
            time.sleep(5)
            
            if self.check_logged_in():
                print("   ✅ Logged in with saved cookies!")
                self.logged_in = True
                return True
            else:
                print("   ⚠️ Cookies expired or invalid")
        
        # Manual login
        print("\n" + "="*70)
        print("📱 MANUAL LOGIN REQUIRED")
        print("="*70)
        print("\n⚠️ This is needed ONLY ONCE (if using cookies)")
        print("\n📋 Instructions:")
        print("   1. Browser window will open")
        print("   2. Login to Twitter/X manually")
        print("   3. Complete any verification")
        print("   4. Wait until you see your homepage")
        print("   5. Script will auto-detect and save cookies")
        print("\n⏰ You have 120 seconds...")
        print("="*70)
        
        self.driver.get("https://twitter.com/i/flow/login")
        
        login_timeout = 120
        start_time = time.time()
        
        while (time.time() - start_time) < login_timeout:
            time.sleep(5)
            
            if self.check_logged_in():
                print("\n   ✅ Login detected!")
                
                if self.use_cookies:
                    print("   💾 Saving cookies for future use...")
                    self.save_cookies(account_name)
                    print("   🎉 SUCCESS! Next time will be automatic!")
                
                self.logged_in = True
                return True
            
            elapsed = int(time.time() - start_time)
            remaining = login_timeout - elapsed
            print(f"   ⏳ Waiting for login... ({remaining}s remaining)", end='\r')
        
        print("\n   ⏰ Login timeout")
        return False
    
    def try_scrape_without_login(self):
        """Try to scrape without login (preview mode)"""
        print("\n" + "="*70)
        print("🔓 ATTEMPTING NO-LOGIN SCRAPE (Preview Mode)")
        print("="*70)
        print("⚠️ Note: Without login, results may be limited")
        print("   Twitter may show login wall after a few tweets")
        print()
        
        self.logged_in = False
        return True
    
    def expand_tweet_text(self, tweet_elem):
        """
        Click 'Show more' to get full tweet text
        
        Args:
            tweet_elem: Tweet element
        
        Returns:
            str: Full tweet text
        """
        try:
            # Try to find and click "Show more" button
            show_more_buttons = tweet_elem.find_elements(By.XPATH, ".//span[contains(text(), 'Show more') or contains(text(), 'Show')]")
            
            for button in show_more_buttons:
                try:
                    # Scroll button into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.3)
                    
                    # Click button
                    button.click()
                    time.sleep(0.5)
                    break
                except:
                    continue
        except:
            pass
        
        # Now extract the (hopefully expanded) text
        try:
            text_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            return text_elem.text
        except:
            return ""
    
    def extract_single_tweet(self, tweet_elem):
        """
        Extract data from a single tweet element
        
        Args:
            tweet_elem: Selenium WebElement for tweet
        
        Returns:
            dict or None: Tweet data
        """
        try:
            # Get tweet URL first (used as unique ID)
            try:
                time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                timestamp = time_elem.get_attribute('datetime')
                tweet_link = time_elem.find_element(By.XPATH, './..').get_attribute('href')
            except:
                return None
            
            # Skip if already collected
            if tweet_link in self.collected_tweet_ids:
                return None
            
            # Extract username
            try:
                user_elem = tweet_elem.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                user_text = user_elem.text.split('\n')
                username = user_text[1].replace('@', '') if len(user_text) > 1 else 'unknown'
            except:
                username = 'unknown'
            
            # Expand and extract full text
            text = self.expand_tweet_text(tweet_elem)
            
            # Extract metrics
            def get_count(testid):
                try:
                    elem = tweet_elem.find_element(By.CSS_SELECTOR, f'[data-testid="{testid}"]')
                    label = elem.get_attribute('aria-label')
                    if label:
                        # Extract number from label
                        label = label.lower()
                        import re
                        
                        # Handle K, M notation
                        if 'k' in label:
                            nums = re.findall(r'(\d+\.?\d*)\s*k', label)
                            return int(float(nums[0]) * 1000) if nums else 0
                        elif 'm' in label:
                            nums = re.findall(r'(\d+\.?\d*)\s*m', label)
                            return int(float(nums[0]) * 1000000) if nums else 0
                        else:
                            nums = re.findall(r'\d+', label.replace(',', ''))
                            return int(nums[0]) if nums else 0
                except:
                    pass
                return 0
            
            # Get view count (different selector)
            view_count = 0
            try:
                analytics = tweet_elem.find_elements(By.CSS_SELECTOR, 'a[href*="/analytics"]')
                if analytics:
                    view_label = analytics[0].get_attribute('aria-label')
                    if view_label:
                        import re
                        view_label = view_label.lower()
                        if 'k' in view_label:
                            nums = re.findall(r'(\d+\.?\d*)\s*k', view_label)
                            view_count = int(float(nums[0]) * 1000) if nums else 0
                        elif 'm' in view_label:
                            nums = re.findall(r'(\d+\.?\d*)\s*m', view_label)
                            view_count = int(float(nums[0]) * 1000000) if nums else 0
                        else:
                            nums = re.findall(r'\d+', view_label.replace(',', ''))
                            view_count = int(nums[0]) if nums else 0
            except:
                pass
            
            tweet_data = {
                'date': timestamp,
                'username': username,
                'content': text,
                'reply_count': get_count('reply'),
                'retweet_count': get_count('retweet'),
                'like_count': get_count('like'),
                'view_count': view_count,
                'tweet_url': tweet_link,
            }
            
            # Mark as collected
            self.collected_tweet_ids.add(tweet_link)
            
            return tweet_data
        
        except StaleElementReferenceException:
            # Element is no longer in DOM
            return None
        except Exception as e:
            return None
    
    def smart_scroll_and_collect(self, max_tweets=500, max_scrolls=50, filter_username=None):
        """
        Improved scrolling: collect tweets as we scroll to avoid losing them
        
        Args:
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
            filter_username: Only collect tweets from this user (optional)
        
        Returns:
            int: Number of tweets collected
        """
        print(f"\n📜 Smart scrolling and collecting...")
        print(f"   Target: {max_tweets} tweets | Max scrolls: {max_scrolls}")
        
        scrolls = 0
        no_new_tweets_count = 0
        last_collected_count = 0
        
        progress_bar = tqdm(total=max_tweets, desc="   Collecting tweets", unit="tweet")
        
        while scrolls < max_scrolls and len(self.collected_tweets_data) < max_tweets:
            # Find all visible tweet elements
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            
            # Process each visible tweet
            for tweet_elem in tweet_elements:
                if len(self.collected_tweets_data) >= max_tweets:
                    break
                
                tweet_data = self.extract_single_tweet(tweet_elem)
                
                if tweet_data:
                    # Filter by username if specified
                    if filter_username and tweet_data['username'].lower() != filter_username.lower():
                        continue
                    
                    self.collected_tweets_data.append(tweet_data)
                    progress_bar.update(1)
            
            # Check if we collected new tweets
            current_count = len(self.collected_tweets_data)
            if current_count == last_collected_count:
                no_new_tweets_count += 1
            else:
                no_new_tweets_count = 0
            
            # Stop if no new tweets for 3 scrolls
            if no_new_tweets_count >= 3:
                print(f"\n   ⚠️ No new tweets found after 3 scrolls. Stopping.")
                break
            
            last_collected_count = current_count
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Random delay to seem more human
            time.sleep(random.uniform(2, 4))
            
            scrolls += 1
            
            # Show progress
            progress_bar.set_postfix({
                'scroll': f'{scrolls}/{max_scrolls}',
                'collected': current_count
            })
        
        progress_bar.close()
        
        print(f"\n   ✅ Collected {len(self.collected_tweets_data)} unique tweets")
        return len(self.collected_tweets_data)
    
    def scrape_by_username(self, username, max_tweets=500, max_scrolls=50, allow_no_login=True):
        """
        Scrape tweets from a specific username
        
        Args:
            username: Twitter username (without @)
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
            allow_no_login: Allow scraping without login (preview mode)
        """
        username = username.replace('@', '')
        
        print("\n" + "="*70)
        print(f"🐦 SCRAPING @{username}")
        print("="*70)
        
        # Reset collection
        self.collected_tweet_ids = set()
        self.collected_tweets_data = []
        
        # Check login status
        if not self.logged_in and not allow_no_login:
            print("❌ Not logged in and no-login mode disabled")
            return pd.DataFrame()
        
        if not self.logged_in:
            print("⚠️ Running in NO-LOGIN mode (preview)")
            print("   Results may be limited")
        else:
            print("✅ Logged in - full scraping capability")
        
        try:
            # Navigate to profile
            url = f"https://twitter.com/{username}"
            print(f"\n🔗 Navigating to: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Check for login wall
            if "login" in self.driver.current_url.lower():
                if allow_no_login:
                    print("\n⚠️ Login wall detected in no-login mode")
                    print("   Trying to bypass...")
                    # Sometimes refreshing helps
                    self.driver.refresh()
                    time.sleep(3)
                    
                    if "login" in self.driver.current_url.lower():
                        print("❌ Cannot bypass login wall")
                        return pd.DataFrame()
                else:
                    print("❌ Login required!")
                    return pd.DataFrame()
            
            print("✅ Page loaded")
            
            # Scroll and collect
            self.smart_scroll_and_collect(
                max_tweets=max_tweets,
                max_scrolls=max_scrolls,
                filter_username=username
            )
            
            # Convert to DataFrame
            if self.collected_tweets_data:
                df = pd.DataFrame(self.collected_tweets_data)
                
                # Add total engagement
                df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
                
                # Sort by date
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.sort_values('date', ascending=False)
                
                # Save to CSV
                filename = f"{self.data_dir}/{username}_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"\n✅ Saved {len(df)} tweets to {filename}")
                
                self._print_summary(df)
                
                return df
            else:
                print("\n❌ No tweets collected")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def scrape_by_search(self, query, max_tweets=500, max_scrolls=50, search_type="latest", allow_no_login=True):
        """
        Scrape tweets by search query
        
        Args:
            query: Search query (can be hashtag, mention, keyword)
            max_tweets: Target number of tweets
            max_scrolls: Maximum scrolls
            search_type: "latest" or "top" tweets
            allow_no_login: Allow scraping without login
        """
        print("\n" + "="*70)
        print(f"🔍 SEARCHING: {query}")
        print("="*70)
        
        # Reset collection
        self.collected_tweet_ids = set()
        self.collected_tweets_data = []
        
        if not self.logged_in and not allow_no_login:
            print("❌ Not logged in and no-login mode disabled")
            return pd.DataFrame()
        
        if not self.logged_in:
            print("⚠️ Running in NO-LOGIN mode (preview)")
        else:
            print("✅ Logged in")
        
        try:
            from urllib.parse import quote
            
            # Build search URL
            search_filter = "f=live" if search_type == "latest" else "f=top"
            search_url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&{search_filter}"
            
            print(f"\n🔗 Navigating to search...")
            self.driver.get(search_url)
            time.sleep(5)
            
            # Check for login wall
            if "login" in self.driver.current_url.lower():
                if allow_no_login:
                    print("⚠️ Login wall - trying to bypass...")
                    self.driver.refresh()
                    time.sleep(3)
                    
                    if "login" in self.driver.current_url.lower():
                        print("❌ Cannot bypass login wall")
                        return pd.DataFrame()
                else:
                    print("❌ Login required!")
                    return pd.DataFrame()
            
            print("✅ Search page loaded")
            
            # Scroll and collect
            self.smart_scroll_and_collect(
                max_tweets=max_tweets,
                max_scrolls=max_scrolls
            )
            
            # Convert to DataFrame
            if self.collected_tweets_data:
                df = pd.DataFrame(self.collected_tweets_data)
                
                df['total_engagement'] = df['like_count'] + df['retweet_count'] + df['reply_count']
                
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df = df.sort_values('date', ascending=False)
                
                # Save to CSV
                safe_query = query.replace('#', 'hashtag_').replace('@', 'mention_').replace(' ', '_')
                filename = f"{self.data_dir}/{safe_query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"\n✅ Saved {len(df)} tweets to {filename}")
                
                self._print_summary(df)
                
                return df
            else:
                print("\n❌ No tweets collected")
                return pd.DataFrame()
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
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
        
        print(f"\n💙 Engagement:")
        print(f"   Likes: {df['like_count'].sum():,} (avg: {df['like_count'].mean():.0f})")
        print(f"   Retweets: {df['retweet_count'].sum():,} (avg: {df['retweet_count'].mean():.0f})")
        print(f"   Replies: {df['reply_count'].sum():,} (avg: {df['reply_count'].mean():.0f})")
        
        if 'view_count' in df.columns and df['view_count'].sum() > 0:
            print(f"   Views: {df['view_count'].sum():,} (avg: {df['view_count'].mean():.0f})")
        
        print(f"\n🔥 Top 3 Most Engaged:")
        print("-" * 70)
        for _, row in df.nlargest(3, 'total_engagement').iterrows():
            print(f"\n💙 {row['like_count']:,} | 🔁 {row['retweet_count']:,} | 💬 {row['reply_count']:,}")
            content = row['content'][:100] + "..." if len(row['content']) > 100 else row['content']
            print(f"📝 {content}")
            print(f"🔗 {row['tweet_url']}")
        
        print("\n" + "="*70)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("🐦 ENHANCED TWITTER SCRAPER V3")
    print("="*70)
    print("\n✨ New Features:")
    print("   ✅ Collects tweets DURING scrolling (no receding!)")
    print("   ✅ Expands full text (auto-clicks 'Show more')")
    print("   ✅ Cookie-based login (one-time manual)")
    print("   ✅ Optional no-login scraping (preview mode)")
    print("   ✅ Multiple search options")
    print()
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    TARGET_USERNAME = "cursedkidd"
    MAX_TWEETS = 200
    MAX_SCROLLS = 50
    HEADLESS = False  # Set True after first login
    USE_COOKIES = True  # Use cookie-based login
    ALLOW_NO_LOGIN = True  # Allow preview without login
    ACCOUNT_NAME = "default"  # For multiple accounts
    
    # ========================================
    # Initialize Scraper
    # ========================================
    
    scraper = EnhancedTwitterScraper(headless=HEADLESS, use_cookies=USE_COOKIES)
    scraper.setup_driver()
    
    # ========================================
    # Login Strategy
    # ========================================
    
    login_success = False
    
    if USE_COOKIES:
        # Try login with cookies
        login_success = scraper.login_with_cookies_or_manual(account_name=ACCOUNT_NAME)
    
    # If login failed and no-login is allowed, continue anyway
    if not login_success and ALLOW_NO_LOGIN:
        scraper.try_scrape_without_login()
    elif not login_success:
        print("\n❌ Login failed and no-login mode disabled. Exiting.")
        scraper.close()
        exit()
    
    # ========================================
    # SCRAPING EXAMPLES
    # ========================================
    
    # Example 1: Scrape user's tweets
    print("\n" + "="*70)
    print("1️⃣ SCRAPING USER TWEETS")
    print("="*70)
    
    df_tweets = scraper.scrape_by_username(
        username=TARGET_USERNAME,
        max_tweets=MAX_TWEETS,
        max_scrolls=MAX_SCROLLS,
        allow_no_login=ALLOW_NO_LOGIN
    )
    
    # Example 2: Scrape mentions
    print("\n" + "="*70)
    print("2️⃣ SCRAPING MENTIONS")
    print("="*70)
    
    df_mentions = scraper.scrape_by_search(
        query=f"@{TARGET_USERNAME}",
        max_tweets=MAX_TWEETS,
        max_scrolls=MAX_SCROLLS,
        search_type="latest",
        allow_no_login=ALLOW_NO_LOGIN
    )
    
    # Example 3: Scrape hashtag
    # df_hashtag = scraper.scrape_by_search(
    #     query="#kpop",
    #     max_tweets=100,
    #     max_scrolls=30,
    #     search_type="latest",
    #     allow_no_login=ALLOW_NO_LOGIN
    # )
    
    # ========================================
    # Cleanup
    # ========================================
    
    scraper.close()
    
    print("\n" + "="*70)
    print("✅ SCRAPING COMPLETED!")
    print("="*70)
    
    if not df_tweets.empty:
        print(f"\n✅ Successfully collected {len(df_tweets)} tweets")
        print(f"📁 Files saved in: ./data/raw")
    
    print("\n💡 Tips:")
    print("   • First run: Manual login (saved for future)")
    print("   • Next runs: Fully automated")
    print("   • Use ALLOW_NO_LOGIN=True for quick previews")
    print("   • Tweets are collected during scrolling (no loss!)")
    print("\n🚀 Happy Scraping!")