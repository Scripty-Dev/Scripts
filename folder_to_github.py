import os
import subprocess
import json
import sys

public_description = "Creates a GitHub repository and uploads the contents of a local folder to it."

def upload_folder_to_github(folder_path, repo_name, github_username, github_token, private=True):
    """
    Creates a GitHub repository and uploads the contents of a folder to it.
    
    Args:
        folder_path: Path to the local folder
        repo_name: Name for the new GitHub repository
        github_username: Your GitHub username
        github_token: Your GitHub personal access token
        private: Whether the repository should be private (default: True)
    """
    # Save the current directory
    original_dir = os.getcwd()
    
    try:
        # Change to the folder to upload
        os.chdir(folder_path)
        
        # Initialize git repository
        subprocess.run(["git", "init"], check=True)
        
        # Check if remote exists and remove it
        try:
            subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.PIPE)
        except:
            pass  # It's okay if this fails
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit the files
        try:
            subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        except:
            subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial commit"], check=True)
        
        # Create repository using GitHub API
        create_repo_data = f'{{"name":"{repo_name}","private":{str(private).lower()}}}'
        
        create_repo_cmd = [
            "curl", "-s", "-X", "POST",
            "-H", f"Authorization: token {github_token}", 
            "-H", "Accept: application/vnd.github.v3+json",
            "https://api.github.com/user/repos", 
            "-d", create_repo_data
        ]
        
        result = subprocess.run(create_repo_cmd, capture_output=True, text=True)
        
        if "Bad credentials" in result.stdout or "Bad credentials" in result.stderr:
            return {"error": "GitHub token is invalid. Please check your token has the 'repo' scope."}
        
        if "already exists" in result.stdout or "already exists" in result.stderr:
            print(f"Repository {repo_name} already exists, continuing with push.")
        
        # Add the remote
        remote_url = f"https://{github_username}:{github_token}@github.com/{github_username}/{repo_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        
        # Push to GitHub
        push_result = subprocess.run(["git", "push", "-u", "origin", "master"], capture_output=True, text=True)
        
        if push_result.returncode == 0:
            return {"message": f"Successfully uploaded folder to https://github.com/{github_username}/{repo_name}"}
        else:
            # Try pushing to main branch instead
            push_main_result = subprocess.run(["git", "push", "-u", "origin", "master:main"], capture_output=True, text=True)
            if push_main_result.returncode == 0:
                return {"message": f"Successfully uploaded folder to https://github.com/{github_username}/{repo_name} (main branch)"}
            else:
                return {"error": f"Push failed: {push_main_result.stderr}"}
        
    except subprocess.CalledProcessError as e:
        return {"error": f"Git operation failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Error during GitHub upload: {str(e)}"}
    finally:
        # Change back to the original directory
        os.chdir(original_dir)

async def function(args):
    try:
        folder_path = os.path.expanduser(args.get("folder_path", ""))
        repo_name = args.get("repo_name", "")
        github_username = args.get("github_username", "")
        github_token = args.get("github_token", "")
        is_private = args.get("private", True)
        
        if not folder_path or not repo_name or not github_username or not github_token:
            return json.dumps({
                "error": "Missing required parameters",
                "token_instructions": "To create a GitHub token:\n1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)\n2. Click 'Generate new token' → 'Generate new token (classic)'\n3. Name your token (e.g., 'Repo Creator')\n4. Select the 'repo' scope checkbox\n5. Click 'Generate token' at the bottom\n6. Copy your token"
            })
        
        if not os.path.exists(folder_path):
            return json.dumps({"error": f"Folder not found: {folder_path}"})
            
        result = upload_folder_to_github(folder_path, repo_name, github_username, github_token, is_private)
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# Define object structure for AI assistant compatibility
public_description = "Create a GitHub repository from a local folder."

object = {
    "name": "github_upload",
    "description": """Create a GitHub repository from a local folder and upload all its contents.

Example:
"upload my project folder to GitHub"
→ {"folder_path": "~/Projects/my-app", "repo_name": "my-app", "github_username": "username", "github_token": "your-token", "private": true}

Note: You need a GitHub personal access token with 'repo' scope to use this function.""",
    "parameters": {
        "type": "object",
        "properties": {
            "folder_path": {
                "type": "string",
                "description": "Path to the local folder to upload (use ~ for home directory)"
            },
            "repo_name": {
                "type": "string",
                "description": "Name for the new GitHub repository"
            },
            "github_username": {
                "type": "string",
                "description": "GitHub username"
            },
            "github_token": {
                "type": "string",
                "description": "GitHub personal access token with repo scope"
            },
            "private": {
                "type": "boolean",
                "description": "Whether the GitHub repository should be private",
                "default": True
            }
        },
        "required": ["folder_path", "repo_name", "github_username", "github_token"]
    }
}

# If running directly (not imported)
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schema":
        print(json.dumps(object))
        sys.exit(0)
        
    if len(sys.argv) >= 5:
        folder_path = os.path.expanduser(sys.argv[1])
        repo_name = sys.argv[2]
        github_username = sys.argv[3]
        github_token = sys.argv[4]
        is_private = True if len(sys.argv) <= 5 or sys.argv[5].lower() == "true" else False
        
        result = upload_folder_to_github(folder_path, repo_name, github_username, github_token, is_private)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python folder_to_github.py <folder_path> <repo_name> <github_username> <github_token> [private]")
        print("Or: python folder_to_github.py --schema (to print the JSON schema)")