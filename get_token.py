"""Generate a LiveKit join token for the JARVIS web frontend.

Usage:
    python get_token.py [room]
"""

import sys

import config


def make_token(room: str = "jarvis") -> str:
    from livekit.api import AccessToken, VideoGrants

    if not (config.LIVEKIT_API_KEY and config.LIVEKIT_API_SECRET):
        raise SystemExit("[TOKEN] LIVEKIT_API_KEY / LIVEKIT_API_SECRET missing.")

    token = (
        AccessToken(config.LIVEKIT_API_KEY, config.LIVEKIT_API_SECRET)
        .with_identity("jarvis-user")
        .with_name("User")
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
    )
    return token.to_jwt()


if __name__ == "__main__":
    room = sys.argv[1] if len(sys.argv) > 1 else "jarvis"
    print(make_token(room))