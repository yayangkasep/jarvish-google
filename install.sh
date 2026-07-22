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

# 2. Move/Copy to /opt if not already there
if [ "$CURRENT_DIR" != "$TARGET_DIR" ]; then
    echo "[INFO] Moving installation to $TARGET_DIR..."
    if [ ! -d "$TARGET_DIR" ]; then
        mkdir -p "$TARGET_DIR"
    fi
    
    # Copy all files from current directory to target directory
    # Using cp -rT to copy contents directly into the target folder
    cp -rT "$CURRENT_DIR" "$TARGET_DIR"
    
    # Ensure the real user owns the files, not root
    chown -R "$REAL_USER:$REAL_USER" "$TARGET_DIR"
    
    echo "[OK] Files copied to $TARGET_DIR."
    
    echo "[INFO] Transitioning to $TARGET_DIR to continue installation..."
    cd "$TARGET_DIR" || exit 1
else
    echo "[OK] Already running in $TARGET_DIR."
    chown -R "$REAL_USER:$REAL_USER" "$TARGET_DIR"
fi

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
    # Create venv as the REAL_USER so they own it
    sudo -u "$REAL_USER" python3 -m venv .venv
    echo "[OK] Virtual Environment created."
else
    echo "[OK] Virtual Environment (.venv) already exists."
fi

# 6. Install Requirements
echo ""
echo "[INFO] Installing dependencies..."
# Upgrade pip and install requirements as REAL_USER
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
    # Root can pull docker images
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

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "  J.A.R.V.I.S is now securely installed in $TARGET_DIR"
echo "  - To check status: sudo systemctl status jarvish"
echo "  - To view logs: sudo journalctl -u jarvish -f"
echo "  - To restart: sudo systemctl restart jarvish"
echo "=============================================="
