# voice

Lets agents write and speak as you without sounding like AI.

- `init`: one-time setup. Learns from examples of your own pre-AI writing (Slack, email, Jira, docs, whatever you use), runs a short spoken interview, and builds `VOICE.md`, plus the CLAUDE.md / AGENTS.md snippet to wire it in. Rerun it anytime to retune.
- `write`: produces text as you (messages, comments, tickets, emails, docs). This is the default whenever an agent writes under your name.
- `speak`: produces spoken-style output as you (voice mode, voice notes, talking points).

## Where each part runs

**init: the Claude chat app (desktop or web).** It's the only place with everything init needs: uploading your samples, voice mode for the interview, and file creation for VOICE.md. Claude Code has no voice mode, so the interview would be typed and come out flatter. Upload `init.skill` in the chat app and say "run voice init". If you have a connector for Slack, Jira, email or similar, init can pull samples through it, but pasting or uploading works just as well.

In the desktop app, use the **Chat** tab, not the Code tab. Voice mode only exists in Chat. Start it with the sound-wave icon in the chat input; the microphone next to it is dictation, which only turns speech into text. Voice mode is the same on desktop and web; the phone works too for the interview part if you prefer talking there.

**write: Claude Code.** That's where agents post as you. Install the plugin and it's available as `/voice:write`.

**speak: either.** In the chat apps it works with voice mode. In Claude Code it produces text meant to be said out loud.

## Install

Claude Code (plugin, gives `/voice:init`, `/voice:write`, `/voice:speak`):

```bash
claude plugin marketplace add evan-mcgeek/skills
claude plugin install voice@evan-mcgeek-skills
```

Claude chat app: download [`init.skill`](https://github.com/evan-mcgeek/skills/raw/main/plugins/voice/init.skill) (and [`speak.skill`](https://github.com/evan-mcgeek/skills/raw/main/plugins/voice/speak.skill) if you want spoken output there) and upload them as skills.

## After init

Put VOICE.md at `~/.claude/VOICE.md` and add the snippet init gives you to `~/.claude/CLAUDE.md` (and `AGENTS.md` for Codex or other harnesses).

## Tips for init

- Only feed it text you typed yourself. Filter out anything an agent posted as you.
- Aim for 100+ messages and 20+ longer pieces (tickets, docs, long emails).
- Do the interview in voice mode and talk unpolished. Actually speaking is what reveals your voice patterns: how you chain sentences, which connectors you use, where you put the reason. Typing tidies all of that away, so the spoken profile comes out much closer to you when you talk.
