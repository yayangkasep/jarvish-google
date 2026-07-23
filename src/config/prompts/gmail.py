GMAIL_READ_PROMPT = """Example for reading emails:
```json
{
  "tool_call": {
    "name": "ReadRecentEmails",
    "arguments": {"query": "in:spam"}
  }
}
```"""

GMAIL_SEND_PROMPT = """Example for sending emails:
```json
{
  "tool_call": {
    "name": "SendEmail",
    "arguments": {"to": "target@email.com", "subject": "Subject", "body": "Content"}
  }
}
```"""
