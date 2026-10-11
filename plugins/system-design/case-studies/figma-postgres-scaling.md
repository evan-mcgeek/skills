# 100X Postgres Scaling at Figma

**Domain:** relational database scaling · **Source:** bytebytego.com/guides/100x-postgres-scaling-at-figma

## Overview
Figma's single Postgres database grew 100x as monthly active users grew 200% (to 3M), forcing a staged scaling path from vertical scaling through vertical then horizontal partitioning.

## Scale
3M MAU · user growth 200% since 2018 · underlying Postgres data grew 100x over the same period · hot tables reached terabytes of data / billions of rows.

## Architecture
- **Phase 1 - vertical scaling**: upgraded RDS instance from r5.12xlarge to r5.24xlarge (largest available), added read replicas for read-heavy traffic, added PgBouncer to cap connection growth
- **Phase 2 - vertical partitioning**: split the hottest tables ("Figma Files", "Organizations") into their own dedicated databases, each with its own PgBouncer instances
- **Phase 3 - horizontal partitioning**: sharded the largest tables across multiple physical databases, routed through a custom-built **DBProxy** service for query routing/execution

## Key decisions
- Exhausted vertical scaling and read replicas first, before touching the schema/topology - cheapest lever (bigger box, more replicas, connection pooling) pulled before any application-visible change.
- Vertical-partitioned specific hot tables into their own databases rather than sharding everything, because isolating the two tables actually driving contention let the rest of the schema stay untouched.
- Only reached for horizontal partitioning (the most invasive option) once Postgres VACUUM performance and RDS max IOPS were structurally exceeded - i.e., once the bottleneck became one no bigger instance or replica could fix.
- Built DBProxy before sharding, not after - a routing layer is a prerequisite for horizontal partitioning to be transparent to the application, not an optimization added later.

## Reusable patterns
- **Scale in the cheapest-to-most-invasive order**: vertical scaling → connection pooling → vertical partitioning → horizontal partitioning. Skip straight to sharding only once the earlier rungs are provably exhausted (IOPS/VACUUM ceilings hit), not preemptively.
- **Routing layer before sharding**: introduce a proxy/router service ahead of horizontal partitioning so shard topology stays invisible to callers.
