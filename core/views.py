from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import UserProfile, DiscoverySession, ContentItem, ChatSession, ChatMessage, RepoAnalysisSession, RepoMessage
from .services.search_reddit import SearchRedditClient
from .services.gemini_engine import GeminiEngine
from .services.smart_scraper import SmartRedditScraper
from .services.github_discovery import GitHubDiscoveryService
from .services.github_analyzer import GitHubRepoAnalyzer
from django.conf import settings
import json

def get_gemini_engine(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    api_key = profile.gemini_api_key
    return GeminiEngine(api_key=api_key)

@login_required
def dashboard(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            session = DiscoverySession.objects.create(user=request.user, keywords=query)
            
            # Check cache first
            cache_key = f"search_results_{query.lower().replace(' ', '_')}"
            results = cache.get(cache_key)

            if not results:
                # Try Smart Scraper first (AI Powered)
                try:
                    # Get API key from user profile for the scraper
                    profile, _ = UserProfile.objects.get_or_create(user=request.user)
                    api_key = profile.gemini_api_key or settings.GEMINI_API_KEY
                    
                    if api_key:
                        scraper = SmartRedditScraper(api_key=api_key)
                        print(f"Attempting Smart Search for: {query}")
                        results = scraper.search(query)
                except Exception as e:
                    print(f"Smart Scraper Failed: {e}")
                
                # Fallback to DuckDuckGo scraper if Smart Scraper returns empty or fails
                if not results:
                    print("Falling back to Standard Search...")
                    client = SearchRedditClient()
                    results = client.search(query)
                
                # Cache results for 1 hour (3600 seconds) if we found something
                if results:
                    cache.set(cache_key, results, 3600)
            
            for res in results:
                ContentItem.objects.create(
                    session=session,
                    title=res['title'],
                    url=res['url'],
                    source=f"r/{res.get('subreddit', 'reddit')}"
                )
            
            return redirect('session_detail', session_id=session.id)

    sessions = DiscoverySession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/dashboard.html', {'sessions': sessions})

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(DiscoverySession, user=request.user, id=session_id)
    return render(request, 'core/results.html', {'session': session})

from .services.content_fetcher import RedditContentFetcher

@login_required
def analyze_item(request, item_id):
    item = get_object_or_404(ContentItem, session__user=request.user, id=item_id)
    
    # Fetch real content if we haven't yet
    if not item.raw_content:
        fetcher = RedditContentFetcher()
        content = fetcher.fetch(item.url)
        item.raw_content = content
        item.save()
    
    content_to_analyze = item.raw_content
    
    # Get current language
    lang_code = request.LANGUAGE_CODE
    
    engine = get_gemini_engine(request.user)
    analysis = engine.analyze_content(content_to_analyze, language=lang_code)
    
    item.ai_analysis = analysis
    item.save()
    
    return render(request, 'core/partials/item_card.html', {'item': item})

@login_required
def start_chat(request, item_id):
    item = get_object_or_404(ContentItem, session__user=request.user, id=item_id)
    chat_session = ChatSession.objects.create(
        user=request.user,
        related_content=item,
        title=f"Chat about {item.title[:30]}"
    )
    return redirect('chat_interface', chat_id=chat_session.id)

@login_required
def chat_interface(request, chat_id):
    chat_session = get_object_or_404(ChatSession, user=request.user, id=chat_id)
    return render(request, 'core/chat.html', {'chat_session': chat_session})

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat_session = get_object_or_404(ChatSession, user=request.user, id=chat_id)
        user_msg_text = request.POST.get('message')
        
        user_msg = ChatMessage.objects.create(session=chat_session, sender='user', message=user_msg_text)
        
        engine = get_gemini_engine(request.user)
        
        history = []
        # Exclude the just added message from history passed to API to avoid duplication if API handles it,
        # but Gemini `start_chat` + `send_message` handles the new message.
        # We need history of *previous* turns.
        for msg in chat_session.messages.order_by('timestamp'):
            if msg.message == user_msg_text and msg.sender == 'user' and msg == chat_session.messages.last():
                continue # Don't include the current message in history
            role = 'user' if msg.sender == 'user' else 'model'
            history.append({'role': role, 'parts': [msg.message]})
            
        context = None
        if chat_session.related_content:
            context = {
                'title': chat_session.related_content.title,
                'analysis': chat_session.related_content.ai_analysis,
                'raw_content': chat_session.related_content.raw_content or chat_session.related_content.title
            }
        
        # Get current language
        lang_code = request.LANGUAGE_CODE
            
        ai_response_text = engine.chat(chat_session.id, user_msg_text, history=history, context=context, language=lang_code)
        
        ai_msg = ChatMessage.objects.create(session=chat_session, sender='ai', message=ai_response_text)
        
        user_msg_html = render_to_string('core/partials/chat_message.html', {'message': user_msg}, request=request)
        ai_msg_html = render_to_string('core/partials/chat_message.html', {'message': ai_msg}, request=request)
        
        return HttpResponse(user_msg_html + ai_msg_html)

    return HttpResponse(status=400)

from django.http import HttpResponse

# ... existing imports and functions remain unchanged ...

@login_required
def delete_session(request, session_id):
    """Delete a single discovery session (POST only)."""
    if request.method == "POST":
        session = get_object_or_404(DiscoverySession, user=request.user, id=session_id)
        session.delete()
        return redirect('dashboard')
    return HttpResponse(status=405)

@login_required
def clear_sessions(request):
    """Delete all discovery sessions for the current user (POST only)."""
    if request.method == "POST":
        DiscoverySession.objects.filter(user=request.user).delete()
        return redirect('dashboard')
    return HttpResponse(status=405)
@login_required
def github_surf(request):
    """Renders the GitHub Surf interface."""
    return render(request, 'core/github_surf.html')

@login_required
def github_discover(request):
    """API endpoint for GitHub discovery strategies."""
    mode = request.GET.get('mode', 'trending')
    query = request.GET.get('query', '')
    service = GitHubDiscoveryService()
    
    # Create cache key based on mode and query
    import hashlib
    if mode == 'deep_research' and query:
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        cache_key = f"github_surf_{mode}_{query_hash}"
    else:
        cache_key = f"github_surf_{mode}"
    
    results = cache.get(cache_key)
    
    if not results:
        if mode == 'deep_research':
            query = request.GET.get('query', '')
            if query:
                engine = get_gemini_engine(request.user)
                
                # Step 1: Generate research strategy (multiple queries)
                print(f"🧠 Step 1: Generating research strategy for '{query}'")
                queries = engine.generate_research_strategy(query)
                print(f"📋 Generated {len(queries)} queries: {queries}")
                
                # Step 2: Execute all queries and collect results
                print(f"🔍 Step 2: Executing queries and harvesting repos")
                all_repos = service.deep_research(queries)
                print(f"📦 Collected {len(all_repos)} unique repositories")
                
                # Step 3: AI filtering and curation
                print(f"🎯 Step 3: AI analyzing and filtering results")
                results = engine.filter_repositories(query, all_repos)
                print(f"✨ Curated to {len(results)} best matches")
        elif mode == 'search':
            query = request.GET.get('query', '')
            if query:
                # Use Gemini to convert natural language to GitHub query
                engine = get_gemini_engine(request.user)
                github_query = engine.generate_github_query(query)
                print(f"Natural Language: '{query}' -> GitHub Query: '{github_query}'")
                results = service._fetch(github_query)
        elif mode == 'awesome':
            results = service.discover_awesome()
        elif mode == 'trending':
            results = service.discover_trending()
        elif mode == 'hidden_gems':
            results = service.discover_hidden_gems()
        elif mode == 'serendipity':
            results = service.discover_serendipity()
        
        # Cache for 30 minutes
        if results:
            cache.set(cache_key, results, 1800)
        
    return render(request, 'core/partials/repo_list.html', {'repos': results, 'mode': mode})

@login_required
def analyze_repo(request):
    """Initiates deep analysis of a GitHub repository."""
    repo_url = request.GET.get('url', '')
    
    # Parse owner and repo name from URL
    # Expected format: https://github.com/owner/repo
    try:
        parts = repo_url.rstrip('/').split('/')
        owner = parts[-2]
        repo = parts[-1]
    except:
        return HttpResponse("Invalid GitHub URL", status=400)
    
    # Create or get analysis session
    session, created = RepoAnalysisSession.objects.get_or_create(
        user=request.user,
        repo_owner=owner,
        repo_name=repo,
        defaults={'repo_url': repo_url}
    )
    
    return redirect('repo_chat', session_id=session.id)

@login_required
def repo_chat_interface(request, session_id):
    """Renders the repository analysis chat interface."""
    session = get_object_or_404(RepoAnalysisSession, user=request.user, id=session_id)
    return render(request, 'core/repo_chat.html', {'repo_session': session})

@login_required
def send_repo_message(request, session_id):
    """Handles messages in repository analysis chat."""
    if request.method == 'POST':
        session = get_object_or_404(RepoAnalysisSession, user=request.user, id=session_id)
        user_msg_text = request.POST.get('message')
        
        # Save user message
        user_msg = RepoMessage.objects.create(session=session, sender='user', message=user_msg_text)
        
        # Prepare repository context
        analyzer = GitHubRepoAnalyzer()
        repo_context = analyzer.prepare_deep_context(session.repo_owner, session.repo_name)
        
        # Add structure summary
        if repo_context.get('structure'):
            repo_context['structure_summary'] = analyzer.generate_structure_summary(repo_context['structure'])
        
        # Get chat history (exclude the message we just created)
        history = []
        all_messages = list(session.messages.order_by('timestamp'))
        for msg in all_messages[:-1]:  # Exclude the last message (current user message)
            role = 'user' if msg.sender == 'user' else 'model'
            history.append({'role': role, 'parts': [msg.message]})
        
        # Get language
        lang_code = request.LANGUAGE_CODE
        
        # Get AI response
        engine = get_gemini_engine(request.user)
        ai_response_text = engine.chat_with_repo(user_msg_text, repo_context, history=history, language=lang_code)
        
        # Save AI message
        ai_msg = RepoMessage.objects.create(session=session, sender='ai', message=ai_response_text)
        
        # Return both messages
        user_msg_html = render_to_string('core/partials/repo_message.html', {'message': user_msg}, request=request)
        ai_msg_html = render_to_string('core/partials/repo_message.html', {'message': ai_msg}, request=request)
        
        return HttpResponse(user_msg_html + ai_msg_html)
    
    return HttpResponse(status=400)


@login_required
@login_required
def settings_view(request):
    from django.contrib import messages
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        gemini_key = request.POST.get('gemini_api_key', '').strip()
        github_token = request.POST.get('github_token', '').strip()
        
        # Update API keys
        if gemini_key:
            profile.gemini_api_key = gemini_key
        if github_token:
            profile.github_access_token = github_token
            
        profile.save()
        messages.success(request, '✅ API keys saved successfully!')
        return redirect('settings')
        
    return render(request, 'core/settings.html')

