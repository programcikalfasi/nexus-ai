import requests
from bs4 import BeautifulSoup

def test_search(query):
    url = "https://www.searchreddit.io/"
    params = {'q': query}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Searching for: {query}")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Print first 500 chars of HTML to see if we are getting blocked or if structure is different
        print("HTML Preview:")
        print(soup.prettify()[:1000])
        
        results = []
        links = soup.find_all('a', href=True)
        print(f"Found {len(links)} links.")
        
        for link in links:
            href = link['href']
            if 'reddit.com/r/' in href:
                print(f"Found Reddit Link: {href}")
                title = link.get_text(strip=True)
                results.append({'title': title, 'url': href})
        
        print(f"Total Results: {len(results)}")
        return results

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("AI Agents")
