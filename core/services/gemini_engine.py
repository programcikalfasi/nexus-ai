import google.generativeai as genai
from django.conf import settings
import json

class GeminiEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            # Fallback or handle gracefully if no key is present
            pass
        else:
            genai.configure(api_key=self.api_key)
            # Updated to gemini-2.0-flash based on available models for this key
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def analyze_content(self, text, language='en'):
        if not hasattr(self, 'model'):
             return {
                "hype_score": 0,
                "difficulty": "Unknown",
                "summary": "API Key missing.",
                "tech_stack": []
            }

        lang_instruction = "Respond in English."
        if language == 'tr':
            lang_instruction = "Respond in Turkish. Translate technical terms only if commonly used in Turkish, otherwise keep them in English."

        prompt = f"""
        You are an expert tech analyst. Analyze the following Reddit discussion/article and provide a structured JSON response.
        {lang_instruction}
        
        Content:
        {text[:8000]}
        
        Return ONLY a valid JSON object with these exact keys:
        - hype_score: (integer 0-100) How much excitement/buzz is there?
        - difficulty: (string) "Easy", "Medium", or "Hard" to understand/implement. (Translate these values to Turkish if language is Turkish: "Kolay", "Orta", "Zor")
        - summary: (string) A concise 2-3 sentence summary of the main points in the requested language.
        - tech_stack: (list of strings) Any specific technologies, libraries, or models mentioned.
        """
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text
            # Clean up markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            return json.loads(result_text.strip())
        except Exception as e:
            print(f"Gemini Analysis Error: {e}")
            return {
                "hype_score": 0,
                "difficulty": "Unknown",
                "summary": "Analysis failed.",
                "tech_stack": []
            }

    def chat_with_repo(self, user_message, repo_context, history=[], language='en'):
        """
        Chat interface specifically for deep repository analysis.
        Includes file structure, README, and critical files as context.
        """
        if not hasattr(self, 'model'):
            return "Error: Gemini API Key is missing."

        lang_instruction = "Respond in English."
        if language == 'tr':
            lang_instruction = "Respond in Turkish."

        # Build comprehensive system prompt
        system_prompt = f"""
You are a Senior Code Auditor and Software Architect with 15+ years of experience. {lang_instruction}

REPOSITORY ANALYSIS CONTEXT:
Repository: {repo_context.get('owner')}/{repo_context.get('repo')}

README.md (First 8000 chars):
{repo_context.get('readme', 'No README available')}

REPOSITORY STRUCTURE:
{repo_context.get('structure_summary', 'No structure available')}

CRITICAL FILES CONTENT:
"""
        
        # Add critical file contents
        for file_path, content in repo_context.get('critical_files', {}).items():
            system_prompt += f"\n\n--- {file_path} ---\n{content}\n"
        
        system_prompt += """

YOUR ROLE:
1. Analyze the architecture and design patterns used
2. Identify all libraries, frameworks, and dependencies
3. Critique the code organization and structure
4. Explain how different components interact
5. Point out potential improvements or issues
6. Answer specific technical questions about the codebase

When answering:
- Be direct and technical
- Reference specific files when relevant
- If you don't have enough context about a file, say so
- Suggest which files to examine for more details
"""

        # Start chat with history
        chat = self.model.start_chat(history=history)
        
        # For first message, include full context
        if not history:
            full_message = f"{system_prompt}\n\nUser Question: {user_message}"
        else:
            full_message = user_message
        
        try:
            response = chat.send_message(full_message)
            return response.text
        except Exception as e:
            return f"Error analyzing repository: {e}"

    def generate_research_strategy(self, user_prompt):
        """
        Step 1: Generates 3-5 distinct GitHub search queries from a complex user prompt.
        Returns a list of search queries covering different angles.
        """
        if not hasattr(self, 'model'):
            return [user_prompt]

        prompt = f"""
You are a GitHub Search Strategist. The user wants to do deep research with this complex request:

"{user_prompt}"

Your job: Generate 3-5 DISTINCT GitHub Search API queries to cover different angles of this request.

Strategy:
- Query A: Broad/General search (main topics/language)
- Query B: Niche/Specific tags (advanced features, patterns)
- Query C: Trending/Recent (created recently, high activity)
- Query D (optional): Quality filters (well-documented, production-ready)
- Query E (optional): Alternative approaches or related topics

Rules:
1. Use valid GitHub qualifiers: topic:, language:, stars:, created:, pushed:, size:
2. Each query must be DIFFERENT (don't repeat the same logic)
3. Return ONLY a JSON array of query strings, no explanations
4. Example format: ["topic:networking language:rust stars:>500", "topic:async-io topic:p2p language:rust", "language:rust created:>2024-01-01 stars:50..500"]

Output (JSON array only):
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up markdown code blocks if present
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            queries = json.loads(result_text.strip())
            return queries if isinstance(queries, list) else [user_prompt]
        except Exception as e:
            print(f"Error generating research strategy: {e}")
            return [user_prompt]

    def filter_repositories(self, user_prompt, repo_list):
        """
        Step 3: Analyzes a list of repositories and filters them based on the user's specific request.
        Returns curated list with reasoning.
        """
        if not hasattr(self, 'model'):
            return repo_list[:10]

        # Prepare repo data for analysis
        repo_data = []
        for repo in repo_list[:60]:  # Limit to 60 to avoid token overflow
            repo_data.append({
                "name": f"{repo.get('owner', {}).get('login', '')}/{repo.get('name', '')}",
                "description": repo.get('description', 'No description')[:200],
                "topics": repo.get('topics', [])[:5],
                "stars": repo.get('stargazers_count', 0),
                "updated": repo.get('updated_at', '')[:10],
                "language": repo.get('language', 'N/A')
            })

        prompt = f"""
You are a Senior Developer doing code research. The user asked:

"{user_prompt}"

Here are {len(repo_data)} potential repositories found. Your job: CURATE the best matches.

REPOSITORIES:
{json.dumps(repo_data, indent=2)}

TASK:
1. Analyze each repo against the user's SPECIFIC request
2. Filter out: abandoned projects (no recent updates), too generic, irrelevant to the nuance
3. Pick the TOP 10 that best fit the request
4. For each pick, provide a one-sentence "Why this matches" reason

OUTPUT FORMAT (JSON only):
[
  {{
    "repo": "owner/name",
    "reason": "Why this is a great match for the user's specific request"
  }},
  ...
]

Return ONLY valid JSON array, no extra text:
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up markdown code blocks
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            filtered = json.loads(result_text.strip())
            
            # Map back to full repo objects
            curated_repos = []
            for item in filtered:
                repo_name = item.get('repo', '')
                reason = item.get('reason', '')
                
                # Find matching repo in original list
                for repo in repo_list:
                    full_name = f"{repo.get('owner', {}).get('login', '')}/{repo.get('name', '')}"
                    if full_name == repo_name:
                        repo['ai_reason'] = reason
                        curated_repos.append(repo)
                        break
            
            return curated_repos[:10]
        except Exception as e:
            print(f"Error filtering repositories: {e}")
            return repo_list[:10]

    def generate_github_query(self, user_input):
        """
        Converts natural language input into a strict GitHub Search API query string.
        """
        if not hasattr(self, 'model'):
            return user_input

        prompt = f"""
        You are an expert at GitHub Search Syntax. Convert the following natural language user request into a strict GitHub Search API query string.
        
        User Request: "{user_input}"
        
        Rules:
        1. Use only valid GitHub qualifiers: topic:, language:, stars:, created:, pushed:, user:, org:.
        2. Do NOT include any explanation. Return ONLY the query string.
        3. If the user asks for "popular" or "best", assume stars:>500.
        4. If the user asks for "recent" or "new", assume created:>2024-01-01 (adjust year as needed).
        
        Examples:
        - "python web frameworks" -> "topic:web-framework language:python stars:>1000"
        - "tools to build a database in C" -> "topic:database language:c stars:>100"
        - "machine learning papers" -> "topic:machine-learning topic:papers"
        
        Query String:
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Query Generation Error: {e}")
            return user_input

    def chat(self, session_id, user_message, history=[], context=None, language='en'):
        if not hasattr(self, 'model'):
            return "Error: Gemini API Key is missing."

        lang_instruction = "Respond in English."
        if language == 'tr':
            lang_instruction = "Respond in Turkish."

        system_instruction = f"You are a helpful research assistant. {lang_instruction}"
        if context:
            analysis_data = context.get('analysis', {})
            hype = analysis_data.get('hype_score', 'N/A')
            difficulty = analysis_data.get('difficulty', 'N/A')
            tech_stack = ", ".join(analysis_data.get('tech_stack', []))
            summary = analysis_data.get('summary', '')

            system_instruction += f"""
            
            CONTEXT INFORMATION:
            Title: {context.get('title')}
            
            AI ANALYSIS METADATA:
            - Hype Score: {hype}/100
            - Difficulty Level: {difficulty}
            - Identified Tech Stack: {tech_stack}
            - Brief Summary: {summary}
            
            RAW CONTENT SOURCE:
            {context.get('raw_content')[:4000]}
            
            INSTRUCTIONS:
            Use the metadata above to inform your tone. If the hype is low, be skeptical. If difficulty is high, explain concepts simply.
            Answer the user's question based primarily on the content provided above.
            """

        # Convert history to Gemini format if needed, or rely on client to pass correctly formatted history.
        # Here we assume history is passed in a compatible format or we start fresh.
        
        chat = self.model.start_chat(history=history)
        
        full_message = user_message
        if context and not history:
             full_message = f"{system_instruction}\n\nUser Query: {user_message}"
        else:
            # Inject system instruction into the message for context if history exists
            full_message = f"[System Note: {lang_instruction}]\n{user_message}"
        
        try:
            response = chat.send_message(full_message)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"
