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
    google_token = get_input_with_default("Enter GITHUB_PERSONAL_ACCESS_TOKEN (Optional)", "GITHUB_PERSONAL_ACCESS_TOKEN")
    searxng_secret = get_input_with_default("Enter SEARXNG_SECRET (Required for Search Engine Security)", "SEARXNG_SECRET")
    elevenlabs_key = get_input_with_default("Enter ELEVENLABS_API_KEY (Required for Voice Chat)", "ELEVENLABS_API_KEY")
    
    env_content = f"""TELEGRAM_BOT_TOKEN="{token}"
TELEGRAM_ALLOWED_USERS="{allowed}"
GOOGLE_CLIENT_ID="{google_id}"
GOOGLE_CLIENT_SECRET="{google_secret}"
ANTIGRAVITY_ENDPOINT="http://localhost:8045/v1/chat/completions"
GITHUB_PERSONAL_ACCESS_TOKEN="{google_token}"
SEARXNG_SECRET="{searxng_secret}"
ELEVENLABS_API_KEY="{elevenlabs_key}"
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

def configure_models():
    import dotenv
    env_file = paths.get_env_file()
    existing_env = dotenv.dotenv_values(env_file)
    
    print("=============================================")
    print("     J.A.R.V.I.S Model Configurator          ")
    print("=============================================")
    print("Available Models:")
    
    models = [
        "gemini-3.6-flash-high",
        "gemini-3.6-flash-medium",
        "gemini-3.6-flash-low",
        "gemini-3.5-flash-high",
        "gemini-3.1-pro-high",
        "gemini-3.1-pro-low",
        "claude-sonnet-4.6-thinking",
        "claude-opus-4.6-thinking",
        "gpt-oss-120b-medium",
        "gemini-2.5-flash"
    ]
    
    for idx, model in enumerate(models):
        print(f"[{idx + 1}] {model}")
        
    current_model = existing_env.get("LLM_MODEL", "gemini-3-pro-high")
    print(f"\nCurrent Model: {current_model}")
    
    choice = input(f"Select model number (1-{len(models)}) or press Enter to keep current: ").strip()
    
    if choice and choice.isdigit() and 1 <= int(choice) <= len(models):
        selected_model = models[int(choice) - 1]
    else:
        selected_model = current_model
        
    current_temp = existing_env.get("LLM_TEMPERATURE", "0.7")
    temp_choice = input(f"Enter Temperature (e.g., 0.7 for normal, 0.2 for strict, 1.0 for creative) [Current: {current_temp}]: ").strip()
    
    if temp_choice:
        try:
            float(temp_choice)
            selected_temp = temp_choice
        except ValueError:
            print("Invalid temperature, keeping current.")
            selected_temp = current_temp
    else:
        selected_temp = current_temp
        
    # Read entire env file and update
    lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
            
    # Remove existing LLM_MODEL and LLM_TEMPERATURE
    lines = [l for l in lines if not l.startswith("LLM_MODEL=") and not l.startswith("LLM_TEMPERATURE=")]
    
    # Append new values
    lines.append(f"LLM_MODEL=\"{selected_model}\"\n")
    lines.append(f"LLM_TEMPERATURE=\"{selected_temp}\"\n")
    
    with open(env_file, 'w') as f:
        f.writelines(lines)
        
    print(f"✅ AI Model successfully updated to {selected_model} (Temp: {selected_temp})!")
    print("Please run 'jarvish restart' to apply the new model.")

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
    print("  models        - Switch AI Models (e.g. Gemini Pro, Claude) and Temperature")
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
    elif cmd == "models":
        configure_models()
    elif cmd == "auth-google":
        auth_google()
    elif cmd in ("help", "--help", "-h"):
        print_help()
    else:
        print(f"Unknown command: {cmd}")
        print("Run 'jarvish help' to see available commands.")

if __name__ == "__main__":
    main()
