import os
import subprocess
import requests
import json
import sys

def get_pr_info():
    """Extract PR information from GitHub event data."""
    try:
        event_path = os.environ['GITHUB_EVENT_PATH']
        with open(event_path, 'r') as f:
            event = json.load(f)
        
        pr_number = event['pull_request']['number']
        base_sha = event['pull_request']['base']['sha']
        head_sha = event['pull_request']['head']['sha']
        
        return pr_number, base_sha, head_sha
    except (KeyError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading GitHub event data: {e}")
        sys.exit(1)

def get_code_diff(base_sha, head_sha):
    """Get the diff between base and head commits."""
    try:
        # Fetch the base branch to ensure we have the latest
        subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
        
        # Get the diff
        result = subprocess.run(
            ["git", "diff", f"{base_sha}...{head_sha}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        return None

# Get PR information
pr_number, base_sha, head_sha = get_pr_info()
print(f"Processing PR #{pr_number}")

# Get the diff of the PR
diff = get_code_diff(base_sha, head_sha)

if not diff or not diff.strip():
    print("No code changes found.")
    exit(0)

# Truncate diff if too long (Gemini has token limits)
max_diff_length = 8000
if len(diff) > max_diff_length:
    diff = diff[:max_diff_length] + "\n\n... (diff truncated due to length)"

# Prepare Gemini prompt
prompt = f"""
You are a senior developer. Review the following GitHub pull request diff:

{diff}

Provide clear feedback in markdown about:
- Code quality
- Potential bugs
- Suggestions for improvement

Be concise but thorough. If the code looks good, mention that too.
"""

# Send to Gemini
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 1000
    }
}

try:
    response = requests.post(f"{url}?key={os.environ['GEMINI_API_KEY']}", headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    # Check if we have a valid response
    if 'candidates' not in result or len(result['candidates']) == 0:
        print(f"No candidates in response: {result}")
        sys.exit(1)
    
    message = result['candidates'][0]['content']['parts'][0]['text']
    
except requests.exceptions.RequestException as e:
    print(f"Error calling Gemini API: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response status: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
    sys.exit(1)
except (KeyError, IndexError) as e:
    print(f"Error parsing Gemini response: {e}")
    print(f"Full response: {result}")
    sys.exit(1)
# Format the message with a header
formatted_message = f"""## 🤖 AI Code Review (Gemini)

{message}

---
*This review was generated automatically by Google Gemini.*
"""

# Post review as a PR comment
comment_url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
comment_headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}
comment_body = {"body": formatted_message}

try:
    r = requests.post(comment_url, headers=comment_headers, json=comment_body, timeout=30)
    r.raise_for_status()
    print("Posted review comment:", r.status_code)
except requests.exceptions.RequestException as e:
    print(f"Error posting comment: {e}")
    sys.exit(1)
