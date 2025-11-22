import requests
from bs4 import BeautifulSoup

class RedditContentFetcher:
    def fetch(self, url):
        # 1. Try Reddit JSON API first (Cleanest data)
        try:
            json_url = url.rstrip('/') + '.json'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(json_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                post_data = data[0]['data']['children'][0]['data']
                title = post_data.get('title', '')
                selftext = post_data.get('selftext', '')
                
                # Get top comments for context
                comments = []
                if len(data) > 1:
                    for c in data[1]['data']['children'][:5]:
                        if 'body' in c.get('data', {}):
                            comments.append(c['data']['body'])
                
                content = f"Title: {title}\n\nPost Body:\n{selftext}\n\nTop Comments:\n" + "\n---\n".join(comments)
                return content
        except Exception as e:
            print(f"JSON Fetch failed, falling back to HTML: {e}")

        # 2. Fallback to HTML scraping
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"Error: Failed to fetch content (Status: {response.status_code})"
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Strategy 1: Meta Description (often contains the snippet)
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
            description = meta_desc['content'] if meta_desc else ""

            # Strategy 2: Shreddit (New Reddit)
            shreddit_post = soup.find('shreddit-post')
            if shreddit_post:
                title = shreddit_post.get('post-title', '')
                return f"Title: {title}\n\nDescription/Snippet:\n{description}"

            # Strategy 3: Old Reddit / Generic
            title = soup.find('title').get_text(strip=True)
            paragraphs = soup.find_all('p')
            text_content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            return f"Title: {title}\n\nDescription:\n{description}\n\nExtracted Text:\n{text_content[:5000]}"
            
        except Exception as e:
            return f"Error fetching content: {e}"
