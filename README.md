# evan-mcgeek skills

A [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Plugins

| Plugin | What it does |
|---|---|
| [voice](plugins/voice/) | Lets agents write and speak as you without sounding like AI. `/voice:init` builds your `VOICE.md` once from examples of your own pre-AI writing (Slack, email, Jira, docs, anything) plus a short spoken interview. `/voice:write` (the default) and `/voice:speak` then produce output in your voice, and `/voice:update` tunes it anytime. |
| [image-to-ansi](plugins/image-to-ansi/) | Converts an image into terminal ANSI or ASCII art for CLI splash screens, TUI banners, README art and `neofetch`-style logos. |
| [system-design](plugins/system-design/) | Grounds system design in how big tech solved the same problem. Ships 47 case studies (WhatsApp, Stripe, Uber, Figma and others) indexed by problem, with `/system-design:create` to design a new system, `/system-design:analyze` to review an existing one, `/system-design:question` for narrow questions and `/system-design:add-case-study` to grow the library. |

## Install

Add the marketplace once:

```bash
claude plugin marketplace add evan-mcgeek/skills
```

Then install the plugins you want:

```bash
claude plugin install voice@evan-mcgeek-skills
claude plugin install image-to-ansi@evan-mcgeek-skills
claude plugin install system-design@evan-mcgeek-skills
```

Restart Claude Code after installing.
See each plugin's README for usage.

## License

MIT
