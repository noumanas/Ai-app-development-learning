#!/usr/bin/env bash
set -euo pipefail

: "${OPENAI_API_KEY:?Set OPENAI_API_KEY first}"

curl https://api.openai.com/v1/responses \
  --header "Authorization: Bearer ${OPENAI_API_KEY}" \
  --header "Content-Type: application/json" \
  --data '{"model":"gpt-5","input":[{"role":"user","content":"Hello, world"}],"instructions":"You are a helpful assistant."}'

