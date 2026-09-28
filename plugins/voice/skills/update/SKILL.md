---
name: update
description: Tune an existing VOICE.md without rebuilding it. Invoked as /voice:update. Works from the user's comments on how agent output sounds ("too polished", "I'd never say that"), their corrections to drafts, new writing samples, or a fresh spoken interview, and changes only the parts of VOICE.md that need it. Use when the user wants to adjust, tune, fix or refresh their voice profile, says agent output doesn't sound like them, wants to add a new channel, or wants to redo the interview. To build a VOICE.md from scratch, use /voice:init.
---

# /voice:update

Fix what's off in `VOICE.md` and keep everything else.
The profile was built from evidence, so every change needs evidence too: the user's own words, their corrections, new samples, or new speech.

## 1. Load VOICE.md

Look in the project root, then `~/.claude/VOICE.md`, then anything the user attached or pointed to.
Read it in full.
If there's no VOICE.md, suggest `/voice:init` and stop.

If `voice-samples.md` sits next to it, load that too.
It's the evidence base for checking any change.

## 2. Pick how to tune

Infer it from what the user said, or ask.
Several can be combined in one run.

- **Comments.** The user says what's off in plain words: "too formal", "I never start with 'as well'", "no emoji with my boss". Turn each into a concrete change to a specific line.
- **Corrections.** The user pastes an agent draft next to their own rewrite, or points to messages agents already posted as them. Compare the two: every edit they made is a signal. Only patterns go into VOICE.md; one-off content fixes don't.
- **New samples.** More of their own writing, e.g. a channel init didn't cover. Collect and filter per `references/collecting-samples.md`, analyze with `references/writing-checklist.md`, and append them to `voice-samples.md`.
- **New interview.** Redo or add the spoken section. Run it exactly as `/voice:init` does: voice mode in the Claude chat app (the sound-wave icon, not the dictation microphone), a minute or two per topic, no interrupting, no steering. Analyze with `references/speaking-checklist.md` and merge into the spoken section per `references/voice-template.md`. In Claude Code, say plainly that the interview works much better in the chat app, and offer dictation as a fallback.

## 3. Propose the changes

Before editing, show a short list: section, current line, new line.
Only include what the evidence supports.

- Hard rules change only when the user explicitly asks. Never relax one by inference.
- When a comment contradicts the samples ("I never say 'so basically'", but it's in 30 samples), show two or three of those samples and ask. People misjudge their own style, and it's still their call.
- Prefer editing an existing line over adding a new one. Keep the file under ~250 lines.
- Placeholder names in examples, never real colleagues.

## 4. Apply and test

Once the user confirms, edit VOICE.md in place.
In the chat app, where you can't reach their machine, hand over the updated file as a download.

Then produce one or two outputs that exercise what changed, ideally the same kind of message that prompted the comment, and ask whether it's closer.
Keep going until it is.
