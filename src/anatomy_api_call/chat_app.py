from __future__ import annotations

import json
import os
from urllib import error, request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .openai_client import make_client

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
PROJECT1_URL = os.getenv("PROJECT1_SERVICE_URL", "http://127.0.0.1:8001/v1/customer-message")


def build_messages(user_message: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise, helpful coding tutor. "
                "Keep responses short, practical, and easy to test."
            ),
        }
    ]
    for item in history[-12:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(user_message: str, history: list[dict[str, str]], api_key: str | None = None) -> str:
    client = make_client(api_key)
    response = client.responses.create(
        model=DEFAULT_MODEL,
        input=build_messages(user_message, history),
        max_output_tokens=500,
    )
    text = getattr(response, "output_text", "") or ""
    if text:
        return text.strip()
    if getattr(response, "output", None):
        chunks: list[str] = []
        for item in response.output:
            for part in getattr(item, "content", []) or []:
                value = getattr(getattr(part, "text", None), "value", None)
                if isinstance(value, str):
                    chunks.append(value)
        return "".join(chunks).strip()
    return "No response text was returned."


def forward_customer_message(message: str) -> dict[str, Any]:
    payload = json.dumps({"message": message}).encode("utf-8")
    req = request.Request(
        PROJECT1_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"detail": raw}
        raise RuntimeError(body.get("detail") or body.get("error") or f"HTTP {exc.code}")
    except error.URLError as exc:
        raise RuntimeError(f"Unable to reach project1 service at {PROJECT1_URL}: {exc}") from exc


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>API Chat Lab</title>
  <style>
    :root {
      --bg: #08111f;
      --panel: rgba(15, 23, 42, 0.86);
      --panel-2: rgba(30, 41, 59, 0.9);
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #38bdf8;
      --accent-2: #22c55e;
      --border: rgba(148, 163, 184, 0.18);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 30%),
        radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.14), transparent 26%),
        linear-gradient(180deg, #020617 0%, #0f172a 100%);
    }
    .wrap {
      max-width: 980px;
      margin: 0 auto;
      padding: 24px;
    }
    .hero {
      padding: 24px 0 18px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(2rem, 5vw, 3.5rem);
      letter-spacing: -0.04em;
    }
    .sub {
      color: var(--muted);
      max-width: 72ch;
      line-height: 1.6;
    }
    .grid {
      display: grid;
      grid-template-columns: 1.7fr 0.9fr;
      gap: 18px;
      align-items: start;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 18px;
      backdrop-filter: blur(14px);
      box-shadow: 0 24px 60px rgba(2, 6, 23, 0.35);
    }
    .chat {
      overflow: hidden;
    }
    .chat-log {
      height: 62vh;
      overflow: auto;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .msg {
      padding: 14px 16px;
      border-radius: 16px;
      line-height: 1.55;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--border);
    }
    .msg-wrap {
      display: flex;
      flex-direction: column;
      gap: 8px;
      max-width: 92%;
    }
    .user {
      background: rgba(56, 189, 248, 0.12);
      align-self: flex-end;
      border-top-right-radius: 4px;
    }
    .assistant {
      background: rgba(30, 41, 59, 0.92);
      align-self: flex-start;
      border-top-left-radius: 4px;
    }
    .details-toggle {
      align-self: flex-start;
      padding: 8px 12px;
      font-size: 0.82rem;
      min-width: 0;
      border-radius: 999px;
    }
    .details-panel {
      display: none;
      background: rgba(2, 6, 23, 0.7);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 14px;
      color: var(--muted);
      font-size: 0.9rem;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .details-panel.open {
      display: block;
    }
    .composer {
      display: flex;
      gap: 12px;
      padding: 16px;
      border-top: 1px solid var(--border);
      background: rgba(2, 6, 23, 0.35);
    }
    textarea {
      flex: 1;
      min-height: 56px;
      resize: vertical;
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: rgba(15, 23, 42, 0.95);
      color: var(--text);
      font: inherit;
      outline: none;
    }
    button {
      border: 0;
      border-radius: 14px;
      padding: 0 18px;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      color: #02111f;
      font-weight: 700;
      cursor: pointer;
      min-width: 104px;
    }
    button.secondary {
      background: transparent;
      color: var(--text);
      border: 1px solid var(--border);
      min-width: 88px;
    }
    .side {
      padding: 18px;
    }
    .side h2 {
      margin: 0 0 10px;
      font-size: 1rem;
    }
    .side p, .side li {
      color: var(--muted);
      line-height: 1.6;
    }
    .status {
      margin-top: 14px;
      font-size: 0.95rem;
      color: var(--muted);
    }
    .pill {
      display: inline-block;
      padding: 6px 10px;
      margin-right: 8px;
      border-radius: 999px;
      border: 1px solid var(--border);
      color: var(--text);
      background: rgba(15, 23, 42, 0.8);
      font-size: 0.85rem;
    }
    @media (max-width: 880px) {
      .grid { grid-template-columns: 1fr; }
      .chat-log { height: 56vh; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>API Chat Lab</h1>
      <p class="sub">A local test UI for exploring OpenAI chat requests. Type a prompt, inspect the conversation flow, and test the backend without leaving the browser.</p>
    </section>
    <div class="grid">
      <section class="card chat">
        <div id="chatLog" class="chat-log"></div>
        <div class="composer">
          <textarea id="prompt" placeholder="Ask something about API calls, structured output, or Python..."></textarea>
          <button id="sendBtn">Send</button>
          <button id="clearBtn" class="secondary">Clear</button>
        </div>
      </section>
      <aside class="card side">
        <h2>What this tests</h2>
        <p>This app sends your message to the Week 1 service endpoint, which runs tools and returns structured JSON.</p>
        <div>
          <span class="pill">Service endpoint</span>
          <span class="pill">Local UI</span>
          <span class="pill">Structured JSON</span>
        </div>
        <h2 style="margin-top:18px;">Tips</h2>
        <ul>
          <li>Start the Week 1 service on <code>http://127.0.0.1:8001</code>.</li>
          <li>Put <code>OPENAI_API_KEY</code> in <code>.env</code> or your environment.</li>
          <li>Change <code>OPENAI_MODEL</code> to test another model.</li>
        </ul>
        <div id="status" class="status">Ready.</div>
      </aside>
    </div>
  </div>
  <script>
    const chatLog = document.getElementById('chatLog');
    const prompt = document.getElementById('prompt');
    const sendBtn = document.getElementById('sendBtn');
    const clearBtn = document.getElementById('clearBtn');
    const statusEl = document.getElementById('status');
    let history = JSON.parse(localStorage.getItem('api-chat-history') || '[]');

    function saveHistory() {
      localStorage.setItem('api-chat-history', JSON.stringify(history));
    }

    function addMessage(role, content, details = '') {
      if (role === 'assistant') {
        const wrap = document.createElement('div');
        wrap.className = 'msg-wrap';

        const el = document.createElement('div');
        el.className = `msg ${role}`;
        el.textContent = content;
        wrap.appendChild(el);

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'details-toggle secondary';
        toggle.textContent = 'Show details';
        wrap.appendChild(toggle);

        const panel = document.createElement('div');
        panel.className = 'details-panel';
        if (details) {
          panel.textContent = details;
        }
        wrap.appendChild(panel);

        toggle.addEventListener('click', () => {
          const isOpen = panel.classList.toggle('open');
          toggle.textContent = isOpen ? 'Hide details' : 'Show details';
        });

        chatLog.appendChild(wrap);
        chatLog.scrollTop = chatLog.scrollHeight;
        return { el, panel, toggle };
      }

      const el = document.createElement('div');
      el.className = `msg ${role}`;
      el.textContent = content;
      chatLog.appendChild(el);
      chatLog.scrollTop = chatLog.scrollHeight;
      return { el };
    }

    function typeMessage(role, content, speed = 16) {
      const msg = addMessage(role, '');
      const el = msg.el;
      let index = 0;
      const tick = () => {
        index += 1;
        el.textContent = content.slice(0, index);
        chatLog.scrollTop = chatLog.scrollHeight;
        if (index < content.length) {
          window.setTimeout(tick, speed);
        }
      };
      tick();
      return el;
    }

    function render() {
      chatLog.innerHTML = '';
      if (!history.length) {
        addMessage('assistant', 'Start with a question. The app will call the service endpoint and show structured JSON here.');
        return;
      }
      history.forEach(item => addMessage(item.role, item.content, item.details || ''));
    }

    async function sendMessage() {
      const text = prompt.value.trim();
      if (!text) return;
      history.push({ role: 'user', content: text });
      saveHistory();
      addMessage('user', text);
      prompt.value = '';
      sendBtn.disabled = true;
      statusEl.textContent = 'Thinking...';
      try {
        const res = await fetch('/api/customer-message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history })
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || data.error || 'Request failed');
        }
        const answer = data.answer || data;
        const display = answer.summary || 'No summary returned.';
        const details = [
          `Summary: ${answer.summary || 'n/a'}`,
          `Customer: ${answer.customer_name || 'n/a'} (${answer.customer_tier || 'n/a'})`,
          `Math: ${answer.math_result || 'n/a'}`,
          `FX: ${answer.fx_pair || 'n/a'} @ ${answer.fx_rate || 'n/a'}`,
          `Action: ${answer.recommended_action || 'n/a'}`,
          `Lookup: ${answer.source_lookup || 'n/a'}`,
          '',
          'Tool log:',
          JSON.stringify(data.debug || [], null, 2),
          '',
          'Full JSON:',
          JSON.stringify(answer, null, 2),
        ].join('\n');
        history.push({ role: 'assistant', content: display, details });
        saveHistory();
        const msg = typeMessage('assistant', display);
        if (msg.panel) {
          msg.panel.textContent = details;
        }
        statusEl.textContent = 'Received structured response.';
      } catch (err) {
        const msg = `Error: ${err.message}`;
        addMessage('assistant', msg);
        statusEl.textContent = msg;
      } finally {
        sendBtn.disabled = false;
      }
    }

    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', () => {
      history = [];
      saveHistory();
      render();
      statusEl.textContent = 'Conversation cleared.';
    });
    prompt.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });

    render();
  </script>
</body>
</html>
"""


class ChatHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status: int, body_text: str) -> None:
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(HTTPStatus.OK, HTML)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_HEAD(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(HTTPStatus.OK, HTML)
            return
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/api/chat", "/api/customer-message"}:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return

        message = str(payload.get("message", "")).strip()
        history = payload.get("history", [])
        if not message:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "empty_message"})
            return

        if not isinstance(history, list):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_history"})
            return

        try:
            if path == "/api/customer-message":
                data = forward_customer_message(message)
                self._send_json(HTTPStatus.OK, data)
                return

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self._send_json(HTTPStatus.OK, {
                    "reply": "Set OPENAI_API_KEY in the shell before using the chat UI.",
                    "model": DEFAULT_MODEL,
                })
                return

            reply = generate_reply(message, history, api_key=api_key)
        except Exception as exc:  # pragma: no cover - surface API errors to UI
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": str(exc)})
            return

        self._send_json(HTTPStatus.OK, {"reply": reply, "model": DEFAULT_MODEL})

    def log_message(self, format: str, *args: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), ChatHandler)
    print(f"Chat app running at http://{host}:{port}")
    if os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY loaded.")
    else:
        print("Put OPENAI_API_KEY in .env or your environment before sending messages.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()
