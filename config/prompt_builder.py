from config.prompts.base import BASE_PERSONA, STYLE_GUIDELINES, TOOL_USAGE_INTRO, FOOTER_INSTRUCTION
from config.prompts.gmail import GMAIL_READ_PROMPT, GMAIL_SEND_PROMPT
from config.prompts.system_os import SYSTEM_OS_PROMPT
from config.prompts.google_calendar import CALENDAR_PROMPT
from config.prompts.google_tasks import TASKS_PROMPT
from config.prompts.google_drive import DRIVE_PROMPT
from config.prompts.github import GITHUB_PROMPT
from config.prompts.web_search import WEB_SEARCH_PROMPT
from config.prompts.image_gen import IMAGE_GEN_PROMPT
from config.prompts.coding import CODING_PROMPT
from config.prompts.skill_management import SKILL_MANAGEMENT_PROMPT
import os
import re

def load_active_skills(messages):
    if not messages: return ""
    
    skills_dirs = [
        os.path.join(os.path.dirname(__file__), "skills"),
        os.path.expanduser("~/.jarvish/skills")
    ]
        
    available_skills = {}
    for skills_dir in skills_dirs:
        if not os.path.exists(skills_dir):
            continue
            
        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            if os.path.isdir(item_path):
                skill_md_path = os.path.join(item_path, "SKILL.md")
                if os.path.exists(skill_md_path):
                    skill_name = item.lower()
                    available_skills[skill_name] = skill_md_path
            
    active_skills_content = []
    activated = set()
    
    # Check all user messages for @skillname
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, list): # handle image payload
                text_content = " ".join([c.get("text", "") for c in content if c.get("type") == "text"])
            else:
                text_content = content
                
            # Find words starting with @
            matches = re.findall(r'@([a-zA-Z0-9_-]+)', text_content.lower())
            for match in matches:
                if match in available_skills and match not in activated:
                    activated.add(match)
                    with open(available_skills[match], "r", encoding="utf-8") as f:
                        active_skills_content.append(f"--- SKILL ACTIVATED: {match} ---\n{f.read()}")
                        
    if active_skills_content:
        return "ATURAN TAMBAHAN BERDASARKAN SKILLS YANG DIAKTIFKAN:\n" + "\n\n".join(active_skills_content)
    return ""

# Mapping of tool names to their respective prompts
TOOL_PROMPTS_MAPPING = {
    "ReadRecentEmails": GMAIL_READ_PROMPT,
    "SendEmail": GMAIL_SEND_PROMPT,
    "SystemCommand": SYSTEM_OS_PROMPT,
    "UpdateJarvish": SYSTEM_OS_PROMPT,
    "InstallSkill": SKILL_MANAGEMENT_PROMPT,
    "CalendarTool": CALENDAR_PROMPT,
    "TaskTool": TASKS_PROMPT,
    "DriveTool": DRIVE_PROMPT,
    "WebSearch": WEB_SEARCH_PROMPT,
    "ReadWebpage": WEB_SEARCH_PROMPT,
    "ListDirectory": CODING_PROMPT,
    "ReadFile": CODING_PROMPT,
    "GrepSearch": CODING_PROMPT,
    "WriteFile": CODING_PROMPT,
    "ReplaceContent": CODING_PROMPT,
    "MakeDirectory": CODING_PROMPT,
    "RemoveFile": CODING_PROMPT,
    "MoveFile": CODING_PROMPT,
    "CopyFile": CODING_PROMPT,
}

def build_system_prompt(current_time, required_tools=None, messages=None):
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
                    
    # 5. Inject Skills
    skills_prompt = load_active_skills(messages)
    if skills_prompt:
        prompt_parts.append(skills_prompt)
        
    # 6. Footer & Execution Rules
    prompt_parts.append(FOOTER_INSTRUCTION.format(current_time=current_time))
    
    # Join everything with double newlines
    return "\n\n".join(prompt_parts)
