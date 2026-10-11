---
name: create
description: Use when designing a new system or service from scratch and want to ground the design in how real large-scale systems solved the same subproblems, instead of inventing architecture from first principles.
---

# System Design: Create

Design target: "$ARGUMENTS"

## Steps

1. Read the pattern index: `${CLAUDE_PLUGIN_ROOT}/pattern-index.md`.
2. If the target's expected scale isn't known (QPS, data volume, consistency requirements, read:write ratio), ask before committing to a specific pattern - the right choice depends on those numbers, not on what sounds impressive.
3. Match the subproblems in the design target against the pattern-index rows. Read only the matched case study files.
4. Propose an architecture. For each major choice, cite which case study it's borrowed from and why the *rationale* fits this target's actual constraints, not just the pattern name.
5. Actively watch for over-borrowing: several case studies explicitly rejected heavier machinery at their own scale (e.g. Airbnb rejected sagas/2PC at 17 write TPS; Instagram optimized code before scaling hardware). If the target's scale doesn't justify what a case study used, say so and propose the lighter option instead.

## Output

An architecture proposal with each component traced to a cited case study, plus an explicit note on any place a lighter approach was chosen over the case study's own pattern (and why).
