import os
import subprocess
import requests
from google import genai

TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    # 1. Gemini Yapılandırması (v1 stabil sürüme zorla)
    client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
    
    # 2. GitHub'dan veri çek
    url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
    headers = {"Authorization": f"token {TOKEN}"}
    res = requests.get(url, headers=headers).json()
    repo = res.get('items', [])[0]
    name = repo['name']
    
    # 3. Gemini ile analiz
    print(f"[*] {name} analiz ediliyor...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Bu '{name}' projesini tek bir teknik cumleyle anlat."
    )
    
    # 4. Dosya Yazma
    if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
    file_path = f"P_SOLUTIONS/{name}_Analiz.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    # 5. GitHub'a Gönder
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"Otonom Analiz: {name}"])
    subprocess.run(["git", "push"])
    print("[SUCCESS] Islem tamamlandi.")

if __name__ == "__main__":
    run()
