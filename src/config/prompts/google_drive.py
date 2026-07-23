DRIVE_PROMPT = """Example of searching for files in Google Drive:
```json
{
  "tool_call": {
    "name": "DriveTool",
    "arguments": {"action": "search_files", "query": "name contains 'report'"}
  }
}
```"""
