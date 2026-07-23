GITHUB_PROMPT = """Examples of managing GitHub (tool names always start with `github_`, e.g., `github_search_repositories`, `github_create_issue`, `github_list_commits`, etc.):
- If asked to list someone's repositories, use `github_search_repositories` with query `user:username`.
- If asked to "surf the homepage" or find trending repos, use specific trending queries, e.g., `stars:>500 sort:stars-desc`.
- If asked to search for repositories with specific keywords, use a query matching those keywords.
```json
{
  "tool_call": {
    "name": "github_search_repositories",
    "arguments": {"query": "machine learning stars:>1000"}
  }
}
```"""
