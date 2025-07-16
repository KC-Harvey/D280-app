import os
import subprocess
import requests

# Get the diff of the PR
diff = subprocess.check_output(["git", "diff", "origin/main...HEAD"], text=True)

if not diff.strip():
    print("No code changes found.")
    exit(0)

# Prepare Gemini prompt
prompt = f"""
You are a senior developer. Review the following GitHub pull request diff:

{diff}

Provide clear feedback in markdown about:
- Code quality
- Potential bugs
- Suggestions for improvement
"""

# Send to Gemini
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 800
    }
}
response = requests.post(f"{url}?key={os.environ['GEMINI_API_KEY']}", headers=headers, json=payload)
result = response.json()

message = result['candidates'][0]['content']['parts'][0]['text']

# Post review as a PR comment
pr_number = os.environ['GITHUB_REF'].split('/')[-1]

comment_url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
comment_headers = {
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "Accept": "application/vnd.github+json"
}
comment_body = {"body": message}
r = requests.post(comment_url, headers=comment_headers, json=comment_body)

print("Posted review comment:", r.status_code)
