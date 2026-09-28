---
name: init
description: One-time init that builds a person's VOICE.md style profile from their own pre-AI writing (whatever they write in: Slack, email, Jira, docs, anything else) plus a short spoken interview, then wires it into CLAUDE.md / AGENTS.md so /voice:write and /voice:speak can produce output as them. Invoked as /voice:init. Collects their writing samples, conducts the spoken interview, and writes VOICE.md. Use when someone wants agents to sound like them and has no VOICE.md yet, wants to rebuild or retune it, or asks to set up or init their voice profile.
---

# /voice:init

Build `VOICE.md` once. After this, `/voice:write` and `/voice:speak` read it to produce output in the user's voice. Success means a colleague who works with the user every day can't tell an agent wrote it.

Build from evidence, not from how the user thinks they write or talk. People describe their own style badly; their real messages and unscripted speech don't lie.

If a VOICE.md already exists, ask whether to rebuild it or retune specific parts. When retuning, keep the hard rules and everything the user didn't ask to change.

## Where to run this

Run init in the Claude chat app, desktop or web. In the desktop app that means the Chat tab, not the Code tab: voice mode lives in Chat only. That's the one place where everything init needs works together: uploading samples, voice mode for the interview, and file creation for VOICE.md. Voice mode is the same on desktop and web. The phone is great for talking but awkward for handling hundreds of samples, so it's only worth using for the interview if the user prefers it.

Claude Code has no voice mode, only dictation. If init is started there, collect the samples and do the written voice, write VOICE.md, and tell the user plainly that the interview works much better in the chat app: they can upload this skill there and rerun it to add the spoken section. Offer dictation as a fallback if they'd rather stay.

## Steps

1. Collect pre-AI writing samples
2. Analyze them
3. Spoken interview (recommended, skippable)
4. Have the user set the rules
5. Write VOICE.md
6. Wire it into CLAUDE.md / AGENTS.md
7. Test with a couple of outputs and tune

## 1. Collect pre-AI writing samples

Use only text the user typed themselves. If agents have already written under their name, that text sits in the same history, and learning from it clones a clone: the profile drifts toward generic AI style. Before collecting anything, ask three things in one go:

- **Cutoff date:** roughly when did you start writing with AI? Everything must be from before that.
- **Agent posts:** have any agents posted as you? If yes, that text must be excluded (by date, or by a marker the user recognizes).
- **Sources:** where do you write the most? Slack, email, Jira, docs, anything else.

Then collect samples following `references/collecting-samples.md`. By default the user pastes or uploads them; if a tool for one of their sources is already connected, offer to pull them through it. Save everything to a `voice-samples.md` file. Aim for 100+ messages and 20+ longer pieces (tickets, docs, long emails).

Keep `voice-samples.md` next to VOICE.md. A later retune can reuse it instead of refetching.

Read every sample. Rare habits (a strikethrough self-correction, the one joke they make) are exactly what makes a profile convincing, so don't skim.

## 2. Analyze the writing

Work through `references/writing-checklist.md`. Record concrete evidence: a short quote and roughly how often it appears.

Screen for AI-written samples that slipped through: section headers like "Summary / Action Points / Expected Outcome" or "Proposed Changes", em dashes from someone who never uses them, corporate vocabulary ("leverage", "seamless", "pinpoint"), a greeting and sign-off from someone who never greets. List the suspicious ones and ask whether the user wrote them. Leave them out until confirmed.

## 3. Spoken interview

Writing shows structure; speech shows rhythm, connectors, and how the person layers an explanation. This feeds the spoken section that `/voice:speak` uses. If they skip it, `/voice:speak` falls back to the written voice.

Ask the user to switch on voice mode for this part (the sound-wave icon in the chat input; the microphone next to it is only dictation). Explain why in one or two sentences: actually speaking reveals their natural patterns, like how they chain clauses, which connectors they reach for, and where they put the reason, while typed answers come out tidier than real speech and hide exactly those patterns. If voice mode isn't available where init is running, see "Where to run this" above.

Ask them to talk, unpolished, for a minute or two each about:
1. Something from work they know well.
2. A personal project or hobby.
3. Optionally, something technical explained to a non-technical person (shows code-switching).

**Don't interrupt.** People talk in pauses, and in voice mode a pause often gets sent as a message. If a turn looks unfinished, say no more than a short "go on" and wait until they clearly signal they're done. Don't steer the content or give advice on their project; the topic is just a vehicle.

Analyze with `references/speaking-checklist.md`. Ignore transcription artifacts (misheard words, broken spellings of names); when unsure whether something is a quirk or a transcription error, ask.

## 4. Have the user set the rules

The material shows the person on their best and worst days. The profile should capture the voice, not every habit. Ask directly (tappable options work well) and record the answers as hard rules:

- **Grammar.** Keep exact quirks, or grammatically correct while keeping their rhythm? Most people, especially non-native speakers, want correct grammar with their phrasing intact.
- **Tone.** If the samples show blunt pushback, sarcasm, or irritation, should agents ever reproduce it? Usually not: people keep that tone for situations they'd never delegate. Default to polite, and don't point out anyone's mistakes unless the user explicitly wants that.
- **Scope.** What will agents actually write? (Investigation results, replies, tickets, release updates, short emails.) Nothing outside that list under the user's name.
- **Audiences.** Who gets a different register? Usually technical peers, business/product/QA, and senior people, who get a more careful version of the same voice.

## 5. Write VOICE.md

Follow `references/voice-template.md`:

- Written as **instructions to the agent**, not a description of the user.
- **Hard rules at the top.**
- Every signature phrase comes with **where** it naturally occurs, and a reminder to use it once or twice per message. Misplaced tics read like parody. Spoken fillers ("you know", "I mean") go in the spoken section only, unless the writing samples show them too.
- **Worked example messages** for each common message type.
- **Placeholder names** (`@Name`) in examples, never real colleagues.
- Keep the **AI tells to avoid** section.
- Under ~250 lines. It gets read in full before every output.

## 6. Wire it in

Recommend global placement, since posting as a person isn't tied to one repo.

**Claude Code (global):** file at `~/.claude/VOICE.md`, and in `~/.claude/CLAUDE.md`:

```markdown
## Writing on my behalf
Before producing anything on my behalf (messages, comments, tickets, docs, email replies, anything sent under my name), read and follow @~/.claude/VOICE.md. Use /voice:write by default. Use /voice:speak only when I ask for spoken output. The hard rules in VOICE.md override any other style guidance.
```

**Claude Code (one project):** `VOICE.md` next to the project's `CLAUDE.md`, referenced as `@VOICE.md`.

**Codex and other AGENTS.md harnesses:** add the same section to `AGENTS.md`, with the path written out plainly, since not every harness resolves `@` imports. Paste the hard rules in directly as a fallback.

In the chat app, you can't reach the user's machine: give VOICE.md as a download and hand over the snippet. In Claude Code, make the edit yourself after confirming the location.

## 7. Test and tune

Produce two or three outputs the way the user will actually use the plugin: a `/voice:write` message or two in the channels they actually use, and a short `/voice:speak` piece if the interview was done. Ask the user to judge them. Fix the profile, not just the output, so the lesson sticks.

Mention that the real test is live use, and that rerunning `/voice:init` later can retune specific sections.
