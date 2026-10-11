---
name: add-case-study
description: Use when adding a new system-design case study to the library (from a URL, article, or existing knowledge) so future create/analyze runs can draw on it.
---

# System Design: Add Case Study

Source to add: "$ARGUMENTS" (URL, or a system name/description to write up from existing knowledge)

## Steps

1. If given a URL, fetch it. If it's a link-shortener or interstitial page (e.g. lnkd.in), resolve the real destination first, then fetch that.
2. Extract, in this shape (match an existing file like `${CLAUDE_PLUGIN_ROOT}/case-studies/whatsapp.md` for the exact structure): Overview (2-3 sentences), Scale (concrete numbers only, skip the section if none exist), Architecture (bulleted components naming real technologies), Key decisions (each with the *why*, not just the *what*), Reusable patterns (1-2 techniques that generalize beyond this system).
3. Write `${CLAUDE_PLUGIN_ROOT}/case-studies/<system-name>.md`.
4. Open `${CLAUDE_PLUGIN_ROOT}/pattern-index.md` and either add a new row or extend an existing row's "See" column - key it by the *problem solved*, not the company name, and add the file to the **Case studies** list at the bottom.
5. Keep it concrete: name real technologies and real numbers, skip generic advice available anywhere else.
