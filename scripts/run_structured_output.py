from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from anatomy_api_call.structured_output import extract_invoice_total


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Set OPENAI_API_KEY first")

    result = extract_invoice_total(
        "Invoice #1842 total due: USD 149.50. Please pay by Friday.",
        model=os.getenv("OPENAI_MODEL", "gpt-5"),
        api_key=api_key,
    )
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()

