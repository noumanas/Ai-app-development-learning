# Week 4 - Fine-Tuning Judgment, Production Hardening, Deploy

Goal by Friday: a deployable, observable AI app with guardrails, streaming, and monitoring.

## Lessons

### 4.1 Fine-tuning: mostly learning when not to

- Prompt first
- RAG second
- Fine-tune only for behavior, not facts

### 4.2 Evals and observability

- Trace every call
- Keep regression tests

### 4.3 Cost, latency, throughput

- Streaming
- Prompt caching
- Model routing
- Token budgeting

### 4.4 Reliability

- Timeouts
- Retries
- Fallbacks

### 4.5 Security and data privacy

- Prompt injection defense
- PII handling
- Access control

### 4.6 Deployment

- Containerize
- Health checks
- Monitoring
- Cost alerts

## Project

Ship the app with:

- tracing
- streaming
- retries
- fallback model
- security review
- deployment plan

## Code map for this repo

This repo currently contains the core app skeleton and UI, but not the full observability/deploy stack.

