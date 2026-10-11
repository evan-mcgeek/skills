# How Slack Works

**Domain:** real-time team messaging at multi-tenant scale · **Source:** systemdesign.one/slack-architecture

## Overview
Combines email-like persistence with IRC-style real-time delivery, sharded by workspace/channel so tenants stay isolated from each other's load.

## Scale
10M DAU, 7M concurrent at peak · 12K write QPS / 120K read QPS (10:1) · ~100GB/day, 150TB over 5yr at 3x replication · snapshot service ~1M QPS.

## Architecture
- **WebSockets via Envoy edge proxies** for persistent low-latency delivery (messages, typing indicators)
- **Sharding by channel_id**: spreads load, avoids hot spots; teams never span shards
- **Pub-sub gateway**: gateway servers subscribe to channels via an endpoint store; dispatcher only routes to data centers with active subscribers, minimizing cross-DC traffic
- **Flannel (snapshot service)**: in-memory cache serving client bootstrap payloads, predictively pushes related objects ("just-in-time annotation")
- **Multi-layer cache**: client-side (libchat) → Redis around chat DB → cross-DC snapshot service
- **Vitess** wraps MySQL for automatic re-sharding/topology management
- **Actor model** for gateway servers: lightweight per-connection actors, high throughput per thread

## Key decisions
- Active-active replication chooses availability over strict consistency - survives leader failure.
- Shard by channel, not by user - lower conflict probability than user-based sharding for this access pattern.
- Cursor-based pagination over offset - avoids full table scans at this data volume.
- Lazy-load workspace snapshots instead of sending full state upfront - cuts initial connect latency.

## Reusable patterns
- **Logical clocks (Lamport/vector)** for causal ordering when server timestamps can't be trusted across nodes.
- **Scatter-gather with consistent hashing** to balance cache locality against request latency for partitioned stateless services.
