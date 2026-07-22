import os
import asyncio
import threading
import contextlib
import json
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


class McpManager:
    def __init__(self, command, args=None, env=None):
        self.command = command
        self.args = args or []
        self.env = env or os.environ.copy()

        self.server_params = StdioServerParameters(
            command=self.command, args=self.args, env=self.env
        )

        self.tools = []
        self._initialized = threading.Event()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        # Start connection
        asyncio.run_coroutine_threadsafe(self._init_session(), self.loop)

        # Wait up to 10 seconds for init
        self._initialized.wait(timeout=10)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _init_session(self):
        try:
            self._exit_stack = contextlib.AsyncExitStack()
            (
                self.read_stream,
                self.write_stream,
            ) = await self._exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(self.read_stream, self.write_stream)
            )

            await self.session.initialize()

            tools_response = await self.session.list_tools()
            self.tools = tools_response.tools
            print(
                f"McpManager: Connected to {self.command}. Loaded {len(self.tools)} tools."
            )
        except Exception as e:
            print(f"McpManager: Error initializing MCP session - {e}")
        finally:
            self._initialized.set()

    def GetSchemas(self):
        schemas = []
        for tool in self.tools:
            # Format according to OpenAI function calling spec
            # MCP inputSchema is already JSON schema
            properties = tool.inputSchema.get("properties", {})
            required = tool.inputSchema.get("required", [])

            schema = {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            schemas.append(schema)
        return schemas

    def Execute(self, tool_name, arguments):
        future = asyncio.run_coroutine_threadsafe(
            self.session.call_tool(tool_name, arguments), self.loop
        )
        try:
            # Wait up to 60s for tool execution
            result = future.result(timeout=60)

            output = ""
            for content in result.content:
                if content.type == "text":
                    output += content.text + "\n"

            if result.isError:
                output = f"[Error] {output}"

            return output.strip()
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"


class McpToolWrapper:
    def __init__(self, manager, tool_name):
        self.manager = manager
        self.tool_name = tool_name

    def Execute(self, arguments):
        return self.manager.Execute(self.tool_name, arguments)
