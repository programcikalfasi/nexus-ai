from playwright.sync_api import sync_playwright
import time
import random
import logging

logger = logging.getLogger(__name__)

class SmartRedditScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def search(self, query, max_retries=3):
        """
        Searches specifically on Reddit using Playwright to get Google Search results.
        Includes retry logic and robust error handling.
        """
        print(f"SmartRedditScraper: Searching for '{query}'...")
        results = []
        
        for attempt in range(max_retries):
            try:
                with sync_playwright() as p:
                    # Launch browser (headless=True for server environment)
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    )
                    page = context.new_page()
                    
                    # Use Google Search with site:reddit.com
                    search_url = f"https://www.google.com/search?q=site:reddit.com+{query.replace(' ', '+')}"
                    
                    # Go to page with timeout
                    page.goto(search_url, timeout=10000)
                    
                    # Wait for results to load
                    try:
                        page.wait_for_selector('div.g', timeout=5000)
                    except:
                        print(f"Attempt {attempt + 1}: No results selector found.")
                        browser.close()
                        continue

                    # Extract results
                    search_results = page.query_selector_all('div.g')
                    
                    for result in search_results:
                        if len(results) >= 5:
                            break
                            
                        try:
                            # Extract Title (h3)
                            title_el = result.query_selector('h3')
                            if not title_el:
                                continue
                            title = title_el.inner_text()
                            
                            # Extract Link (a)
                            link_el = result.query_selector('a')
                            if not link_el:
                                continue
                            url = link_el.get_attribute('href')
                            
                            if not url or 'reddit.com/r/' not in url:
                                continue
                                
                            # Extract Subreddit
                            subreddit = 'reddit'
                            if '/r/' in url:
                                parts = url.split('/r/')
                                if len(parts) > 1:
                                    subreddit = parts[1].split('/')[0]
                            
                            # Avoid duplicates
                            if any(r['url'] == url for r in results):
                                continue

                            results.append({
                                'title': title,
                                'url': url,
                                'subreddit': subreddit
                            })
                            
                        except Exception as e:
                            print(f"Error parsing result: {e}")
                            continue
                    
                    browser.close()
                    
                    # If we found results, break the retry loop
                    if results:
                        break
                        
            except Exception as e:
                print(f"SmartRedditScraper Error (Attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 * (attempt + 1)) # Exponential backoff
        
        return results
