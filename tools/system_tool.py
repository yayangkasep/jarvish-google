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

class UpdateJarvishTool:
    def __init__(self):
        self.ToolName = "UpdateJarvish"
        self.Schema = {
            "type": "function",
            "function": {
                "name": self.ToolName,
                "description": "Mengupdate kode J.A.R.V.I.S secara otomatis dari repositori Git dan merestart service J.A.R.V.I.S.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }

    def Execute(self, Arguments):
        try:
            # Jalankan git pull origin master
            pull_result = subprocess.run(
                "git pull origin master", shell=True, capture_output=True, text=True, timeout=30
            )
            output = pull_result.stdout + pull_result.stderr
            
            if pull_result.returncode != 0:
                return f"Gagal melakukan update Git:\n{output}"
                
            # Jika berhasil pull, jalankan restart service di background dengan delay
            # agar J.A.R.V.I.S sempat merespons ke pengguna
            subprocess.Popen(
                "sleep 5 && sudo systemctl restart jarvish.service", 
                shell=True, 
                start_new_session=True
            )
            
            return f"Berhasil update kode dari Git:\n{output}\nSistem akan restart otomatis dalam 5 detik."
        except Exception as e:
            return f"Terjadi kesalahan saat update: {str(e)}"
