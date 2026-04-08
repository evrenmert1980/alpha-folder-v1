import os
import requests
import base64
import subprocess
from datetime import datetime, timedelta
import google.generativeai as genai

# AYARLAR
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def run_alpha_engine():
    print(f"[*] Operasyon Basladi: {datetime.now()}")
    
    # 1. TARAYICI
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=language:python created:>{last_week}&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        repos = requests.get(url, headers=headers).json().get('items', [])[:1]
        
        for repo in repos:
            name = repo['name']
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_data = requests.get(readme_url, headers=headers).json()
            readme_text = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # 2. KATLAMA
            prompt = f"Asagidaki projenin teknik ozetini cikar: {readme_text[:1000]}"
            response = model.generate_content(prompt)
            p_solution = response.text
            
            # 3. KLASOR VE DOSYA OLUSTURMA
            if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
            with open(f"P_SOLUTIONS/{name}_Analiz.txt", "w", encoding="utf-8") as f:
                f.write(f"PROJE: {name}\n\nANALIZ:\n{p_solution}")
            
            # 4. KRITIK ADIM: DOSYAYI GITHUB'A YUKLE
            subprocess.run(["git", "config", "user.name", "AlphaBot"])
            subprocess.run(["git", "config", "user.email", "bot@alpha.com"])
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", f"Yeni cozum: {name}"])
            subprocess.run(["git", "push"])
            
            print(f"[SUCCESS] {name} kaydedildi ve yuklendi.")
            
    except Exception as e:
        print(f"[!] Hata: {e}")

if __name__ == "__main__":
    run_alpha_engine()
