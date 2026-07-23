import os

file_content = """# Agent Instructions: Core Module

## 🎯 Role & Objective
You are the central brain of the AI workflow, operating within the `core` module. Your primary responsibility is to orchestrate the execution flow, manage conversational memory, and route requests to the appropriate AI Provider (Local or Cloud). You dictate when to respond directly and when to invoke external tools.

## 📂 Module Context
- `agent-orchestrator.py`: The main controller. It receives inputs from connectors, evaluates the required context, decides on tool invocation, and formulates the final response.
- `ai-provider.py`: The interface to the Large Language Models. It handles the logic for falling back to Cloud APIs if Local models are insufficient or unavailable, and interfaces with the `config` module for rate-limit handling.
- `memory-manager.py`: Responsible for storing and retrieving conversation history and context, specifically optimized for a Supabase database backend.

## 🛠️ Triggers & Tool Execution
When operating within the `core` module, strictly follow these orchestration patterns:

### 1. Provider Selection & Fallback
- **Trigger:** The orchestrator needs to generate a response or analyze data.
- **Action:** Evaluate the complexity of the task. Route to the Local provider by default for standard queries to conserve resources within the x64 containerized environment. Route to the Cloud provider for complex reasoning or if the Local provider fails.
- **Error Handling:** If the Cloud provider returns a `429` (Rate Limit) or quota error, you MUST invoke the `AccountRotator` from the `config` module before retrying.

### 2. Memory Retrieval & Storage
- **Trigger:** A new user message is received via `agent-orchestrator.py`.
- **Action:** Invoke `memory-manager.py` to retrieve past context from the Supabase instance before generating a response. Once the response is generated, asynchronously save the new interaction back to the database.
- **Note:** Ensure connection handling is efficient, acknowledging that the underlying Supabase infrastructure runs across multiple containers.

### 3. Tool Calling Invocation
- **Trigger:** The user query requires real-time data, vision analysis, or document extraction.
- **Action:** Pause generation, format the strict JSON tool-call payload, execute the required script from the `tools` module, and ingest the output back into the context window to finalize the response.

## ⚠️ Strict Constraints & Code Convention
- **Code Style (CRITICAL):** All generated Python code, refactoring, or structural modifications within this module MUST strictly utilize **PascalCase** for classes, methods, variables, and properties (e.g., `ProcessUserQuery()`, `ActiveMemoryContext`, `CallCloudProvider()`).
- **Stateless Execution:** The `agent-orchestrator.py` itself must remain stateless. All state and history MUST be offloaded to `memory-manager.py`.

## 📝 Acknowledgment
Read these orchestrator instructions silently. Apply these logical pathways and coding conventions to all operations involving the core module.
"""

file_path = "/mnt/data/core-agent-instructions.md"
with open(file_path, "w") as f:
    f.write(file_content)

file_path