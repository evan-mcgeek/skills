---
name: question
description: Use for a narrow, specific system-design question (e.g. "how does X handle Y", "what does the Z case study say about..."), rather than a full design or audit - answers it from the case-study library first, falling back to a quick targeted lookup only if the library doesn't cover it.
---

# System Design: Question

Question: "$ARGUMENTS"

## Steps

1. Read the pattern index: `${CLAUDE_PLUGIN_ROOT}/pattern-index.md` and scan for rows matching the question's topic.
2. If a matched case study exists, read it and answer directly from its Architecture / Key decisions / Reusable patterns - cite the case study.
3. If nothing in the library covers it, do a narrow, targeted search (WebSearch/WebFetch) for just enough to answer this one question. Don't write a new case-study file for it - that's `add-case-study`'s job, not this one.
4. If the answer turned up something that would make a good permanent case study (concrete numbers, real architecture, a generalizable pattern) and the library doesn't have it yet, mention that as an optional follow-up - don't add it unprompted.

## Output

A direct answer: a few sentences to a short paragraph, citing the case study or source it came from. No architecture proposal, no audit findings, no new files - just the answer to the question asked.
