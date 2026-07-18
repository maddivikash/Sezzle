"""Vercel serverless endpoint for the static support interface."""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# The function lives in /api but the agent module and its data/ live at the
# project root. Put the root on the import path so `agent` resolves both when
# run locally and inside Vercel's serverless bundle.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import SupportAgent


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 10_000:
                raise ValueError("Message is too large.")
            payload = json.loads(self.rfile.read(length))
            question, user_id = payload.get("question"), payload.get("user_id")
            if not isinstance(question, str) or not question.strip() or not isinstance(user_id, str):
                raise ValueError("Please provide a question and account.")
            result = SupportAgent().answer(question.strip(), user_id)
            self._send(200, result)
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
        except RuntimeError as exc:
            self._send(503, {"error": str(exc)})
        except Exception:
            self._send(500, {"error": "Unable to process this request right now."})

    def _send(self, status: int, body: dict[str, str]) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)
