TASKS_PROMPT = """Example of managing tasks (Google Tasks):
```json
{
  "tool_call": {
    "name": "TaskTool",
    "arguments": {"action": "list_tasks"}
  }
}
```"""
