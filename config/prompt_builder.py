from config.prompts.base import BASE_PERSONA, STYLE_GUIDELINES, TOOL_USAGE_INTRO, FOOTER_INSTRUCTION
from config.prompts.gmail import GMAIL_READ_PROMPT, GMAIL_SEND_PROMPT
from config.prompts.system_os import SYSTEM_OS_PROMPT
from config.prompts.google_calendar import CALENDAR_PROMPT
from config.prompts.google_tasks import TASKS_PROMPT
from config.prompts.google_drive import DRIVE_PROMPT
from config.prompts.github import GITHUB_PROMPT
from config.prompts.web_search import WEB_SEARCH_PROMPT
from config.prompts.image_gen import IMAGE_GEN_PROMPT

# Mapping of tool names to their respective prompts
TOOL_PROMPTS_MAPPING = {
    "ReadRecentEmails": GMAIL_READ_PROMPT,
    "SendEmail": GMAIL_SEND_PROMPT,
    "SystemCommand": SYSTEM_OS_PROMPT,
    "CalendarTool": CALENDAR_PROMPT,
    "TaskTool": TASKS_PROMPT,
    "DriveTool": DRIVE_PROMPT,
    "WebSearch": WEB_SEARCH_PROMPT,
    "ReadWebpage": WEB_SEARCH_PROMPT,
}

def build_system_prompt(current_time, required_tools=None):
    """
    Builds a dynamic system prompt based on the tools currently available.
    """
    # 1. Base Identity
    prompt_parts = [BASE_PERSONA]
    
    # 2. Style Guidelines
    prompt_parts.append(STYLE_GUIDELINES.format(current_time=current_time))
    
    # 3. Always-available "virtual" tools
    prompt_parts.append(IMAGE_GEN_PROMPT)
    
    # 4. Dynamic Tool Instructions
    if required_tools:
        prompt_parts.append(TOOL_USAGE_INTRO)
        
        added_prompts = set()
        
        for tool in required_tools:
            # Check if it's OpenAI format or raw schema format
            if "function" in tool:
                tool_name = tool.get("function", {}).get("name")
            else:
                tool_name = tool.get("name")
            
            if tool_name in TOOL_PROMPTS_MAPPING:
                tool_prompt = TOOL_PROMPTS_MAPPING[tool_name]
                if tool_prompt not in added_prompts:
                    prompt_parts.append(tool_prompt)
                    added_prompts.add(tool_prompt)
            # Match ANY Github tool
            elif tool_name and tool_name.startswith("github_"):
                if GITHUB_PROMPT not in added_prompts:
                    prompt_parts.append(GITHUB_PROMPT)
                    added_prompts.add(GITHUB_PROMPT)
                    
    # 5. Footer & Execution Rules
    prompt_parts.append(FOOTER_INSTRUCTION.format(current_time=current_time))
    
    # Join everything with double newlines
    return "\n\n".join(prompt_parts)
