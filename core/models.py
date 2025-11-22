from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # API Keys for SaaS model - each user brings their own keys
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True, 
                                      help_text="Your personal Gemini API key for AI features")
    github_access_token = models.CharField(max_length=255, blank=True, null=True,
                                          help_text="Your personal GitHub access token for higher rate limits")
    
    # Premium features
    is_premium = models.BooleanField(default=False)
    search_limit_daily = models.IntegerField(default=5)
    
    # Usage tracking
    last_search_date = models.DateField(null=True, blank=True)
    searches_today = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    
    def has_gemini_key(self):
        """Check if user has configured Gemini API key"""
        return bool(self.gemini_api_key and self.gemini_api_key.strip())
    
    def has_github_token(self):
        """Check if user has configured GitHub token"""
        return bool(self.github_access_token and self.github_access_token.strip())
    
    def can_search(self):
        """Check if user can perform a search based on daily limit"""
        from datetime import date
        today = date.today()
        
        if self.last_search_date != today:
            self.searches_today = 0
            self.last_search_date = today
            self.save()
        
        return self.is_premium or self.searches_today < self.search_limit_daily
    
    def increment_search_count(self):
        """Increment search counter"""
        self.searches_today += 1
        self.save()

class DiscoverySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keywords = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.keywords}"

class ContentItem(models.Model):
    session = models.ForeignKey(DiscoverySession, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=2000)
    source = models.CharField(max_length=50, default='searchreddit')
    raw_content = models.TextField(blank=True)
    ai_analysis = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    related_content = models.ForeignKey(ContentItem, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"
class RepoAnalysisSession(models.Model):
    """Stores GitHub repository analysis chat sessions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_owner = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255)
    repo_url = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.repo_owner}/{self.repo_name}"

class RepoMessage(models.Model):
    """Stores messages in a repository analysis chat."""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    session = models.ForeignKey(RepoAnalysisSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"
