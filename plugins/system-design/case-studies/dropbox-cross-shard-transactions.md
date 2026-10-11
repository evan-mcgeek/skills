# Cross-Shard Transactions at Dropbox

**Domain:** distributed transactions / sharded metadata store · **Source:** dropbox.tech/infrastructure/cross-shard-transactions-at-10-million-requests-per-second

## Overview
Dropbox's Edgestore metadata store guarantees transactional consistency only within a shard ("colo"); operations that must touch two users on different shards (e.g. a share between users who aren't collocated) had no atomic primitive, forcing costly application-level workarounds. Dropbox built a three-phase, copy-on-write variant of two-phase commit to close that gap without paying full multiversioning cost.

## Scale
10M requests/sec across Edgestore · petabytes of data across thousands of MySQL nodes · cross-shard transactions are only 5-10% of all Edgestore operations · staging approach cut write amplification by up to 95% vs. naive multiversioning.

## Architecture
- **Colos**: collocated shard groups that already guarantee single-shard transactional consistency
- **Modified two-phase commit** for the cross-shard case, split into: Phase 0 (leader durably writes a pending transaction record), Phase 1 (participants durably stage mutations, signal commit-intent without knowing the final decision), Phase 2a (leader writes the commit/abort decision - the actual commit point), Phase 2b (participants apply or roll back their staged mutation)
- **External transaction record** collocated with one participant (not queried from every participant), so worst-case lookup touches at most two nodes: the local participant and the node holding the transaction record
- **Copy-on-write staging table**: mutations land in a small secondary MySQL table first and are only materialized into the real table at commit time - steady-state read filtering is just a local existence check against a table small enough to stay in memory
- **Shadow/validation deployment**: a "validation" protocol version ran the new commit path alongside the existing API as shadow writes, so real production traffic measured performance before cutover, without user-visible risk

## Key decisions
- Kept the fast, single-shard-collocated path untouched and added the cross-shard protocol only for the minority (5-10%) of operations that need it, instead of redesigning Edgestore's consistency model wholesale for a rare case.
- Staged mutations via copy-on-write into a small secondary table rather than full multiversioning, because the existence-check read cost stays O(1) and in-memory, while multiversioning would have meant doubling write latency across the whole system.
- Collocated the transaction record with a participant rather than a separate coordinator service, bounding the worst-case lookup to two nodes instead of an all-participants query.
- Validated with shadow writes in production before cutover, rather than trusting load-test/staging numbers alone, because distributed-transaction correctness bugs only surface under real traffic shape and fault patterns.

## Reusable patterns
- **Precedence-graph verification**: model transactions as a directed graph where edges encode operation ordering; a cycle proves a serializability violation and a missing edge proves an atomicity violation - a systematic way to fault-hunt a new commit protocol beyond ad hoc testing.
- **Shadow-write validation**: run a new consistency/commit protocol as a no-op shadow path alongside the existing one in production, so performance and correctness are measured under real traffic before the switch is user-visible.
- **Copy-on-write staging over full multiversioning**: when only a minority of operations need cross-partition atomicity, stage changes cheaply in a small side table rather than paying multiversioning overhead for every write in the system.
