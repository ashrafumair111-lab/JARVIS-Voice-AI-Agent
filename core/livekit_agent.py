"""JARVIS realtime voice agent (LiveKit Agents 1.8).

@function_tool methods on this Agent subclass become LLM tools. The full
realtime pipeline (VAD/STT/LLM/TTS) is wired up in ``worker.py``.
"""

import asyncio
import json
import logging

from livekit.agents import Agent, RunContext
from livekit.agents.llm import function_tool

from tools.memory_tools import MemoryTools
from tools.system_tools import SystemTools
from tools.web_tools import WebTools

logger = logging.getLogger("jarvis.livekit")

SYSTEM_PROMPT = """You are JARVIS, an extraordinarily capable, professional and mildly witty AI personal assistant in a realtime voice conversation.
You speak aloud, so keep replies concise and natural for voice: a sentence or three, no markdown, no code fences, no symbol lists. Call the user "sir" when natural..

Rules:
1. ACT: when a task needs a tool, call it. Never invent results..
2. open apps/URLs via open_application / open_url..
3. live or unknown info: web_search. To read a page: fetch_webpage..
4. to remember facts: save_note. If a question concerns things told before: recall_memory first..
5. run_command runs real shell commands on this PC. Only safe, reversible commands. NEVER destructive ones (deleting system files, formatting, killing processes.. If a result says needs_confirmation, do NOT claim success: ask the user to confirm out loud, then re-run with confirmed=True only if they agree..
6. if a tool errors, say so honestly and try a sensible alternative..
7. Never claim an action you did not perform..
"""


class JarvisAgent(Agent):
    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)
        self.sys = SystemTools(mongo=None)
        self.web = WebTools()
        self.mem = MemoryTools(mongo=None, vectors=None)

    # ------------------------------------------------------------------
    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="Greet the user as JARVIS, briefly introduce yourself, "
                         "and ask how you can help today."
        )

    async def _run(self, fn, *args, **kwargs):
        """Run a blocking tool method off the event loop; return JSON str."""
        result = await asyncio.to_thread(fn, *args, **kwargs)
        return json.dumps(result, ensure_ascii=False)

    # ------------------------------- tools ----------------------------
    @function_tool
    async def get_time(self, context: RunContext) -> str:
        """Get the current local date and time of the user's computer.

        Args:
            None..
        """
        return await self._run(self.sys.get_time)

    @function_tool
    async def system_status(self, context: RunContext) -> str:
        """Get CPU, RAM,, disk and battery status of the user's PC..

        Args:
            None..
        """
        return await self._run(self.sys.system_status)

    @function_tool
    async def open_application(self, context: RunContext, name: str) -> str:
        """Open an application on the Windows PC (notepad, calculator, chrome, cmd, settings.,

        Args:
            name: Name of the app to open.

        """
        return await self._run(self.sys.open_application, name)

    @function_tool
    async def open_url(self, context: RunContext, url: str) -> str:
        """Open a URL in the default web browser..

        Args:
            url: Full URL to open..
        """
        return await self._run(self.sys.open_url, url)
    @function_tool
    async def run_command(self, context: RunContext, command: str,
                          confirmed: bool = False) -> str:
        """Run a safe shell command on the user's Windows PC and return its output..

        Destructive commands are refused. If the result is needs_confirmation,
        ask the user out loud first,, then re-run with confirmed=True only if they agree..

        Args:
            command: The shell command to run..
            confirmed: True allows flagged sensitive commands after user agrees..
        """
        return await self._run(self.sys.execute_managed, command, confirmed)

    @function_tool
    async def web_search(self, context: RunContext, query: str,
                         max_results: int = 5) -> str:
        """Search the live web (Tavily) and return snippets plus a short answer..

        Args:
            query: Natural-language search query..
            max_results: Max results (1-8..
        """
        return await self._run(self.web.search, query, max_results)

    @function_tool
    async def fetch_webpage(self, context: RunContext, url: str) -> str:
        """Fetch and extract readable text from a webpage URL..

        Args:
            url: The page URL to fetch..
        """
        return await self._run(self.web.fetch, url)

    @function_tool
    async def save_note(self, context: RunContext, text: str,
                        tags: list[str] | None = None) -> str:
        """Save a note/fact to long-term memory so JARVIS remembers it later..

        Args:
            text: The note text to remember..
            tags: Optional list of tags..
        """
        return await self._run(self.mem.save_note, text, tags)

    @function_tool
    async def recall_memory(self, context: RunContext, query: str,
                            limit: int = 5) -> str:
        """Recall notes/facts the user asked to remember (semantic search..

        Args:
            query: What to recall..
            limit: Max hits..
        """
        return await self._run(self.mem.recall, query, limit)