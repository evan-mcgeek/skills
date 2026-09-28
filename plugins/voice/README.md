# voice

Lets agents write and speak as you, so nobody can tell it wasn't you who typed it.

It's a set of 4 skills:

1. `/voice:init`: one-time setup. Learns from examples of your own pre-AI writing (Slack, email, Jira, docs, whatever you use), runs a short spoken interview and builds your `VOICE.md`.
2. `/voice:write`: writes as you (messages, comments, tickets, emails, docs). It's the default whenever an agent writes under your name.
3. `/voice:speak`: speaks as you (voice mode, voice notes, talking points).
4. `/voice:update`: tunes your `VOICE.md` anytime. Tell it what sounds off, paste an agent draft next to your own rewrite, add more samples or redo the interview.

## Install

Claude Code:

```bash
claude plugin marketplace add evan-mcgeek/skills
claude plugin install voice@evan-mcgeek-skills
```

Claude chat app: download [`init.skill`](https://github.com/evan-mcgeek/skills/raw/main/plugins/voice/init.skill) and [`update.skill`](https://github.com/evan-mcgeek/skills/raw/main/plugins/voice/update.skill) and upload them as skills.
As well, add [`speak.skill`](https://github.com/evan-mcgeek/skills/raw/main/plugins/voice/speak.skill) if you want spoken output there.

## Where to run what

**init** works best in the Claude chat app (desktop or web), since it's the only place with voice mode for the interview.
Claude Code has dictation only, so the interview would be typed and your spoken profile comes out flatter.

1. open the **Chat** tab, not the Code tab
2. upload `init.skill` and say "run voice init"
3. share your writing samples: paste them, upload an export, or pull them through a connector if you have one (Slack, Jira, email etc.)
4. for the interview, start voice mode with the sound-wave icon in the chat input. The microphone next to it is just dictation, so it won't work the same way.

The phone works for the interview part too, if you prefer talking there.

**write** runs in Claude Code, since that's where agents post as you.

**speak** runs in both: with voice mode in the chat app, or as text meant to be said out loud in Claude Code.

**update** runs in both as well. To redo the interview, use the chat app.

## After init

Put `VOICE.md` at `~/.claude/VOICE.md` and add the snippet init gives you to `~/.claude/CLAUDE.md` (or `AGENTS.md` for Codex and other harnesses).

## Tips

1. only feed it text you typed yourself, so filter out anything an agent posted as you
2. aim for **100+ messages** and **20+ longer pieces** (tickets, docs, long emails)
3. do the interview in voice mode and talk unpolished. Speaking is what shows how you actually chain sentences, which connectors you use and where you put the reason. Typing tidies all of that away.
