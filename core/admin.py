from django.contrib import admin
from .models import (
    UserProfile, DiscoverySession, ContentItem, 
    ChatSession, ChatMessage, RepoAnalysisSession, RepoMessage
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_premium', 'search_limit_daily')
    list_filter = ('is_premium',)
    search_fields = ('user__username', 'user__email')

@admin.register(DiscoverySession)
class DiscoverySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'keywords', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'keywords')
    date_hierarchy = 'created_at'

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'session', 'url')
    list_filter = ('source',)
    search_fields = ('title', 'url')

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'title')
    date_hierarchy = 'created_at'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'timestamp', 'message_preview')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

@admin.register(RepoAnalysisSession)
class RepoAnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'repo_owner', 'repo_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'repo_owner', 'repo_name')
    date_hierarchy = 'created_at'

@admin.register(RepoMessage)
class RepoMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'timestamp', 'message_preview')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
