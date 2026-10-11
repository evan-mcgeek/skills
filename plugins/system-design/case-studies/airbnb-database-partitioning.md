# How Airbnb Partitioned Its Main Database in Two Weeks

**Domain:** relational database scaling · **Source:** medium.com/airbnb-engineering/how-we-partitioned-airbnb-s-main-database-in-two-weeks

## Overview
Airbnb's messaging inbox tables lived in the same monolithic MySQL database as core product data and accounted for a third of all writes; with traffic compounding annually, the team split messaging onto its own database using replication promotion instead of custom migration tooling.

## Scale
Messaging = ~1/3 of all main-DB writes, projected +50% within months · peak traffic growing 3.5x/year · infra team of a handful supporting 130+ engineers · project completed in 2 weeks with a 7.5-minute downtime window · result: main DB size -20%, master writes -33%.

## Architecture
- Stood up **message-master** and **message-replica** as MySQL read replicas off the existing main database
- **Promoted the replica** to an independent master serving message data - MySQL's own replication mechanism handled data consistency, so no custom bookkeeping/migration code was written
- Pre-work: hunted down and eliminated cross-table joins between messaging and other domains so messaging data had no remaining hard dependency on the main DB
- Cutover: coordinated traffic routing to the new master through eight phases, accepting a short downtime window during promotion rather than building a zero-downtime migration path

## Key decisions
- Chose replication-promotion over dual-write/backfill migration tooling because a small infra team couldn't afford weeks of consistency-mechanism engineering - trading 7.5 minutes of downtime for months of engineering effort was the explicit tradeoff.
- Scoped the split to exactly the tables causing the write pressure (messaging), not a general sharding rewrite - the fix targeted the specific subsystem driving the growth curve.
- Treated eliminating cross-table joins as a prerequisite step, not an afterthought - a table can't be promoted to its own master while other domains still join across it live.

## Reusable patterns
- **Replica-promotion split**: when one subsystem's tables can be cleanly decoupled (no live cross-joins), promoting a read replica to master is a far cheaper way to give it its own database than writing a consistency-preserving migration.
- **Accept a short downtime window deliberately**: a bounded, scheduled downtime is often strictly cheaper than the engineering cost of avoiding it - worth stating as an explicit tradeoff rather than defaulting to "zero downtime required."
- **Watch backup/snapshot latency as a leading indicator**: RDS/backup snapshot operations can cause non-linear latency spikes under load well before the primary growth metric looks urgent - a warning sign the database is closer to its ceiling than steady-state numbers suggest.
