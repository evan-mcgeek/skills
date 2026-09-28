---
name: write
description: Build or update a VOICE.md style profile from a person's own pre-AI writing (Jira comments, ticket descriptions, Confluence pages, Slack, emails), so agents can post as them without sounding like AI, and wire it into CLAUDE.md / AGENTS.md. Invoked as /voice:write. Use whenever someone wants agents to "write like me", "post as me in Jira", clone their writing style, build an impersonation or writing-style profile, or complains that agent-posted comments read like a robot. Pairs with /voice:speak for spoken style.
---

# /voice:write

Produce (or update) a `VOICE.md` from the user's real writing. Success means a colleague who reads their messages every day can't tell an agent wrote it.

Build from evidence, not from how the user thinks they write. People describe their own style badly; their real comments don't lie.

This is the backbone for anything posted as text. `/voice:speak` adds rhythm from speech on top; if the user wants both, run this first.

## 1. Collect pre-AI samples

Use only text the user typed themselves. If agents have already posted under their name, those comments sit in the same history, and learning from them clones a clone: the profile drifts toward generic AI style. Ask:

- Roughly when did you (or your tools) start writing with AI? Use samples from before that.
- Have any agents posted as you? If yes, exclude those, or ask the user to filter them.

Good sources, in order of value: Jira comments (replies, investigation results, status updates), Jira ticket descriptions, Confluence pages they authored, Slack messages, sent emails. Aim for 100+ comments and 20+ tickets or pages. Skip anything under ~10 words; "done" and "thanks" carry no signal.

How to get them:
- If an Atlassian / Jira / Confluence connector is available, use it: search by author within the pre-AI date range. Example JQL for tickets: `reporter = currentUser() AND created < "2025-10-01" ORDER BY created DESC`. For comments, fetch issues the user commented on in that range and keep only their comments.
- Otherwise ask for an exported file (markdown or text, one sample per block, with ticket key and date). A paste works for smaller sets.

Read every sample. Rare habits (a strikethrough self-correction, the one joke they make) are exactly what makes a profile convincing, so don't skim.

## 2. Analyze

Work through `references/writing-checklist.md`: structure, rhythm, signature phrases, formatting, audience switching, message types, tickets, non-native markers, AI contamination. Record concrete evidence, a short quote and roughly how often it appears.

Screen for AI-written samples that slipped through: section headers like "Summary / Action Points / Expected Outcome" or "Proposed Changes", em dashes from someone who never uses them, corporate vocabulary ("leverage", "seamless", "pinpoint"), a greeting and sign-off from someone who never greets. List the suspicious ones and ask whether the user wrote them. Leave them out of the signal until confirmed.

## 3. Finish

Follow `references/finishing.md`: have the user set the grammar, tone, scope, and audience rules, write or update VOICE.md from `references/voice-template.md`, wire it into CLAUDE.md / AGENTS.md, and test with a few drafts.

At the end, if `/voice:speak` hasn't been run, mention it once as an optional next step for capturing their spoken rhythm.
