"""Vercel serverless endpoint for the static support interface."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

# The function lives in /api but the agent module and its data/ live at the
# project root. Put the root on the import path so `agent` resolves both when
# run locally and inside Vercel's serverless bundle.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import SupportAgent

# Per-IP message cap. Backed by Upstash Redis (Vercel Marketplace), which injects
# UPSTASH_REDIS_REST_* env vars; the older KV_REST_API_* names are also accepted.
# Enforcement fails open: with no store configured or on any Redis error the
# request is allowed, so a storage outage never blocks support.
try:
    RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "30"))
    RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "86400"))
except ValueError:
    RATE_LIMIT_MAX, RATE_LIMIT_WINDOW = 30, 86400


def _redis_config() -> tuple[str | None, str | None]:
    url = os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN")
    return (url.rstrip("/"), token) if url and token else (None, None)


def _client_ip(headers) -> str:
    forwarded = headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return headers.get("x-real-ip", "").strip() or "unknown"


def _over_message_limit(headers) -> bool:
    """Atomically count this IP's messages in a rolling window; fail open on error."""
    url, token = _redis_config()
    if not url or not token:
        return False
    key = f"ratelimit:msg:{_client_ip(headers)}"
    pipeline = [["INCR", key], ["EXPIRE", key, str(RATE_LIMIT_WINDOW)]]
    request = urllib.request.Request(
        f"{url}/pipeline",
        data=json.dumps(pipeline).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            count = int(json.loads(response.read())[0]["result"])
    except (urllib.error.URLError, ValueError, KeyError, IndexError, TypeError):
        return False
    return count > RATE_LIMIT_MAX


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
            if _over_message_limit(self.headers):
                self._send(429, {
                    "error": (
                        f"You’ve reached the message limit for this session "
                        f"({RATE_LIMIT_MAX} messages). Please check back later — "
                        "thanks for trying the Sezzle support assistant!"
                    ),
                    "limit_reached": True,
                })
                return
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
