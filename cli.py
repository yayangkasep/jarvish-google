import sys
import os
import json

def prompt_multiline(prompt_text):
    print(f"\n{prompt_text}")
    print("Tempelkan (Paste) konten Anda di bawah ini.")
    print("Setelah selesai, ketik kata 'EOF' di baris baru lalu tekan Enter:")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines).strip()

def configure_env():
    print("\n--- Konfigurasi .env (Telegram & Rahasia) ---")
    token = input("Masukkan TELEGRAM_BOT_TOKEN: ").strip()
    allowed = input("Masukkan TELEGRAM_ALLOWED_USERS (pisahkan dengan koma jika lebih dari satu, misal: 12345,67890): ").strip()
    google_id = input("Masukkan GOOGLE_CLIENT_ID (Boleh dikosongkan sementara): ").strip()
    google_secret = input("Masukkan GOOGLE_CLIENT_SECRET (Boleh dikosongkan sementara): ").strip()
    github_token = input("Masukkan GITHUB_PERSONAL_ACCESS_TOKEN (Boleh dikosongkan): ").strip()
    
    env_content = f"""TELEGRAM_BOT_TOKEN="{token}"
TELEGRAM_ALLOWED_USERS="{allowed}"
ENVIRONMENT_MODE="production"
GOOGLE_CLIENT_ID="{google_id}"
GOOGLE_CLIENT_SECRET="{google_secret}"
ANTIGRAVITY_ENDPOINT="http://localhost:8045/v1/chat/completions"
GITHUB_PERSONAL_ACCESS_TOKEN="{github_token}"
"""
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Berkas .env berhasil dikonfigurasi!")

def configure_antigravity():
    content = prompt_multiline("--- Konfigurasi config/antigravity-accounts.json ---")
    if not content:
        print("Dilewati.")
        return
    try:
        data = json.loads(content)
        os.makedirs('config', exist_ok=True)
        with open("config/antigravity-accounts.json", "w") as f:
            json.dump(data, f, indent=4)
        print("✅ Berkas config/antigravity-accounts.json berhasil disimpan!")
    except json.JSONDecodeError as e:
        print(f"❌ Format JSON tidak valid: {e}")

def configure_credentials():
    content = prompt_multiline("--- Konfigurasi config/credentials.json (Dari Google Cloud) ---")
    if not content:
        print("Dilewati.")
        return
    try:
        data = json.loads(content)
        os.makedirs('config', exist_ok=True)
        with open("config/credentials.json", "w") as f:
            json.dump(data, f, indent=4)
        print("✅ Berkas config/credentials.json berhasil disimpan!")
    except json.JSONDecodeError as e:
        print(f"❌ Format JSON tidak valid: {e}")

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python cli.py configure")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "configure":
        print("=============================================")
        print("  Selamat Datang di J.A.R.V.I.S Configurator ")
        print("=============================================")
        configure_env()
        configure_antigravity()
        configure_credentials()
        print("\n🎉 Konfigurasi Selesai! Silakan jalankan 'jarvish restart' untuk menerapkan perubahan.")
    else:
        print(f"Perintah tidak dikenal: {cmd}")

if __name__ == "__main__":
    main()
