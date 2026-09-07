# JARVIS — Advanced Voice AI Agent

A professional, Jarvis-style **realtime voice AI agent** for Windows that you talk to out loud in your browser.

**LiveKit realtime voice** — full-duplex, low-latency conversation over WebRTC (LiveKit Cloud) with **Silero VAD** turn detection, **Deepgram** speech-to-text, **Groq** LLM brain with tool calling, and **Cartesia** (heavy robot "Jarvis") text-to-speech.

## Realtime stack (LiveKit)

| Layer | Service | Role |
|---|---|---|
| Transport | LiveKit Cloud `wss://jarvis-fx99558r.livekit.cloud` | WebRTC audio in/out |
| Turn detection | Silero VAD (`livekit-plugins-silero`) | Detects when you start/stop speaking, enables barge-in |
| Ears (STT) | Deepgram `nova-3` | Speech → text |
| Brain (LLM) | Groq `openai/gpt-oss-120b` (OpenAI-compatible) | Reasoning, planning, **live tool calling** |
| Mouth (TTS) | Cartesia `sonic-3` — voice *Ronald (deep/intense)* | Text → heavy robot "Jarvis" voice |
| Web search | Tavily | Online search + sourced answers |
| Semantic memory | Cohere embeddings + Qdrant | Long-term recall of facts & notes |
| Long-term store | MongoDB Atlas | Conversation history, command audit log |

## Features

- 🎙️ **Real-time voice chat** — speak, get interrupted, talk over the agent
- 🧠 **Autonomous agent loop** — thinks, calls tools, acts, answers — all by voice
- 💻 **Runs any command** — with a safety gate (destructive commands denied; sensitive ones ask for your verbal confirmation)
- 🌐 **Real-time web search** (Tavily) + **full webpage reading**
- 🧠 **Permanent semantic memory** (Qdrant + Cohere) — remembers facts across sessions
- 🗄️ **MongoDB persistence** — transcripts & command audit logs
- ⚙️ **System status** — CPU, RAM, disk, battery (psutil)
- 🖥️ **Web frontend** — talk to JARVIS from a browser

## Quick Start

```powershell
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Copy .env.example to .env and fill in your API keys
copy .env.example .env

# 3. Start the voice worker (terminal 1) - registers with LiveKit Cloud
python worker.py dev

# 4. Start the web frontend (terminal 2)
python frontend_server.py

# 5. Open http://localhost:8000, click "Connect & Start Talking", and speak.
#    (Silero VAD detects your speech; Cartesia talks back in the Jarvis voice.)
```

> **Note:** The worker must be running before you connect — LiveKit Cloud
> auto-dispatches it to any room a participant joins. If a connect seems to
> hang with no agent, check the worker window for `JARVIS dispatched to room …`.

## Safety model

- **DENY** (refused outright): destructive/system-damaging operations (`rm -rf`, disk format, registry nukes, etc.)
- **CONFIRM** (asks you out loud): shutdown/restart, taskkill, file deletion, etc. — the agent verbally asks, then re-runs only if you agree.
- Everything logged to MongoDB `command_log` for audit.

## What you can say

- "What time is it?" / "Check system status"
- "Open notepad" / "Open chrome and go to github.com"
- "Search online for today's AI news" / "Fetch and summarize https://…"
- "Remember that my car plate is ABC-123" → later "What is my car plate?"
- "Run `ipconfig`" / "Run `echo hello from jarvis`"

## Environment (.env)

`GROQ_API_KEY` / `GROQ_MODEL` · `TAVILY_API_KEY` · `COHERE_API_KEY` ·
`QDRANT_URL` / `QDRANT_API_KEY` · `Mongodb_url` · `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` ·
`DEEPGRAM_API_KEY` / `DEEPGRAM_MODEL` · `CARTESIA_API_KEY` / `CARTESIA_MODEL` / `CARTESIA_VOICE` / `CARTESIA_EMOTION` / `CARTESIA_SPEED`

## Project layout

```
start_worker.bat      one-click launcher: LiveKit worker
start_frontend.bat    one-click launcher: web server (opens the browser)
worker.py             LiveKit worker (AgentServer + rtc_session entrypoint)
core/livekit_agent.py JarvisAgent + @function_tool tools (the realtime brain)
tools/                system (run cmd, open apps), web (Tavily), memory (notes)
memory/               MongoDB store + Qdrant/Cohere vector memory
frontend/             browser voice client
frontend_server.py    serves the page + issues join tokens
get_token.py          manual token generator
config.py             central config from .env
```