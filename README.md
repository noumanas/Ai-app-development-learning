# Anatomy of an API Call

This project is a small Python learning lab for understanding what happens during an API call.

## What you will learn

- The parts of a request: method, URL, headers, query params, and body
- What a response contains: status code, headers, and payload
- How to make a real API request in Python using the standard library
- How to inspect and print each part clearly
- How to call OpenAI's Python SDK and GPT models from the same project
- Lesson 1.2: how to think about the API call shape as message roles plus system instructions

## Project layout

- `src/anatomy_api_call/` contains the teaching code
- `src/anatomy_api_call/demo.py` runs a sample request and prints the anatomy
- `src/anatomy_api_call/client.py` contains the reusable API helper
- `src/anatomy_api_call/lesson_1_2.py` contains the lesson text for the message-role pattern

## Run it

```bash
python -m src.anatomy_api_call.demo
```

## OpenAI examples

Raw HTTP:

```bash
bash scripts/run_openai_curl.sh
```

Python SDK:

```bash
python3 scripts/run_openai.py
```

Structured output:

```bash
python3 scripts/run_structured_output.py
```

Local chat UI:

```bash
python3 scripts/run_chat_app.py
```

Week 1 service skeleton:

```bash
python3 scripts/run_project1_service.py
```

## OpenAI setup

1. Install dependencies

```bash
pip install -e .
```

2. Set your API key

```bash
export OPENAI_API_KEY="your_key_here"
```

3. Optional: choose a model

```bash
export OPENAI_MODEL="gpt-5"
```

If `OPENAI_API_KEY` is not set, the demo skips the live OpenAI request and still shows the anatomy lesson.

The structured output example uses a JSON schema and expects a single JSON object back.

The chat UI runs locally at `http://127.0.0.1:8000` and sends messages to `/api/chat`.

The Project 1 service runs locally at `http://127.0.0.1:8001` with:

- `GET /health`
- `POST /v1/customer-message`

It exposes three stubbed tools behind the LLM:

- `lookup_customer`
- `calculator`
- `get_exchange_rate`

## Suggested learning path

1. Read `src/anatomy_api_call/demo.py`
2. Read `src/anatomy_api_call/client.py`
3. Run the demo
4. Change the URL, query params, or headers and observe the output
