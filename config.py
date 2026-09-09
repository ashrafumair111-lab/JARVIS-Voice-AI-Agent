"""Central configuration - loads .env and exposes all service constants."""

import os
import re
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# override=True so .env is the authoritative source, even if the same vars
# are already exported in the OS/shell environment (e.g. an old GROQ_API_KEY
# or GROQ_MODEL lingering in a conda activation script or profile).
load_dotenv(BASE_DIR / ".env", override=True)

# ----------------------------------------------------------------- Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# ----------------------------------------------------------------- LiveKit Cloud
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")

# ----------------------------------------------------------------- Deepgram STT
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
DEEPGRAM_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-3")

# ----------------------------------------------------------------- Cartesia TTS
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", "")
CARTESIA_MODEL = os.getenv("CARTESIA_MODEL", "sonic-3")
CARTESIA_VOICE = os.getenv("CARTESIA_VOICE", "5ee9feff-1265-424a-9d7f-8e4d431a12c7")
CARTESIA_EMOTION = os.getenv("CARTESIA_EMOTION", "Confident")
# Cartesia sonic-3 requires a float speed (e.g. "0.94"); "normal"/"" disables it.
_raw_speed = os.getenv("CARTESIA_SPEED", "").strip().lower()
try:
    CARTESIA_SPEED = float(_raw_speed) if _raw_speed else None
except ValueError:
    CARTESIA_SPEED = None

# ----------------------------------------------------------------- Tavily
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_URL = "https://api.tavily.com/search"

# ----------------------------------------------------------------- Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
EMBED_MODEL = "embed-english-v3.0"
VECTOR_SIZE = 1024  # embed-english-v3.0 output dims

# ----------------------------------------------------------------- Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
MEMORY_COLLECTION = "jarvis_memory"

# ----------------------------------------------------------------- MongoDB
MONGO_URL = os.getenv("MONGO_URL") or os.getenv("Mongodb_url", "")
MONGO_DB = "jarvis_db"

# ----------------------------------------------------------------- Behaviour
MAX_TOKENS = 2048
TEMPERATURE = 0.6

# ----------------------------------------------------------------- Safety
DENY_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*\s+)*[-/][a-zA-Z]:?\\",
    r"rm\s+-[a-zA-Z]*[rR]",
    r"format\s+[a-zA-Z]:",
    r"diskpart",
    r"del\s+/[sfq].*[A-Z]:?\\",
    r"rd\s+/s\s+/q.*[A-Z]:?\\",
    r"Remove-Item\s+-Recurse.*[A-Z]:?\\",
    r"bootrec",
    r"cipher\s+/w:",
    r"taskkill.*svchost",
    r"vssadmin\s+delete|shadowcopy",
]

CONFIRM_PATTERNS = [
    r"shutdown|stop-computer|restart-computer|reboot",
    r"taskkill|Stop-Process|kill\s+-9",
    r"\bdel\s+|Remove-Item|rm\s+",
    r"net\s+user",
    r"reg\s+(add|delete)",
    r"sc\s+config|Set-Service",
    r"pip\s+uninstall|pip3\s+uninstall",
    r"conda\s+(remove|uninstall)",
    r"fsutil",
    r"bcdedit",
]

def pattern_matches(patterns, command):
    """Return True if any regex pattern matches command (case-insensitive)."""
    for pat in patterns:
        if re.search(pat, command, re.IGNORECASE):
            return True
    return False


def load_enabled_services() -> dict:
    """Quick health summary of configured services."""
    return {
        "groq_llm": bool(GROQ_API_KEY),
        "groq_stt": bool(GROQ_API_KEY),
        "groq_tts": bool(GROQ_API_KEY),
        "tavily": bool(TAVILY_API_KEY),
        "cohere": bool(COHERE_API_KEY),
        "qdrant": bool(QDRANT_URL and QDRANT_API_KEY),
        "mongo": bool(MONGO_URL),
        "livekit": bool(LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET),
        "deepgram": bool(DEEPGRAM_API_KEY),
        "cartesia": bool(CARTESIA_API_KEY),
        "silero_vad": True,
    }
