from .base import BASE_PERSONA, STYLE_GUIDELINES, TOOL_USAGE_INTRO
from .system_os import SYSTEM_OS_PROMPT
from .gmail import GMAIL_READ_PROMPT, GMAIL_SEND_PROMPT
from .google_calendar import CALENDAR_PROMPT
from .google_tasks import TASKS_PROMPT
from .google_drive import DRIVE_PROMPT
from .image_gen import IMAGE_GEN_PROMPT
from .web_search import WEB_SEARCH_PROMPT
from .coding import CODING_PROMPT

__all__ = [
    "BASE_PERSONA", 
    "STYLE_GUIDELINES",
    "TOOL_USAGE_INTRO",
    "IMAGE_GEN_PROMPT",
    "SYSTEM_OS_PROMPT",
    "GMAIL_READ_PROMPT",
    "GMAIL_SEND_PROMPT",
    "CALENDAR_PROMPT",
    "TASKS_PROMPT",
    "DRIVE_PROMPT",
    "WEB_SEARCH_PROMPT",
    "CODING_PROMPT"
]
