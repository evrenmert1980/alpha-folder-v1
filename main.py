import os
import requests
import base64
import subprocess
from datetime import datetime, timedelta
import google.generativeai as genai

# AYARLAR
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Yeni Model Yapılandırması (Guncel ve Hizli)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def run_alpha_engine():
    print(f"[*] Operasyon Basladi: {datetime.now()}")
    
    # 1. TARAYICI (Son 7 gunun populer Python projeleri)
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=language:python created:>{last_week}&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        repos = response.json().get('items', [])[:1]
        
        if not repos:
            print("[!] Yeni proje bulunamadi.")
            return

        for repo in repos:
            name = repo['name']
            full_name = repo['full_name']
            print(f"[+] Analiz ediliyor: {name}")
            
            readme_url = f"https://api.github.com/repos/{full_name}/readme"
            readme_res = requests.get(readme_url, headers=headers).json()
            readme_text = base64.b64decode(readme_res['content']).decode('utf-8')
            
            # 2. KATLAMA (Gemini 1.5 Flash ile)
            prompt = f"Bu projenin amacini ve ne ise yaradigini 3 maddede ozetle: {readme_text[:1500]}"
            response = model.generate_content(prompt)
            p_solution = response.text
            
            # 3. DOSYALAMA
            if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
            file_path = f"P_SOLUTIONS/{name}_Analiz.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"PROJE: {name}\nLINK: https://github.com/{full_name}\n\nANALIZ:\n{p_solution}")
            
            # 4. GITHUB'A GONDER
            subprocess.run(["git", "config", "user.name", "AlphaBot"])
            subprocess.run(["git", "config", "user.email", "bot@alpha.com"])
            subprocess.run(["git", "add", "."])
            subprocess.run(["git", "commit", "-m", f"Otonom Analiz: {name}"])
            subprocess.run(["git", "push"])
            
            print(f"[SUCCESS] {name} dosyasi ana sayfaya eklendi.")
            
    except Exception as e:
        print(f"[!] Kritik Hata: {e}")

if __name__ == "__main__":
    run_alpha_engine()
