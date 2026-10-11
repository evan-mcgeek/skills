# How Reddit Works

**Domain:** feed ranking / write decoupling · **Source:** newsletter.systemdesign.one/p/reddit-architecture

## Overview
Scaled from a single-machine monolith to 100M DAU by decomposing write-heavy operations (posts, votes) into async job queues and pre-computing feed rankings so reads stay cheap.

## Scale
100M DAU · millions of concurrent posts/votes needing live rank updates · thousands of subreddits each with their own feed list.

## Architecture
- **Load-balanced app servers** behind an LB
- **Database partitioning** by subreddit/content type - avoids a single write bottleneck
- **Async job queues** for post submission, vote processing, cache invalidation - nothing expensive happens synchronously on the request path
- **Denormalized rank cache**: post IDs + rank stored directly on the cache server for O(1) feed reads
- **Read replicas** for read-heavy query load
- **Cassandra** for durable storage of popular pre-computed lists
- **Zookeeper**-based distributed locks to prevent races on shared resources

## Key decisions
- Lock contention on popular posts caused queue latency spikes → **partition the queue by subreddit ID (modulo hashing)**, isolating contention to fewer processors per resource without adding hardware.
- Ranking-on-every-read was too expensive → precompute ranked lists asynchronously, cache the IDs, serve with a lookup instead of a sort.

## Reusable patterns
- **Decouple writes from reads**: queue the expensive mutation, serve reads from a precomputed cache.
- **Partition by entity ID (modulo hashing)** to shrink lock contention and enable horizontal scaling of queues/shards.
