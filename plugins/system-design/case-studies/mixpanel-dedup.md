# Mixpanel's Petabyte-Scale Data Deduplication

**Domain:** data pipeline correctness · **Source:** medium.com/mixpaneleng/petabyte-scale-data-deduplication-mixpanel-engineering

## Overview
Mixpanel ingests petabytes of event data at 1M+ events/sec; unreliable client networks cause retries that duplicate events, and standard ingestion-time dedup (KV store lookup against a 7-day window) couldn't catch retroactive duplicates or scale without dedicated infrastructure. Mixpanel instead defers deduplication to indexing and query time.

## Scale
1M+ events/sec ingest · petabytes of event data · largest columnar file ~2M events · indexing overhead at 2% duplicate rate: 4-10% · query-time overhead: ~10ns/event (~2% query time increase).

## Architecture
- **Sharding by (project, user, time)**: guarantees every duplicate of a given user's event lands in the same shard, so dedup never needs a cross-shard/global lookup
- **Lambda architecture**: real-time writes go to append-only files; a periodic compaction job indexes them into columnar files
- **Indexing-time pass**: an in-memory hashset of `$insert_id` values during compaction flags duplicates with a bit rather than deleting them
- **Query-time pass**: reads skip bit-flagged duplicates in indexed (columnar) files, and do a cheap hash-based dedup on the small unindexed append-only files

## Key decisions
- Rejected the industry-standard ingestion-time KV dedup (RocksDB/Cassandra + 7-day retention window) because it requires standalone infrastructure, can't catch duplicates arriving after the window closes, and deletes data irreversibly if it guesses wrong.
- Moved dedup to indexing + query time instead of ingest time, trading a small per-query overhead (~2%) for correctness that isn't bounded by a retention window and needs no extra datastore.
- Flag-not-delete at indexing time: marking a bit instead of removing the duplicate keeps the operation reversible and idempotent under re-indexing.

## Reusable patterns
- **Scope reduction through sharding**: shard key chosen so all potential duplicates of one entity co-locate in a single partition - turns an expensive global dedup problem into a cheap local one.
- **Amortized deduplication across pipeline stages**: split the cost between a batch/compaction pass (cheap, infrequent) and a query-time pass (tiny, per-read) instead of a dedicated real-time dedup service.
