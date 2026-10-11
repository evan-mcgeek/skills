# Cloudflare's Rate Limiting at Scale

**Domain:** DDoS mitigation / rate limiting · **Source:** blog.cloudflare.com/counting-things-a-lot-of-different-things

## Overview
Rate limiting across millions of customer domains without a centralized counter store - accurate enough to stop attacks, cheap enough to check on every request, and fast enough to never slow down legitimate traffic.

## Scale
Several billion requests/day · attacks up to 400,000 req/sec against a single domain · validated on 400M requests from 270,000 distinct sources: 0.003% wrongly allowed/blocked, ~6% average deviation from the true rate.

## Architecture
- **Anycast routing** means traffic from a given source IP normally lands on the same PoP, so rate limiting only needs to be correct per-datacenter, not globally coordinated
- **Twemproxy cluster per PoP** fronting sharded memcached, using consistent hashing to place each rate-limit counter deterministically
- **Sliding window counter**: two integers per key (previous-period count, current-period count) combined with a decay formula - `rate = previous_count × ((period_length − elapsed) / period_length) + current_count` - approximating a true sliding window without storing a timestamped log of every request
- **Asynchronous `INCR`**: the counter update fires off-path; the request that triggered it is never held up waiting on memcached
- **Local decision caching**: once a source is flagged for mitigation, the edge server caches that verdict locally so repeat requests from the same source skip the counter lookup entirely

## Key decisions
- Scoped the problem to per-PoP counting instead of a global rate limiter, because anycast already gives "same source → same PoP" for free - avoids the latency and availability cost of cross-datacenter coordination for a check that runs on every request.
- Chose an approximate sliding window (2 numbers + decay math) over an exact one (log of every request timestamp), trading ~6% accuracy for O(1) memory per key and a single atomic increment - acceptable because rate limiting only needs to catch abuse, not bill to the request.
- Made the counter update asynchronous relative to the request path, so a slow or degraded memcached shard degrades rate-limit accuracy, never request latency.
- Cached the mitigation decision locally after the first trigger, turning a sustained attack into one memcached round-trip instead of one per request.

## Reusable patterns
- **Approximate sliding window via decay-weighted two-counter scheme**: cheap O(1) memory per rate-limited key, bounded error, no per-request log - the general pattern for any high-volume rate limiter.
- **Exploit existing routing determinism to avoid coordination**: if your infra already guarantees "same key routes to the same node" (anycast, consistent hashing, sticky sessions), scope stateful counting to that node instead of building a distributed consensus layer.
