# How Discord Stores Trillions of Messages

**Domain:** chat message storage · **Source:** bytebytego.com/guides/how-discord-stores-trillions-of-messages

## Overview
Evolution of Discord's message-storage backend from a single MongoDB replica to a 177-node Cassandra cluster to a Rust-service-fronted ScyllaDB cluster, driven by read-latency degradation as message volume grew from millions to trillions.

## Scale
2015: single MongoDB replica, 100M messages · 2017: 12 Cassandra nodes, billions of messages · early 2022: 177 Cassandra nodes, trillions of messages, degraded p99s · post-migration p99 read 15ms / write 5ms (ScyllaDB) vs. 40-125ms read / 5-70ms write (Cassandra).

## Architecture
- **MongoDB (2015)**: single replica; message working set didn't fit in RAM, causing unpredictable read latency
- **Cassandra (2017-2022)**: wide-column store scaled to 177 nodes; LSM-tree storage engine made reads far more expensive than writes, and SSTable compaction plus JVM garbage-collection pauses caused recurring latency spikes under Discord's read-heavy load
- **ScyllaDB (current)**: Cassandra-compatible, C++-based rewrite with no JVM/GC; fronted by a monolithic API and a Rust-based data service layer that owns query routing and shaping before hitting storage

## Key decisions
- Moved off MongoDB once the data no longer fit in memory - a single-replica document store was never going to scale horizontally for this access pattern, so the fix was a storage-model change, not more RAM.
- Chose Cassandra for the 2017 rewrite because horizontal scale-out matched message growth, accepting write-optimized LSM-tree trade-offs.
- Replaced Cassandra with ScyllaDB rather than tuning further, because the bottlenecks (GC pauses, compaction overhead, read amplification) were structural to the JVM/LSM design, not misconfiguration - a drop-in wire-compatible C++ engine removed the GC pause class of latency entirely while keeping the existing data model and client protocol.

## Reusable patterns
- **Protocol-compatible engine swap**: when a database's fundamental runtime (JVM GC, storage engine) is the ceiling, migrate to a wire-compatible alternative instead of rewriting the application layer.
- **Watch p99, not average, when read volume outpaces writes**: LSM-tree stores that are fine at low read concurrency degrade specifically at the tail under high concurrent reads - track p99 latency as the early-warning signal before a full cluster resize is needed.
