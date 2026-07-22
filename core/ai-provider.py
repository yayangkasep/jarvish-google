import os
import sys
import requests
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import importlib

app_settings_mod = importlib.import_module("config.app-settings")


class AiProvider:
    def __init__(self):
        self.Settings = app_settings_mod.AppSettings()
        # Antigravity backend running in the same Docker network
        self.Endpoint = os.getenv(
            "ANTIGRAVITY_ENDPOINT",
            "http://antigravity-manager:8045/v1/chat/completions",
        )
        self.ApiKey = os.getenv("ANTIGRAVITY_API_KEY", "test")
        self._seed_accounts()

    def _seed_accounts(self):
        print("Ensuring accounts are loaded into Antigravity proxy...")
        import time

        try:
            with open(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "config",
                    "antigravity-accounts.json",
                ),
                "r",
            ) as f:
                import json

                accounts = json.load(f)

            url = self.Endpoint.replace("/v1/chat/completions", "/api/accounts")
            headers = {
                "Authorization": f"Bearer {self.ApiKey}",
                "Content-Type": "application/json",
            }

            # Wait for proxy to start up
            max_wait_retries = 10
            for attempt in range(max_wait_retries):
                try:
                    res = requests.get(
                        self.Endpoint.replace(
                            "/v1/chat/completions", "/api/system/version"
                        ),
                        timeout=5,
                    )
                    break
                except Exception:
                    print(
                        f"Waiting for Antigravity proxy to boot... ({attempt + 1}/{max_wait_retries})"
                    )
                    time.sleep(2)

            for acc in accounts:
                token = acc.get("refresh_token")
                if token:
                    try:
                        res = requests.post(
                            url,
                            headers=headers,
                            json={"refreshToken": token},
                            timeout=30,
                        )
                        if res.status_code == 200:
                            print(
                                f"Seeded account to proxy: {acc.get('email', 'Unknown')}"
                            )
                        else:
                            print(
                                f"Failed to seed account {acc.get('email')}: {res.status_code} - {res.text}"
                            )
                    except Exception as e:
                        print(
                            f"Failed to connect while seeding {acc.get('email')}: {e}"
                        )

            # Unpause the proxy service now that accounts are seeded
            start_url = self.Endpoint.replace(
                "/v1/chat/completions", "/api/proxy/start"
            )
            res = requests.post(start_url, headers=headers, timeout=10)
            if res.status_code == 200:
                print("Successfully started proxy service!")
            else:
                print(
                    f"Warning: Failed to start proxy service: {res.status_code} - {res.text}"
                )

            # Warm up accounts to fetch Project ID and initialize Cloud Code
            print("Warming up accounts...")
            warmup_url = self.Endpoint.replace(
                "/v1/chat/completions", "/api/accounts/warmup"
            )
            res = requests.post(warmup_url, headers=headers, timeout=30)
            if res.status_code == 200:
                print("Successfully warmed up accounts!")
            else:
                print(
                    f"Warning: Failed to warm up accounts: {res.status_code} - {res.text}"
                )

        except Exception as e:
            print(f"Failed to auto-seed accounts: {e}")

    def ExecutePrompt(self, PromptText=None, RequiredTools=None, Messages=None):
        print(f"Executing prompt via Antigravity backend...")

        Headers = {
            "Authorization": f"Bearer {self.ApiKey}",
            "Content-Type": "application/json",
        }

        Payload = {"model": "gemini-2.5-flash", "temperature": 0.7}

        if Messages is not None:
            # Inject System Prompt as the first message
            from datetime import datetime, timedelta

            # Ensure timezone is WIB (UTC+7)
            current_time = (datetime.utcnow() + timedelta(hours=7)).strftime(
                "%Y-%m-%d %H:%M:%S WIB"
            )
            from config.prompt_builder import build_system_prompt

            SystemPrompt = {
                "role": "system",
                "content": build_system_prompt(current_time, RequiredTools),
            }
            Payload["messages"] = [SystemPrompt] + Messages
        else:
            Payload["messages"] = [{"role": "user", "content": PromptText}]

        # Add tools if provided (OpenAI tool format)
        if RequiredTools:
            # Assume RequiredTools is a list of dicts formatted for OpenAI
            Payload["tools"] = RequiredTools
            Payload["tool_choice"] = "auto"

        import time

        max_retries = 5

        for attempt in range(max_retries):
            try:
                Response = requests.post(
                    self.Endpoint, headers=Headers, json=Payload, timeout=120
                )

                if Response.status_code == 200:
                    Data = Response.json()
                    Choices = Data.get("choices", [])
                    if Choices:
                        Message = Choices[0].get("message", {})
                        print(f"RAW API MESSAGE: {json.dumps(Message)}")

                        # Return the full message object (including content and tool_calls)
                        return Message
                    return {
                        "role": "assistant",
                        "content": "Error: No choices returned from proxy.",
                    }
                elif Response.status_code == 503:
                    print(
                        f"Proxy not ready (503). Retrying in 3 seconds... ({attempt + 1}/{max_retries})"
                    )
                    time.sleep(3)
                    continue
                else:
                    return {
                        "role": "assistant",
                        "content": f"API Error from Antigravity ({Response.status_code}): {Response.text}",
                    }

            except Exception as e:
                print(
                    f"Connection failed. Retrying in 3 seconds... ({attempt + 1}/{max_retries}) - {e}"
                )
                import time

                time.sleep(3)

        return {
            "role": "assistant",
            "content": "Failed to connect to Antigravity proxy after multiple attempts.",
        }
