"""Local touchscreen bridge. Master is queried with GET requests only."""
import json
import os
import subprocess
from threading import Lock
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text())
MASTER = CONFIG["master"].rstrip("/")
QUEUE = "https://api.oharafamilylightshow.com"
TOKEN_FILE = ROOT / ".device-token"
CAMERA_LOCK = Lock()
QUEUE_LOCK = Lock()


def fetch(base, path, payload=None, token=None):
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["X-Device-Token"] = token
    data = None if payload is None else json.dumps(payload).encode()
    try:
        response = urlopen(Request(base + path, data, headers), timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.status, json.load(response)


def read(base, path):
    code, value = fetch(base, path)
    if code != 200:
        raise ValueError("Upstream unavailable")
    return value


def show():
    status = read(MASTER, "/api/system/status")
    playlist = CONFIG["playlist"]
    entries = read(MASTER, "/api/playlist/" + quote(playlist, safe=""))["mainPlaylist"]
    installed = {entry.get("sequenceName") for entry in entries if entry.get("enabled", 1)}
    catalog = read(QUEUE, "/catalog")["catalog"]
    songs = [song for song in catalog if song.get("allowRequest") and song["seqId"] in installed]
    active = status.get("current_playlist", {}).get("playlist") == playlist
    titles = {song["seqId"]: song["title"] for song in songs}
    current = titles.get(status.get("current_sequence"), status.get("current_song", ""))
    return {"songs": songs, "open": active and status.get("status_name") == "playing",
            "current": current, "playlist": playlist}


def queue(payload):
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text().strip()
    else:
        code, device = fetch(QUEUE, "/device", {})
        if not 200 <= code < 300:
            return code, device
        token = device["deviceToken"]
        TOKEN_FILE.touch(mode=0o600)
        TOKEN_FILE.write_text(token)
    return fetch(QUEUE, "/requests", payload, token)


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, kind="application/json"):
        body = json.dumps(data).encode() if kind == "application/json" else data
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def camera(self):
        if not CAMERA_LOCK.acquire(blocking=False):
            self.reply(503, {})
            return
        try:
            device = next(iter(Path("/dev/v4l/by-id").glob("*j5create*-video-index0")), None)
            if device is None:
                self.reply(404, {})
                return
            with subprocess.Popen(
                ["/usr/bin/ffmpeg", "-loglevel", "error", "-f", "v4l2",
                 "-input_format", "mjpeg", "-video_size", "640x480",
                 "-framerate", "5", "-i", str(device), "-an", "-c:v", "mjpeg", "-threads", "1", "-q:v", "5",
                 "-f", "mpjpeg", "-boundary_tag", "frame", "pipe:1"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            ) as capture:
                try:
                    self.send_response(200)
                    self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    while chunk := capture.stdout.read1(16384):
                        self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    capture.terminate()
        finally:
            CAMERA_LOCK.release()

    def do_GET(self):
        try:
            if self.path == "/":
                self.reply(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            elif self.path.split("?", 1)[0] == "/camera":
                self.camera()
            elif self.path == "/pip/context":
                self.reply(200, self.pip_context())
            elif self.path == "/pip.js":
                self.reply(200, (ROOT / "pip.js").read_bytes(), "text/javascript; charset=utf-8")
            elif self.path == "/show":
                self.reply(200, show())
            else:
                self.reply(404, {})
        except (OSError, ValueError, KeyError):
            self.reply(503, {"message": "The show is out of reach. Trying again soon."})

    def pip_context(self):
        try:
            public = read("https://oharafamilylightshow.com", "/config.json")
            season, visit = public["season"], public["visit"]
            facts = {
                "season": season["name"], "hours": season["hours"],
                "hoursDetail": season.get("hoursDetail", ""),
                "location": f'{visit["addressLine1"]}, {visit["city"]}, {visit["state"]}',
                "visitorNotes": visit.get("notes", []),
            }
        except (OSError, ValueError, KeyError):
            facts = {"visitorNotes": ["Tune to 87.9 FM. Visit oharafamilylightshow.com for hours and directions."]}
        try:
            live = show()
        except (OSError, ValueError, KeyError):
            live = {"open": False, "current": "", "songs": []}
        return {"facts": facts, "live": live}

    def voice_session(self):
        key = os.environ.get("XAI_API_KEY")
        if not key:
            self.reply(503, {"message": "Pip’s voice isn’t set up yet."})
            return
        request = Request(
            "https://api.x.ai/v1/realtime/client_secrets",
            json.dumps({"expires_after": {"seconds": 60}}).encode(),
            {"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=8) as response:
                token = json.load(response)["value"]
        except (OSError, ValueError, KeyError):
            self.reply(502, {"message": "Pip couldn’t reach the voice service."})
            return
        self.reply(200, {"token": token})

    def do_POST(self):
        if self.path == "/pip/session" and self.headers.get("Origin") == "http://127.0.0.1:8795":
            self.voice_session()
            return
        if (self.path != "/request" or self.headers.get("Origin") != "http://127.0.0.1:8795"
                or self.headers.get_content_type() != "application/json"):
            self.reply(403, {})
            return
        try:
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size <= 2048:
                self.reply(400, {})
                return
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                self.reply(400, {})
                return
            if payload.get("action") == "status" and isinstance(payload.get("requestId"), str):
                with QUEUE_LOCK:
                    code, value = queue({"action": "status", "requestId": payload["requestId"]})
            else:
                live = show()
                if not live["open"]:
                    self.reply(409, {"message": "Come back when the show starts!"})
                    return
                seq_id = payload.get("seqId")
                if not any(song["seqId"] == seq_id for song in live["songs"]):
                    self.reply(400, {"message": "That song is unavailable."})
                    return
                with QUEUE_LOCK:
                    code, value = queue({"seqId": seq_id})
            self.reply(code, value)
        except (OSError, ValueError, KeyError):
            self.reply(503, {"message": "Could not confirm your request. Check again before retrying."})


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8795), Handler).serve_forever()
