import os, subprocess, google.generativeai as genai
import requests, base64
from datetime import datetime, timedelta

# Ayarlar
TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def run():
    # 1. Trend bir proje bul
    url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
    headers = {"Authorization": f"token {TOKEN}"}
    repo = requests.get(url, headers=headers).json().get('items', [])[0]
    name = repo['name']
    
    # 2. Gemini ile analiz et
    prompt = f"Bu projeyi 3 madde ile teknik olarak ozetle: {name}"
    response = model.generate_content(prompt)
    
    # 3. Klasore kaydet
    if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
    file_path = f"P_SOLUTIONS/{name}_Analiz.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"PROJE: {name}\n\n{response.text}")
    
    # 4. GitHub'a Gonder (Calisan yontem)
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Otonom Analiz: {name}"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    run()
