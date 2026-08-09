from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from anatomy_api_call.openai_client import generate_text


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY first")

    result = generate_text(
        "Hello, world",
        model=os.getenv("OPENAI_MODEL", "gpt-5"),
        max_output_tokens=1024,
        api_key=api_key,
    )
    print(result.text)


if __name__ == "__main__":
    main()

