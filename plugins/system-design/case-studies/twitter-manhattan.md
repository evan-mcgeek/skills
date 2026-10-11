# Manhattan: Twitter's In-House Distributed Database

**Domain:** distributed key-value storage · **Source:** blog.twitter.com/engineering (2014), InfoQ coverage

## Overview
Twitter replaced Cassandra as its primary storage layer with Manhattan, an in-house real-time, multi-tenant distributed database built to serve millions of queries/sec at low latency with pluggable storage engines per workload.

## Scale
6,000 tweets/sec ingested · 240M+ users queried against · tens of millions of queries/sec across Manhattan clusters · 2+ years in production before the 2014 announcement.

## Architecture
- **Interfaces layer**: key/value access, with a graph-based interface added later for edge/relationship queries
- **Storage services layer**: higher-level services built on top (batch Hadoop import, time-series counters)
- **Storage engines layer**: three pluggable engines chosen per access pattern - one for read-only Hadoop-derived data, one write-heavy, one read-heavy
- **Core layer**: handles failure detection, routing, topology/cluster membership, intra- and inter-datacenter replication, and conflict resolution - shared across every storage engine

## Key decisions
- Replaced Cassandra specifically because expanding the cluster to new machines was operationally too hard at Twitter's growth rate - not a performance complaint, an operability one.
- Chose strong consistency over Cassandra's eventual-consistency default, because Twitter's workload needed correctness guarantees eventual consistency couldn't give, even at the cost of the availability trade-offs strong consistency implies.
- Pluggable storage engines under one shared core, instead of one engine tuned to a compromise - read-heavy, write-heavy, and Hadoop-batch workloads have incompatible optimal layouts, so the core (replication, routing, failure handling) is written once and each engine only owns its own on-disk format.

## Reusable patterns
- **Shared control plane, swappable data plane**: put cluster membership/replication/routing/conflict-resolution in one core, and let workload-specific storage engines plug in underneath it - new access patterns don't require re-solving distributed-systems correctness each time.
- **Migrate off a general-purpose store when the pain is operational, not just architectural**: "hard to add machines" was the trigger here, not a benchmark number - operability at scale is itself a first-class design requirement.
