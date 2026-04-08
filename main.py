import os
import subprocess
import requests
from google import genai

TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    try:
        # 1. API Sürümünü v1 olarak net şekilde tanımlıyoruz
        client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1'})
        
        # 2. Veri Çekme
        url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        res = requests.get(url, headers=headers).json()
        repo = res.get('items', [])[0]
        name = repo['name']
        
        # 3. Gemini ile Analiz
        # NOT: 'models/gemini-1.5-flash' şeklinde tam yol kullanmak 404 hatalarını genelde çözer.
        response = client.models.generate_content(
            model="models/gemini-1.5-flash", 
            contents=f"Bu '{name}' projesi ne yapar? Tek cumle."
        )
        
        output_text = f"PROJE: {name}\n\nANALIZ:\n{response.text}"
        file_name = f"{name}_Analiz"
        
    except Exception as e:
        # Hata devam ederse raporu klasöre yazmaya devam et ki görelim
        output_text = f"Guncel Hata: {str(e)}"
        file_name = "Hata_Logu_Son"

    # 4. Kayıt ve Push
    if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
    file_path = f"P_SOLUTIONS/{file_name}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Otonom Analiz: v1-Fix"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    run()
