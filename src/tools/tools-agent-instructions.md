import os

file_content = """# Agent Instructions: Tools Module

## 🎯 Role & Objective
You are the AI workflow executor managing the `tools` module. Your task is to provide the core agent with extended capabilities by executing external functions (tools) such as web searching, image analysis, and document reading.

## 📂 Module Context
- `tool-registry.py`: The central registry where all available tools are registered and mapped to their respective execution schemas.
- `web-search-tool.py`: Executes queries against search engines to retrieve real-time information.
- `vision-analyzer-tool.py`: Processes image inputs and returns descriptions, OCR text, or specific object analysis.
- `document-reader-tool.py`: Parses and extracts text from various document formats (e.g., PDF, TXT, DOCX).

## 🛠️ Triggers & Tool Execution
When the `AgentOrchestrator` determines a tool call is necessary, follow these protocols:

### 1. Tool Registration & Routing
- **Trigger:** System startup or tool initialization.
- **Action:** Ensure `tool-registry.py` properly catalogs all tools with clear JSON schemas so the LLM understands exactly what inputs are required. 

### 2. Execution Logic
- **Web Search:** Execute when queries require up-to-date factual data, news, or specific references not present in the model's weights.
- **Vision Analysis:** Execute when the user payload includes an image file path or URL. Ensure the image is passed correctly to the Vision API.
- **Document Reading:** Execute when a user requests summarization or extraction from an uploaded file.

### 3. Response Handling
- **Format:** All tools MUST return their results in a structured format (preferably JSON or clean text) that the main Agent can easily parse and integrate into its final natural language response.
- **Error Handling:** If a tool fails (e.g., search API timeout, unreadable document), return a clear error message to the orchestrator instead of crashing the process.

## ⚠️ Strict Constraints & Code Convention
- **Code Style:** All Python code within this module MUST strictly follow the **PascalCase** naming convention for classes, methods, and variables (e.g., `WebSearchTool`, `ExecuteSearch()`, `VisionAnalyzer`).
- **Stateless Execution:** Tool classes should be stateless. Do not store conversational memory within individual tool instances.

## 📝 Acknowledgment
Read these instructions silently. Apply these execution rules automatically whenever interacting with the tools module.
"""

file_path = "/mnt/data/tools-agent-instructions.md"
with open(file_path, "w") as f:
    f.write(file_content)

file_path