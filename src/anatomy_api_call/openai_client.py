from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class OpenAIResult:
    model: str
    text: str


def make_client(api_key: str | None = None) -> Any:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    return OpenAI(api_key=key)


def generate_text(
    prompt: str,
    *,
    model: str = "gpt-5",
    max_output_tokens: int = 300,
    api_key: str | None = None,
    system: str = "You are a precise data-extraction service. Output only what is asked.",
) -> OpenAIResult:
    client = make_client(api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "user", "content": prompt},
        ],
        instructions=system,
        max_output_tokens=max_output_tokens,
    )
    return OpenAIResult(model=model, text=response.output_text)
