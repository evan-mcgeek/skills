# How Tinder Works

**Domain:** geospatial matching · **Source:** newsletter.systemdesign.one/p/tinder-architecture

## Overview
Matches nearby users via Google's S2 geospatial indexing (hierarchical cells on a Hilbert curve), specifically to avoid the hot-shard problem that a naive uniform grid creates.

## Scale
1.6B swipes/day · 26M matches/day · ~500 microservices · ~3 shards queried per 160km-radius location lookup.

## Architecture
- **S2 geospatial index**: hierarchical, variable-sized cells preserve spatial locality; Hilbert-curve ordering keeps physically-close cells close in ID space
- **DynamoDB + Streams**: user profiles in KV storage, streams push location changes into indices in near real-time
- **Kafka partitioned by user**: guarantees FIFO ordering of a single user's location updates, preventing "user in two places at once" races
- **Redis cache-aside** for read-heavy profile/location lookups
- **Kinesis** streams swipe events for match detection against cached "likes"
- **WebSockets** push match notifications in real time
- **Multi-shard-per-server assignment**: shards randomly distributed across servers to smooth out time-zone-driven peak load

## Key decisions
- Rejected uniform grid sharding - creates overloaded shards over cities, empty shards over oceans. S2's hierarchy naturally concentrates partitions where users actually are.
- Location updates aren't atomic across services, so per-user Kafka partitioning enforces sequential processing instead of relying on distributed locks.
- Rate-limit writes even though reads are cached - write hotspots during regional peak hours still need protection.

## Reusable patterns
- **S2/H3-style hierarchical geo-indexing** applies to any location-matching system: rideshare, local commerce, logistics (see also Uber's H3 case study).
- **Partition-by-key streaming (Kafka)** solves ordering for any distributed system with concurrent per-entity state mutation.
