#!/bin/bash

echo "=============================================="
echo "   J.A.R.V.I.S Installation Script (VPS)      "
echo "=============================================="
echo ""

# 1. Check if python3 is installed
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "[OK] Python 3 is installed (Version: $PY_VER)."
else
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.10+ and pip before running this installer."
    echo "Example for Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# 2. Check if python3-venv is available
if ! python3 -c "import venv" &>/dev/null; then
    echo "[ERROR] Python 'venv' module is missing!"
    echo "Please install it using: sudo apt install python3-venv"
    exit 1
fi

# 3. Create Virtual Environment
echo ""
echo "[INFO] Creating Virtual Environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[OK] Virtual Environment created."
else
    echo "[OK] Virtual Environment (.venv) already exists."
fi

# 4. Activate Virtual Environment and Install Requirements
echo ""
echo "[INFO] Installing dependencies..."
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "[OK] Dependencies installed successfully."
else
    echo "[WARNING] requirements.txt not found! Skipping dependency installation."
fi

# 5. Install Backend Services (Docker Images)
echo ""
echo "[INFO] Setting up Backend Docker Services..."
if command -v docker &>/dev/null; then
    echo "[OK] Docker is installed. Pulling necessary images..."
    docker pull lbjlaq/antigravity-manager:latest
    docker pull searxng/searxng:latest
    
    if [ -f "docker-compose.yml" ]; then
        echo "[INFO] Starting Antigravity Manager via docker-compose..."
        # Fallback to older docker-compose if 'docker compose' is not a plugin
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

# 6. Setup Systemd Service
echo ""
echo "[INFO] Setting up J.A.R.V.I.S Systemd Service..."
SERVICE_PATH="/etc/systemd/system/jarvish.service"
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

echo "Generating service file..."
cat <<EOF | sudo tee $SERVICE_PATH > /dev/null
[Unit]
Description=Jarvish AI Telegram Bot
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/.venv/bin/python $CURRENT_DIR/main.py
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting J.A.R.V.I.S service..."
sudo systemctl daemon-reload
sudo systemctl enable jarvish.service
sudo systemctl start jarvish.service
echo "[OK] Service jarvish.service is now running in the background!"

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "  J.A.R.V.I.S is now installed as a background service."
echo "  - To check status: sudo systemctl status jarvish"
echo "  - To view logs: sudo journalctl -u jarvish -f"
echo "  - To restart: sudo systemctl restart jarvish"
echo "=============================================="
