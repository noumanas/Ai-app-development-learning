from __future__ import annotations

import os
import json

from .openai_client import generate_text
from .client import build_url, fetch_json


def print_section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def main() -> None:
    base_url = "https://jsonplaceholder.typicode.com/posts/1"
    query_params = {"demo": "true"}
    url = build_url(base_url, query_params)

    print_section("Request")
    print(f"Method: GET")
    print(f"URL: {url}")
    print("Headers: User-Agent: anatomy-of-an-api-call/0.1")
    print("Body: none")

    response = fetch_json(url)

    print_section("Response")
    print(f"Status code: {response.status_code}")
    print("Headers:")
    for key in sorted(response.headers):
        if key.lower() in {"content-type", "content-length", "server"}:
            print(f"  {key}: {response.headers[key]}")

    print_section("Payload")
    if response.parsed_json is not None:
        print(json.dumps(response.parsed_json, indent=2))
    else:
        print(response.body_text[:1000])

    print_section("OpenAI SDK")
    if os.getenv("OPENAI_API_KEY"):
        result = generate_text(
            "Explain the anatomy of an API call in one short paragraph.",
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
        )
        print(f"Model: {result.model}")
        print(result.text)
    else:
        print("Set OPENAI_API_KEY to run a live OpenAI request.")


if __name__ == "__main__":
    main()
