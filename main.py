import os
from google import genai

API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    client = genai.Client(api_key=API_KEY)
    
    print("[*] Mevcut Modeller Listeleniyor...")
    try:
        # Google'dan senin API anahtarınla erişebileceğin modelleri soruyoruz
        for m in client.models.list():
            print(f"-> Model Adi: {m.name} | Desteklenen Metotlar: {m.supported_generation_methods}")
    except Exception as e:
        print(f"[!] Liste cekilirken hata oluştu: {e}")

if __name__ == "__main__":
    run()
