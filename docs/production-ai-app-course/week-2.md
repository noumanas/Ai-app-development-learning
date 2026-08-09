# Week 2 - RAG for Production

Goal by Friday: a production-style retrieval pipeline with citations and evals.

## Lessons

### 2.1 The RAG pipeline and where it breaks

- Ingest, chunk, embed, store, retrieve, rerank, generate

### 2.2 Chunking

- Structural chunking beats naive fixed windows
- Keep source metadata attached to every chunk

### 2.3 Embeddings

- Same embedding model at ingest and query time
- Re-embed if the model changes

### 2.4 Vector storage

- Start with Postgres and pgvector
- Add ANN indexing when scale requires it

### 2.5 Retrieval quality

- Hybrid search
- Reranking
- Citations

### 2.6 Retrieval evaluation

- Build a small truth set
- Measure Recall@k and answer faithfulness

## Project

Upgrade the Week 1 service into a RAG-backed service:

- structural chunking with metadata
- vector storage
- hybrid search + reranking
- citations in output
- a small eval harness

## Code map for this repo

This repo does not yet include the Week 2 RAG implementation.
Use this doc as the implementation target for the next code pass.

