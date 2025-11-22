"""
Test script for Deep Research functionality without hitting GitHub API
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/Users/nzbmod/Desktop/webuygulamasi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexus_ai.settings')
django.setup()

from core.services.gemini_engine import GeminiEngine

# Test the strategy generation
print("=" * 60)
print("TEST: Deep Research Strategy Generation")
print("=" * 60)

engine = GeminiEngine()

test_prompt = "Find me high-performance Rust networking libraries not yet mainstream"

print(f"\n📝 User Prompt: '{test_prompt}'")
print("\n🧠 Generating research strategy...")

queries = engine.generate_research_strategy(test_prompt)

print(f"\n✨ Generated {len(queries)} search queries:")
for i, query in enumerate(queries, 1):
    print(f"   {i}. {query}")

# Test filtering logic (mock data)
print("\n" + "=" * 60)
print("TEST: Repository Filtering Logic")
print("=" * 60)

mock_repos = [
    {
        'name': 'tokio',
        'owner': {'login': 'tokio-rs'},
        'description': 'A runtime for writing reliable asynchronous applications with Rust',
        'topics': ['async', 'runtime', 'networking'],
        'stargazers_count': 25000,
        'updated_at': '2024-11-20T00:00:00Z',
        'language': 'Rust'
    },
    {
        'name': 'quinn',
        'owner': {'login': 'quinn-rs'},
        'description': 'QUIC protocol implementation in Rust',
        'topics': ['quic', 'networking', 'async'],
        'stargazers_count': 3200,
        'updated_at': '2024-11-19T00:00:00Z',
        'language': 'Rust'
    },
    {
        'name': 'smoltcp',
        'owner': {'login': 'smoltcp-rs'},
        'description': 'A standalone, event-driven TCP/IP stack for embedded systems',
        'topics': ['tcp-ip', 'embedded', 'networking'],
        'stargazers_count': 2800,
        'updated_at': '2024-11-18T00:00:00Z',
        'language': 'Rust'
    }
]

print(f"\n📦 Mock Repositories: {len(mock_repos)}")
print("\n🎯 AI analyzing and filtering...")

filtered = engine.filter_repositories(test_prompt, mock_repos)

print(f"\n✅ Curated to {len(filtered)} repositories:")
for repo in filtered:
    print(f"\n   🔹 {repo.get('owner', {}).get('login')}/{repo.get('name')}")
    if 'ai_reason' in repo:
        print(f"      💡 {repo['ai_reason']}")

print("\n" + "=" * 60)
print("✓ Deep Research Test Complete")
print("=" * 60)
