import os
import subprocess
import requests
import json

# GitHub Secrets'tan anahtarları çekiyoruz
TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run_alpha_engine():
    try:
        # 1. GitHub'dan Trend Bir Proje Bul (Veri Kaynağı)
        # Python dilinde en çok star alan projeyi seçiyoruz
        github_url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        
        repo_res = requests.get(github_url, headers=headers)
        repo_data = repo_res.json()
        
        if 'items' not in repo_data or not repo_data['items']:
            raise Exception("GitHub'dan proje verisi cekilemedi.")
            
        repo = repo_data['items'][0]
        name = repo['name']
        description = repo.get('description', 'Aciklama yok.')

        # 2. Gemini API - Doğrudan HTTP İsteği (Zeka Katmanı)
        # v1 sürümü üzerinden gemini-1.5-flash modeline bağlanıyoruz
        gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Bu '{name}' projesini ({description}) teknik olarak 2 cumleyle analiz et ve ne ise yaradigini soyle."}]
            }]
        }
        
        gemini_res = requests.post(gemini_url, json=payload)
        res_json = gemini_res.json()
        
        if gemini_res.status_code == 200:
            analysis = res_json['candidates'][0]['content']['parts'][0]['text']
            output_text = f"PROJE: {name}\n\nANALIZ:\n{analysis}"
            file_name = f"{name}_Analiz"
        else:
            output_text = f"Gemini API Hatasi: {gemini_res.status_code}\n{gemini_res.text}"
            file_name = "Hata_Gemini_Baglanti"

    except Exception as e:
        output_text = f"Sistem Hatasi Olustu: {str(e)}"
        file_name = "Hata_Sistem_Logu"

    # 3. Dosya Yazma ve GitHub'a Push (Lojistik)
    if not os.path.exists("P_SOLUTIONS"):
        os.makedirs("P_SOLUTIONS")
        
    file_path = f"P_SOLUTIONS/{file_name}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    # Git komutlarını çalıştırarak dosyayı depoya yüklüyoruz
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
        subprocess.run(["git", "add", "."])
        # Değişiklik yoksa commit hatası almamak için kontrol
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout:
            subprocess.run(["git", "commit", "-m", f"Otonom Analiz Yuklendi: {name}"])
            subprocess.run(["git", "push"])
            print(f"[SUCCESS] {name} dosyasi basariyla yuklendi.")
        else:
            print("[INFO] Yeni bir degisiklik yok, push atlanmadi.")
    except Exception as git_err:
        print(f"[!] Git hatasi: {git_err}")

if __name__ == "__main__":
    run_alpha_engine()
