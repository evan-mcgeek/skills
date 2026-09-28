# voice

Build a `VOICE.md` so agents can write or speak as you without sounding like AI.

- `/voice:write` analyzes your own pre-AI writing (Jira comments, tickets, Confluence, Slack, emails).
- `/voice:speak` runs a short spoken interview and captures your rhythm and phrasing.

Use either or both. Running `/voice:write` first, then `/voice:speak`, gives the strongest profile. Each run updates an existing VOICE.md instead of replacing it, and ends with the CLAUDE.md / AGENTS.md snippet to wire it in.

## Install (Claude Code)

Try it locally:

```bash
claude --plugin-dir ./voice
```

Or install from this marketplace:

```bash
claude plugin marketplace add evan-mcgeek/skills
claude plugin install voice@evan-mcgeek-skills
```

## Tips

- Only feed it text you typed yourself. Filter out anything an agent posted as you.
- Aim for 100+ comments and 20+ tickets or pages.
- For `/voice:speak`, voice mode works best. Talk unpolished, it's the rhythm that matters.
