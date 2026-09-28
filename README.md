# evan-mcgeek skills

A [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Plugins

| Plugin | What it does |
|---|---|
| [voice](plugins/voice/) | Builds a `VOICE.md` so agents can write or speak as you without sounding like AI. `/voice:write` learns from your pre-AI Jira, Confluence, Slack or email writing. `/voice:speak` learns from a short spoken interview. |
| [image-to-ansi](plugins/image-to-ansi/) | Converts an image into terminal ANSI or ASCII art for CLI splash screens, TUI banners, README art and `neofetch`-style logos. |

## Install

Add the marketplace once:

```bash
claude plugin marketplace add evan-mcgeek/skills
```

Then install the plugins you want:

```bash
claude plugin install voice@evan-mcgeek-skills
claude plugin install image-to-ansi@evan-mcgeek-skills
```

Restart Claude Code after installing.
See each plugin's README for usage.

## License

MIT
