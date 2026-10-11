# How Uber's M3 Metrics Platform Works

**Domain:** time-series metrics / observability infrastructure · **Source:** eng.uber.com/m3 (via uber.com/blog/m3), uber.com/blog/billion-data-point-challenge

## Overview
Uber's in-house metrics platform (M3) replaced a Graphite/Whisper stack that couldn't survive disk failures or reshard without downtime, adding a distributed TSDB (M3DB), a Prometheus-compatible coordinator, and a query engine built to answer high-cardinality queries without blowing memory.

## Scale
6.6B time series stored · 500M metrics ingested/sec · 20M metrics/sec persisted globally (3x quorum replication per region) · query engine: 2,500 queries/sec, 8.5B data points/sec, 35Gbps throughput (Nov 2018) · retention policies from 2 days to 5 years, granularity from 1s to 1h.

## Architecture
- **M3DB**: distributed time-series store + reverse index, immutable data model (no Cassandra-style compaction rewrites), out-of-order write support, values compressed with **M3TSZ** (an optimized variant of Facebook's Gorilla TSZ)
- **M3 Coordinator**: sits beside Prometheus, exposes a global query interface, owns downsampling/retention/aggregation rules stored in embedded etcd, fans queries out to remote coordinators for cross-region reads instead of replicating data across regions
- **Query engine**: three-phase pipeline - parse (M3QL or PromQL into a DAG) → execute (resource-tracked, cancellable) → retrieve (thin wrapper over M3DB) - decoupling query language from execution so multiple languages share one execution path
- Storage blocks indexed with Bloom filters and mmap'd for a "write once, read rarely" access pattern
- Downsampling applied at ingestion (via **Largest Triangle Three Bucket**, not naive averaging) rather than at query time, to avoid re-paying network/CPU/disk cost on every read

## Key decisions
- Built a custom TSDB only after evaluating and rejecting the existing stack (statsite + Cassandra + Elasticsearch) - Cassandra's Date-Tiered Compaction meant continuously rewriting immutable time-series data for no benefit, which was pure operational cost with no correctness upside at Uber's ingest rate.
- Downsample at ingestion, not at query time - paying the CPU/network cost once during write is cheaper than re-decompressing full-resolution data on every dashboard load.
- Lazy, column-at-a-time evaluation in the query engine instead of decompress-then-compute: measured 1.7GB vs. 241KB memory for the same query, because full decompression scales with series × datapoints while lazy evaluation scales with series alone.
- Regional fan-out queries instead of cross-region replication - avoids paying replication bandwidth/storage cost for data that's usually queried from where it was written; only the query result crosses regions, not the raw data.
- LTTB downsampling over averaging for visualization - averaging silently erases spikes/outliers that are often the reason someone opened the dashboard; LTTB preserves visual shape while still reducing point count.

## Reusable patterns
- **Immutable time-series storage**: treat each write as append-only and skip Cassandra-style background compaction entirely - it only exists to reconcile mutable data, which time-series metrics never are.
- **Lazy/streaming evaluation for high-cardinality queries**: defer decompression and allocation until the last possible operation in the query DAG; memory scales with series count, not with series × resolution.
- **Aggregate-before-storage, not before-query**: push downsampling/rollups to the write path so every subsequent read is cheap, instead of computing rollups fresh per query.
