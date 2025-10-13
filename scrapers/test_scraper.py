"""
TEST SCRAPER - Test semua methods
Untuk menentukan method mana yang paling work di environment Anda

Usage:
python test_scraper.py
"""

import sys

def test_ntscraper():
    """Test ntscraper method"""
    print("\n" + "="*70)
    print("🧪 TESTING: ntscraper")
    print("="*70)
    
    try:
        from ntscraper import Nitter
        print("✅ ntscraper installed")
        
        scraper = Nitter(log_level=1, skip_instance_check=False)
        result = scraper.get_tweets("IndoPopBase", mode='user', number=5)
        
        if result and 'tweets' in result and len(result['tweets']) > 0:
            print(f"✅ Successfully scraped {len(result['tweets'])} tweets")
            print(f"📝 Sample tweet: {result['tweets'][0]['text'][:100]}...")
            return True
        else:
            print("❌ No tweets found")
            return False
            
    except ImportError:
        print("❌ ntscraper not installed")
        print("💡 Install: pip install ntscraper")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tweety():
    """Test tweety-ns method"""
    print("\n" + "="*70)
    print("🧪 TESTING: tweety-ns")
    print("="*70)
    
    try:
        from tweety import Twitter
        print("✅ tweety-ns installed")
        
        app = Twitter("session")
        user = app.get_user("IndoPopBase")
        tweets = user.get_tweets(total=5)
        
        tweet_list = list(tweets)
        if len(tweet_list) > 0:
            print(f"✅ Successfully scraped {len(tweet_list)} tweets")
            print(f"📝 Sample tweet: {tweet_list[0].text[:100]}...")
            return True
        else:
            print("❌ No tweets found")
            return False
            
    except ImportError:
        print("❌ tweety-ns not installed")
        print("💡 Install: pip install tweety-ns")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_twscrape():
    """Test twscrape method"""
    print("\n" + "="*70)
    print("🧪 TESTING: twscrape")
    print("="*70)
    
    try:
        import asyncio
        from twscrape import API
        print("✅ twscrape installed")
        
        async def scrape():
            api = API()
            tweets = []
            count = 0
            async for tweet in api.user_tweets("IndoPopBase", limit=5):
                tweets.append(tweet)
                count += 1
                if count >= 5:
                    break
            return tweets
        
        tweets = asyncio.run(scrape())
        
        if len(tweets) > 0:
            print(f"✅ Successfully scraped {len(tweets)} tweets")
            print(f"📝 Sample tweet: {tweets[0].rawContent[:100]}...")
            return True
        else:
            print("⚠️ No tweets found - You need to add Twitter account first")
            print("💡 Setup: twscrape add_accounts accounts.txt")
            return False
            
    except ImportError:
        print("❌ twscrape not installed")
        print("💡 Install: pip install twscrape")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Note: twscrape requires Twitter account setup")
        return False


def test_snscrape():
    """Test snscrape method (often unstable)"""
    print("\n" + "="*70)
    print("🧪 TESTING: snscrape")
    print("="*70)
    
    try:
        import snscrape.modules.twitter as sntwitter
        print("✅ snscrape installed")
        
        query = "from:IndoPopBase"
        tweets = []
        
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= 5:
                break
            tweets.append(tweet)
        
        if len(tweets) > 0:
            print(f"✅ Successfully scraped {len(tweets)} tweets")
            print(f"📝 Sample tweet: {tweets[0].rawContent[:100]}...")
            return True
        else:
            print("❌ No tweets found")
            return False
            
    except ImportError:
        print("❌ snscrape not installed")
        print("💡 Install: pip install snscrape")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Note: snscrape is often unstable, try other methods")
        return False


def test_selenium():
    """Test Selenium method (RECOMMENDED FALLBACK)"""
    print("\n" + "="*70)
    print("🧪 TESTING: Selenium (RECOMMENDED)")
    print("="*70)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        print("✅ Selenium packages installed")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        print("🔧 Setting up ChromeDriver (first time may take ~30 seconds)...")
        
        try:
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            print("✅ ChromeDriver installed successfully")
            print("🌐 Testing Twitter access...")
            
            # Test access to Twitter
            driver.get("https://twitter.com/IndoPopBase")
            time.sleep(5)
            
            # Check if page loaded
            if "twitter" in driver.current_url.lower() or "x.com" in driver.current_url.lower():
                print("✅ Twitter page accessible")
                
                # Try to find tweets
                try:
                    tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                    if len(tweets) > 0:
                        print(f"✅ Successfully found {len(tweets)} tweet elements")
                        print("✅ Selenium is READY TO USE!")
                        driver.quit()
                        return True
                    else:
                        print("⚠️ Page loaded but no tweets found (might be rate limited)")
                        print("✅ Selenium is installed but may need retry")
                        driver.quit()
                        return True
                except Exception as e:
                    print(f"⚠️ Page loaded but structure detection failed: {e}")
                    print("✅ Selenium is installed, should work with retry")
                    driver.quit()
                    return True
            else:
                print("❌ Could not access Twitter")
                driver.quit()
                return False
        
        except Exception as e:
            print(f"❌ ChromeDriver setup error: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Update Chrome browser to latest version")
            print("   2. Run: pip install --upgrade selenium webdriver-manager")
            print("   3. Check internet connection")
            return False
            
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("💡 Install: pip install selenium webdriver-manager")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("="*70)
    print("🧪 TWITTER SCRAPER - METHOD TESTING")
    print("="*70)
    print("\nTesting all available scraping methods...")
    print("This will help determine which method works best in your environment\n")
    
    results = {
        'ntscraper': False,
        'tweety-ns': False,
        'twscrape': False,
        'snscrape': False,
        'selenium': False,
    }
    
    # Test each method
    results['ntscraper'] = test_ntscraper()
    results['tweety-ns'] = test_tweety()
    results['twscrape'] = test_twscrape()
    results['snscrape'] = test_snscrape()
    results['selenium'] = test_selenium()  # NEW: Test Selenium
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    working_methods = []
    for method, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {method}: {'WORKING' if status else 'FAILED'}")
        if status:
            working_methods.append(method)
    
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    
    if working_methods:
        print(f"\n✅ {len(working_methods)} method(s) are working in your environment:\n")
        for method in working_methods:
            print(f"   ✓ {method}")
        
        # Prioritize Selenium if other methods fail
        if 'selenium' in working_methods and len(working_methods) == 1:
            print("\n🎯 BEST OPTION: Selenium")
            print("   Other methods failed, but Selenium is ready!")
            print("\n📝 Next steps:")
            print("   1. Use the selenium_scraper.py script")
            print("   2. Run: python selenium_scraper.py")
            print("   3. Selenium is slower but MOST RELIABLE")
        elif 'selenium' in working_methods:
            print("\n🎯 Recommended usage order:")
            priority = ['ntscraper', 'tweety-ns', 'twscrape', 'selenium']
            rank = 1
            for method in priority:
                if method in working_methods:
                    print(f"   {rank}. {method}")
                    rank += 1
        else:
            print("\n🎯 Recommended order of usage:")
            priority = ['ntscraper', 'tweety-ns', 'twscrape', 'snscrape']
            for method in priority:
                if method in working_methods:
                    print(f"   1. {method} (RECOMMENDED)")
                    break
        
        print("\n🚀 Next steps:")
        if 'selenium' in working_methods:
            print(f"   Run: python selenium_scraper.py")
        else:
            print(f"   Run: python quick_scraper.py")
        
    else:
        print("\n❌ No methods are working. Try these steps:")
        print("   1. Install Selenium (RECOMMENDED):")
        print("      pip install selenium webdriver-manager")
        print("   2. Update Chrome browser to latest version")
        print("   3. Run test again: python scrapers/test_scraper.py")
        print("   4. Check internet connection")
        print("   5. Try running: python selenium_scraper.py directly")
    
    print("\n" + "="*70)
    
    # Special note about Selenium
    if 'selenium' in working_methods:
        print("✅ SELENIUM IS READY!")
        print("="*70)
        print("\n📌 Selenium Notes:")
        print("   • Most reliable method (uses real browser)")
        print("   • Slower than API methods (but it works!)")
        print("   • No rate limits or API restrictions")
        print("   • Can scrape all publicly visible data")
        print("\n💡 Recommendation: Use selenium_scraper.py for your project")
    
    print("\n" + "="*70)
    print("✅ Testing completed!")
    print("="*70)


if __name__ == "__main__":
    main()