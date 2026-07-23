import sys
import os
import json
import subprocess
from config import paths

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
    env_file = paths.get_env_file()
    existing_env = dotenv.dotenv_values(env_file)
    
    def get_input_with_default(prompt_text, key):
        default_val = existing_env.get(key, "")
        if default_val:
            masked = default_val[:4] + "***" + default_val[-4:] if len(default_val) > 8 else "***"
            ans = input(f"{prompt_text} [Current: {masked}]: ").strip()
            return ans if ans else default_val
        else:
            return input(f"{prompt_text}: ").strip()

    print("\n--- Configuring .env (Telegram & Secrets) ---")
    print("(Press Enter to keep the existing value)")
    token = get_input_with_default("Enter TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    allowed = get_input_with_default("Enter TELEGRAM_ALLOWED_USERS (comma-separated)", "TELEGRAM_ALLOWED_USERS")
    google_id = get_input_with_default("Enter GOOGLE_CLIENT_ID (Optional)", "GOOGLE_CLIENT_ID")
    google_secret = get_input_with_default("Enter GOOGLE_CLIENT_SECRET (Optional)", "GOOGLE_CLIENT_SECRET")
    github_token = get_input_with_default("Enter GITHUB_PERSONAL_ACCESS_TOKEN (Optional)", "GITHUB_PERSONAL_ACCESS_TOKEN")
    searxng_secret = get_input_with_default("Enter SEARXNG_SECRET (Required for Search Engine Security)", "SEARXNG_SECRET")
    
    env_content = f"""TELEGRAM_BOT_TOKEN="{token}"
TELEGRAM_ALLOWED_USERS="{allowed}"
GOOGLE_CLIENT_ID="{google_id}"
GOOGLE_CLIENT_SECRET="{google_secret}"
ANTIGRAVITY_ENDPOINT="http://localhost:8045/v1/chat/completions"
GITHUB_PERSONAL_ACCESS_TOKEN="{github_token}"
SEARXNG_SECRET="{searxng_secret}"
"""
    with open(env_file, "w") as f:
        f.write(env_content)
    print(f"✅ .env configured successfully in {env_file}!")

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
        target_path = os.path.join(paths.get_config_dir(), "antigravity-accounts.json")
        with open(target_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ antigravity-accounts.json saved successfully in {target_path}!")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")

def upgrade_system():
    print("=============================================")
    print("     J.A.R.V.I.S Upgrade Initiated           ")
    print("=============================================")
    print("Pulling latest code and upgrading package...")
    try:
        # Use uv if available for much faster upgrades
        uv_bin = os.path.expanduser("~/.local/bin/uv")
        if not os.path.exists(uv_bin):
            uv_bin = os.path.expanduser("~/.cargo/bin/uv")
            
        if os.path.exists(uv_bin):
            subprocess.check_call([uv_bin, "pip", "install", "--upgrade", "git+https://github.com/yayangkasep/jarvish.git", "--python", sys.executable])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "git+https://github.com/yayangkasep/jarvish.git"])
        print("✅ Upgrade successful!")
        print("Restarting J.A.R.V.I.S service...")
        subprocess.check_call(["sudo", "systemctl", "restart", "jarvish.service"])
        print("✅ Service restarted successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Upgrade failed: {e}")

def status_system():
    subprocess.call(["sudo", "systemctl", "status", "jarvish.service"])

def logs_system():
    subprocess.call(["sudo", "journalctl", "-u", "jarvish.service", "-f"])

def restart_system():
    print("Restarting J.A.R.V.I.S service...")
    try:
        subprocess.check_call(["sudo", "systemctl", "restart", "jarvish.service"])
        print("✅ Service restarted successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restart service: {e}")

def auth_google():
    print("=============================================")
    print("     Google OAuth Authentication Wizard      ")
    print("=============================================")
    try:
        from tools import login_google
        login_google.main()
    except Exception as e:
        print(f"❌ Failed to launch Google Auth: {e}")

def print_help():
    print("Usage: jarvish [command]")
    print("\nCommands:")
    print("  configure     - Setup API keys and environment variables")
    print("  upgrade       - Pull latest code and upgrade the system")
    print("  auth-google   - Authenticate with Google (Calendar/Gmail) via OAuth")
    print("  restart       - Restart the J.A.R.V.I.S background service")
    print("  status        - Check if J.A.R.V.I.S service is running")
    print("  logs          - View live logs of J.A.R.V.I.S")
    print("  help          - Show this help message")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "configure":
        print("=============================================")
        print("     J.A.R.V.I.S Configurator Wizard         ")
        print("=============================================")
        configure_env()
        configure_antigravity()
        print("\n🎉 Configuration Complete! Please run 'sudo systemctl restart jarvish.service' to apply changes.")
    elif cmd == "upgrade":
        upgrade_system()
    elif cmd == "restart":
        restart_system()
    elif cmd == "status":
        status_system()
    elif cmd in ("logs", "log"):
        logs_system()
    elif cmd == "auth-google":
        auth_google()
    elif cmd in ("help", "--help", "-h"):
        print_help()
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'jarvish help' to see available commands.")

if __name__ == "__main__":
    main()
