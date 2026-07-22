import subprocess


class SystemCommandTool:
    def __init__(self):
        self.ToolName = "SystemCommand"
        self.Schema = {
            "type": "function",
            "function": {
                "name": self.ToolName,
                "description": "Mengeksekusi perintah terminal pada sistem operasi (misalnya apt update, df -h, ls). Peringatan: Gunakan hanya jika diminta pengguna.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Perintah bash/terminal yang ingin dieksekusi.",
                        }
                    },
                    "required": ["command"],
                },
            },
        }

    def Execute(self, Arguments):
        command = Arguments.get("command")
        if not command:
            return "Error: Argumen 'command' kosong."

        try:
            # Gunakan timeout agar tidak hang
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            output = result.stdout + result.stderr

            if not output.strip():
                return f"Perintah `{command}` berhasil dieksekusi tetapi tidak menghasilkan output (keluaran kosong)."

            # Batasi panjang output agar tidak over-limit di Telegram/AI Token
            if len(output) > 2000:
                output = (
                    output[:2000] + "\n...[Output terpotong karena terlalu panjang]..."
                )

            return f"Output dari `{command}`:\n{output}"

        except subprocess.TimeoutExpired:
            return (
                f"Error: Perintah `{command}` melebihi batas waktu eksekusi (timeout)."
            )
        except Exception as e:
            return f"Terjadi kesalahan saat mengeksekusi perintah: {str(e)}"
