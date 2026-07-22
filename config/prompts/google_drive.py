DRIVE_PROMPT = """Contoh mencari file di Google Drive:
```json
{
  "tool_call": {
    "name": "DriveTool",
    "arguments": {"action": "search_files", "query": "name contains 'laporan'"}
  }
}
```"""
