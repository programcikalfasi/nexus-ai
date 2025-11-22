import requests
from bs4 import BeautifulSoup

def test_ddg_search(query):
    url = "https://html.duckduckgo.com/html/"
    params = {'q': f"site:reddit.com {query}"}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Searching DDG for: {query}")
    try:
        response = requests.post(url, data=params, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        # DDG HTML results usually have class 'result__a' for the main link
        for link in soup.find_all('a', class_='result__a'):
            href = link.get('href')
            title = link.get_text(strip=True)
            if href and 'reddit.com/r/' in href:
                results.append({'title': title, 'url': href})
        
        print(f"Found {len(results)} results.")
        for r in results[:3]:
            print(r)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ddg_search("AI Agents")
