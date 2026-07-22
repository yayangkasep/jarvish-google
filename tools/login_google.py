import os
import sys

# Ensure we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
# We request full Gmail access and Calendar/Drive access if needed later.
# For now, just Gmail readonly and send.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/tasks",
]


def main():
    """Shows basic usage of the Gmail API.
    Logs the user in and saves the token.json file.
    """
    creds = None
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    token_path = os.path.join(config_dir, "token.json")
    credentials_path = os.path.join(config_dir, "credentials.json")

    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"Error: Could not find {credentials_path}")
        print(
            "Please ensure you renamed your client_secret_*.json to config/credentials.json"
        )
        return

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("No valid token found. Please visit the URL below to authorize:")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            # Run local server on port 8080 (must match what's allowed in Google Console)
            creds = flow.run_local_server(port=8080, open_browser=False)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            print(f"\nSuccess! Credentials saved to {token_path}")
            print("Jarvish can now access your Gmail securely!")
    else:
        print(f"Credentials are already valid and saved at {token_path}")


if __name__ == "__main__":
    main()
