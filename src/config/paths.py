import os
from pathlib import Path

# The directory containing the code (e.g. .../site-packages/jarvis/config)
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALL_DIR = os.path.dirname(CONFIG_DIR)

# The directory for user data/config (~/.jarvish)
USER_DIR = os.path.expanduser("~/.jarvish")

def ensure_dirs():
    os.makedirs(os.path.join(USER_DIR, "data"), exist_ok=True)
    os.makedirs(os.path.join(USER_DIR, "config"), exist_ok=True)

def get_data_dir():
    ensure_dirs()
    return os.path.join(USER_DIR, "data")

def get_config_dir():
    ensure_dirs()
    return os.path.join(USER_DIR, "config")

def get_env_file():
    ensure_dirs()
    return os.path.join(USER_DIR, ".env")
