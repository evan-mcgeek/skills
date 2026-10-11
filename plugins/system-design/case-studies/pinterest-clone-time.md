# Pinterest's One-Line Fix for a 99% Clone-Time Reduction

**Domain:** CI/build infrastructure · **Source:** bytebytego.com/guides/the-one-line-change-that-reduced-clone-times-by-a-whopping-99-says-pinterest

## Overview
Pinterest's Jenkins pipeline cloned its largest monorepo (Pinboard) on every build; a missing Git refspec parameter meant every clone silently fetched all 2,500+ branches instead of just the one being built.

## Scale
Repo: 20GB fully cloned, 350K commits, 2,500+ branches · 60,000 git pulls/day · clone time 40 min → 30 sec (99% reduction) after the fix.

## Architecture
- Jenkins checkout stage used a shallow clone (`--depth`) but omitted the `refspec` parameter
- Without a scoped refspec, Git still enumerates and fetches ref data for every branch in the repo, even under `--depth`-limited history
- Fix: pass an explicit refspec naming only the branch needed (`master`), so Git never touches the other 2,500+ refs

## Key decisions
- Diagnosed via Git operation timing rather than assuming "monorepo is just slow" - the root cause (fetching all refspecs) was invisible from clone time alone until they profiled what the checkout step actually transferred.
- Fixed the checkout config directly instead of splitting the monorepo or changing CI infrastructure - the problem was one missing parameter, not a scale limit of Git or Jenkins itself.

## Reusable patterns
- **Shallow clone is not enough on its own**: `--depth` limits history depth per ref, but without a `refspec` filter every ref in the repo is still enumerated/fetched. Always pair depth-limiting with explicit refspec scoping in CI checkouts of large multi-branch repos.
- **Profile what a "slow" pipeline step actually transfers before architecting around it** - a 40-minute clone looked like a scale problem but was a one-line config bug.
