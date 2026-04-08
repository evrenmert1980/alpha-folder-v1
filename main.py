import os
import requests
import base64
from datetime import datetime, timedelta
import google.generativeai as genai

# 1. AYARLAR VE ANAHTARLAR
GITHUB_TOKEN = os.getenv("MY_GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Yapılandırması
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def run_alpha_engine():
    print(f"[*] Operasyon Basladi: {datetime.now()}")
    
    # 2. TARAYICI: Son 7 gunun trend Python projelerini bul
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=language:python created:>{last_week}&sort=stars&order=desc"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        repos = requests.get(url, headers=headers).json().get('items', [])[:1] # Test icin ilk 1 projeyi aliyoruz
        
        for repo in repos:
            name = repo['name']
            print(f"[+] Proje bulundu: {name}")
            
            # 3. GURULTUYU OKU (README)
            readme_url = f"https://api.github.com/repos/{repo['full_name']}/readme"
            readme_data = requests.get(readme_url, headers=headers).json()
            readme_text = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # 4. KATLAMA (GEMINI ILE COZUME DONUSTUR)
            prompt = f"Bu karmaşık projenin README verisini al ve kurulum gerektirmeyen, tek dosyada çalışan basit bir Python çözümüne indirge: {readme_text[:2000]}"
            response = model.generate_content(prompt)
            p_solution = response.text
            
            # 5. DOSYALAMA (P-Solution klasorune kaydet)
            if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
            with open(f"P_SOLUTIONS/{name}_Solution.txt", "w", encoding="utf-8") as f:
                f.write(f"PROJE: {name}\n\nCOZUM:\n{p_solution}")
            
            print(f"[SUCCESS] {name} katlandi ve P_SOLUTIONS klasorune eklendi.")
            
    except Exception as e:
        print(f"[!] Hata olustu: {e}")

if __name__ == "__main__":
    run_alpha_engine()
