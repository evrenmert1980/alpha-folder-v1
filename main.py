import os
import subprocess
import requests
import json

# Kasadan anahtarları çek
TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run_alpha_engine():
    name = "Bilinmeyen_Proje" # Değişkeni önden tanımlıyoruz (Hata almamak için)
    try:
        # 1. GitHub Verisi
        github_url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        
        repo_res = requests.get(github_url, headers=headers)
        repo_data = repo_res.json()
        
        if 'items' in repo_data and repo_data['items']:
            repo = repo_data['items'][0]
            name = repo['name']
            description = repo.get('description', 'Aciklama yok.')
        else:
            raise Exception("GitHub verisi bos dondu.")

        # 2. Gemini Analizi
        gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"Bu '{name}' projesini teknik olarak 2 cumleyle analiz et."}]
            }]
        }
        
        gemini_res = requests.post(gemini_url, json=payload)
        res_json = gemini_res.json()
        
        if gemini_res.status_code == 200:
            analysis = res_json['candidates'][0]['content']['parts'][0]['text']
            output_text = f"PROJE: {name}\n\nANALIZ:\n{analysis}"
            file_name = f"{name}_Analiz"
        else:
            output_text = f"Gemini Hatasi: {gemini_res.text}"
            file_name = "Hata_Gemini"

    except Exception as e:
        output_text = f"Sistem Hatasi: {str(e)}"
        file_name = "Hata_Logu"

    # 3. Dosya Yazma ve Push
    if not os.path.exists("P_SOLUTIONS"):
        os.makedirs("P_SOLUTIONS")
        
    file_path = f"P_SOLUTIONS/{file_name}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    # Git Operasyonu
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
        subprocess.run(["git", "add", "."])
        # Değişiklik var mı kontrolü
        diff = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if diff.stdout:
            subprocess.run(["git", "commit", "-m", f"Otonom Kayit: {name}"])
            # Push komutunda token kullanarak yetkiyi garantileyelim
            repo_url = f"https://x-access-token:{TOKEN}@github.com/evrenmert1980/alpha-folder-v1.git"
            subprocess.run(["git", "push", repo_url, "HEAD:main"])
            print(f"[SUCCESS] {name} yuklendi.")
        else:
            print("[INFO] Yeni dosya yok.")
    except Exception as git_err:
        print(f"[!] Git Hatasi: {git_err}")

if __name__ == "__main__":
    run_alpha_engine()
