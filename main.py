import os
import subprocess
import requests
from google import genai

TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    try:
        # 1. En güncel istemci yapılandırması
        client = genai.Client(api_key=API_KEY)
        
        # 2. Veri Kaynağı (GitHub Trendleri)
        url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        res = requests.get(url, headers=headers).json()
        repo = res.get('items', [])[0]
        name = repo['name']
        
        # 3. Gemini ile Analiz (En güvenli model ismi)
        # 2026 standartlarında 'gemini-1.5-flash' en stabil olandır.
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Bu '{name}' projesini 2 cumleyle ozetle."
        )
        
        output_text = f"PROJE: {name}\n\nANALIZ:\n{response.text}"
        
    except Exception as e:
        # Eğer bir hata olursa, hatayı klasöre dosya olarak yaz (Görmemizi sağlar)
        output_text = f"Hata Olustu: {str(e)}"
        name = "Hata_Raporu"

    # 4. Klasör ve Dosya İşlemleri
    if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
    file_path = f"P_SOLUTIONS/{name}.txt"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    # 5. GitHub'a Gönder
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Otonom Kayit: {name}"])
        subprocess.run(["git", "push"])
        print("[SUCCESS] İslem tamamlandi.")
    except:
        print("[!] Git push hatasi.")

if __name__ == "__main__":
    run()
