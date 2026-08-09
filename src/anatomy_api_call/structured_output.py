from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class InvoiceExtraction:
    invoice_total: str
    currency: str
    confidence: float


INVOICE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "invoice_total": {"type": "string"},
        "currency": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["invoice_total", "currency", "confidence"],
    "additionalProperties": False,
}


def make_client(api_key: str | None = None) -> Any:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set")

    from openai import OpenAI

    return OpenAI(api_key=key)


def extract_invoice_total(
    text: str,
    *,
    model: str = "gpt-5",
    api_key: str | None = None,
) -> InvoiceExtraction:
    client = make_client(api_key)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": (
                    "Extract the invoice total, currency, and confidence from the text.\n"
                    f"Text: {text}"
                ),
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "invoice_extraction",
                "schema": INVOICE_SCHEMA,
                "strict": True,
            }
        },
        max_output_tokens=300,
    )

    raw_text = getattr(response, "output_text", "") or ""
    if not raw_text and getattr(response, "output", None):
        chunks: list[str] = []
        for item in response.output:
            content = getattr(item, "content", None)
            if not content:
                continue
            for part in content:
                text_value = getattr(part, "text", None)
                if isinstance(text_value, str):
                    chunks.append(text_value)
                elif hasattr(text_value, "value"):
                    chunks.append(text_value.value)
        raw_text = "".join(chunks)

    if not raw_text:
        raise RuntimeError(f"OpenAI returned no structured text: {response!r}")

    payload = json.loads(raw_text)
    return InvoiceExtraction(
        invoice_total=payload["invoice_total"],
        currency=payload["currency"],
        confidence=float(payload["confidence"]),
    )
