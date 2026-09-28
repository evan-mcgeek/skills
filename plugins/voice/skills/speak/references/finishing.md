# Finishing: rules, VOICE.md, wiring, testing

Shared by `/voice:write` and `/voice:speak`. Do these after the analysis.

## 1. Ask the user to set the rules

Samples show how the person writes and talks on their best and worst days. The profile should capture the voice, not every habit. Ask these directly (tappable options work well) and record the answers as hard rules. If a VOICE.md already exists with these rules, don't ask again.

- **Grammar.** "Keep your exact quirks, or grammatically correct while keeping your rhythm?" Most people, especially non-native speakers, want correct grammar with their phrasing intact. Then the profile says: reproduce rhythm and signature words, never typos or grammar slips.
- **Tone.** If the material shows blunt pushback, sarcasm, or irritation, ask whether agents should ever reproduce it. Usually not: people keep that tone for specific people or situations they'd never delegate. Default to polite, and don't have the agent point out anyone's mistakes unless the user explicitly wants that.
- **Scope.** What will agents actually write? (Investigation results, replies to questions, tickets, release updates, short emails.) The agent shouldn't attempt anything outside that list under the user's name.
- **Audiences.** Who gets a different register? Usually technical peers, business/product/QA, and senior people (boss, leadership), who get a more careful version of the same voice.

## 2. Write or update VOICE.md

If a VOICE.md already exists (in the conversation, the repo, or `~/.claude/`), update it: add or revise the sections this mode covers and keep everything else, especially the hard rules. Otherwise create it from `voice-template.md`.

- Write it as **instructions to the agent**, not a description of the user.
- **Hard rules at the top**, so they win over everything else.
- Every signature phrase comes with **where** it naturally occurs, and a reminder to use it once or twice per message, not in every sentence. Misplaced tics read like parody.
- **Worked example messages** for each common message type, fully in the voice.
- **Placeholder names** (`@Name`) in examples, never real colleagues. Real ticket keys or IDs only if the user is fine with it.
- Keep the **AI tells to avoid** section; it does as much work as the positive rules.
- Include only sections the analysis supports. No invented spoken style without `/voice:speak`, no invented Jira conventions without `/voice:write`.
- Under ~250 lines. An agent reads it in full before every post, so every line has to earn its place.

Save as `VOICE.md` (in Claude Code, where the user wants it; in chat, in the outputs folder) and present it.

## 3. Wire it in

Recommend global placement, since posting as a person isn't tied to one repo.

**Claude Code (global):** file at `~/.claude/VOICE.md`, and in `~/.claude/CLAUDE.md`:

```markdown
## Writing on my behalf
Before posting anything on my behalf (Jira comments, tickets, Confluence, email replies, any message sent under my name), read and follow @~/.claude/VOICE.md. Its hard rules override any other style guidance.
```

The `@` path makes Claude Code import the file automatically.

**Claude Code (one project):** `VOICE.md` next to the project's `CLAUDE.md`, referenced as `@VOICE.md`.

**Codex and other AGENTS.md harnesses:** add the same section to `AGENTS.md`. Not every harness resolves `@` imports, so write the path out plainly ("read `~/.codex/VOICE.md` in full before...") or paste the hard rules into AGENTS.md as a fallback.

With file access, make the edit after confirming the location. Without it, hand over the snippet.

## 4. Test and tune

Draft 2-3 realistic messages (e.g. an investigation result for a developer, a release update for QA, a short answer to a product person) and ask the user to judge them. Expect "too polished", "I'd never say that there", "wrong phrase in the wrong place". Fix the profile, not only the draft, so the lesson sticks.

When the user asks to hear the voice ("tell me about X the way I'd say it"), stay in it for every reply until they say stop. Drifting back into your own rhythm after a turn or two is the most common failure. When they ask for something short in their voice, just deliver it; don't workshop it or explain the bit.

The real test is live posting. Suggest reviewing a few days of agent-posted messages together and tuning whatever reads off.
