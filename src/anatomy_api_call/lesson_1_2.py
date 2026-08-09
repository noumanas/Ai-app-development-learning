"""Lesson 1.2: Anatomy of an API call.

Core idea:
- The request is a structured call with a message list.
- `instructions` or a `system` role message is a high-priority instruction channel, not magic.
- The API response is still just data you inspect and parse.
"""

from __future__ import annotations

LESSON_TITLE = "Lesson 1.2 - Anatomy of an API call"

LESSON_TEXT = """
The core object is a list of messages with roles:
- system
- user
- assistant

The system prompt sets behavior and role. It is not magic.
It is just high-priority instructions that help shape the model's output.

OpenAI Python pattern:

```python
from openai import OpenAI

client = OpenAI()  # API key from env

resp = client.responses.create(
    model="gpt-5",
    max_output_tokens=1024,
    instructions="You are a precise data-extraction service. Output only what is asked.",
    input=[
        {"role": "user", "content": "Extract the invoice total from: ...text..."}
    ],
)

text = resp.output_text
```

Key habit:
- Treat the system prompt as code.
- Version it.
- Do not hardcode a growing string inline across files.

Node equivalent:
- The official SDK uses the same overall shape.
- The request structure is role-based input plus an instruction layer.
""".strip()
