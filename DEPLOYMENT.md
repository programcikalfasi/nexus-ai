# 🚀 Nexus AI - Production Deployment Guide

## 📋 Overview

Nexus AI is a SaaS platform where each user brings their own API keys (Gemini + GitHub). This guide covers deploying to various platforms.

---

## 🎯 Quick Start Options

### Option 1: Railway (Recommended - Easiest) ⭐
### Option 2: Heroku (Popular)
### Option 3: DigitalOcean App Platform
### Option 4: Traditional VPS (Ubuntu)

---

## 🛠️ Pre-Deployment Checklist

- [ ] PostgreSQL database ready
- [ ] Domain name (optional but recommended)
- [ ] SSL certificate (handled by platforms automatically)
- [ ] Environment variables prepared

---

##  1️⃣ Railway Deployment (Fastest)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### Step 2: Create Project
```bash
cd /path/to/nexus_ai
railway init
```

### Step 3: Add PostgreSQL
```bash
railway add -d postgres
```

### Step 4: Set Environment Variables
```bash
railway variables set SECRET_KEY="your-super-secret-key-here"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-app.up.railway.app"
railway variables set DJANGO_SETTINGS_MODULE="nexus_ai.settings_production"
```

### Step 5: Deploy
```bash
# Create Procfile
echo "web: gunicorn nexus_ai.wsgi --bind 0.0.0.0:\$PORT" > Procfile

# Create runtime.txt
echo "python-3.11" > runtime.txt

# Deploy
railway up
```

### Step 6: Run Migrations
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py collectstatic --no-input
```

**Done! Your app is live at: `https://your-app.up.railway.app`**

---

## 2️⃣ Heroku Deployment

### Step 1: Install Heroku CLI
```bash
brew install heroku/brew/heroku  # macOS
heroku login
```

### Step 2: Create App
```bash
cd /path/to/nexus_ai
heroku create nexus-ai-yourname
```

### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

### Step 4: Configure Environment
```bash
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG="False"
heroku config:set DJANGO_SETTINGS_MODULE="nexus_ai.settings_production"
heroku config:set ALLOWED_HOSTS=".herokuapp.com"
```

### Step 5: Create Procfile
```bash
cat > Procfile << EOF
web: gunicorn nexus_ai.wsgi
release: python manage.py migrate
EOF
```

### Step 6: Deploy
```bash
git init
git add .
git commit -m "Initial deployment"
heroku git:remote -a nexus-ai-yourname
git push heroku main
```

### Step 7: Scale & Migrate
```bash
heroku ps:scale web=1
heroku run python manage.py createsuperuser
heroku run python manage.py collectstatic --no-input
```

**Live at: `https://nexus-ai-yourname.herokuapp.com`**

---

## 3️⃣ DigitalOcean App Platform

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/yourusername/nexus-ai.git
git push -u origin main
```

### Step 2: Create App on DigitalOcean
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect your GitHub repository
4. Select branch: `main`

### Step 3: Configure App
```yaml
name: nexus-ai
region: nyc
services:
  - name: web
    github:
      repo: yourusername/nexus-ai
      branch: main
      deploy_on_push: true
    run_command: gunicorn nexus_ai.wsgi
    environment_slug: python
    instance_size_slug: basic-xxs
    instance_count: 1
    
databases:
  - name: db
    engine: PG
    version: "15"
    
envs:
  - key: SECRET_KEY
    value: "your-secret-key"
  - key: DEBUG
    value: "False"
  - key: DJANGO_SETTINGS_MODULE
    value: "nexus_ai.settings_production"
```

### Step 4: Deploy
Click "Create Resources" - Done!

---

## 4️⃣ Traditional VPS (Ubuntu 22.04)

### Step 1: SSH into Server
```bash
ssh root@your-server-ip
```

### Step 2: Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib -y
```

### Step 3: Create User & Database
```bash
sudo -u postgres psql
CREATE DATABASE nexusai;
CREATE USER nexususer WITH PASSWORD 'strong_password';
ALTER ROLE nexususer SET client_encoding TO 'utf8';
ALTER ROLE nexususer SET default_transaction_isolation TO 'read committed';
ALTER ROLE nexususer SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE nexusai TO nexususer;
\q
```

### Step 4: Setup Application
```bash
cd /opt
git clone https://github.com/yourusername/nexus-ai.git
cd nexus-ai
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Configure Environment
```bash
cat > .env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://nexususer:strong_password@localhost/nexusai
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SETTINGS_MODULE=nexus_ai.settings_production
EOF
```

### Step 6: Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --no-input
```

### Step 7: Setup Gunicorn
```bash
sudo nano /etc/systemd/system/nexusai.service
```

Paste:
```ini
[Unit]
Description=Nexus AI Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/nexus-ai
Environment="PATH=/opt/nexus-ai/venv/bin"
ExecStart=/opt/nexus-ai/venv/bin/gunicorn --workers 3 --bind unix:/opt/nexus-ai/nexusai.sock nexus_ai.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Step 8: Setup Nginx
```bash
sudo nano /etc/nginx/sites-available/nexusai
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /opt/nexus-ai/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/nexus-ai/nexusai.sock;
    }
}
```

### Step 9: Enable & Start
```bash
sudo ln -s /etc/nginx/sites-available/nexusai /etc/nginx/sites-enabled
sudo systemctl start nexusai
sudo systemctl enable nexusai
sudo systemctl restart nginx
```

### Step 10: SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**Done! Visit: `https://your-domain.com`**

---

## 🔒 Security Best Practices

1. **Change SECRET_KEY** - Generate new:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Environment Variables** - Never commit `.env` to Git

3. **Database Backups** - Setup automated backups:
   ```bash
   pg_dump nexusai > backup_$(date +%Y%m%d).sql
   ```

4. **Rate Limiting** - Consider adding django-ratelimit

5. **Monitoring** - Use Sentry for error tracking:
   ```bash
   pip install sentry-sdk
   ```

---

## 📊 Database Migration (SQLite → PostgreSQL)

### Local Export
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > datadump.json
```

### Production Import
```bash
python manage.py loaddata datadump.json
```

---

## 🎭 Post-Deployment Checklist

- [ ] SSL certificate active (HTTPS)
- [ ] Admin panel accessible at `/admin`
- [ ] User registration working
- [ ] API key settings page functional
- [ ] Reddit Surf working
- [ ] GitHub Surf working
- [ ] Deep research functional
- [ ] Chat features operational
- [ ] Static files loading correctly
- [ ] Database backups configured
- [ ] Error monitoring setup

---

## 🆘 Troubleshooting

### Static Files Not Loading
```bash
python manage.py collectstatic --no-input
```

### Database Connection Error
Check `DATABASE_URL` environment variable format:
```
postgresql://user:password@host:5432/database
```

### 502 Bad Gateway
```bash
sudo systemctl status nexusai
sudo tail -f /var/log/nginx/error.log
```

### Memory Issues
Increase Gunicorn workers or upgrade plan

---

## 📞 Support

For issues, check:
1. Application logs
2. Database logs
3. Nginx error logs (if applicable)

**Your SaaS is ready! Users can now sign up and add their own API keys!** 🎉
