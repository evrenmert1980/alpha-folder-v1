import os, requests, base64, subprocess
from datetime import datetime, timedelta
import google.generativeai as genai

GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_NAME = "evrenmert1980/alpha-folder-v1"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def run_alpha_engine():
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=language:python created:>{last_week}&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        repos = requests.get(url, headers=headers).json().get('items', [])[:1]
        for repo in repos:
            name = repo['name']
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_res = requests.get(readme_url, headers=headers).json()
            readme_text = base64.b64decode(readme_res['content']).decode('utf-8')
            
            response = model.generate_content(f"Ozetle: {readme_text[:1000]}")
            
            if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
            with open(f"P_SOLUTIONS/{name}_Analiz.txt", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            subprocess.run(["git", "config", "user.name", "AlphaBot"])
            subprocess.run(["git", "config", "user.email", "bot@alpha.com"])
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", f"Analiz: {name}"])
            # KRIZ COZUCU SATIR:
            subprocess.run(["git", "push", f"https://x-access-token:{GITHUB_TOKEN}@github.com/{REPO_NAME}.git", "HEAD:main"])
            print(f"[SUCCESS] {name} yuklendi.")
    except Exception as e: print(f"Hata: {e}")

if __name__ == "__main__": run_alpha_engine()
