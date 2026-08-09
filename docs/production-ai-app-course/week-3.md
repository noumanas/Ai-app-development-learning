# Week 3 - Agents, MCP, and Orchestration

Goal by Friday: a guarded agentic workflow that retrieves context, uses tools, and returns structured results.

## Lessons

### 3.1 What an agent actually is

- An LLM in a loop with tools and a goal

### 3.2 Build an agent loop from scratch

- Step cap
- Tool validation
- Fail-safe exit

### 3.3 Failure modes and guardrails

- Loop limits
- Argument validation
- Human approval on destructive actions

### 3.4 MCP

- Standard tool/data exposure layer
- Reusable across assistants and apps

### 3.5 Orchestration

- LangGraph for stateful control flow
- n8n for plumbing and integrations

## Project

Build an agent workflow that:

- retrieves context
- calls 2 to 3 tools
- validates outputs
- returns a cited structured result

## Code map for this repo

This repo does not yet include a dedicated MCP server or LangGraph workflow.
Use this week as the design and implementation target.

