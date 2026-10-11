---
name: add-case-study
description: Use when adding a new system-design case study to the library (from a URL, article, or existing knowledge) so future create/analyze runs can draw on it. Opens a pull request against the library's repo.
---

# System Design: Add Case Study

Source to add: "$ARGUMENTS" (URL, or a system name/description to write up from existing knowledge)

The library lives in the `evan-mcgeek/skills` GitHub repo under `plugins/system-design/`. The installed copy at `${CLAUDE_PLUGIN_ROOT}` is replaced on every plugin update, so a case study only persists once it is merged there.

## Steps

1. If given a URL, fetch it. If it's a link-shortener or interstitial page (e.g. lnkd.in), resolve the real destination first, then fetch that.
2. Read `${CLAUDE_PLUGIN_ROOT}/pattern-index.md`. If the system is already in the **Case studies** list, stop and say so instead of adding a duplicate.
3. Get a working copy in a temp directory: `gh repo clone evan-mcgeek/skills`, or `gh repo fork evan-mcgeek/skills --clone` without push access. Create a branch `case-study/<system-name>` from the default branch. If `gh` is missing or not logged in, say so and stop.
4. Extract, in this shape (match an existing file like `plugins/system-design/case-studies/whatsapp.md` for the exact structure): Overview (2-3 sentences), Scale (concrete numbers only, skip the section if none exist), Architecture (bulleted components naming real technologies), Key decisions (each with the *why*, not just the *what*), Reusable patterns (1-2 techniques that generalize beyond this system). Name the source at the top.
5. Write `plugins/system-design/case-studies/<system-name>.md` in the working copy.
6. Open `plugins/system-design/pattern-index.md` in the working copy and either add a new row or extend an existing row's "See" column - key it by the *problem solved*, not the company name. Add the file to the **Case studies** list at the bottom and bump the count there and in `plugins/system-design/README.md` and the root `README.md`.
7. Keep it concrete: name real technologies and real numbers, skip generic advice available anywhere else. Summarize in your own words, never paste the source's text.
8. Show the user the case study and the index change, and wait for their go-ahead before publishing anything.
9. Commit only those files as `system-design: add <system-name> case study`, push the branch, and open the pull request with `gh pr create`. The body is one or two lines: what the system is, which index row it landed in, and the source link.
10. Copy the new case study and the updated `pattern-index.md` into `${CLAUDE_PLUGIN_ROOT}` so it is usable right away. The next plugin update replaces them with the merged version.

## Output

The pull request URL, plus the index row the case study was filed under.
