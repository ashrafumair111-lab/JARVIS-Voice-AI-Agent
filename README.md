<div align="center">

<img src="assets/jarvis-logo.svg" alt="JARVIS AI" width="640"/>

**A real-time, full-duplex AI voice assistant for your PC — talk to it, it talks back.**

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python" height="22"/></a>
  <a href="https://livekit.io/"><img src="https://img.shields.io/badge/LiveKit-Cloud-00C2A8?logo=livekit&logoColor=white" alt="LiveKit" height="22"/></a>
  <a href="https://webrtc.org/"><img src="https://img.shields.io/badge/WebRTC-Realtime-333333?logo=webrtc&logoColor=white" alt="WebRTC" height="22"/></a>
  <a href="https://deepgram.com/"><img src="https://img.shields.io/badge/Deepgram-STT-13EF93?logo=deepgram&logoColor=black" alt="Deepgram" height="22"/></a>
  <a href="https://groq.com/"><img src="https://img.shields.io/badge/Groq-LLM-F55036?logo=groq&logoColor=white" alt="Groq" height="22"/></a>
  <a href="https://cartesia.ai/"><img src="https://img.shields.io/badge/Cartesia-TTS-111111?logo=cartesia&logoColor=white" alt="Cartesia" height="22"/></a>
  <a href="https://github.com/snakers4/silero-vad"><img src="https://img.shields.io/badge/Silero_VAD-Turn_Detection-8A2BE2" alt="Silero VAD" height="22"/></a>
  <a href="https://tavily.com/"><img src="https://img.shields.io/badge/Tavily-Search-2B7BB9?logo=tavily&logoColor=white" alt="Tavily" height="22"/></a>
  <a href="https://cohere.com/"><img src="https://img.shields.io/badge/Cohere-Embeddings-39594D?logo=cohere&logoColor=white" alt="Cohere" height="22"/></a>
  <a href="https://qdrant.tech/"><img src="https://img.shields.io/badge/Qdrant-Memory-DC382D?logo=qdrant&logoColor=white" alt="Qdrant" height="22"/></a>
  <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-History-47A248?logo=mongodb&logoColor=white" alt="MongoDB" height="22"/></a>
  <a href="https://www.microsoft.com/windows"><img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows11&logoColor=white" alt="Windows" height="22"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2f8fe0.svg" alt="MIT License" height="22"/></a>
</p>

*Deepgram STT · Groq LLM · Cartesia TTS · Silero VAD — over WebRTC*

</div>

---

## ✨ What is JARVIS?

JARVIS is a **realtime voice agent** you run on your own machine. Open a web page, click one
button, and just speak — no wake words, no push-to-talk. It hears you, thinks with an LLM,
calls tools when needed, and answers in a deep "Jarvis-style" robotic voice, with full
**barge-in** (interrupt it whenever you like).

```
 ┌──────────┐   WebRTC    ┌─────────────────────────────┐
 │  Browser │◄═══════════►│      LiveKit Cloud          │
 │  (mic +  │             │  room + audio transport     │
 │ speaker) │             └──────────────┬──────────────┘
 └──────────┘                            │ job dispatch
                              ┌──────────▼───────────────┐
                              │   JARVIS worker (local)  │
                              │  ┌────────────────────┐  │
                              │  │ Silero VAD (local) │──┼── turn detection & barge-in
                              │  │ Deepgram  STT      │──┼── speech → text
                              │  │ Groq      LLM      │──┼── reasoning + tool calls
                              │  │ Cartesia  TTS      │──┼── text → Jarvis voice
                              │  └────────────────────┘  │
                              └───┬───────┬─────────┬────┘
                                  │       │         │
                             MongoDB    Qdrant +   Tavily
                          (history &   Cohere     (web search)
                           audit log)  (memory)
```

## 🚀 Features

| | |
|---|---|
| 🎙️ **Realtime voice chat** | Full-duplex WebRTC audio — speak and get answers with sub-second latency |
| ✋ **Barge-in & interruption** | Interrupt JARVIS mid-sentence just by talking (local Silero VAD, no cloud round-trip) |
| 🧠 **LLM brain with tools** | Groq (`gpt-oss-120b`) plans and calls tools autonomously |
| 💻 **PC control — with a safety gate** | Runs commands, opens apps, checks CPU/RAM/battery. Destructive commands are **denied**, risky ones **require verbal confirmation** |
| 🌐 **Live web search** | Tavily search + full webpage reading & summarization |
| 🧬 **Permanent semantic memory** | Remembers facts across sessions (Qdrant + Cohere embeddings) |
| 🗄️ **Persistence** | Conversation history & command audit log in MongoDB Atlas |
| 🖥️ **Browser UI** | One-click connect, live captions, mic level meter, sound check |

## ⚡ Quick Start

### Prerequisites
- **Python 3.10+** on your PATH
- API keys: [LiveKit](https://cloud.livekit.io/) · [Groq](https://console.groq.com/keys) · [Deepgram](https://console.deepgram.com/) · [Cartesia](https://play.cartesia.ai/keys) · [Tavily](https://tavily.com/) *(optional: Qdrant, Cohere, MongoDB)*

### Install & run

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/jarvis-ai.git
cd jarvis-ai

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Create your .env
cp .env.example .env        # Windows: copy .env.example .env
#    → fill in your API keys

# 4. Terminal 1 — start the voice worker (the agent itself)
python worker.py dev
#    wait for:  registered worker

# 5. Terminal 2 — start the web UI
python frontend_server.py

# 6. Open http://localhost:8000 → Connect & Start Talking → just speak 🎙️
```

## 💬 Things to say

- *"What time is it?"* — *"Check system status"*
- *"Open notepad"* — *"Open chrome and go to github.com"*
- *"Search online for today's AI news"* — *"Fetch and summarize https://…"*
- *"Remember that my car plate is ABC-123"* → later: *"What is my car plate?"*
- *"Run ipconfig"* — *"Run echo hello from jarvis"*

## 🛡️ Safety model

Every command the LLM wants to run passes through a local gate in `config.py`:

| Level | Behaviour | Examples |
|---|---|---|
| ✅ **ALLOW** | runs instantly | `ipconfig`, `echo`, opening apps |
| ⚠️ **CONFIRM** | JARVIS asks out loud; runs only after you agree | `shutdown`, `taskkill`, deleting files |
| ⛔ **DENY** | refused outright | `format`, `diskpart`, `rm -rf`, registry wipes |

All executed commands are written to a MongoDB `command_log` for auditing.

## 📁 Project structure

```
jarvis-ai/
├── worker.py               LiveKit worker — builds the voice pipeline & agent session
├── frontend_server.py      Local web server: serves the UI + issues join tokens
├── get_token.py            Standalone LiveKit token generator
├── config.py               Central config — reads .env, safety patterns
├── core/
│   └── livekit_agent.py    JarvisAgent — system prompt + @function_tool definitions
├── tools/
│   ├── system_tools.py     run commands, open apps, system status (psutil)
│   ├── web_tools.py        Tavily search + webpage reading
│   └── memory_tools.py     save/recall semantic memories
├── memory/
│   ├── mongo_store.py      MongoDB history + command audit log
│   └── vector_store.py     Qdrant + Cohere vector memory
├── frontend/
│   └── index.html          Browser client (LiveKit SDK, captions, mic meter)
├── assets/
│   └── jarvis-logo.svg     Project logo
└── .env.example            All required environment variables, documented
```

## 🔧 Troubleshooting

| Symptom | Fix |
|---|---|
| `Python was not found` | `python.exe` folder missing from PATH — add it, or disable the Microsoft Store alias (*Settings → Apps → Advanced app settings → App execution aliases*) |
| `python worker.py dev` exits immediately | Re-check `LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET` in `.env` |
| Page connects but no agent joins | The worker window must show `registered worker` **before** you connect |
| You speak, agent stays silent | Wait for the green **Listening** state; pause ~0.6 s after speaking; click **🔊 Test sound** to verify browser output; check the Windows Volume Mixer for your browser |
| Frequent reconnects | Unstable route to your LiveKit region — the worker auto-reconnects; pick a closer region in your LiveKit project |

## 📜 License

[MIT](LICENSE) © 2026 Ashraf Umair

---

<div align="center">
<sub>Built with <a href="https://livekit.io/">LiveKit Agents</a> · <a href="https://groq.com/">Groq</a> · <a href="https://deepgram.com/">Deepgram</a> · <a href="https://cartesia.ai/">Cartesia</a> · <a href="https://github.com/snakers4/silero-vad">Silero VAD</a></sub>
</div>
