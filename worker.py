"""
JARVIS realtime voice worker (LiveKit Agents).

Run with:
    python worker.py dev

Registers the JARVIS agent with your LiveKit Cloud project (LIVEKIT_URL) and
auto-dispatches it to any room a participant joins from the web frontend.
"""

import logging

from livekit import agents
from livekit.agents import AgentServer, AgentSession, cli, room_io
from livekit.plugins import cartesia, deepgram, openai, silero

import config
from core.livekit_agent import JarvisAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def build_vad():
    """Silero VAD tuned for responsive, interruption-aware turn taking."""
    return silero.VAD.load(
        min_speech_duration=0.05,
        min_silence_duration=0.55,
        prefix_padding_duration=0.5,
        max_buffered_speech=60.0,
        activation_threshold=0.5,
        sample_rate=16000,
    )


def build_llm():
    # Groq is OpenAI-compatible; use the OpenAI plugin against Groq's endpoint.
    return openai.LLM(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        base_url=config.GROQ_BASE_URL,
        temperature=config.TEMPERATURE,
        max_completion_tokens=config.MAX_TOKENS,
        _strict_tool_schema=False,
    )


def build_stt():
    return deepgram.STT(
        model=config.DEEPGRAM_MODEL,
        api_key=config.DEEPGRAM_API_KEY,
        language="en-US",
        smart_format=True,
    )


def build_tts():
    # Cartesia "Ronald - Thinker" - intense, deep male -> heavy Jarvis robot voice.
    return cartesia.TTS(
        api_key=config.CARTESIA_API_KEY,
        model=config.CARTESIA_MODEL,
        voice=config.CARTESIA_VOICE,
        emotion=config.CARTESIA_EMOTION or None,
        speed=config.CARTESIA_SPEED or None,
    )


server = AgentServer(
    ws_url=config.LIVEKIT_URL,
    api_key=config.LIVEKIT_API_KEY,
    api_secret=config.LIVEKIT_API_SECRET,
)


@server.rtc_session()
async def entrypoint(ctx: agents.JobContext) -> None:
    logging.getLogger("jarvis.worker").info(
        "JARVIS dispatched to room %s", ctx.room.name
    )
    session = AgentSession(
        vad=build_vad(),
        stt=build_stt(),
        llm=build_llm(),
        tts=build_tts(),
        # High-latency links stall the default *remote* turn-detector /
        # adaptive-interruption services (agent-gateway.livekit.cloud), which
        # makes the agent go silent mid-conversation. Use the local Silero VAD
        # for turn detection + interruptions instead — fully offline decisions.
        turn_handling={
            "turn_detection": "vad",
            "endpointing": {"mode": "fixed", "min_delay": 0.6, "max_delay": 2.0},
            "interruption": {"enabled": True, "mode": "vad", "min_duration": 0.5},
            "preemptive_generation": {"enabled": False},
        },
    )
    await session.start(
        agent=JarvisAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(),
            audio_output=room_io.AudioOutputOptions(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)