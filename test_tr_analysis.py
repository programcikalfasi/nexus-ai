#!/usr/bin/env python3
import requests
import time

session = requests.Session()

# Login
login_url = 'http://127.0.0.1:8000/en/accounts/login/'
response = session.get(login_url)

csrf_token = None
for line in response.text.split('\n'):
    if 'csrfmiddlewaretoken' in line and 'value' in line:
        start = line.find('value="') + 7
        end = line.find('"', start)
        csrf_token = line[start:end]
        break

if csrf_token:
    login_data = {
        'username': 'testuser',
        'password': 'password123',
        'csrfmiddlewaretoken': csrf_token
    }
    session.post(login_url, data=login_data, headers={'Referer': login_url})
    
    # Switch to Turkish
    print("🇹🇷 Switching to Turkish...")
    session.post('http://127.0.0.1:8000/i18n/setlang/', data={'language': 'tr', 'next': '/tr/'}, headers={'Referer': 'http://127.0.0.1:8000/en/'})
    
    # Create a new session (search)
    print("🔍 Searching for 'Python Web Frameworks'...")
    dashboard_url = 'http://127.0.0.1:8000/tr/'
    response = session.get(dashboard_url)
    
    # Get CSRF again
    for line in response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break
            
    search_data = {
        'query': 'Python Web Frameworks',
        'csrfmiddlewaretoken': csrf_token
    }
    response = session.post(dashboard_url, data=search_data, headers={'Referer': dashboard_url})
    
    # Get the session ID from redirect
    session_url = response.url
    print(f"📄 Session URL: {session_url}")
    
    # Get the page content to find an item ID
    response = session.get(session_url)
    
    # Find an item ID to analyze (simple parsing)
    import re
    match = re.search(r'hx-post="/tr/analyze/(\d+)/"', response.text)
    if match:
        item_id = match.group(1)
        print(f"🤖 Analyzing item {item_id}...")
        
        analyze_url = f'http://127.0.0.1:8000/tr/analyze/{item_id}/'
        # HTMX request
        headers = {
            'HX-Request': 'true',
            'Referer': session_url,
            'X-CSRFToken': csrf_token
        }
        response = session.post(analyze_url, headers=headers) # HTMX uses POST for this action in our template? No wait, hx-post
        
        print("\n📊 Analysis Result:")
        print("-" * 50)
        
        if "Heyecan" in response.text:
            print("✅ 'Heyecan' found (Turkish translation of Hype)")
        else:
            print("❌ 'Heyecan' NOT found")
            
        if "Bununla sohbet et" in response.text:
             print("✅ 'Bununla sohbet et' found")
        else:
             print("❌ 'Bununla sohbet et' NOT found")
             
        # Check for Turkish characters in summary (rough check)
        tr_chars = ['ı', 'ğ', 'ü', 'ş', 'ö', 'ç', 'İ', 'Ğ', 'Ü', 'Ş', 'Ö', 'Ç']
        has_tr_chars = any(char in response.text for char in tr_chars)
        if has_tr_chars:
            print("✅ Turkish characters found in response (likely Turkish summary)")
        else:
            print("⚠️ No specific Turkish characters found (might be English or simple Turkish)")
            
        print("-" * 50)
        # Print a snippet of the summary
        summary_match = re.search(r'<p class="card-text[^>]*>(.*?)</p>', response.text, re.DOTALL)
        if summary_match:
            print(f"Summary Snippet: {summary_match.group(1).strip()[:100]}...")
            
    else:
        print("❌ No items found to analyze")

else:
    print("❌ Could not login")
