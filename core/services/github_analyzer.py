import requests
from django.conf import settings

class GitHubRepoAnalyzer:
    """
    Deep analyzer for GitHub repositories.
    Fetches file tree, critical files, and prepares context for AI analysis.
    """
    
    def __init__(self, access_token=None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        token = access_token or getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def get_repo_structure(self, owner, repo, branch="main"):
        """
        Fetches the complete file tree of a repository.
        Returns a dict with folders, files, and their paths.
        """
        # Try both main and master branches
        for try_branch in [branch, "master", "develop"]:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{try_branch}?recursive=1"
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    tree = response.json().get("tree", [])
                    
                    # Organize by type
                    structure = {
                        "directories": [],
                        "files": [],
                        "config_files": [],
                        "entry_points": [],
                        "test_files": [],
                        "branch": try_branch
                    }
                    
                    for item in tree:
                        path = item.get("path", "")
                        item_type = item.get("type", "")
                        
                        if item_type == "tree":
                            structure["directories"].append(path)
                        elif item_type == "blob":
                            structure["files"].append(path)
                            
                            # Identify critical files
                            if any(config in path.lower() for config in [
                                "package.json", "requirements.txt", "composer.json",
                                "cargo.toml", "go.mod", "pom.xml", "build.gradle",
                                "dockerfile", "docker-compose"
                            ]):
                                structure["config_files"].append(path)
                            
                            # Identify entry points
                            if any(entry in path.lower() for entry in [
                                "main.py", "app.py", "index.js", "main.js", "app.js",
                                "main.go", "main.rs", "index.html", "server.py"
                            ]):
                                structure["entry_points"].append(path)
                            
                            # Identify test files
                            if "test" in path.lower() or "spec" in path.lower():
                                structure["test_files"].append(path)
                    
                    return structure
                    
            except requests.exceptions.Timeout:
                print(f"Timeout while fetching tree for branch {try_branch}")
                continue
            except Exception as e:
                print(f"Error fetching tree for branch {try_branch}: {e}")
                continue
        
        # If all branches fail, return empty structure
        print(f"Could not fetch structure for {owner}/{repo}")
        return None
    
    def get_file_content(self, owner, repo, file_path):
        """
        Fetches the raw content of a specific file from the repository.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # GitHub returns base64 encoded content
            import base64
            content = base64.b64decode(data.get("content", "")).decode("utf-8")
            return content
        except Exception as e:
            print(f"Error fetching file {file_path}: {e}")
            return None
    
    def get_readme(self, owner, repo):
        """
        Fetches the README.md content.
        """
        return self.get_file_content(owner, repo, "README.md")
    
    def prepare_deep_context(self, owner, repo):
        """
        Prepares a comprehensive context for AI analysis.
        Includes: README, file structure, and critical file contents.
        """
        context = {
            "owner": owner,
            "repo": repo,
            "readme": "",
            "structure": None,
            "critical_files": {}
        }
        
        # Fetch README
        readme = self.get_readme(owner, repo)
        if readme:
            context["readme"] = readme[:8000]  # Limit to 8000 chars
        
        # Fetch structure
        structure = self.get_repo_structure(owner, repo)
        if structure:
            context["structure"] = structure
            
            # Fetch critical files (limit to avoid token overflow)
            files_to_fetch = []
            
            # Prioritize: entry points > config files
            files_to_fetch.extend(structure["entry_points"][:2])  # Max 2 entry points
            files_to_fetch.extend(structure["config_files"][:3])  # Max 3 config files
            
            for file_path in files_to_fetch:
                content = self.get_file_content(owner, repo, file_path)
                if content:
                    # Limit each file to 2000 chars
                    context["critical_files"][file_path] = content[:2000]
        
        return context
    
    def generate_structure_summary(self, structure):
        """
        Generates a human-readable summary of the repository structure.
        """
        if not structure:
            return "No structure available."
        
        summary = f"""
Repository Structure Overview:
- Total Directories: {len(structure['directories'])}
- Total Files: {len(structure['files'])}
- Configuration Files: {', '.join(structure['config_files'][:5]) or 'None'}
- Entry Points: {', '.join(structure['entry_points']) or 'None'}
- Has Tests: {'Yes' if structure['test_files'] else 'No'}

Key Directories:
{chr(10).join(f'  - {d}' for d in structure['directories'][:10])}
"""
        return summary
