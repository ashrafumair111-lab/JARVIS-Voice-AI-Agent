"""Local web server for the JARVIS voice frontend.

Serves the frontend page and issues LiveKit join tokens.

    python frontend_server.py [port]
Then open http://localhost:8000
"""

import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import get_token

FRONTEND = Path(__file__).resolve().parent / "frontend"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND), **kwargs)

    def do_GET(self):
        if self.path.startswith("/token"):
            room = "jarvis"
            for part in self.path.split("?"):
                if part.startswith("room="):
                    room = part[5:]
            token = get_token.make_token(room)
            body = json.dumps({"token": token, "room": room, "url": get_token.config.LIVEKIT_URL}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        sys.stdout.write("[frontend] %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"JARVIS frontend: http://localhost:{port}")
    print("Run the audio worker in another terminal:  python worker.py")
    server.serve_forever()


if __name__ == "__main__":
    main()