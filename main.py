import os, subprocess, google.generativeai as genai

# Ayarlar
TOKEN = os.getenv("MY_GITHUB_TOKEN")
API_KEY = os.getenv("GEMINI_API_KEY")

def run():
    # Klasor yarat
    if not os.path.exists("P_SOLUTIONS"):
        os.makedirs("P_SOLUTIONS")
    
    # Test dosyasi olustur (Saat bilgisini ekleyelim ki degisiklik olsun)
    import datetime
    now = datetime.datetime.now().strftime("%H-%M-%S")
    file_name = f"P_SOLUTIONS/test_{now}.txt"
    
    with open(file_name, "w") as f:
        f.write(f"Otonom test basarili! Saat: {now}")
    
    # GitHub'a Gonder
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"])
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Otonom dosya ekleme"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    run()
