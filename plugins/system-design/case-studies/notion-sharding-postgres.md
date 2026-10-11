# Sharding Postgres at Notion

**Domain:** relational database scaling · **Source:** notion.com/blog/sharding-postgres-at-notion

## Overview
Notion's single Postgres monolith hit a wall in 2020 after five years and four orders of magnitude of growth: VACUUM stalled under the write volume and transaction-ID wraparound became an existential risk. They split it into 480 logical shards across 32 physical databases with near-zero downtime.

## Scale
480 logical shards · 32 physical databases (15 shards each) · backfill took ~3 days on a fully-provisioned m5.24xlarge (96 CPUs) · final cutover maintenance window: 5 minutes · billions of blocks/files/spaces migrated.

## Architecture
- **Partition key: workspace ID (UUID)** - every block and its transitively-reachable foreign-key-linked tables colocate on one shard, since almost all queries stay within a single workspace
- **480 logical shards, not a power of 2** - chosen for its large factor count (2, 3, 4, 5, 6, 8, 10...) so physical database count can grow incrementally instead of only doubling
- **Separate per-shard tables** (`schema001.block`, `schema002.block`, ...) instead of native Postgres declarative partitioning, giving the application a single routing model instead of dual logic for partitioned vs. unpartitioned tables
- **Migration in three phases**: (1) double-write new data to both monolith and shards via an audit-log table with a catch-up script, plus a reverse audit log prepared for rollback; (2) backfill old data with version comparison so writes converge regardless of execution order; (3) verify via random UUID sampling and "dark reads" (query both DBs, diff results, log discrepancies) before switchover

## Key decisions
- Picked workspace ID as the shard key specifically because it eliminates cross-shard joins for the dominant query pattern - sharding by a key that doesn't match access patterns would have just moved the join problem to the network.
- Chose 480 over a power-of-2 shard count so future capacity growth (32 → 40 → 48 physical DBs) doesn't require doubling everything - a power-of-2 scheme would force wasteful all-or-nothing rehoming.
- Ran backfill and live double-writing concurrently with a reverse audit log as an explicit rollback path, because a migration this large needed a tested way back, not just a tested way forward.
- Verified with dark reads before cutover instead of trusting the backfill script's exit code - comparing live query results catches convergence bugs that a completed backfill log cannot.

## Reusable patterns
- **Shard key = dominant query's natural boundary**: pick the partition key that already matches how your data is queried (tenant/workspace ID), not an arbitrary hash, to avoid rebuilding cross-shard joins after the fact.
- **Shard count with many factors beats a power of 2**: makes physical database count independently adjustable later instead of forcing capacity doubling.
- **Double-write + version-compared backfill + dark-read verification**: a three-phase migration pattern for splitting a live database with near-zero downtime and a real rollback path.
