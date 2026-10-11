# MySQL High Availability at GitHub

**Domain:** database failover / high availability · **Source:** github.blog/2018-06-20-mysql-high-availability-at-github

## Overview
GitHub's automated MySQL failover system replaces manual/DNS-based primary promotion with a raft-coordinated detection-and-promotion service (orchestrator), instant-propagation service discovery (Consul), and connection-level routing (GLB/HAProxy) - aiming for lossless, low-outage failover across multiple data centers.

## Scale
Multiple MySQL clusters across several data centers, one or two orchestrator nodes per DC · total outage during failover: 10-13s typical, up to 20-25s in extended scenarios · semi-sync replication ack timeout: 500ms.

## Architecture
- **orchestrator**: holistic failure detection and promotion; runs as a raft-consensus cluster spanning DCs so no single, network-isolated DC can unilaterally decide a primary is dead and promote a replacement (avoids split-brain)
- **Consul**: key-value store (not DNS) holding current primary identity; readers/writers watch it directly, so a promotion propagates instantly instead of waiting out a DNS TTL
- **GLB/HAProxy**: anycast-IP connection routing layer in front of MySQL; on promotion, HAProxy is reconfigured to "hard-stop-after" existing connections to the demoted primary, forcing clients onto the new one rather than leaving them talking to a stale host
- **Semi-synchronous replication**: enabled only on local-DC replicas, with a 500ms ack timeout, so a promoted replica is guaranteed to have the last acknowledged write

## Key decisions
- Raft consensus for the failure-detection layer itself, not just for MySQL - because the risk isn't only "is the primary down," it's "can this DC's view of the world be trusted," and a network partition can make a healthy primary look dead from one DC's vantage point.
- Consul over DNS for primary discovery - DNS TTLs impose a floor on failover time that's independent of how fast you detect and promote; a directly-watched KV store removes that floor.
- Semi-sync scoped to local-DC replicas only, with a short (500ms) timeout, rather than fully synchronous or async-everywhere - sync-everywhere would let a slow/unreachable remote replica stall every write; the local-only + timeout combination bounds the availability cost of durability to milliseconds instead of cross-region RTT.
- Connection-level forced disconnect (hard-stop-after) instead of relying on clients to notice a promotion and reconnect - removes an entire class of "client silently kept writing to the old primary" bugs.

## Reusable patterns
- **Consensus-based failure detection before automated promotion**: any auto-promotion system is only as safe as its failure detector; back it with raft/quorum so a partitioned minority can't trigger a bad promotion.
- **Directly-watched service discovery over DNS for anything failover-critical**: DNS TTLs cap your best-case failover time regardless of how fast the rest of the pipeline is.
