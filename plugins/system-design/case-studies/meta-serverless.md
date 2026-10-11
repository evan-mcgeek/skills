# How Meta Serverless Works (XFaaS)

**Domain:** FaaS scheduling / cold-start mitigation · **Source:** newsletter.systemdesign.one/p/serverless-architecture

## Overview
Meta's XFaaS handles 11.5M function calls/sec by optimizing for idle-resource cost, not raw latency-at-any-cost - most functions are called too rarely to justify staying warm.

## Scale
11.5M calls/sec · 81% of functions invoked ≤1×/minute · keeping everything warm would waste ~33,400 servers at Meta's scale.

## Architecture
- **Universal worker model**: workers in a language-specific namespace can run *any* function in that language - shared runtime init cuts cold starts
- **Locality groups**: co-locate workers that run the same functions often, improving JIT cache hit rate
- **Pre-pushed container images**: function code lives on worker SSDs ahead of time, no download-on-invoke
- **Cooperative JIT compilation**: one worker compiles new code once, distributes the compiled binary to peers - avoids redundant compilation
- **Backpressure throttling**: TCP-congestion-control-style tracking of backend error rate/latency/capacity
- **Concurrency ramp-up**: start new load at low concurrency, let backend caches warm, then scale up
- **Per-function resource quotas**, geographic spreading, deferring low-priority work to off-peak

## Key decisions
- Don't keep idle functions warm - 144 idle servers for 10 minutes wastes a full server-day; cache/pre-position instead of pooling warm capacity.
- Protect backend services with backpressure, not fixed rate limits - adapts to real downstream health.

## Reusable patterns
- **Adaptive throttling via backpressure signals** (latency/errors/capacity) generalizes to any system fronting variable-capacity downstreams.
- **Graduated ramp-up**: start conservative, scale as the backend proves it can take it - avoids thundering-herd outages.
