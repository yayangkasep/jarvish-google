import sys
import os
import json

def prompt_multiline(prompt_text):
    print(f"\n{prompt_text}")
    print("Paste your content below.")
    print("When done, type 'EOF' on a new line and press Enter:")
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
    import dotenv
    existing_env = dotenv.dotenv_values(".env")
    
    def get_input_with_default(prompt_text, key):
        default_val = existing_env.get(key, "")
        if default_val:
            masked = default_val[:4] + "***" + default_val[-4:] if len(default_val) > 8 else "***"
            ans = input(f"{prompt_text} [Punya Anda: {masked}]: ").strip()
            return ans if ans else default_val
        else:
            return input(f"{prompt_text}: ").strip()

    print("\n--- Configuring .env (Telegram & Secrets) ---")
    print("(Tekan Enter jika tidak ingin mengubah nilai yang sudah ada)")
    token = get_input_with_default("Enter TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    allowed = get_input_with_default("Enter TELEGRAM_ALLOWED_USERS (comma-separated)", "TELEGRAM_ALLOWED_USERS")
    google_id = get_input_with_default("Enter GOOGLE_CLIENT_ID (Optional)", "GOOGLE_CLIENT_ID")
    google_secret = get_input_with_default("Enter GOOGLE_CLIENT_SECRET (Optional)", "GOOGLE_CLIENT_SECRET")
    github_token = get_input_with_default("Enter GITHUB_PERSONAL_ACCESS_TOKEN (Optional)", "GITHUB_PERSONAL_ACCESS_TOKEN")
    
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
    print("✅ .env configured successfully!")

def configure_antigravity():
    print("\n--- Configuring config/antigravity-accounts.json ---")
    print("Drag and drop your JSON file here and press Enter, OR paste the raw JSON content.")
    print("If pasting raw JSON, type 'EOF' on a new line and press Enter when done:")
    
    try:
        line = input().strip()
    except EOFError:
        print("Skipped.")
        return
        
    if not line:
        print("Skipped.")
        return
        
    # Check if the first line is a file path (stripping quotes that drag-n-drop adds)
    clean_path = line.strip("'\" ")
    if os.path.isfile(clean_path):
        print(f"Reading from file: {clean_path}")
        with open(clean_path, 'r') as f:
            content = f.read()
    else:
        # It's raw JSON, continue reading until EOF
        lines = [line]
        if line.strip() != "EOF":
            while True:
                try:
                    next_line = input()
                    if next_line.strip() == "EOF":
                        break
                    lines.append(next_line)
                except EOFError:
                    break
        content = "\n".join(lines).strip()
        
    if not content:
        print("Skipped.")
        return
        
    try:
        data = json.loads(content)
        os.makedirs('config', exist_ok=True)
        with open("config/antigravity-accounts.json", "w") as f:
            json.dump(data, f, indent=4)
        print("✅ config/antigravity-accounts.json saved successfully!")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py configure")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "configure":
        print("=============================================")
        print("     J.A.R.V.I.S Configurator Wizard         ")
        print("=============================================")
        configure_env()
        configure_antigravity()
        print("\n🎉 Configuration Complete! Please run 'jarvish restart' to apply changes.")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
