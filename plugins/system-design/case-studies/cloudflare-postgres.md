# How Cloudflare Scaled Postgres

**Domain:** database resource isolation / multi-tenancy · **Source:** newsletter.systemdesign.one/p/postgresql-scalability

## Overview
Cloudflare serves 20% of internet traffic on just 15 Postgres clusters by pushing resource isolation and congestion control into the connection-pooling layer, not the database itself.

## Scale
55M HTTP req/sec · 15 Postgres clusters · 100+ DB servers incl. replicas · 2 regions × 3 servers/region/cluster.

## Architecture
- **PgBouncer**: TCP proxy in front of Postgres; cheap to hold many client connections, expensive real DB connections stay pooled and throttleable per-tenant
- **HAProxy**: distributes traffic across primary + read replicas, sitting in front of PgBouncer
- **TCP-Vegas-style congestion control**: samples per-tenant round-trip time to Postgres, dynamically resizes that tenant's pool before the DB starves
- **Priority queueing** (peak only): ranks queries by historical resource cost, expensive ones queued last so most tenants stay fast
- **Stolon**: cluster manager for replication, leader election, failover; **pg_rewind** resyncs a rejoining node
- **Bare metal**: avoids virtualization tax for raw throughput

## Key decisions
- Isolate contention at the proxy, before it ever reaches Postgres - per-tenant throttling is nearly impossible to do cleanly inside the DB itself.
- Congestion algorithms (RTT-sampling) over static connection limits - adapts pool size automatically instead of manual tuning per tenant.
- Priority queuing only kicks in at peak, so it doesn't add overhead or starve anyone under normal load.

## Reusable patterns
- **Proxy-layer multi-tenant fairness**: throttle/queue before a shared resource, not inside it.
- **Adaptive concurrency via latency sampling**: let a congestion-control-style feedback loop size the pool instead of a fixed number.
