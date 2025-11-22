import requests
from bs4 import BeautifulSoup
import urllib.parse

class SearchRedditClient:
    BASE_URL = "https://html.duckduckgo.com/html/"

    def search(self, query):
        # Search specifically on reddit.com
        search_query = f"site:reddit.com {query}"
        data = {'q': search_query}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://html.duckduckgo.com/'
        }
        
        try:
            # DDG HTML version uses POST for the search form usually, but GET also works. 
            # Using POST as validated in debug script.
            response = requests.post(self.BASE_URL, data=data, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        
        # DDG HTML results links have class 'result__a'
        for link in soup.find_all('a', class_='result__a'):
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if not href or not title:
                continue
                
            # DDG sometimes wraps links in their own redirect, but usually html version gives direct links or easy to parse.
            # If it's a DDG redirect, we might need to decode it, but usually for 'html' version it's direct enough or we can use it.
            # Actually, looking at debug output: 'https://www.reddit.com/r/AI_Agents/' -> It is direct.
            
            if 'reddit.com/r/' in href:
                # Extract subreddit
                try:
                    # expected format: ...reddit.com/r/SubredditName/...
                    parts = href.split('/r/')
                    if len(parts) > 1:
                        subreddit = parts[1].split('/')[0]
                    else:
                        subreddit = 'reddit'
                except:
                    subreddit = 'reddit'

                results.append({
                    'title': title,
                    'url': href,
                    'subreddit': subreddit
                })
                
                if len(results) >= 15:
                    break
        
        return results
