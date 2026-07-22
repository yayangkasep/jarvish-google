TASKS_PROMPT = """Contoh mengelola tugas (Google Tasks):
```json
{
  "tool_call": {
    "name": "TaskTool",
    "arguments": {"action": "list_tasks"}
  }
}
```"""
