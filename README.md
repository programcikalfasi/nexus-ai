# 🌟 Nexus AI - Intelligent Discovery Platform

> **SaaS Platform for AI-Powered Content Discovery & Analysis**

Nexus AI is a modern web application that combines Reddit intelligence and GitHub exploration with advanced AI capabilities. Each user brings their own API keys for a personalized, secure experience.

---

## ✨ Features

### 🔍 Reddit Surf
- **Smart Scraping**: Discovers relevant Reddit discussions
- **AI Analysis**: Gemini-powered content analysis  
- **Interactive Chat**: Conversation with discovered content
- **Session Management**: Save and revisit research sessions

### 🌊 GitHub Surf
- **4 Discovery Modes**:
  - 🔥 Trending Now
  - 😎 Awesome Lists
  - 💎 Hidden Gems  
  - 🎲 Serendipity
- **Deep Research Agent**: 3-step AI-powered repository discovery
- **Code Analysis**: Chat with repository architecture

### 🤖 AI-Powered Features
- Deep technical code analysis
- Natural language search
- Conversation history
- Multi-language support (EN/TR)

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/nexus-ai.git
cd nexus-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your keys (optional for development)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## 🔑 SaaS Model - User API Keys

**Important**: Nexus AI operates as a SaaS platform where users provide their own API keys.

### For Users:
1. Sign up for an account
2. Go to Settings (⚙️)
3. Add your personal API keys:
   - **Gemini API Key** (Required for AI features)
   - **GitHub Access Token** (Optional, for higher rate limits)

### Getting API Keys:

#### Gemini API Key (Free)
1. Visit: https://ai.google.dev/gemini-api/docs/api-key
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the key starting with `AIza...`

#### GitHub Access Token (Optional)
1. Visit: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scope: `public_repo`
4. Copy token starting with `ghp_...` or `github_pat_...`

---

## 📊 Tech Stack

### Backend
- **Django 5.2.8** - Web framework
- **Python 3.11** - Programming language
- **PostgreSQL** - Production database (SQLite for dev)
- **Gunicorn** - WSGI server

### Frontend
- **Bootstrap 5.3** - UI framework
- **HTMX** - Dynamic interactions
- **Vanilla JS** - Interactivity

### AI & APIs
- **Google Gemini** - AI analysis & chat
- **GitHub API** - Repository discovery
- **Playwright** - Web scraping

### Caching & Performance
- **Django Cache** - In-memory caching
- **Redis** (Optional) - Production cache
- **WhiteNoise** - Static file serving

---

## 🏗️ Project Structure

```
nexus_ai/
├── core/                      # Main Django app
│   ├── models.py             # Database models
│   ├── views.py              # View controllers  
│   ├── urls.py               # URL routing
│   ├── services/             # Business logic
│   │   ├── gemini_engine.py # AI integration
│   │   ├── github_*.py       # GitHub services
│   │   └── smart_scraper.py  # Reddit scraping
│   └── templates/            # HTML templates
├── nexus_ai/                 # Project settings
│   ├── settings.py           # Development settings
│   ├── settings_production.py # Production config
│   └── urls.py               # Root URL config
├── locale/                   # Translations (EN/TR)
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment config
├── DEPLOYMENT.md             # Deployment guide
└── README.md                 # This file
```

---

## 🌐 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides for:
- **Railway** (Recommended - 1-click deploy)
- **Heroku** (Popular PaaS)
- **DigitalOcean** (App Platform)
- **Traditional VPS** (Ubuntu + Nginx)

### Quick Deploy to Railway

```bash
npm install -g @railway/cli
railway init
railway add -d postgres
railway up
```

---

## 🔒 Security Features

- ✅ CSRF protection
- ✅ SQL injection prevention (Django ORM)
- ✅ XSS protection
- ✅ Encrypted API key storage
- ✅ User-specific API keys (no shared secrets)
- ✅ HTTPS enforced in production
- ✅ Rate limiting ready

---

## 🎨 Customization

### Add New Language
```bash
python manage.py makemessages -l es  # Spanish
python manage.py compilemessages
```

### Custom Themes
Edit `core/templates/core/base.html` CSS variables:
```css
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 📈 Usage Limits (Per User)

| Tier | Reddit Searches | GitHub Requests | Chat Messages |
|------|----------------|-----------------|---------------|
| **Free** | 5/day | 60/hour (no token) | Unlimited* |
| **Premium** | Unlimited | 5000/hour (with token) | Unlimited |

*Depends on user's Gemini API quota

---

## 🐛 Troubleshooting

### "No repositories found"
- Check if GitHub rate limit exceeded
- Add GitHub Access Token in Settings

### AI features not working
- Verify Gemini API key in Settings
- Check API key quota at Google AI Studio

### Static files not loading
```bash
python manage.py collectstatic --no-input
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI capabilities
- **Django** - Web framework
- **Bootstrap** - UI components
- **GitHub** - Repository data

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/nexus-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nexus-ai/discussions)

---

## 🎯 Roadmap

- [ ] OAuth social login (Google, GitHub)
- [ ] API rate limiting dashboard
- [ ] Export research to PDF
- [ ] Collaborative sessions
- [ ] Mobile app (React Native)
- [ ] Browser extension

---

**Built with ❤️ using Django & Gemini AI**
