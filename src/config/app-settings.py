import os
from dotenv import load_dotenv

from . import paths

class AppSettings:
    def __init__(self):
        # Path to .env in the user directory
        self.EnvFilePath = paths.get_env_file()
        load_dotenv(self.EnvFilePath)

        self.TelegramBotToken = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.TelegramAllowedUsers = os.getenv("TELEGRAM_ALLOWED_USERS", "*")
        self.EnvironmentMode = os.getenv("ENVIRONMENT_MODE", "development")
        self.GoogleClientId = os.getenv("GOOGLE_CLIENT_ID", "")
        self.GoogleClientSecret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    def GetTelegramToken(self):
        return self.TelegramBotToken

    def GetAllowedUsers(self):
        return [u.strip() for u in self.TelegramAllowedUsers.split(",") if u.strip()]

    def GetGoogleCredentials(self):
        return {
            "ClientId": self.GoogleClientId,
            "ClientSecret": self.GoogleClientSecret,
        }
