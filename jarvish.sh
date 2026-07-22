#!/bin/bash
# J.A.R.V.I.S Global Command Line Wrapper

JARVIS_DIR="/opt/jarvish-google"

if [ "$1" == "configure" ]; then
    echo "Menjalankan J.A.R.V.I.S Configurator..."
    cd $JARVIS_DIR && sudo .venv/bin/python cli.py configure
    # Ensure correct ownership after writing configs if the user running this is not root
    # but the config was written by root. We will run it as the current user context using bash trickery or just fixing chown
    # Actually, the wrapper is often run with sudo or standard user. We'll fix permissions to ensure safety.
    sudo chown -R $SUDO_USER:$SUDO_USER $JARVIS_DIR/.env $JARVIS_DIR/config &>/dev/null
elif [ "$1" == "start" ]; then
    echo "Memulai J.A.R.V.I.S..."
    sudo systemctl start jarvish.service
elif [ "$1" == "stop" ]; then
    echo "Menghentikan J.A.R.V.I.S..."
    sudo systemctl stop jarvish.service
elif [ "$1" == "restart" ]; then
    echo "Memuat ulang J.A.R.V.I.S..."
    sudo systemctl restart jarvish.service
elif [ "$1" == "status" ]; then
    sudo systemctl status jarvish.service
elif [ "$1" == "logs" ]; then
    sudo journalctl -u jarvish.service -f
else
    echo "=============================================="
    echo "             J.A.R.V.I.S CLI                  "
    echo "=============================================="
    echo "Penggunaan: jarvish [perintah]"
    echo ""
    echo "Perintah yang tersedia:"
    echo "  configure   Jalankan wizard pengisian rahasia (.env, json, dll)"
    echo "  start       Nyalakan layanan J.A.R.V.I.S"
    echo "  stop        Matikan layanan J.A.R.V.I.S"
    echo "  restart     Muat ulang layanan J.A.R.V.I.S (wajib setelah configure)"
    echo "  status      Cek apakah bot sedang online/mati"
    echo "  logs        Lihat layar log bot secara langsung (Live)"
    echo "=============================================="
fi
