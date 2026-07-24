class ToolRegistry:
    def __init__(self):
        self.AvailableTools = {}

    def RegisterTool(self, ToolName, ToolInstance, Schema):
        """
        Registers a tool with its corresponding Google Cloud function calling schema.
        """
        self.AvailableTools[ToolName] = {"Instance": ToolInstance, "Schema": Schema}
        print(f"Tool Registered: {ToolName}")

    def GetToolSchemas(self):
        """
        Returns a list of all registered schemas, which can be passed directly to the AiProvider.
        """
        Schemas = []
        for ToolName, ToolData in self.AvailableTools.items():
            Schemas.append(ToolData["Schema"])
        return Schemas

    def AutoDiscoverTools(self, tools_dir):
        """
        Automatically discovers and registers tools from a given directory.
        """
        import os
        import importlib
        import inspect

        if not os.path.exists(tools_dir):
            print(f"Tools directory {tools_dir} not found.")
            return

        for filename in os.listdir(tools_dir):
            if (
                filename.endswith(".py")
                and filename != "tool-registry.py"
                and filename != "__init__.py"
            ):
                module_name = filename[:-3]
                # Try to import assuming it's in the 'tools' package or relative
                try:
                    try:
                        module_path = f"{os.path.basename(tools_dir)}.{module_name}"
                        module = importlib.import_module(module_path)
                    except ImportError:
                        import importlib.util
                        import sys
                        file_path = os.path.join(tools_dir, filename)
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Ensure the class is defined in the module, not imported
                        if obj.__module__ == module.__name__:
                            # We assume any class ending in 'Tool' is a tool to be registered
                            if name.endswith("Tool"):
                                try:
                                    instance = obj()
                                    if hasattr(instance, "ToolName") and hasattr(
                                        instance, "Schema"
                                    ):
                                        self.RegisterTool(
                                            instance.ToolName, instance, instance.Schema
                                        )
                                except Exception as inner_e:
                                    print(f"Error instantiating tool {name}: {inner_e}")
                except Exception as e:
                    print(f"Error loading tool module {filename}: {e}")

    def ExecuteTool(self, ToolName, Arguments):
        """
        Executes a specific tool by name with the given arguments.
        """
        if ToolName in self.AvailableTools:
            ToolInstance = self.AvailableTools[ToolName]["Instance"]

            # Assuming all tools implement an Execute() method per PascalCase convention
            if hasattr(ToolInstance, "Execute"):
                return ToolInstance.Execute(Arguments)
            else:
                return f"Error: Tool {ToolName} does not have an Execute method."
        return f"Error: Tool {ToolName} not found."
