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

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "  To start J.A.R.V.I.S, run the following:"
echo "  1. source .venv/bin/activate"
echo "  2. python main.py"
echo "=============================================="
