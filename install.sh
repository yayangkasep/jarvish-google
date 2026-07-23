#!/bin/bash

echo "=============================================="
echo "   J.A.R.V.I.S Installation Script (VPS)      "
echo "=============================================="
echo ""

# 1. Require Sudo
if [ "$EUID" -ne 0 ]; then
  echo "[INFO] Skrip ini membutuhkan hak akses root (sudo)."
  echo "Sistem akan meminta password Anda sekarang..."
  
  # Jika script dijalankan dari file lokal, jalankan ulang dirinya sendiri dengan sudo
  if [ -f "$0" ]; then
      exec sudo bash "$0" "$@"
  else
      # Jika script dijalankan dari curl/piping, kita hentikan agar user menjalankannya ulang
      echo "[ERROR] Anda menjalankan skrip dari curl tanpa sudo."
      echo "Jalankan ulang dengan perintah: curl -sSL <URL> | sudo bash"
      exit 1
  fi
fi

# Determine the real user who invoked sudo
if [ -n "$SUDO_USER" ]; then
    REAL_USER=$SUDO_USER
    REAL_HOME_DIR=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    REAL_USER=$(whoami)
    REAL_HOME_DIR=$HOME
fi

TARGET_DIR="$REAL_HOME_DIR/.jarvish"
CURRENT_DIR=$(pwd)
VENV_DIR="$TARGET_DIR/venv"
REPO_URL="https://github.com/yayangkasep/jarvish.git"

# 2. Check and Install Basic Dependencies
echo "[INFO] Memeriksa paket-paket sistem yang diperlukan..."
sudo apt-get update -yqq >/dev/null 2>&1
for pkg in python3 python3-pip git curl; do
    if ! command -v $pkg &>/dev/null; then
        echo "[INFO] Menginstal $pkg secara otomatis..."
        sudo apt-get install -y $pkg >/dev/null 2>&1
    fi
done

# 3. Create target directory
echo "[INFO] Preparing J.A.R.V.I.S directory at $TARGET_DIR..."
if [ ! -d "$TARGET_DIR" ]; then
    sudo -u "$REAL_USER" mkdir -p "$TARGET_DIR"
fi

# 4. Install 'uv' if not present
echo "[INFO] Ensuring 'uv' is installed for fast environment building..."
if ! sudo -u "$REAL_USER" command -v uv &>/dev/null; then
    echo "[INFO] Installing uv..."
    sudo -u "$REAL_USER" curl -LsSf https://astral.sh/uv/install.sh | sudo -u "$REAL_USER" sh
    export PATH="$REAL_HOME_DIR/.cargo/bin:$PATH"
fi

# Use uv from cargo bin if it's not in PATH globally yet
UV_BIN="$REAL_HOME_DIR/.cargo/bin/uv"
if [ ! -f "$UV_BIN" ]; then
    UV_BIN=$(sudo -u "$REAL_USER" which uv)
fi

# 5. Create Virtual Environment and Install Package
echo ""
echo "[INFO] Creating Virtual Environment at $VENV_DIR using uv..."
sudo -u "$REAL_USER" "$UV_BIN" venv "$VENV_DIR"

echo "[INFO] Installing J.A.R.V.I.S package..."
sudo -u "$REAL_USER" "$UV_BIN" pip install . --python "$VENV_DIR"

# 6. Install Backend Services (Docker Images)
echo ""
echo "[INFO] Memeriksa instalasi Docker..."
if ! command -v docker &>/dev/null; then
    echo "[INFO] Docker tidak ditemukan! Memulai instalasi otomatis Docker Engine..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh >/dev/null 2>&1
    rm -f get-docker.sh
    
    echo "[INFO] Mendaftarkan user '$REAL_USER' ke dalam grup docker..."
    sudo usermod -aG docker "$REAL_USER"
    
    # Enable and start docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    echo "[OK] Docker berhasil diinstal!"
else
    echo "[OK] Docker sudah terinstal."
fi

echo "[INFO] Setting up Backend Docker Services..."
echo "[INFO] Pulling necessary images..."
sudo docker pull lbjlaq/antigravity-manager:latest
sudo docker pull searxng/searxng:latest

if [ -f "docker-compose.yml" ]; then
    echo "[INFO] Starting Antigravity Manager and SearXNG via docker-compose..."
    if sudo docker compose version &>/dev/null; then
        sudo docker compose up -d antigravity-manager searxng
    elif command -v docker-compose &>/dev/null; then
        sudo docker-compose up -d antigravity-manager searxng
    fi
    echo "[OK] Backend services started."
fi

# 7. Setup Systemd Service
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
ExecStart=$VENV_DIR/bin/jarvish-server
Environment=PYTHONUNBUFFERED=1
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

echo "Enabling and starting J.A.R.V.I.S service..."
systemctl daemon-reload
systemctl enable jarvish.service
systemctl restart jarvish.service
echo "[OK] Service jarvish.service is now running in the background!"

# 8. Setup Global CLI Wrapper
echo ""
echo "[INFO] Setting up 'jarvish' Global Command..."
ln -sf "$VENV_DIR/bin/jarvish" /usr/local/bin/jarvish
chmod +x /usr/local/bin/jarvish
echo "[OK] 'jarvish' command is now available everywhere!"

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "  J.A.R.V.I.S is now securely installed in $TARGET_DIR"
echo "  - To configure secrets: jarvish configure"
echo "  - To upgrade system:    jarvish upgrade"
echo "  - To check status:      sudo systemctl status jarvish.service"
echo "  - To view logs:         sudo journalctl -u jarvish.service -f"
echo "=============================================="
