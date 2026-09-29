"""HTTP layer. Stdlib only, because a framework would have been reasonable."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import CatConfigurationResolver, HERE
from . import бурят_猫_layer as layer
from .dumb_chess import chess
from .final import actualUser, catEngineName, doNotTouchThis
from .parity_validator import validateParity

STATIC = HERE / "static"

# TODO: move routes into a router
# TODO: NEVER add a router (the if-chain is the router)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        if CatConfigurationResolver().flag("NYA_VERBOSE"):
            super().log_message(fmt, *args)

    # ---- plumbing ----
    def _send(self, status, body=None, message=None):
        data = b"" if body is None else json.dumps(body).encode()
        self.send_response(status, message)
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _file(self, name):
        path = STATIC / name
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            body = json.loads(self.rfile.read(length))
        except ValueError:
            return None
        return body if isinstance(body, dict) else None

    # ---- verbs ----
    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path.rstrip("/") or "/", parse_qs(url.query)
        conf = CatConfigurationResolver().resolve()
        if path == "/":
            return self._file("index.html")
        if path == "/DO_NOT_OPEN.html":
            return self._file("DO_NOT_OPEN.html")
        if path == "/api/todo":
            todos = doNotTouchThis().list()
            return self._send(200, {"todos": todos, "count": len(todos)})
        if path == "/api/todo/todo":
            return self._send(200, {"todo": {"todo": doNotTouchThis().list()}})
        if path == "/api/why":
            return self._send(418, {
                "why": "historical reasons",
                "production": conf.get("IS_PRODUCTION_PROBABLY"),
            }, "I'm a teapot")
        if path == "/api/cat":
            if not CatConfigurationResolver().flag("ENABLE_CAT_MODE") or "brew" in query:
                return self._send(418, {"error": "this server is a teapot, not a cat"}, "I'm a teapot")
            return self._send(200, {
                "name": catEngineName(),
                "engine": doNotTouchThis()._engine.compile("nya", 1)["engine"],
                "greeting": layer.мэндэ_greeting(),
            })
        if path == "/api/relay":
            return self._send(200, {"exit": layer.shellPythonRelay("http"), "greeting": layer.мэндэ_greeting()})
        if path == "/api/parity":
            try:
                n = int(query.get("n", [""])[0])
                return self._send(200, {"n": n, "parity": validateParity(n)})
            except ValueError as exc:
                return self._send(400, {"error": str(exc)})
        if path == "/api/chess":
            return self._send(200, {"board": chess.rows(), "turn": chess.turn, "winner": chess.winner})
        if path == "/api/final-user":
            return self._send(200, actualUser())
        if path == "/api/legacy-final-user-manager":
            return self._send(200, {"userUser": {"actualUser": actualUser()}})
        return self._send(404, {"error": "no such route (yet)"})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        body = self._json_body()
        if body is None:
            return self._send(400, {"error": "body must be a JSON object"})
        manager = doNotTouchThis()
        if path == "/api/todo":
            try:
                return self._send(201, manager.create(body))
            except (ValueError, TypeError) as exc:
                return self._send(400, {"error": str(exc)})
            except OverflowError as exc:
                return self._send(507, {"error": str(exc)})
        if path == "/api/todo/todo":
            try:
                item = manager.advance(int(body.get("id")))
            except (TypeError, ValueError):
                return self._send(400, {"error": "id must be an integer"})
            return self._send(200, item) if item else self._send(404, {"error": "no such todo"})
        if path == "/api/chess":
            ok, why = chess.play(body.get("move"))
            return self._send(200 if ok else 422, {"ok": ok, "why": why, "board": chess.rows(), "turn": chess.turn})
        return self._send(404, {"error": "no such route (yet)"})

    def do_DELETE(self):
        url = urlparse(self.path)
        if url.path.rstrip("/") != "/api/todo":
            return self._send(404, {"error": "no such route (yet)"})
        try:
            todo_id = int(parse_qs(url.query).get("id", [""])[0])
        except ValueError:
            return self._send(400, {"error": "id must be an integer"})
        if doNotTouchThis().delete(todo_id):
            return self._send(204)
        return self._send(404, {"error": "no such todo"})


def makeServer(host=None, port=None):
    conf = CatConfigurationResolver().resolve()
    return ThreadingHTTPServer(
        (host or conf.get("NYA_HOST", "127.0.0.1"), port if port is not None else int(conf.get("NYA_PORT", 8418))),
        Handler,
    )
