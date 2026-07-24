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

class TestPythonTool:
    def __init__(self):
        self.ToolName = "TestPythonTool"
        self.Schema = {
            "type": "function",
            "function": {
                "name": self.ToolName,
                "description": "Mengompilasi dan menguji kelayakan file Python (khususnya untuk alat baru) sebelum di-deploy. Gunakan ini untuk memastikan kode Anda bebas dari syntax error dan struktur class sudah benar.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path absolut atau relatif ke file Python yang ingin diuji (contoh: src/tools/math_tool.py).",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        }

    def Execute(self, Arguments):
        import py_compile
        import importlib.util
        import sys
        import inspect
        import os

        file_path = Arguments.get("file_path")
        if not file_path or not os.path.exists(file_path):
            return f"Error: File '{file_path}' tidak ditemukan."

        try:
            # 1. Syntax Check
            py_compile.compile(file_path, doraise=True)
            
            # 2. Dynamic Import Check
            module_name = os.path.basename(file_path)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 3. Validation Check
            tool_classes = []
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__ and name.endswith("Tool"):
                    tool_classes.append(obj)
            
            if not tool_classes:
                return "Syntax OK, tetapi tidak ditemukan kelas yang berakhiran 'Tool' di dalam file ini."
                
            report = ["Syntax OK. Ditemukan kelas Tool berikut:"]
            for cls in tool_classes:
                try:
                    instance = cls()
                    missing = []
                    if not hasattr(instance, "ToolName"): missing.append("ToolName")
                    if not hasattr(instance, "Schema"): missing.append("Schema")
                    if not hasattr(instance, "Execute"): missing.append("fungsi Execute()")
                    
                    if missing:
                        report.append(f"- Kelas {cls.__name__} kehilangan properti wajib: {', '.join(missing)}")
                    else:
                        report.append(f"- Kelas {cls.__name__} valid dan siap di-deploy!")
                except Exception as e:
                    report.append(f"- Error saat mencoba instansiasi kelas {cls.__name__}: {str(e)}")
                    
            return "\n".join(report)

        except py_compile.PyCompileError as e:
            return f"Syntax Error pada kode Anda:\n{str(e)}"
        except Exception as e:
            return f"Runtime Error saat menguji kode Anda:\n{str(e)}"

class RestartJarvishTool:
    def __init__(self):
        self.ToolName = "RestartJarvish"
        self.Schema = {
            "type": "function",
            "function": {
                "name": self.ToolName,
                "description": "Me-restart background service J.A.R.V.I.S secara aman. Wajib digunakan SETELAH Anda membuat/mengubah kode sumber dan lulus pengujian dari TestPythonTool.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }

    def Execute(self, Arguments):
        try:
            subprocess.Popen(
                "sleep 5 && sudo systemctl restart jarvish.service", 
                shell=True, 
                start_new_session=True
            )
            return "Sistem akan restart otomatis dalam 5 detik untuk menerapkan seluruh perubahan kode yang baru Anda buat!"
        except Exception as e:
            return f"Terjadi kesalahan saat restart: {str(e)}"
