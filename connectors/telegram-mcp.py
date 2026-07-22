import importlib
import sys
import os
import requests
import time

# Import BaseConnector with dashed name
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
base_connector_mod = importlib.import_module("connectors.base-connector")
BaseConnector = base_connector_mod.BaseConnector


class TelegramMcp(BaseConnector):
    def __init__(self, Token, AllowedUsers=None):
        super().__init__()
        self.PlatformType = "Telegram"
        self.Token = Token
        self.ApiUrl = f"https://api.telegram.org/bot{self.Token}"

        # Security Policies (Strictly enforced)
        self.DmPolicy = "allowlist"
        self.AllowFrom = AllowedUsers if AllowedUsers else ["*"]

    def Connect(self):
        if not self.Token or self.Token == "mock_telegram_token_123":
            print("TelegramMcp Error: Missing or invalid Token.")
            self.IsConnected = False
            return False

        try:
            print(f"[{self.PlatformType}] Connecting with token: {self.Token[:10]}...")
            res = requests.get(f"{self.ApiUrl}/getMe", timeout=10)
            if res.status_code == 200:
                bot_info = res.json().get("result", {})
                print(
                    f"[{self.PlatformType}] Connected successfully as @{bot_info.get('username')}"
                )
                self.IsConnected = True
                return True
            else:
                print(f"[{self.PlatformType}] Failed to connect: {res.text}")
                self.IsConnected = False
                return False
        except Exception as e:
            print(f"[{self.PlatformType}] Connection error: {e}")
            self.IsConnected = False
            return False

    def StartPolling(self, callback):
        """Continuously polls Telegram for new messages and calls callback(UserId, Text)"""
        if not self.IsConnected:
            print("Cannot start polling: Not connected.")
            return

        print(f"[{self.PlatformType}] Started polling for messages...")
        offset = 0
        while True:
            try:
                # Use long polling (timeout 30s)
                res = requests.get(
                    f"{self.ApiUrl}/getUpdates",
                    params={
                        "offset": offset,
                        "timeout": 30,
                        "allowed_updates": ["message"],
                    },
                    timeout=40,
                )

                if res.status_code == 200:
                    data = res.json()
                    updates = data.get("result", [])

                    for update in updates:
                        update_id = update.get("update_id")
                        offset = update_id + 1  # Acknowledge the update

                        message = update.get("message")
                        if not message:
                            continue

                        user_id = message.get("from", {}).get("id")
                        text = message.get("text", "")

                        document = message.get("document")
                        photo = message.get("photo")
                        image_base64 = None

                        if document:
                            file_id = document.get("file_id")
                            file_name = document.get("file_name", "document")
                            caption = message.get("caption", "")
                            print(
                                f"[{self.PlatformType}] Received document: {file_name}"
                            )
                            doc_text = self._download_and_extract_document(
                                file_id, file_name
                            )
                            text = f"[Isi Dokumen {file_name}:\n{doc_text}]\n\nUser: {caption}"
                        elif photo:
                            largest_photo = max(
                                photo, key=lambda x: x.get("file_size", 0)
                            )
                            file_id = largest_photo.get("file_id")
                            caption = message.get("caption", "")
                            if caption:
                                text = caption
                            print(f"[{self.PlatformType}] Received photo.")
                            image_base64 = self._download_and_encode_photo(file_id)

                        if user_id and (text or image_base64):
                            # Policy enforcement check
                            if self.DmPolicy == "allowlist" and (
                                "*" in self.AllowFrom
                                or str(user_id) in self.AllowFrom
                                or user_id in self.AllowFrom
                            ):
                                print(
                                    f"[{self.PlatformType}] Received message from {user_id}"
                                )
                                # Execute the callback in a safe manner
                                try:
                                    callback(user_id, text, image_base64)
                                except Exception as e:
                                    print(
                                        f"[{self.PlatformType}] Error in message callback: {e}"
                                    )
                                    self.SendMessage(
                                        user_id,
                                        "Sorry, I encountered an internal error processing your request.",
                                    )
                            else:
                                print(
                                    f"[{self.PlatformType}] Blocked message from unauthorized user {user_id}"
                                )
                                self.SendMessage(
                                    user_id,
                                    "Maaf anda bukan bos saya, saya hanya melayani bos saya @yayangkasep",
                                )
                elif res.status_code == 409:
                    print(
                        f"[{self.PlatformType}] Conflict error. Is another instance polling?"
                    )
                    time.sleep(10)
                else:
                    print(
                        f"[{self.PlatformType}] Polling error {res.status_code}: {res.text}"
                    )
                    time.sleep(5)

            except requests.exceptions.Timeout:
                # Normal for long polling
                continue
            except Exception as e:
                print(f"[{self.PlatformType}] Polling exception: {e}")
                time.sleep(5)

    def SendMessage(self, TargetId, MessageText):
        if not self.IsConnected:
            print("Cannot send message: Not connected to Telegram.")
            return False

        try:
            print(f"[{self.PlatformType}] Sending response to {TargetId}...")
            res = requests.post(
                f"{self.ApiUrl}/sendMessage",
                json={"chat_id": TargetId, "text": MessageText},
                timeout=10,
            )
            if res.status_code == 200:
                data = res.json()
                return data.get("result", {}).get("message_id")
            else:
                print(f"[{self.PlatformType}] Failed to send message: {res.text}")
                return None
        except Exception as e:
            print(f"[{self.PlatformType}] Send message error: {e}")
            return None

    def SendPhoto(self, TargetId, PhotoUrl, Caption=""):
        if not self.IsConnected:
            print("Cannot send photo: Not connected to Telegram.")
            return False

        try:
            print(f"[{self.PlatformType}] Sending photo to {TargetId}...")
            res = requests.post(
                f"{self.ApiUrl}/sendPhoto",
                json={"chat_id": TargetId, "photo": PhotoUrl, "caption": Caption},
                timeout=15,
            )
            if res.status_code == 200:
                return True
            else:
                print(f"[{self.PlatformType}] Failed to send photo: {res.text}")
                return False
        except Exception as e:
            print(f"[{self.PlatformType}] Send photo error: {e}")
            return False

    def EditMessage(self, TargetId, MessageId, NewText):
        if not self.IsConnected:
            print("Cannot edit message: Not connected to Telegram.")
            return False

        try:
            print(
                f"[{self.PlatformType}] Editing message {MessageId} for {TargetId}..."
            )
            res = requests.post(
                f"{self.ApiUrl}/editMessageText",
                json={"chat_id": TargetId, "message_id": MessageId, "text": NewText},
                timeout=10,
            )
            if res.status_code == 200:
                return True
            else:
                print(f"[{self.PlatformType}] Failed to edit message: {res.text}")
                return False
        except Exception as e:
            print(f"[{self.PlatformType}] Edit message error: {e}")
            return False

    def _download_and_extract_document(self, file_id, file_name):
        try:
            res = requests.get(
                f"{self.ApiUrl}/getFile", params={"file_id": file_id}, timeout=10
            )
            if res.status_code == 200:
                file_path = res.json().get("result", {}).get("file_path")
                if not file_path:
                    return "[Error: Unable to get file path from Telegram]"

                download_url = (
                    f"https://api.telegram.org/file/bot{self.Token}/{file_path}"
                )
                file_res = requests.get(download_url, timeout=30)
                if file_res.status_code == 200:
                    import tempfile
                    from core.document_reader import extract_text_from_file

                    ext = os.path.splitext(file_name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(file_res.content)
                        tmp_path = tmp.name

                    try:
                        return extract_text_from_file(tmp_path)
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                else:
                    return f"[Error: Failed to download file, status {file_res.status_code}]"
            else:
                return f"[Error: Failed to get file info, status {res.status_code}]"
        except Exception as e:
            print(f"[{self.PlatformType}] Document extraction error: {e}")
            return f"[Error processing document: {e}]"

    def _download_and_encode_photo(self, file_id):
        try:
            res = requests.get(
                f"{self.ApiUrl}/getFile", params={"file_id": file_id}, timeout=10
            )
            if res.status_code == 200:
                file_path = res.json().get("result", {}).get("file_path")
                if not file_path:
                    return None

                download_url = (
                    f"https://api.telegram.org/file/bot{self.Token}/{file_path}"
                )
                file_res = requests.get(download_url, timeout=30)
                if file_res.status_code == 200:
                    import base64

                    return base64.b64encode(file_res.content).decode("utf-8")
        except Exception as e:
            print(f"[{self.PlatformType}] Photo extraction error: {e}")
        return None

    def ReceiveMessage(self, Payload):
        # Deprecated: Using StartPolling instead
        return None
