import os
import subprocess
import requests
from google import genai

TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    try:
        # 1. v1 Sürümünü zorlamak için yapılandırma
        client = genai.Client(api_key=API_KEY)
        
        # 2. Veri Kaynağı
        url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
        headers = {"Authorization": f"token {TOKEN}"}
        res = requests.get(url, headers=headers).json()
        repo = res.get('items', [])[0]
        name = repo['name']
        
        # 3. Gemini ile Analiz
        # NOT: Eğer 'gemini-1.5-flash' bulunamıyorsa 'models/gemini-1.5-flash' 
        # veya 'gemini-1.5-flash-latest' denemek standart çözümdür.
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"Bu '{name}' projesini 2 cumleyle ozetle."
        )
        
        output_text = f"PROJE: {name}\n\nANALIZ:\n{response.text}"
        file_name = f"{name}_Analiz"
        
    except Exception as e:
        # Hata devam ederse buradaki ismi 'gemini-1.5-flash-latest' yaparak tekrar dene
        output_text = f"Hata Detayi: {str(e)}"
        file_name = "Hata_Logu"

    # 4. Dosya Yazma ve Push
    if not os.path.exists("P_SOLUTIONS"): os.makedirs("P_SOLUTIONS")
    file_path = f"P_SOLUTIONS/{file_name}.txt"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)
    
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Otonom Kayit Update"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    run()
