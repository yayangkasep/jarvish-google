#!/bin/bash
# J.A.R.V.I.S Global Command Line Wrapper

JARVIS_DIR="/opt/jarvish-google"

if [ "$1" == "configure" ]; then
    echo "Starting J.A.R.V.I.S Configurator..."
    cd $JARVIS_DIR && sudo .venv/bin/python cli.py configure
    sudo chown -R $SUDO_USER:$SUDO_USER $JARVIS_DIR/.env $JARVIS_DIR/config &>/dev/null
elif [ "$1" == "auth-google" ]; then
    echo "Starting Google Authentication..."
    cd $JARVIS_DIR && sudo .venv/bin/python tools/login_google.py
    sudo chown -R $SUDO_USER:$SUDO_USER $JARVIS_DIR/data &>/dev/null
elif [ "$1" == "start" ]; then
    echo "Starting J.A.R.V.I.S service..."
    sudo systemctl start jarvish.service
elif [ "$1" == "stop" ]; then
    echo "Stopping J.A.R.V.I.S service..."
    sudo systemctl stop jarvish.service
elif [ "$1" == "restart" ]; then
    echo "Restarting J.A.R.V.I.S service..."
    sudo systemctl restart jarvish.service
elif [ "$1" == "status" ]; then
    sudo systemctl status jarvish.service
elif [ "$1" == "logs" ]; then
    sudo journalctl -u jarvish.service -f
elif [ "$1" == "update" ]; then
    echo "Updating J.A.R.V.I.S..."
    cd $JARVIS_DIR
    OLD_HASH=$(git rev-parse HEAD)
    sudo git pull origin master
    NEW_HASH=$(git rev-parse HEAD)
    
    if [ "$OLD_HASH" == "$NEW_HASH" ]; then
        echo "J.A.R.V.I.S sudah pada versi paling update!"
    else
        echo "Update berhasil! Merestart J.A.R.V.I.S service..."
        sudo systemctl restart jarvish.service
        echo "Restart selesai."
    fi
else
    echo "=============================================="
    echo "             J.A.R.V.I.S CLI                  "
    echo "=============================================="
    echo "Usage: jarvish [command]"
    echo ""
    echo "Available commands:"
    echo "  configure    Run the configuration wizard (setup .env, keys, etc.)"
    echo "  auth-google  Connect your Google Account (Gmail, Drive, Calendar, etc.)"
    echo "  start       Start the J.A.R.V.I.S background service"
    echo "  stop        Stop the J.A.R.V.I.S background service"
    echo "  restart     Restart the service (required after configure)"
    echo "  status      Check if the bot is running"
    echo "  logs        View real-time service logs"
    echo "  update      Pull the latest code from GitHub and restart"
    echo "=============================================="
fi
