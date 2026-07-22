import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleAuthManager:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.token_path = os.path.join(self.data_dir, "token.json")
        self.scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/tasks",
        ]

    def GetCredentials(self):
        """Loads and returns Google Credentials, refreshing them if necessary."""
        if not os.path.exists(self.token_path):
            print(
                "GoogleAuthManager: token.json not found! Please run tools/login_google.py"
            )
            return None

        creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save the refreshed token
                    with open(self.token_path, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"GoogleAuthManager Error refreshing token: {e}")
                    return None
            else:
                print("GoogleAuthManager: Credentials invalid and cannot be refreshed.")
                return None

        return creds
