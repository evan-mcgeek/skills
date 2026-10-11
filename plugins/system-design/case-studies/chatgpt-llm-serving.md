# How ChatGPT Works (LLM serving)

**Domain:** LLM inference serving · **Source:** newsletter.systemdesign.one/p/llm-concepts

## Overview
An LLM serving stack is token-by-token autocomplete at scale: tokenize → embed → run inference → sample next token → repeat. The system-design problems are context-window management, latency (time-to-first-token), and grounding output in facts the model wasn't trained on.

## Scale
Billions of parameters · context windows up to ~128K+ tokens · latency measured as time-to-first-token (TTFT) + per-token interval.

## Architecture
- **Token-by-token generation**: each forward pass predicts one token, enabling streaming partial output instead of waiting for the full response
- **Embedding layer**: maps tokens into a high-dimensional vector space capturing semantic relationships
- **Context window management**: tracks conversation history up to the model's token limit, prunes oldest turns when it overflows
- **Temperature-based sampling**: 0.0 = deterministic, higher = more stochastic output
- **RAG pipeline** (retrieve → augment → generate): a retrieval layer fetches grounding documents before generation, reducing hallucination
- **Safety filtering**: guardrails screen both input and output against policy rules
- **Stateless API**: conversation state travels with the request rather than being held server-side - simplifies fault tolerance and horizontal scaling

## Key decisions
- Pretraining/fine-tuning split: base model learns general patterns cheaply at scale; instruction-tuning (RLHF) aligns it to actual user intent afterward - far cheaper than training instruction-following from scratch.
- Stateless request design over server-held sessions: any server can handle any request, and failures don't lose conversation state.
- Chain-of-thought prompting for complex tasks: forcing explicit intermediate steps measurably improves accuracy over asking for the answer directly.

## Reusable patterns
- **Layered reliability**: combine raw model output with retrieval grounding and external tools (calculators, code execution) rather than trusting the model alone for anything factual or precise.
- **LLM-as-judge**: use a model with a fixed rubric to grade another model's output at scale - the general pattern for evaluating unstructured output cheaply.
