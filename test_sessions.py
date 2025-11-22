#!/usr/bin/env python3
import requests, re, sys

BASE = 'http://127.0.0.1:8000'

# ---------------------------------------------------------------------------
# 1️⃣ Login – token is taken from the cookie after login
login_url = f'{BASE}/en/accounts/login/'
sess = requests.Session()
resp = sess.get(login_url)
# token from login page (needed for the POST)
login_page_token = re.search(
    r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']',
    resp.text,
    re.IGNORECASE,
).group(1)

login_data = {
    'username': 'testuser',
    'password': 'password123',
    'csrfmiddlewaretoken': login_page_token,
    'next': '/',               # redirect after login
}
resp = sess.post(login_url, data=login_data,
                 headers={'Referer': login_url},
                 allow_redirects=True)   # follow redirects
if resp.status_code != 200:
    sys.exit(f'❌ Login failed, status {resp.status_code}')
print('✅ Logged in')

# CSRF token stored in cookie – reliable for all later POSTs
csrf = sess.cookies.get('csrftoken')
if not csrf:
    sys.exit('❌ CSRF token not found in cookies after login')
print('🔑 CSRF token from cookie:', csrf[:10] + '…')

# ---------------------------------------------------------------------------
# 2️⃣ Dashboard URL (no extra token fetch needed)
dashboard_url = f'{BASE}/en/'
print('🔗 Using dashboard URL:', dashboard_url)

def post_with_csrf(url, data=None):
    """POST using the CSRF token taken from the login cookie."""
    if data is None:
        data = {}
    data['csrfmiddlewaretoken'] = csrf
    return sess.post(url, data=data,
                     headers={'Referer': url},
                     allow_redirects=False)

# ---------------------------------------------------------------------------
# 3️⃣ Create a discovery session (search)
search_data = {'query': 'Python web frameworks'}
resp = post_with_csrf(dashboard_url, search_data)
if resp.status_code != 302:
    sys.exit(f'❌ Search request failed, status {resp.status_code}')
print('🔎 Search created, redirect →', resp.headers.get('Location'))

# ---------------------------------------------------------------------------
# 4️⃣ Get newest session ID from dashboard
resp = sess.get(dashboard_url)
match = re.search(r'/en/session/(\d+)/', resp.text)
if not match:
    print('❌ Could not find session ID on dashboard')
    print('--- Dashboard HTML Start ---')
    print(resp.text)
    print('--- Dashboard HTML End ---')
    sys.exit(1)
session_id = match.group(1)
print('📦 Detected session ID:', session_id)

# ---------------------------------------------------------------------------
# 5️⃣ Delete the session
delete_url = f'{BASE}/en/session/{session_id}/delete/'
resp = sess.post(delete_url,
                 data={'csrfmiddlewaretoken': csrf},
                 headers={'Referer': delete_url},
                 allow_redirects=False)
if resp.status_code != 302:
    sys.exit(f'❌ Delete request failed, status {resp.status_code}')
print('🗑️ Session deleted')

# ---------------------------------------------------------------------------
# 6️⃣ Verify deletion
resp = sess.get(dashboard_url)
if re.search(rf'/en/session/{session_id}/', resp.text):
    print('⚠️ Session still appears')
else:
    print('✅ Session removed')

# ---------------------------------------------------------------------------
# 7️⃣ Create another session (to test clear‑all)
resp = post_with_csrf(dashboard_url, {'query': 'AI coding tools'})
if resp.status_code != 302:
    sys.exit('❌ Second search failed')
print('🔎 Second session created')

# ---------------------------------------------------------------------------
# 8️⃣ Clear all sessions
clear_url = f'{BASE}/en/sessions/clear/'
resp = sess.post(clear_url,
                 data={'csrfmiddlewaretoken': csrf},
                 headers={'Referer': clear_url},
                 allow_redirects=False)
if resp.status_code != 302:
    sys.exit(f'❌ Clear all failed, status {resp.status_code}')
print('🧹 All sessions cleared')

# ---------------------------------------------------------------------------
# 9️⃣ Verify empty state
resp = sess.get(dashboard_url)
if 'No research sessions yet' in resp.text:
    print('✅ Dashboard empty')
else:
    print('⚠️ Dashboard still shows sessions')

print('🟢 Test flow completed')