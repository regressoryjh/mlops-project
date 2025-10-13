"""
ENHANCED TWITTER SCRAPER V3 - FULL ENGAGEMENT ANALYSIS
Features:
- Collects tweets DURING scrolling (no receding)
- Auto-expands full text (clicks "Show more" safely)
- Cookie-based persistent login
- Optional no-login preview mode
- FULL ENGAGEMENT ANALYSIS: Scrapes replies & quotes for each tweet

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
import re

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
        Click 'Show more' WITHOUT opening new page
        
        Args:
            tweet_elem: Tweet element
        
        Returns:
            str: Full tweet text
        """
        try:
            # Find "Show more" or "Read more" buttons
            # Use more specific selector to avoid clicking wrong elements
            show_more_elements = tweet_elem.find_elements(
                By.XPATH, 
                ".//div[@data-testid='tweetText']//span[contains(text(), 'Show more') or contains(text(), 'Show') or contains(text(), 'Read more')]"
            )
            
            for elem in show_more_elements:
                try:
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    time.sleep(0.3)
                    
                    # Click using JavaScript to prevent navigation
                    # This ensures it expands inline instead of opening new page
                    self.driver.execute_script("""
                        var elem = arguments[0];
                        elem.click();
                        // Prevent any default navigation behavior
                        event.preventDefault();
                        event.stopPropagation();
                    """, elem)
                    
                    time.sleep(0.5)
                    break
                except:
                    continue
        except:
            pass
        
        # Extract text after expansion
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
                        label = label.lower()
                        
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
            
            # Get view count
            view_count = 0
            try:
                analytics = tweet_elem.find_elements(By.CSS_SELECTOR, 'a[href*="/analytics"]')
                if analytics:
                    view_label = analytics[0].get_attribute('aria-label')
                    if view_label:
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
    
    def scrape_tweet_replies(self, tweet_url, max_replies=200, max_scrolls=30):
        """
        Scrape replies/comments for a specific tweet
        
        Args:
            tweet_url: Full tweet URL
            max_replies: Target number of replies
            max_scrolls: Max scrolls
        
        Returns:
            list: List of reply data dicts
        """
        print(f"\n   💬 Scraping replies for tweet...")
        
        # Save current URL and scroll position
        original_url = self.driver.current_url
        original_scroll = self.driver.execute_script("return window.pageYOffset;")
        
        try:
            # Navigate to tweet
            self.driver.get(tweet_url)
            time.sleep(3)
            
            # Reset collection for this tweet
            temp_collected_ids = set()
            replies_data = []
            
            scrolls = 0
            no_new_count = 0
            last_count = 0
            
            while scrolls < max_scrolls and len(replies_data) < max_replies:
                # Find all tweet elements (original + replies)
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                for tweet_elem in tweet_elements:
                    if len(replies_data) >= max_replies:
                        break
                    
                    try:
                        # Get tweet URL
                        try:
                            time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                            reply_url = time_elem.find_element(By.XPATH, './..').get_attribute('href')
                        except:
                            continue
                        
                        # Skip original tweet and duplicates
                        if reply_url == tweet_url or reply_url in temp_collected_ids:
                            continue
                        
                        temp_collected_ids.add(reply_url)
                        
                        # Extract reply data
                        # Temporarily bypass the collected_tweet_ids check
                        original_ids = self.collected_tweet_ids.copy()
                        self.collected_tweet_ids = set()
                        
                        reply_data = self.extract_single_tweet(tweet_elem)
                        
                        self.collected_tweet_ids = original_ids
                        
                        if reply_data:
                            reply_data['reply_to'] = tweet_url
                            replies_data.append(reply_data)
                    
                    except:
                        continue
                
                # Check progress
                current_count = len(replies_data)
                if current_count == last_count:
                    no_new_count += 1
                else:
                    no_new_count = 0
                
                if no_new_count >= 3:
                    break
                
                last_count = current_count
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 2.5))
                scrolls += 1
            
            print(f"      ✅ Collected {len(replies_data)} replies")
            
            # Return to original page - try back button first
            try:
                self.driver.execute_script("window.history.back();")
                time.sleep(2)
                
                # If URL didn't change, navigate manually
                if self.driver.current_url != original_url:
                    self.driver.get(original_url)
                    time.sleep(2)
                
                # Restore scroll position
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            except:
                # Fallback: navigate directly
                self.driver.get(original_url)
                time.sleep(2)
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            
            return replies_data
        
        except Exception as e:
            print(f"      ⚠️ Error scraping replies: {e}")
            # Try to go back anyway
            try:
                self.driver.get(original_url)
                time.sleep(2)
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            except:
                pass
            return []
    
    def scrape_tweet_quotes(self, tweet_url, max_quotes=200, max_scrolls=30):
        """
        Scrape quote tweets for a specific tweet
        
        Args:
            tweet_url: Full tweet URL
            max_quotes: Target number of quotes
            max_scrolls: Max scrolls
        
        Returns:
            list: List of quote tweet data dicts
        """
        print(f"\n   🔁 Scraping quotes for tweet...")
        
        # Save current state
        original_url = self.driver.current_url
        original_scroll = self.driver.execute_script("return window.pageYOffset;")
        
        try:
            # Navigate to quotes page
            quotes_url = f"{tweet_url}/retweets/with_comments"
            self.driver.get(quotes_url)
            time.sleep(3)
            
            # Reset collection
            temp_collected_ids = set()
            quotes_data = []
            
            scrolls = 0
            no_new_count = 0
            last_count = 0
            
            while scrolls < max_scrolls and len(quotes_data) < max_quotes:
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                
                for tweet_elem in tweet_elements:
                    if len(quotes_data) >= max_quotes:
                        break
                    
                    try:
                        # Get quote tweet URL
                        try:
                            time_elem = tweet_elem.find_element(By.CSS_SELECTOR, 'time')
                            quote_url = time_elem.find_element(By.XPATH, './..').get_attribute('href')
                        except:
                            continue
                        
                        if quote_url in temp_collected_ids:
                            continue
                        
                        temp_collected_ids.add(quote_url)
                        
                        # Extract quote data
                        original_ids = self.collected_tweet_ids.copy()
                        self.collected_tweet_ids = set()
                        
                        quote_data = self.extract_single_tweet(tweet_elem)
                        
                        self.collected_tweet_ids = original_ids
                        
                        if quote_data:
                            quote_data['quote_of'] = tweet_url
                            quotes_data.append(quote_data)
                    
                    except:
                        continue
                
                # Check progress
                current_count = len(quotes_data)
                if current_count == last_count:
                    no_new_count += 1
                else:
                    no_new_count = 0
                
                if no_new_count >= 3:
                    break
                
                last_count = current_count
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 2.5))
                scrolls += 1
            
            print(f"      ✅ Collected {len(quotes_data)} quote tweets")
            
            # Return to original page
            try:
                self.driver.execute_script("window.history.back();")
                time.sleep(2)
                
                if self.driver.current_url != original_url:
                    self.driver.get(original_url)
                    time.sleep(2)
                
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            except:
                self.driver.get(original_url)
                time.sleep(2)
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            
            return quotes_data
        
        except Exception as e:
            print(f"      ⚠️ Error scraping quotes: {e}")
            try:
                self.driver.get(original_url)
                time.sleep(2)
                self.driver.execute_script(f"window.scrollTo(0, {original_scroll});")
                time.sleep(1)
            except:
                pass
            return []
    
    def scrape_with_engagement_analysis(self, username, max_tweets=200, max_replies_per_tweet=50,
                                         max_quotes_per_tweet=50, max_scrolls_main=30):
        """
        FULL ENGAGEMENT ANALYSIS:
        1. Scrape user's recent tweets
        2. For each tweet, scrape ALL replies
        3. For each tweet, scrape ALL quote tweets
        
        Perfect for understanding account's reach and engagement!
        
        Args:
            username: Twitter username
            max_tweets: Number of original tweets to analyze
            max_replies_per_tweet: Max replies to scrape per tweet
            max_quotes_per_tweet: Max quotes to scrape per tweet
            max_scrolls_main: Max scrolls for main profile
        
        Returns:
            dict: {
                'original_tweets': DataFrame,
                'all_replies': DataFrame,
                'all_quotes': DataFrame
            }
        """
        username = username.replace('@', '')
        
        print("\n" + "="*70)
        print(f"📊 FULL ENGAGEMENT ANALYSIS: @{username}")
        print("="*70)
        print(f"\n📋 Plan:")
        print(f"   1. Scrape {max_tweets} recent tweets from @{username}")
        print(f"   2. For each tweet → scrape up to {max_replies_per_tweet} replies")
        print(f"   3. For each tweet → scrape up to {max_quotes_per_tweet} quote tweets")
        print(f"\n   ⚠️ This will take a while! Estimated time: {max_tweets * 2} minutes")
        print("="*70)
        
        # Step 1: Get original tweets
        print("\n" + "="*70)
        print("STEP 1: Scraping original tweets")
        print("="*70)
        
        df_original = self.scrape_by_username(
            username=username,
            max_tweets=max_tweets,
            max_scrolls=max_scrolls_main,
            allow_no_login=True
        )
        
        if df_original.empty:
            print("❌ No original tweets found. Aborting.")
            return {
                'original_tweets': pd.DataFrame(),
                'all_replies': pd.DataFrame(),
                'all_quotes': pd.DataFrame()
            }
        
        print(f"\n✅ Found {len(df_original)} original tweets")
        
        # Step 2 & 3: Get replies and quotes for each tweet
        print("\n" + "="*70)
        print(f"STEP 2 & 3: Scraping engagement for {len(df_original)} tweets")
        print("="*70)
        
        all_replies = []
        all_quotes = []
        
        for idx, row in enumerate(df_original.itertuples(), 1):
            tweet_url = row.tweet_url
            
            print(f"\n[{idx}/{len(df_original)}] Processing: {tweet_url}")
            print(f"   Original engagement: 💙{row.like_count} 🔁{row.retweet_count} 💬{row.reply_count}")
            
            # Scrape replies
            replies = self.scrape_tweet_replies(
                tweet_url=tweet_url,
                max_replies=max_replies_per_tweet,
                max_scrolls=30
            )
            all_replies.extend(replies)
            
            # Scrape quotes
            quotes = self.scrape_tweet_quotes(
                tweet_url=tweet_url,
                max_quotes=max_quotes_per_tweet,
                max_scrolls=30
            )
            all_quotes.extend(quotes)
            
            print(f"   📊 Collected: {len(replies)} replies, {len(quotes)} quotes")
            
            # Small delay between tweets to avoid rate limiting
            if idx < len(df_original):
                time.sleep(random.uniform(2, 4))
        
        # Convert to DataFrames
        df_replies = pd.DataFrame(all_replies) if all_replies else pd.DataFrame()
        df_quotes = pd.DataFrame(all_quotes) if all_quotes else pd.DataFrame()
        
        # Process dataframes
        if not df_replies.empty:
            df_replies['total_engagement'] = df_replies['like_count'] + df_replies['retweet_count'] + df_replies['reply_count']
            if 'date' in df_replies.columns:
                df_replies['date'] = pd.to_datetime(df_replies['date'], errors='coerce')
        
        if not df_quotes.empty:
            df_quotes['total_engagement'] = df_quotes['like_count'] + df_quotes['retweet_count'] + df_quotes['reply_count']
            if 'date' in df_quotes.columns:
                df_quotes['date'] = pd.to_datetime(df_quotes['date'], errors='coerce')
        
        # Save all data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save original tweets
        original_file = f"{self.data_dir}/{username}_original_tweets_{timestamp}.csv"
        df_original.to_csv(original_file, index=False, encoding='utf-8')
        print(f"\n✅ Saved {len(df_original)} original tweets to {original_file}")
        
        # Save replies
        if not df_replies.empty:
            replies_file = f"{self.data_dir}/{username}_all_replies_{timestamp}.csv"
            df_replies.to_csv(replies_file, index=False, encoding='utf-8')
            print(f"✅ Saved {len(df_replies)} replies to {replies_file}")
        
        # Save quotes
        if not df_quotes.empty:
            quotes_file = f"{self.data_dir}/{username}_all_quotes_{timestamp}.csv"
            df_quotes.to_csv(quotes_file, index=False, encoding='utf-8')
            print(f"✅ Saved {len(df_quotes)} quote tweets to {quotes_file}")
        
        # Print summary
        self._print_engagement_summary(df_original, df_replies, df_quotes)
        
        return {
            'original_tweets': df_original,
            'all_replies': df_replies,
            'all_quotes': df_quotes
        }
    
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
    
    def _print_engagement_summary(self, df_original, df_replies, df_quotes):
        """Print engagement analysis summary"""
        print("\n" + "="*70)
        print("📊 ENGAGEMENT ANALYSIS SUMMARY")
        print("="*70)
        
        print(f"\n📈 Original Tweets: {len(df_original)}")
        print(f"💬 Total Replies Collected: {len(df_replies)}")
        print(f"🔁 Total Quote Tweets Collected: {len(df_quotes)}")
        print(f"🎯 Total Engagement Data Points: {len(df_replies) + len(df_quotes)}")
        
        if not df_original.empty:
            print(f"\n💙 Original Tweets Stats:")
            print(f"   Avg Likes: {df_original['like_count'].mean():.0f}")
            print(f"   Avg Retweets: {df_original['retweet_count'].mean():.0f}")
            print(f"   Avg Replies: {df_original['reply_count'].mean():.0f}")
        
        if not df_replies.empty:
            print(f"\n💬 Replies Stats:")
            print(f"   Avg replies per tweet: {len(df_replies) / len(df_original):.1f}")
            most_replied = df_replies.groupby('reply_to').size().sort_values(ascending=False)
            if len(most_replied) > 0:
                print(f"   Most replied tweet got: {most_replied.iloc[0]} replies")
                
            # Top repliers
            top_repliers = df_replies['username'].value_counts().head(3)
            print(f"\n   🔥 Top repliers:")
            for user, count in top_repliers.items():
                print(f"      @{user}: {count} replies")
        
        if not df_quotes.empty:
            print(f"\n🔁 Quote Tweets Stats:")
            print(f"   Avg quotes per tweet: {len(df_quotes) / len(df_original):.1f}")
            most_quoted = df_quotes.groupby('quote_of').size().sort_values(ascending=False)
            if len(most_quoted) > 0:
                print(f"   Most quoted tweet got: {most_quoted.iloc[0]} quotes")
            
            # Top quoters
            top_quoters = df_quotes['username'].value_counts().head(3)
            print(f"\n   🔥 Top quoters:")
            for user, count in top_quoters.items():
                print(f"      @{user}: {count} quotes")
        
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
    print("🐦 ENHANCED TWITTER SCRAPER V3 - FULL ENGAGEMENT ANALYSIS")
    print("="*70)
    print("\n✨ Features:")
    print("   ✅ Collects tweets DURING scrolling (no receding!)")
    print("   ✅ Expands full text (auto-clicks 'Show more' safely)")
    print("   ✅ Cookie-based persistent login")
    print("   ✅ Optional no-login preview mode")
    print("   ✅ Full engagement analysis (replies + quotes per tweet)")
    print()
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    TARGET_USERNAME = "barengwarga"  # Target Twitter username (without @)
    HEADLESS = False  # Set True after first successful login
    USE_COOKIES = True  # Use cookie-based login
    ALLOW_NO_LOGIN = True  # Allow preview without login
    ACCOUNT_NAME = "default"  # For multiple accounts
    
    # Choose scraping mode
    SCRAPING_MODE = "engagement_analysis"  # Options: "simple", "engagement_analysis", "search"
    
    # Simple mode settings
    MAX_TWEETS = 100
    MAX_SCROLLS = 50
    
    # Engagement analysis mode settings
    ANALYSIS_MAX_TWEETS = 100  # Number of original tweets to analyze
    ANALYSIS_REPLIES_PER_TWEET = 30  # Max replies per tweet
    ANALYSIS_QUOTES_PER_TWEET = 30  # Max quotes per tweet
    
    # Search mode settings
    SEARCH_QUERY = "@barengwarga"  # or "#kpop" or "BTS"
    SEARCH_TYPE = "latest"  # or "top"
    
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
    # SCRAPING MODES
    # ========================================
    
    try:
        if SCRAPING_MODE == "engagement_analysis":
            # ========================================
            # MODE 1: FULL ENGAGEMENT ANALYSIS
            # ========================================
            print("\n🎯 Running FULL ENGAGEMENT ANALYSIS mode")
            print("   This will scrape:")
            print(f"   • {ANALYSIS_MAX_TWEETS} original tweets")
            print(f"   • Up to {ANALYSIS_REPLIES_PER_TWEET} replies per tweet")
            print(f"   • Up to {ANALYSIS_QUOTES_PER_TWEET} quotes per tweet")
            print()
            
            results = scraper.scrape_with_engagement_analysis(
                username=TARGET_USERNAME,
                max_tweets=ANALYSIS_MAX_TWEETS,
                max_replies_per_tweet=ANALYSIS_REPLIES_PER_TWEET,
                max_quotes_per_tweet=ANALYSIS_QUOTES_PER_TWEET,
                max_scrolls_main=30
            )
            
            # Access results
            df_original = results['original_tweets']
            df_replies = results['all_replies']
            df_quotes = results['all_quotes']
            
            # You can now analyze:
            # - Which tweets got most engagement
            # - What people are saying in replies
            # - What people quote with
            # - Sentiment analysis on replies/quotes
            # - Top engagers/fans
            
            print("\n📊 Analysis Ideas:")
            print("   • Check df_replies['content'] for sentiment analysis")
            print("   • Group by 'reply_to' to see which tweets got most discussion")
            print("   • Check df_quotes['username'].value_counts() for top quoters")
            print("   • Compare engagement metrics across tweets")
        
        elif SCRAPING_MODE == "simple":
            # ========================================
            # MODE 2: SIMPLE SCRAPING
            # ========================================
            print("\n📝 Running SIMPLE mode")
            print(f"   Scraping {MAX_TWEETS} tweets from @{TARGET_USERNAME}")
            print()
            
            df_tweets = scraper.scrape_by_username(
                username=TARGET_USERNAME,
                max_tweets=MAX_TWEETS,
                max_scrolls=MAX_SCROLLS,
                allow_no_login=ALLOW_NO_LOGIN
            )
            
            if not df_tweets.empty:
                print(f"\n✅ Successfully collected {len(df_tweets)} tweets")
        
        elif SCRAPING_MODE == "search":
            # ========================================
            # MODE 3: SEARCH MODE
            # ========================================
            print("\n🔍 Running SEARCH mode")
            print(f"   Query: {SEARCH_QUERY}")
            print(f"   Type: {SEARCH_TYPE}")
            print()
            
            df_search = scraper.scrape_by_search(
                query=SEARCH_QUERY,
                max_tweets=MAX_TWEETS,
                max_scrolls=MAX_SCROLLS,
                search_type=SEARCH_TYPE,
                allow_no_login=ALLOW_NO_LOGIN
            )
            
            if not df_search.empty:
                print(f"\n✅ Successfully collected {len(df_search)} tweets")
        
        else:
            print(f"\n❌ Unknown scraping mode: {SCRAPING_MODE}")
            print("   Valid modes: 'simple', 'engagement_analysis', 'search'")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # ========================================
    # Cleanup
    # ========================================
    
    scraper.close()
    
    print("\n" + "="*70)
    print("✅ SCRAPING COMPLETED!")
    print("="*70)
    print(f"\n📁 Files saved in: ./data/")
    
    print("\n💡 Tips:")
    print("   • First run: Manual login (saved for future)")
    print("   • Next runs: Fully automated")
    print("   • Use ALLOW_NO_LOGIN=True for quick previews")
    print("   • Tweets are collected during scrolling (no loss!)")
    print("   • Use 'engagement_analysis' mode for deep insights")
    
    print("\n🎯 What's Next:")
    print("   • Analyze sentiment in replies")
    print("   • Find most engaging content types")
    print("   • Identify top fans/engagers")
    print("   • Track conversation topics")
    print("   • Build ML models with this data")
    
    print("\n🚀 Happy Scraping!")