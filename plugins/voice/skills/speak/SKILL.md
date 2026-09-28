---
name: speak
description: Build or update a VOICE.md profile of how a person talks, from a short spoken interview (voice mode or typed-as-spoken), so agents can speak or draft in their natural rhythm without sounding like AI, and wire it into CLAUDE.md / AGENTS.md. Invoked as /voice:speak. Use whenever someone wants an agent to "talk like me", "sound like me", capture their speaking style or catchphrases, or add spoken rhythm to an existing VOICE.md. Pairs with /voice:write for written style.
---

# /voice:speak

Capture how the user talks and put it in `VOICE.md`. Writing shows structure; speech shows rhythm, connectors, and how the person layers an explanation.

If `/voice:write` already produced a VOICE.md, this adds a spoken layer to it. On its own, it produces a speech-first profile; say plainly that this is weaker for Jira and email, and that `/voice:write` would strengthen it.

## 1. Run the interview

Voice mode is ideal; typing works if the user writes the way they'd talk. Ask them to talk, unpolished, for a minute or two each about:

1. Something from work they know well (a system, a bug they chased, a decision they made).
2. A personal project or hobby.

Optionally a third: explain something technical as if to a non-technical person. That shows how they code-switch.

**Don't interrupt.** People talk in pauses, and in voice mode a pause often gets sent as a message. If a turn looks unfinished, say no more than a short "go on" and wait until they clearly signal they're done. Jumping in breaks their rhythm, and the rhythm is what you're capturing.

Don't steer the content either. The topic is just a vehicle; resist giving advice on their project.

## 2. Analyze

Work through `references/speaking-checklist.md`. Record concrete evidence: a short quote and how often it came up.

Watch for transcription artifacts. Speech-to-text mishears words (a drug name heard as a Linux distro, a name spelled wrong), and those aren't the user's style. When unsure whether something is a quirk or a transcription error, ask.

## 3. Merge with writing (if VOICE.md already exists)

The written sections decide how text messages look. Speech adds rhythm, how reasons are chained, and how explanations are layered. Spoken fillers ("you know", "I mean", "whatever else is there") stay in the spoken section; putting them into Jira drafts makes the output read like a transcript. Only carry a spoken habit into the written rules if the writing samples show it too.

Put signature phrases where the user actually puts them. "So basically" opens an explanation, not a greeting; a trailing "as well" goes after an added point, not on every sentence.

## 4. Finish

Follow `references/finishing.md`: have the user set the rules (skip any already in VOICE.md), write or update VOICE.md from `references/voice-template.md` (section 10 is the spoken section), wire it in, and test. For this mode, testing usually means the user asks you to talk about something in their voice: stay in it every reply until they say stop.
