#!/usr/bin/env python3
import requests

# Test dil değiştirme
session = requests.Session()

# Login
login_url = 'http://127.0.0.1:8000/en/accounts/login/'
dashboard_url = 'http://127.0.0.1:8000/en/'

# Get CSRF token
response = session.get(login_url)
csrf_token = None
for line in response.text.split('\n'):
    if 'csrf' in line and 'value' in line:
        start = line.find('value="') + 7
        end = line.find('"', start)
        csrf_token = line[start:end]
        break

if csrf_token:
    # Login
    login_data = {
        'username': 'testuser',
        'password': 'password123',
        'csrfmiddlewaretoken': csrf_token
    }
    response = session.post(login_url, data=login_data, headers={'Referer': login_url})
    
    # Check English page
    response = session.get(dashboard_url)
    if 'Settings' in response.text:
        print("✅ English: 'Settings' found")
    else:
        print("❌ English: 'Settings' NOT found")
    
    # Switch to Turkish
    tr_url = 'http://127.0.0.1:8000/tr/'
    response = session.get(tr_url)
    
    if 'Ayarlar' in response.text:
        print("✅ Turkish: 'Ayarlar' found")
    elif 'Settings' in response.text:
        print("⚠️  Turkish: Still showing 'Settings' instead of 'Ayarlar'")
    else:
        print("❌ Turkish: Neither 'Settings' nor 'Ayarlar' found")
        
    # Check if language switcher is visible
    if '🇬🇧 EN' in response.text and '🇹🇷 TR' in response.text:
        print("✅ Language switcher visible")
    else:
        print("❌ Language switcher NOT visible")
else:
    print("❌ Could not get CSRF token")
