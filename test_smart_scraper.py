#!/usr/bin/env python3
import requests

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
    
    print("🔍 Testing Smart Scraper with query: 'Best AI Coding Tools'")
    dashboard_url = 'http://127.0.0.1:8000/en/'
    
    # Get CSRF again
    response = session.get(dashboard_url)
    for line in response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break
            
    search_data = {
        'query': 'Best AI Coding Tools',
        'csrfmiddlewaretoken': csrf_token
    }
    
    # This request will trigger the scraper
    response = session.post(dashboard_url, data=search_data, headers={'Referer': dashboard_url})
    
    if response.status_code == 200 or response.status_code == 302:
        print("✅ Search request successful")
        # We can't easily see the server logs here, but if it didn't crash, it's a good sign.
        # The server logs will show "Attempting Smart Search..."
    else:
        print(f"❌ Search request failed: {response.status_code}")

else:
    print("❌ Could not login")
