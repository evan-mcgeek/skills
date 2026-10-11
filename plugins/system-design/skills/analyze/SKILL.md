---
name: analyze
description: Use when reviewing an existing system or codebase against how big tech solved the same problem, to find missing best-practice idioms or unjustified over-engineering.
---

# System Design: Analyze

Target to analyze: "$ARGUMENTS"

## Steps

1. Read the pattern index: `${CLAUDE_PLUGIN_ROOT}/pattern-index.md`.
2. Identify which problem domains the target actually touches (real-time delivery, pagination, payments, geospatial, feed generation, etc.) - read the relevant code/docs first if $ARGUMENTS is a path, don't assume from the name alone.
3. For each matched pattern-index row, read the case study and diff the target's current approach against its Architecture and Key decisions sections.
4. Only report two kinds of findings:
   - **Missing load-bearing idiom**: the case study treats something as necessary for correctness/scale (idempotency keys, cursor pagination, heartbeat/timeout, etc.) and the target doesn't have it.
   - **Unjustified heavier machinery**: the target uses something (distributed transactions, saga pattern, microservices split, global cluster) that the matched case study's own numbers wouldn't justify at the target's actual scale.
5. Every finding must cite the specific case study and its numbers - no generic architecture advice untethered to a cited comparison.

## Output

Findings ranked most-severe first: file/component, what's missing or excessive, which case study it's compared against, and the concrete failure scenario or cost. If nothing in a matched row is actually a problem, say so briefly instead of padding the report.
