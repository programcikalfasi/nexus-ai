import requests
import json

def test_reddit_json(url):
    json_url = url.rstrip('/') + '.json'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching: {json_url}")
    try:
        response = requests.get(json_url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Reddit JSON structure: List of 2 items. 
            # Item 0: The listing containing the submission.
            # Item 1: The listing containing the comments.
            
            post_data = data[0]['data']['children'][0]['data']
            title = post_data.get('title', '')
            selftext = post_data.get('selftext', '')
            
            print(f"Title: {title}")
            print(f"Body: {selftext[:200]}...")
            
            comments = []
            if len(data) > 1:
                comment_listing = data[1]['data']['children']
                for c in comment_listing[:5]:
                    if 'body' in c['data']:
                        comments.append(c['data']['body'])
            
            print(f"Top 5 Comments: {comments}")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_reddit_json("https://www.reddit.com/r/LocalLLaMA/comments/17t6d6w/what_is_the_best_open_source_llm_for_coding/")
