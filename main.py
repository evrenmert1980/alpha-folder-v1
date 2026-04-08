import os
import subprocess
import requests
from google import genai # Yeni nesil kütüphane

TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    try:
        # Yeni bağlantı yöntemi
        client = genai.Client(api_key=API_KEY)
        
        # 1. Trend bir proje bul
        url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        res = requests.get(url, headers=headers).json()
        repo = res.get('items', [])[0]
        name = repo['name']
        
        # 2. Gemini ile analiz et (Yeni SDK formatı)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"Bu '{name}' yazilim projesini 2 cumleyle ozetle."
        )
        
        # 3. Klasore kaydet
        if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
        file_path = f"P_SOLUTIONS/{name}_Analiz.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"PROJE: {name}\n\nANALIZ:\n{response.text}")
        
        # 4. GitHub'a Gonder
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Otonom Analiz: {name}"])
        subprocess.run(["git", "push"])
        print("Sistem basariyla calisti.")
        
    except Exception as e:
        print(f"Hata Analizi: {e}")

if __name__ == "__main__":
    run()
