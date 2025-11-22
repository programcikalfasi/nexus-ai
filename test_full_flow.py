#!/usr/bin/env python3
import requests, re, json, time

BASE = 'http://127.0.0.1:8000'

# Helper to extract CSRF token from a page
def get_csrf(html):
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']', html, re.IGNORECASE)
    return match.group(1) if match else None

# 1. Login (use testuser / password123 – create if not exists manually)
login_url = f'{BASE}/en/accounts/login/'
session = requests.Session()
resp = session.get(login_url)

match = re.search(r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
if not match:
    print('❌ Could not get CSRF token for login')
    print('HTML snippet:', resp.text[:500]) # Debug
    exit(1)
csrf = match.group(1)

login_data = {
    'username': 'testuser',
    'password': 'password123',
    'csrfmiddlewaretoken': csrf,
    'next': '/',
}
resp = session.post(login_url, data=login_data, headers={'Referer': login_url})

# Check if we are redirected or if we are on the dashboard
if resp.status_code not in [200, 302]:
    print(f'❌ Login failed with status {resp.status_code}')
    exit(1)
    
# Verify login by checking if we can see the dashboard or if we have a session cookie
if 'sessionid' not in session.cookies:
     print('❌ Login failed (no session cookie)')
     exit(1)

print('✅ Logged in')

# 2. Switch to Turkish
setlang_url = f'{BASE}/i18n/setlang/'
csrf = session.cookies.get('csrftoken')
resp = session.post(setlang_url, data={'language': 'tr', 'next': '/', 'csrfmiddlewaretoken': csrf}, headers={'Referer': f'{BASE}/en/'})
if resp.status_code != 302:
    print(f'⚠️ Language switch might have failed (status {resp.status_code})')
else:
    print('🔁 Language switched to Turkish')

# 3. Perform a search (using SmartScraper)
search_url = f'{BASE}/tr/'
resp = session.get(search_url)
# Update CSRF from cookie if changed
csrf = session.cookies.get('csrftoken')
search_data = {'query': 'Python web frameworks', 'csrfmiddlewaretoken': csrf}
resp = session.post(search_url, data=search_data, headers={'Referer': search_url}, allow_redirects=False)
if resp.status_code != 302:
    print('❌ Search request failed')
    exit(1)
# Follow redirect to session detail page
session_detail = resp.headers['Location']
resp = session.get(f'{BASE}{session_detail}')
print('🔎 Search performed, session page fetched')

# 4. Extract first item ID from the results page
item_match = re.search(r"/tr/analyze/(\d+)/" , resp.text)
if not item_match:
    print('❌ No item found to analyze')
    exit(1)
item_id = item_match.group(1)
print(f'📦 Found item ID: {item_id}')

# 5. Trigger analysis (SmartScraper will be used)
analyze_url = f'{BASE}/tr/analyze/{item_id}/'
# HTMX requests usually send token in header
csrf = session.cookies.get('csrftoken')
resp = session.post(analyze_url, headers={'Referer': f'{BASE}{session_detail}', 'X-CSRFToken': csrf})
if resp.status_code != 200:
    print(f'❌ Analysis request failed with status {resp.status_code}')
    print(resp.text[:200])
    exit(1)
print('🤖 Analysis request sent')

# 6. Fetch the updated item card (the response contains the new HTML)
# The response body is the refreshed card HTML
card_html = resp.text
# Verify that Turkish words appear (e.g., "Heyecan" for Hype badge)
if 'Heyecan' in card_html:
    print('✅ Turkish translation for Hype found (Heyecan)')
else:
    print('⚠️ Turkish Hype translation not found')

if 'Bununla sohbet et' in card_html:
    print('✅ Turkish translation for Chat button found')
else:
    print('⚠️ Turkish Chat button translation not found')

# 7. Optional: start a chat with the item
chat_url = f'{BASE}/tr/chat/start/{item_id}/'
resp = session.get(chat_url, allow_redirects=False)
if resp.status_code == 302:
    chat_detail = resp.headers['Location']
    print(f'💬 Chat session created, redirect to {chat_detail}')
    # Load chat interface
    resp = session.get(f'{BASE}{chat_detail}')
    if 'Chat' in resp.text:
        print('✅ Chat interface loaded')
    else:
        print('⚠️ Chat interface may not have loaded correctly')
else:
    print('⚠️ Chat creation failed')

print('🟢 Full flow test completed')
