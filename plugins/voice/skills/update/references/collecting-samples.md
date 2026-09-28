# Collecting writing samples

Goal: a single `voice-samples.md` containing only text the user wrote themselves, before the AI cutoff date, long enough to carry signal.

## 1. Where samples come from

Anything the user typed for other people to read works: Slack or Teams messages, emails, Jira or Linear comments and tickets, GitHub PR reviews, Confluence, Notion or Google Docs pages, forum posts.
Ask which channels they actually write in and use those.
A mix of short messages and longer pieces (tickets, docs, long emails) gives the best profile.

## 2. How to get them

Default: ask the user to paste or upload them.
Exports work well: a Slack or email export, a Jira CSV, a folder of docs.
Tell them what's useful: roughly 100+ messages and 20+ longer pieces, each with a rough date and where it was posted.

If a tool for one of their sources is already connected (a Jira, Slack, email or docs connector), offer to pull samples through it instead.
When fetching:
- Filter by the user's account ID, not their display name, since names collide.
- Keep only text they authored before the cutoff. Drop anything edited after it; an agent may have rewritten it.
- Page through all results, not just the first page.
- Keep formatting as close to the original as the tool allows: @mentions, code blocks, bold, lists, strikethrough. If it returns rich-text JSON, convert to markdown rather than flattening to plain text.

Never make a connector a requirement.
If none is available, pasted or exported samples are just as good.

## 3. Filter

Drop:
- Anything under ~10 words ("done", "thanks", "LGTM").
- Automated text: bot messages, status-change notes, CI links with no human sentence.
- Anything the user identified as agent-written.
- Pasted content that isn't theirs: logs with no comment, quoted emails, copied specs. Keep the user's own sentence around a log and the log itself in a code block, since how they present logs is style too.

## 4. Save

Write `voice-samples.md`:

```markdown
# <Name>'s writing samples

Sources: <e.g. Slack, email, Jira>. Written by <Name> before <cutoff>, longer than 10 words.
<N> messages, <N> longer pieces.

## Messages

### <source, channel or ticket> (<date>)
<text>

## Longer pieces

### <source>: <title> (<date>)
<text>
```

Tell the user the counts and sources covered, and ask whether anything obvious is missing (a channel, a period) before analyzing.
