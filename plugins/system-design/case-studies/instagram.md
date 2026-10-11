# How Instagram Works

**Domain:** global infrastructure scaling · **Source:** newsletter.systemdesign.one/p/instagram-infrastructure

## Overview
Scaled from 30M to 2.5B users via distributed, region-optimized architecture rather than vertical scaling - regional DB clusters plus aggressive per-server efficiency.

## Scale
30M users (early) → 2.5B users (current) · ~10ms latency for the regional-routing proxy.

## Architecture
- **Cassandra**: separate cluster per continent (eventual consistency), single cross-region replica for DR
- **PostgreSQL**: leader-follower replication for user data/friendships/metadata; reads routed to followers
- **Akkio**: data-placement service that tracks access patterns and migrates a user's data to their active region
- **Global load balancer** routes through an Akkio proxy to the correct regional cluster
- **Python + Cython/C**: hot-path functions rewritten in C to cut per-request CPU cost and GIL overhead
- **Shared memory**: common objects moved from per-process private memory to shared memory to raise process density per server

## Key decisions
- Regional data isolation over one global Cassandra cluster: cuts cross-continent latency and consistency pain; quorum reads + cross-region replica cover HA.
- Optimize code before buying hardware: replacing Python hotspots with compiled code raised users-served-per-server more than scaling out did.
- Migrate data to where the user actually is, based on observed access pattern, not signup location.

## Reusable patterns
- **Geography-based sharding** beats a single globally-replicated cluster for latency-sensitive, geographically clustered traffic.
- **Profile before you scale out**: language-level hotspot optimization is often cheaper than more servers.
