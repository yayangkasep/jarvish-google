GMAIL_READ_PROMPT = """Contoh membaca email:
```json
{
  "tool_call": {
    "name": "ReadRecentEmails",
    "arguments": {"query": "in:spam"}
  }
}
```"""

GMAIL_SEND_PROMPT = """Contoh mengirim email:
```json
{
  "tool_call": {
    "name": "SendEmail",
    "arguments": {"to": "email@tujuan.com", "subject": "Subjek", "body": "Isi"}
  }
}
```"""
