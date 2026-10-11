# system-design

Grounds system design work in how real large-scale systems solved the same problem, instead of inventing architecture from first principles.

It ships a library of 47 short case studies (WhatsApp, Stripe, Uber, Figma, Netflix and others) and a [pattern index](pattern-index.md) keyed by the problem solved, not by company.
Each case study keeps the concrete numbers and the reasoning behind every decision, so a design can be checked against the scale that actually justified it.

It's a set of 4 skills:

1. `/system-design:create`: designs a new system, tracing each major choice to a cited case study and picking the lighter option when your scale doesn't justify the heavier one.
2. `/system-design:analyze`: reviews an existing system or codebase and reports only missing load-bearing idioms and unjustified heavier machinery.
3. `/system-design:question`: answers a narrow question from the library, with a targeted web lookup only if the library doesn't cover it.
4. `/system-design:add-case-study`: writes up a case study from a URL or from existing knowledge, indexes it and opens a pull request to this repo.

## Install

```bash
claude plugin marketplace add evan-mcgeek/skills
claude plugin install system-design@evan-mcgeek-skills
```

## Usage

```text
/system-design:create a notification service for 2M daily users
/system-design:analyze src/payments
/system-design:question how does Stripe keep retries from double charging
/system-design:add-case-study https://example.com/how-we-scaled-x
```

## Growing the library

`add-case-study` writes the case study, indexes it and opens a pull request against this repo, after showing you the draft.
It needs the [GitHub CLI](https://cli.github.com) logged in, and forks the repo if you don't have push access.
The case study is also copied into your installed plugin so it works right away, and the next plugin update replaces it with the merged version.

## Sources

Case studies are summaries distilled from [systemdesign.one](https://newsletter.systemdesign.one), [bytebytego.com/guides](https://bytebytego.com/guides) and company engineering blogs (via [awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)).
Each file names its source at the top.
