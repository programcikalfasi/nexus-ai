import requests
import random
from datetime import datetime, timedelta
from django.conf import settings

class GitHubDiscoveryService:
    BASE_URL = "https://api.github.com/search/repositories"
    
    def __init__(self, access_token=None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        # Use token from settings if not provided, but it's optional for public data
        token = access_token or getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
        if token:
            self.headers["Authorization"] = f"token {token}"

    def _fetch(self, query, per_page=30):
        """Internal method to fetch from GitHub API with error handling."""
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page={per_page}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Handle rate limiting
            if response.status_code == 403:
                print(f"⚠️ GitHub API Rate Limit Exceeded. Try again in an hour or add GITHUB_ACCESS_TOKEN.")
                return []
            
            if response.status_code == 422:
                print(f"⚠️ Invalid query: {query}")
                return []
            
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout while querying GitHub: {query}")
            return []
        except Exception as e:
            print(f"❌ GitHub API Error: {e}")
            return []

    def discover_awesome(self):
        """
        Fetches repositories from the 'Awesome' ecosystem.
        """
        # Randomize page for variety
        page = random.randint(1, 5)
        query = f"topic:awesome&page={page}"
        return self._fetch(query, per_page=10)

    def discover_trending(self):
        """
        Fetches repositories created in the last 7 days with high stars.
        """
        date_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query = f"created:>{date_week_ago}"
        return self._fetch(query, per_page=30)

    def discover_hidden_gems(self):
        """
        Fetches repos with < 2k stars but high recent activity and specific high-quality tags.
        """
        topics = [
            "system-design", "architecture", "learning", "roadmap", 
            "reverse-engineering", "algorithm", "design-patterns", "distributed-systems"
        ]
        selected_topic = random.choice(topics)
        
        # Pushed within last month
        date_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        query = f"topic:{selected_topic} stars:100..2000 pushed:>{date_month_ago}"
        return self._fetch(query, per_page=30)

    def discover_serendipity(self):
        """
        Fetches a random repository from high-quality technical topics.
        """
        topics = [
            "compilers", "generative-ai", "p2p", "os-dev", "database-internals",
            "virtual-machine", "game-engine", "cryptography", "webrtc"
        ]
        selected_topic = random.choice(topics)
        page = random.randint(1, 5)
        query = f"topic:{selected_topic} stars:>500&page={page}"
        
        items = self._fetch(query, per_page=5)
        if items:
            return [random.choice(items)]
        return []
    
    def deep_research(self, queries):
        """
        Step 2: Executes multiple GitHub queries in parallel and deduplicates results.
        Returns a combined list of repositories.
        """
        all_results = []
        seen_repos = set()
        
        for query in queries:
            try:
                results = self._fetch(query, per_page=20)
                for repo in results:
                    repo_id = repo.get('id')
                    if repo_id and repo_id not in seen_repos:
                        seen_repos.add(repo_id)
                        all_results.append(repo)
            except Exception as e:
                print(f"Error executing query '{query}': {e}")
                continue
        
        return all_results

