# Week 1 - The LLM Application Layer

Goal by Friday: a service endpoint that takes messy input, uses tools, validates strict JSON, and retries on failure.

## Lessons

### 1.1 How LLMs work for builders

- Tokens, context windows, sampling, and model selection
- The important habit: every token costs money and latency

### 1.2 Anatomy of an API call

- Messages have roles: `system`, `user`, `assistant`
- The system prompt is high-priority instruction, not magic

### 1.3 Prompt engineering that survives production

- Explicit output contracts
- Few-shot examples
- Separation of system instructions and user task

### 1.4 Structured outputs you can trust

- Ask for schema-shaped output
- Validate and retry

### 1.5 Tool use / function calling

- Give the model tools
- Validate arguments in your code
- Log tool-use blocks

## Project

Build the service endpoint in [`src/anatomy_api_call/project1_service.py`](/Users/macbookpro2018/Desktop/python-learning-Practics/Ai-app-development-learning%20/src/anatomy_api_call/project1_service.py):

- `GET /health`
- `POST /v1/customer-message`

### Tools included

- `lookup_customer`
- `calculator`
- `get_exchange_rate`

### Exercise prompts

- Ask the model to add two numbers and convert USD to PKR
- Ask it to look up a customer and give a recommendation

