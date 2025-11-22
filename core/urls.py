from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('analyze/<int:item_id>/', views.analyze_item, name='analyze_item'),
    path('chat/start/<int:item_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/', views.chat_interface, name='chat_interface'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('sessions/clear/', views.clear_sessions, name='clear_sessions'),
    path('github/', views.github_surf, name='github_surf'),
    path('github/discover/', views.github_discover, name='github_discover'),
    path('github/analyze/', views.analyze_repo, name='analyze_repo'),
    path('repo/chat/<int:session_id>/', views.repo_chat_interface, name='repo_chat'),
    path('repo/chat/<int:session_id>/send/', views.send_repo_message, name='send_repo_message'),
    path('settings/', views.settings_view, name='settings'),
]
