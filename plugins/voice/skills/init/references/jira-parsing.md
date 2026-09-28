# Parsing Jira and Confluence

Goal: a single `voice-samples.md` containing only text the user wrote themselves, before the AI cutoff date, long enough to carry signal.

## 1. Identify the user

Through the connector, get the current user's account ID and display name. Every filter below matches on the account ID, not the name, since names can collide.

## 2. Find candidate issues

Jira JQL can't search by comment author directly, so cast a wide net and filter afterwards:

```
(reporter = currentUser() OR assignee was currentUser() OR watcher = currentUser())
AND updated >= "<cutoff minus 12 months>"
AND created < "<cutoff>"
ORDER BY updated DESC
```

Adjust the window if it returns too few or too many issues. If the user names specific projects, add `project in (...)`. Page through all results; don't stop at the first page.

## 3. Pull the text

For each issue:
- **Description:** keep it if the user is the reporter and the issue was created before the cutoff.
- **Comments:** keep a comment only if its author's account ID is the user's and it was created before the cutoff. If a comment was edited after the cutoff, drop it; an agent may have rewritten it.

Keep the text as close to the original as the connector allows: @mentions, code blocks, bold, lists, strikethrough. Formatting habits are part of the voice. If the connector returns rich-text JSON, convert it to markdown rather than flattening it to plain text.

## 4. Filter

Drop:
- Anything under ~10 words ("done", "thanks", "LGTM").
- Automated text: bot messages, transition notes, build or CI links with no human sentence.
- Anything the user identified as agent-posted.
- Pasted content that isn't theirs: long logs with no comment, quoted emails, copied specs. Keep the user's own sentence around a log and the log itself in a code block, since how they present logs is style too.

## 5. Confluence (optional)

If they write Confluence pages, use CQL:

```
creator = currentUser() AND type = page AND created < "<cutoff>" ORDER BY created DESC
```

Take the 10-20 most recent pages they authored. Skip pages that are mostly tables or templates.

## 6. Save

Write `voice-samples.md`:

```markdown
# <Name>'s writing samples

Source: <site>, projects <list>. Authored by <Name> before <cutoff>, longer than 10 words.
<N> ticket descriptions, <N> comments, <N> Confluence pages.

## Ticket descriptions

### <KEY-123>: <title> (<date>)
<description>

## Comments

### <KEY-456> (<date>)
<comment>

## Confluence pages

### <page title> (<date>)
<body>
```

Tell the user the counts and the projects covered, and ask whether anything obvious is missing (a project, a period) before analyzing.
