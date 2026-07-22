GITHUB_PROMPT = """Contoh mengelola GitHub (nama tool selalu diawali `github_`, misal `github_search_repositories`, `github_create_issue`, `github_list_commits`, dll):
- Jika diminta melist repository milik seseorang, gunakan `github_search_repositories` dengan query `user:username`.
- Jika diminta "berselancar di beranda" atau mencari repo yang sedang tren, gunakan query khusus tren, misal `stars:>500 sort:stars-desc`.
- Jika diminta mencari repository dengan kata spesifik, gunakan query sesuai kata spesifik tersebut.
```json
{
  "tool_call": {
    "name": "github_search_repositories",
    "arguments": {"query": "machine learning stars:>1000"}
  }
}
```"""
