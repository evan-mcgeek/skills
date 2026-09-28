# Writing analysis checklist

Go through every item with the samples in front of you. Write down concrete evidence (a short quote, how often it appears), not impressions. "Uses 'as well' as an opener and as a trailing tag, ~30 times in 190 comments" is useful. "Casual tone" is not.

## Structure
- How does a message open? @mention, greeting, straight to content, lowercase?
- How does it close? cc line, question, next step, sign-off, nothing?
- Typical length. Share of 1-3 line messages vs. long ones.
- Shape of long messages: context → numbered points → conclusion word → ask? Something else?
- Do quick updates drop the subject or start lowercase ("all good", "upd: ...")?
- How does it change per channel? Team chat (Teams, Slack) is often much shorter and looser than tickets or email: less structure, more emoji, no explanations.

## Rhythm
- Sentence length. Short and chained ("so ... and ...") or long and nested?
- Does the reason come before or after the claim? ("won't do it, since X" vs. "since X, we won't")
- How much hedging? ("I believe", "seems like") vs. flat statements.
- How are opinions and disagreement phrased?

## Signature phrases
- Connectors and conclusion words (so, hence, however, basically).
- The main "because" word (since / because / cause / as).
- Recurring phrases ("as per", "as well", "we'd need", "feel free to").
- How they ask for things (could you please, kindly, would you be able to).
- How they own their own mistakes ("my bad", "sorry, my mistake").
- How they delegate or hand work back.
- Abbreviations (atm, smth, f.e., asap, pls, upd:). Note who they're used with.
- Humor: how often, what kind, emoji or not.
- For each: note where in the message it naturally appears.

## Formatting
- What gets bold (IDs, build versions, warnings)?
- Backticks for code identifiers?
- Code blocks for logs?
- Numbered vs. bulleted lists.
- Links inline or pasted raw.
- Strikethrough self-corrections.
- Headers: ever? Almost never in real human messages.

## Audience switching
- Compare messages to developers vs. product/business/QA vs. senior people. What changes: depth, jargon, length, formality, abbreviations?

## Message types
Find the recurring kinds and capture one real pattern for each: investigation result, answering a question, release/availability update, test instructions, asking for info, delegating, status update, POC/spike outcome. Add whatever else is frequent for this person.

## Longer pieces (tickets, docs, long emails)
- Title conventions (prefixes like [APP] [API] [Bug], casing).
- Typical opening sentence of a description.
- When sections appear and what they're called (Tasks:, Acceptance criteria:, Goal:).
- Docs and wiki pages: how they start, header usage, length, tone vs. messages.

## Non-native markers (if relevant)
List recurring slips (missing articles, "in case if", "what's about", "would you mind to", word-order patterns, typos). These go in the profile as things NOT to reproduce if the user wants correct grammar, so the agent knows which "authentic" features to drop.

## AI-written contamination
Flag samples with: section headers like Summary / Action Points / Expected Outcome / Proposed Changes, em dashes, corporate vocabulary, greeting + sign-off out of character, suspiciously perfect grammar compared to the rest. Confirm with the user before using them.
