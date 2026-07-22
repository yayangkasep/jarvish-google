import os
import requests

class InstallSkillTool:
    def __init__(self):
        self.ToolName = "InstallSkill"
        self.Schema = {
            "type": "function",
            "function": {
                "name": self.ToolName,
                "description": "Mengunduh dan memasang skill koding baru ke dalam J.A.R.V.I.S.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Nama folder skill yang akan dibuat (misalnya: 'react', 'python-api'). Gunakan huruf kecil dan strip (kebab-case)."
                        },
                        "source_url": {
                            "type": "string",
                            "description": "URL sumber file markdown skill (misalnya dari raw.githubusercontent.com). Jika ada."
                        },
                        "content": {
                            "type": "string",
                            "description": "Isi teks manual dari skill tersebut jika tidak menggunakan source_url."
                        }
                    },
                    "required": ["skill_name"]
                }
            }
        }

    def Execute(self, Arguments):
        skill_name = Arguments.get("skill_name")
        source_url = Arguments.get("source_url")
        content = Arguments.get("content")

        if not skill_name:
            return "Error: skill_name harus diisi."

        if not source_url and not content:
            return "Error: Anda harus menyertakan source_url atau content."

        # Menyiapkan path
        skills_dir = os.path.expanduser("~/.jarvish/skills")
        skill_path = os.path.join(skills_dir, skill_name)
        skill_file = os.path.join(skill_path, "SKILL.md")

        try:
            # Membuat folder skill
            os.makedirs(skill_path, exist_ok=True)

            final_content = content
            if source_url:
                response = requests.get(source_url, timeout=10)
                if response.status_code == 200:
                    final_content = response.text
                else:
                    return f"Error: Gagal mengunduh dari URL. HTTP Status: {response.status_code}"

            if not final_content:
                return "Error: Konten skill kosong."

            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(final_content)

            return f"Sukses! Skill '{skill_name}' berhasil dipasang dan disimpan di {skill_file}. Sekarang Anda bisa menggunakan '@{skill_name}' di obrolan."

        except Exception as e:
            return f"Terjadi kesalahan saat memasang skill: {str(e)}"
