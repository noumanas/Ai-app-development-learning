from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import parse, request, error


@dataclass
class ApiResponse:
    status_code: int
    headers: dict[str, str]
    body_text: str
    parsed_json: Any | None


def build_url(base_url: str, query_params: dict[str, str] | None = None) -> str:
    if not query_params:
        return base_url

    parsed = parse.urlsplit(base_url)
    current_params = parse.parse_qsl(parsed.query, keep_blank_values=True)
    current_params.extend(query_params.items())
    new_query = parse.urlencode(current_params)
    return parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment)
    )


def fetch_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
    timeout: float = 10.0,
) -> ApiResponse:
    request_body = None
    request_headers = {"User-Agent": "anatomy-of-an-api-call/0.1"}

    if headers:
        request_headers.update(headers)

    if body is not None:
        request_body = json.dumps(body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    req = request.Request(url, data=request_body, headers=request_headers, method=method)

    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            parsed_json = None
            try:
                parsed_json = json.loads(raw)
            except json.JSONDecodeError:
                pass

            return ApiResponse(
                status_code=response.status,
                headers=dict(response.headers.items()),
                body_text=raw,
                parsed_json=parsed_json,
            )
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        parsed_json = None
        try:
            parsed_json = json.loads(raw)
        except json.JSONDecodeError:
            pass

        return ApiResponse(
            status_code=exc.code,
            headers=dict(exc.headers.items()) if exc.headers else {},
            body_text=raw,
            parsed_json=parsed_json,
        )
    except error.URLError as exc:
        fallback = {
            "error": "network_unavailable",
            "message": str(exc),
            "url": url,
            "method": method,
        }
        raw = json.dumps(fallback, indent=2)
        return ApiResponse(
            status_code=0,
            headers={},
            body_text=raw,
            parsed_json=fallback,
        )
