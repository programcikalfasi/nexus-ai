import requests

def test_reddit_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
    }
    print(f"Fetching HTML: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        if response.status_code == 200:
            print("Preview:")
            print(response.text[:500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reddit_html("https://www.reddit.com/r/LocalLLaMA/comments/17t6d6w/what_is_the_best_open_source_llm_for_coding/")
