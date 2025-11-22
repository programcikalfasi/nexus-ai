# ⚡ Nexus AI - One-Click Deploy

## Railway Deploy Button

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/nexus-ai?referralCode=YOUR_CODE)

## Manual Deploy to Railway

1. Click: https://railway.app/new/template?template=https://github.com/programcikalfasi/nexus-ai
2. Add PostgreSQL database
3. Set environment variables:
   - `SECRET_KEY`: `$m0bz&abdof8@s-9oj^j^$o8-iuoh9iy$-)!ty2fsa#a55*+7c`
   - `DEBUG`: `False`
   - `DJANGO_SETTINGS_MODULE`: `nexus_ai.settings_production`
4. Deploy!

## Alternative: Localhost Tunnel (Instant)

```bash
# Option 1: localtunnel (easiest)
npx localtunnel --port 8000

# Option 2: ngrok (requires signup)
ngrok http 8000

# Option 3: Cloudflare Tunnel (free, no signup)
cloudflared tunnel --url http://localhost:8000
```

Your local server is already running on port 8000!
