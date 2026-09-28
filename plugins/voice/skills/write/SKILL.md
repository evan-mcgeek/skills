---
name: write
description: Write anything on the user's behalf in their own voice, using their VOICE.md (Jira comments and replies, ticket descriptions, investigation results, release updates, Confluence pages, Slack messages, short emails). Invoked as /voice:write, and it is the default whenever an agent produces text that goes out under the user's name, even if they don't mention the skill. Use whenever the user asks to comment, reply, post, create a ticket, or draft a message as them.
---

# /voice:write

Produce text as the user, following their `VOICE.md`. This is the default whenever output goes out under their name. The goal: a colleague reading it can't tell the user didn't type it.

## 1. Load VOICE.md

Look in this order: the current project root (`VOICE.md`), `~/.claude/VOICE.md`, anything the user attached or pointed to. Read it in full every time, even if you read it earlier in the session. Voices drift fast when you rely on memory of the file.

If there's no VOICE.md, say so in one line and suggest `/voice:init`. Don't improvise a voice.

## 2. Work out what's needed

- **Message type:** investigation result, reply to a question, release update, test instructions, asking for info, delegating, ticket, email, etc. VOICE.md has a pattern for most of them; use it.
- **Audience:** developer, business/product/QA, or senior person. Pick the register VOICE.md defines for them.
- **Content:** the facts come from the task (the investigation, the ticket, the thread). Never invent facts, IDs, versions, or people to make a message feel complete. If something essential is missing (who it's for, the build number), ask one short question.
- **Scope:** if the request falls outside the scope listed in VOICE.md's hard rules (e.g. calling out a colleague), don't write it in the user's name. Say so briefly.

## 3. Write it

Follow VOICE.md exactly: hard rules first, then structure, openers and closers, signature phrasing, formatting, and the AI tells to avoid. In practice:

- Keep it as short as the user would. Most of their messages are shorter than your instinct.
- Signature phrases once or twice, in the spots VOICE.md says they belong. Never stack them.
- No greeting, sign-off, summary headers, or corporate vocabulary unless VOICE.md says the user does that.
- Grammar per the hard rule. If it says correct grammar, keep the rhythm and fix the slips.

Run VOICE.md's final checklist before handing it over.

## 4. Deliver

Give the text ready to paste, with nothing around it: no "Here's a draft", no explanation of choices. If there are a couple of genuinely different ways to go (e.g. short update vs. full investigation write-up), give the likely one and offer the other in a single line.

If a tool is available to post it (a Jira or Slack connector) and the user asked you to post, post it. Otherwise hand it over for them to paste.

When the user corrects a draft ("I'd never say that"), fix the draft, and if it's a pattern rather than a one-off, suggest the matching line to change in VOICE.md.
