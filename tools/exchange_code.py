import os
import sys

# Ensure we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def main(code):
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    token_path = os.path.join(config_dir, "token.json")
    credentials_path = os.path.join(config_dir, "credentials.json")

    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path, SCOPES, redirect_uri="http://localhost:8080/"
    )
    flow.fetch_token(code=code)

    creds = flow.credentials
    with open(token_path, "w") as token:
        token.write(creds.to_json())
        print(f"Success! Credentials saved to {token_path}")


if __name__ == "__main__":
    main(sys.argv[1])
