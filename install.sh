#!/bin/bash

echo "=============================================="
echo "   J.A.R.V.I.S Installation Script (VPS)      "
echo "=============================================="
echo ""

# 1. Require Sudo
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Please run this installer with sudo privileges."
  echo "Command: sudo bash $0"
  exit 1
fi

# Determine the real user who invoked sudo
if [ -n "$SUDO_USER" ]; then
    REAL_USER=$SUDO_USER
else
    REAL_USER=$(whoami)
fi

TARGET_DIR="/opt/jarvish-google"
CURRENT_DIR=$(pwd)
REPO_URL="https://github.com/yayangkasep/jarvish-google.git"

# 2. Get the Source Code (Clone or Move)
echo "[INFO] Preparing J.A.R.V.I.S directory at $TARGET_DIR..."

if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    chown "$REAL_USER:$REAL_USER" "$TARGET_DIR"
fi

# Check if we are already inside a cloned repo (has .git) and not already in /opt
if [ -d "$CURRENT_DIR/.git" ] && [ "$CURRENT_DIR" != "$TARGET_DIR" ]; then
    echo "[INFO] Local repository found. Moving files to $TARGET_DIR..."
    cp -rT "$CURRENT_DIR" "$TARGET_DIR"
    chown -R "$REAL_USER:$REAL_USER" "$TARGET_DIR"
elif [ ! -d "$TARGET_DIR/.git" ]; then
    echo "[INFO] No local repository found (run via curl). Cloning from GitHub..."
    
    # Clone as the REAL_USER so they own the git config
    sudo -u "$REAL_USER" git clone "$REPO_URL" "$TARGET_DIR"
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to clone the repository. Please check your credentials or SSH keys."
        exit 1
    fi
else
    echo "[OK] Repository already exists in $TARGET_DIR. Updating to latest version..."
    git config --global --add safe.directory "$TARGET_DIR"
    git -C "$TARGET_DIR" fetch origin
    git -C "$TARGET_DIR" reset --hard origin/master
    chown -R "$REAL_USER:$REAL_USER" "$TARGET_DIR"
fi

# Transition to the target directory
cd "$TARGET_DIR" || exit 1

# 3. Check if python3 is installed
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "[OK] Python 3 is installed (Version: $PY_VER)."
else
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.10+ and pip before running this installer."
    exit 1
fi

# 4. Check if python3-venv is available
if ! python3 -c "import venv" &>/dev/null; then
    echo "[ERROR] Python 'venv' module is missing!"
    echo "Please install it using: sudo apt install python3-venv"
    exit 1
fi

# 5. Create Virtual Environment
echo ""
echo "[INFO] Creating Virtual Environment (.venv)..."
if [ ! -d ".venv" ]; then
    sudo -u "$REAL_USER" python3 -m venv .venv
    echo "[OK] Virtual Environment created."
else
    echo "[OK] Virtual Environment (.venv) already exists."
fi

# 6. Install Requirements
echo ""
echo "[INFO] Installing dependencies..."
sudo -u "$REAL_USER" .venv/bin/pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    sudo -u "$REAL_USER" .venv/bin/pip install -r requirements.txt
    echo "[OK] Dependencies installed successfully."
else
    echo "[WARNING] requirements.txt not found! Skipping dependency installation."
fi

# 7. Install Backend Services (Docker Images)
echo ""
echo "[INFO] Setting up Backend Docker Services..."
if command -v docker &>/dev/null; then
    echo "[OK] Docker is installed. Pulling necessary images..."
    docker pull lbjlaq/antigravity-manager:latest
    docker pull searxng/searxng:latest
    
    if [ -f "docker-compose.yml" ]; then
        echo "[INFO] Starting Antigravity Manager via docker-compose..."
        if docker compose version &>/dev/null; then
            docker compose up -d antigravity-manager
        elif command -v docker-compose &>/dev/null; then
            docker-compose up -d antigravity-manager
        fi
        echo "[OK] Backend services started."
    fi
else
    echo "[WARNING] Docker is not installed!"
    echo "Please install Docker to run Antigravity Manager and SearXNG."
fi

# 8. Setup Systemd Service
echo ""
echo "[INFO] Setting up J.A.R.V.I.S Systemd Service..."
SERVICE_PATH="/etc/systemd/system/jarvish.service"

echo "Generating service file..."
cat <<EOF > $SERVICE_PATH
[Unit]
Description=Jarvish AI Telegram Bot
After=network.target

[Service]
Type=simple
User=$REAL_USER
WorkingDirectory=$TARGET_DIR
ExecStart=$TARGET_DIR/.venv/bin/python $TARGET_DIR/main.py
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting J.A.R.V.I.S service..."
systemctl daemon-reload
systemctl enable jarvish.service
systemctl start jarvish.service
echo "[OK] Service jarvish.service is now running in the background!"

# 9. Setup Global CLI Wrapper
echo ""
echo "[INFO] Setting up 'jarvish' Global Command..."
cp "$TARGET_DIR/jarvish.sh" /usr/local/bin/jarvish
chmod +x /usr/local/bin/jarvish
echo "[OK] 'jarvish' command is now available everywhere!"

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "  J.A.R.V.I.S is now securely installed in $TARGET_DIR"
echo "  - To configure secrets: jarvish configure"
echo "  - To check status:      jarvish status"
echo "  - To view logs:         jarvish logs"
echo "  - To restart:           jarvish restart"
echo "=============================================="
