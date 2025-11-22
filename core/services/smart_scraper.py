import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

class SmartRedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def search(self, query, limit=10):
        """
        Search Google for Reddit threads using requests + BeautifulSoup
        """
        print(f"🔍 Searching for: {query}")
        
        # Add site:reddit.com to query
        search_query = f"{query} site:reddit.com"
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.google.com/search?q={encoded_query}&num={limit+5}"
        
        results = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 429:
                print("⚠️ Google rate limit hit. Waiting...")
                time.sleep(2)
                return []
                
            if response.status_code != 200:
                print(f"❌ Search failed: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            search_items = soup.select('div.g')
            
            for item in search_items:
                if len(results) >= limit:
                    break
                    
                link_tag = item.select_one('a')
                if not link_tag:
                    continue
                    
                href = link_tag.get('href')
                if not href or 'reddit.com' not in href:
                    continue
                
                title_tag = item.select_one('h3')
                title = title_tag.text if title_tag else "No Title"
                
                # Extract snippet
                snippet_tag = item.select_one('div.VwiC3b') or item.select_one('div.IsZvec')
                snippet = snippet_tag.text if snippet_tag else ""
                
                results.append({
                    'title': title,
                    'url': href,
                    'snippet': snippet,
                    'source': 'reddit'
                })
                
            print(f"✅ Found {len(results)} results")
            return results

        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            return []

    def close(self):
        pass
