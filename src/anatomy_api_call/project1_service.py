from __future__ import annotations

import json
import os
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .openai_client import make_client

app = FastAPI(title="Project 1", version="0.1.0")


class CustomerRequest(BaseModel):
    message: str = Field(min_length=1)


class StructuredAnswer(BaseModel):
    summary: str
    customer_name: str
    customer_tier: Literal["bronze", "silver", "gold", "unknown"]
    recommended_action: str
    math_result: str
    source_lookup: str
    fx_rate: str
    fx_pair: str


STUB_DB: dict[str, dict[str, str]] = {
    "alice": {"customer_name": "Alice", "customer_tier": "gold", "source_lookup": "stub:customers/alice"},
    "bob": {"customer_name": "Bob", "customer_tier": "silver", "source_lookup": "stub:customers/bob"},
}


def lookup_customer(customer_key: str) -> dict[str, str]:
    key = customer_key.strip().lower()
    return STUB_DB.get(
        key,
        {"customer_name": "Unknown", "customer_tier": "unknown", "source_lookup": f"stub:customers/{key or 'unknown'}"},
    )


def calculate(expression: str) -> str:
    allowed = set("0123456789+-*/(). %")
    if not expression or any(ch not in allowed for ch in expression):
        raise ValueError("Unsupported calculator expression")
    return str(eval(expression, {"__builtins__": {}}, {}))


def get_exchange_rate(from_currency: str, to_currency: str) -> dict[str, str]:
    rates: dict[tuple[str, str], str] = {
        ("USD", "PKR"): "278.50",
        ("USD", "EUR"): "0.92",
        ("EUR", "USD"): "1.09",
        ("GBP", "USD"): "1.27",
    }
    src = from_currency.strip().upper()
    dst = to_currency.strip().upper()
    rate = rates.get((src, dst))
    if rate is None:
        rate = "1.00" if src == dst else "0.00"
    return {
        "from_currency": src,
        "to_currency": dst,
        "rate": rate,
        "source_lookup": f"stub:fx/{src}-{dst}",
    }


def build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "name": "lookup_customer",
            "description": "Look up a customer in a stubbed data source.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_key": {"type": "string"},
                },
                "required": ["customer_key"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "calculator",
            "description": "Evaluate a simple arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
            "strict": True,
        },
        {
            "type": "function",
            "name": "get_exchange_rate",
            "description": "Get the current fx rate between two ISO currency codes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"},
                },
                "required": ["from_currency", "to_currency"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    ]


FINAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "customer_name": {"type": "string"},
        "customer_tier": {"type": "string", "enum": ["bronze", "silver", "gold", "unknown"]},
        "recommended_action": {"type": "string"},
        "math_result": {"type": "string"},
        "source_lookup": {"type": "string"},
        "fx_rate": {"type": "string"},
        "fx_pair": {"type": "string"},
    },
    "required": [
        "summary",
        "customer_name",
        "customer_tier",
        "recommended_action",
        "math_result",
        "source_lookup",
        "fx_rate",
        "fx_pair",
    ],
    "additionalProperties": False,
}


def _extract_output_text(response: Any) -> str:
    text = getattr(response, "output_text", "") or ""
    if isinstance(text, str) and text.strip():
        return text.strip()

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for part in getattr(item, "content", []) or []:
            part_type = getattr(part, "type", "")
            if part_type not in {"output_text", "text"}:
                continue

            value = getattr(part, "text", None)
            if isinstance(value, str):
                chunks.append(value)
                continue

            if hasattr(value, "value") and isinstance(value.value, str):
                chunks.append(value.value)
                continue

            if hasattr(part, "value") and isinstance(part.value, str):
                chunks.append(part.value)

    return "".join(chunks).strip()


def _validate_answer(payload: dict[str, Any]) -> StructuredAnswer:
    return StructuredAnswer.model_validate(payload)


def run_agent(message: str, *, api_key: str | None = None, max_rounds: int = 6, debug_log: list[dict[str, Any]] | None = None) -> StructuredAnswer:
    client = make_client(api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-5")
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a service orchestrator. "
                    "Use the lookup_customer, calculator, and get_exchange_rate tools when needed. "
                    "You must return only valid JSON that matches the provided schema."
                ),
            },
            {"role": "user", "content": message},
        ],
        tools=build_tools(),
        tool_choice="required",
        reasoning={"effort": "low"},
        max_output_tokens=800,
    )

    tool_results: list[dict[str, Any]] = []
    for _ in range(max_rounds):
        tool_calls = [item for item in getattr(response, "output", []) or [] if getattr(item, "type", "") == "function_call"]
        if debug_log is not None:
            for call in tool_calls:
                debug_log.append(
                    {
                        "type": "tool_use",
                        "name": getattr(call, "name", ""),
                        "call_id": getattr(call, "call_id", ""),
                        "arguments": getattr(call, "arguments", ""),
                    }
                )
        if not tool_calls:
            break

        outputs = []
        for call in tool_calls:
            args = json.loads(getattr(call, "arguments", "{}"))
            if call.name == "lookup_customer":
                tool_result = lookup_customer(args["customer_key"])
            elif call.name == "calculator":
                tool_result = {"result": calculate(args["expression"])}
            elif call.name == "get_exchange_rate":
                tool_result = get_exchange_rate(args["from_currency"], args["to_currency"])
            else:
                raise RuntimeError(f"Unknown tool: {call.name}")

            tool_results.append({"name": call.name, "arguments": args, "result": tool_result})
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(tool_result),
                }
            )

        response = client.responses.create(
            model=model,
            previous_response_id=response.id,
            input=outputs,
            reasoning={"effort": "low"},
            max_output_tokens=800,
        )

    final_prompt = (
        "Return one JSON object that matches the schema exactly.\n"
        f"Original message: {message}\n"
        f"Tool results: {json.dumps(tool_results, indent=2)}"
    )

    retries = 2
    last_error: Exception | None = None
    last_response_repr = ""
    for attempt in range(retries + 1):
        final_response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict JSON serializer. "
                        "Return only valid JSON that matches the schema."
                    ),
                },
                {"role": "user", "content": final_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "final_answer",
                    "schema": FINAL_SCHEMA,
                    "strict": True,
                }
            },
            reasoning={"effort": "low"},
            max_output_tokens=1200,
        )

        last_response_repr = repr(final_response)
        raw = _extract_output_text(final_response)
        if not raw:
            if getattr(final_response, "incomplete_details", None) and getattr(final_response.incomplete_details, "reason", None) == "max_output_tokens":
                last_error = RuntimeError(f"Final response ran out of output tokens. Response: {last_response_repr}")
                final_prompt = (
                    f"{final_prompt}\n\nThe previous attempt ran out of tokens. "
                    "Return a shorter JSON object and keep the fields concise."
                )
                continue
            last_error = RuntimeError(f"Model returned no final structured output. Response: {last_response_repr}")
            final_prompt = f"{final_prompt}\n\nError: no output returned. Try again."
            continue

        try:
            payload = json.loads(raw)
            return _validate_answer(payload)
        except (json.JSONDecodeError, Exception) as exc:
            last_error = exc
            final_prompt = (
                f"{final_prompt}\n\nThe previous output was invalid.\n"
                f"Fix it and return only valid JSON.\nPrevious output: {raw}"
            )

    raise RuntimeError(f"Final structured answer failed after retries: {last_error}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/customer-message")
def customer_message(payload: CustomerRequest) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    logs: list[dict[str, Any]] = []
    try:
        answer = run_agent(payload.message, api_key=api_key, debug_log=logs)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"answer": answer.model_dump(), "debug": logs}
