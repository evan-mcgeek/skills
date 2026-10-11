# Running Kafka at Scale at LinkedIn

**Domain:** distributed messaging / log aggregation · **Source:** engineering.linkedin.com/kafka/running-kafka-scale

## Overview
LinkedIn built Kafka in-house and runs it as the backbone for four distinct message categories - queuing, metrics, logging, and user-activity tracking - each isolated into its own clusters, mirrored from per-datacenter local clusters into aggregate clusters.

## Scale
800B messages/day · 175+TB ingested/day, 650+TB consumed/day · peak 13M+ messages/sec (2.75GB/sec) · 1,100+ brokers across 60+ clusters.

## Architecture
- **Local clusters per datacenter** feeding **aggregate clusters** via **Kafka Mirror Maker**, so cross-datacenter data is copied exactly once per datacenter instead of once per consumer
- **Four cluster categories** kept separate rather than shared: queuing (inter-service messages), metrics, logging, tracking (search/revenue analytics) - isolates noisy-neighbor load per category
- **Per-topic retention policy** chosen from three modes: time-based, size-based, or key-based (compacted, latest-value-per-key)
- **Standardized producer/consumer libraries** (`TrackerProducer`, a schema-aware consumer library) wrapping raw Kafka clients to enforce headers, Avro schema registration/retrieval, and audit instrumentation
- **Kafka Audit system**: an independent counting pipeline that compares producer-side message counts against counts observed at each downstream tier, to prove end-to-end delivery completeness

## Key decisions
- Mirror once per datacenter into an aggregate cluster instead of letting every remote consumer pull directly from local clusters - collapses N-consumers-times-cross-DC-traffic into one mirrored copy per datacenter.
- Split clusters by message category instead of running one shared Kafka fleet, so a spike in tracking volume can't starve queuing or metrics traffic.
- Built an audit system as a separate counting pipeline rather than trusting producer/consumer ack codes alone - acks confirm a single hop succeeded, not that a message survived every tier between producer and final consumer.
- Centralized schema/audit concerns in shared client libraries instead of leaving each team to hand-roll Avro serialization and tracking - makes correctness (schema compatibility, audit coverage) a library guarantee, not a per-team convention.

## Reusable patterns
- **Mirror-once fan-out**: for cross-region replication, copy data once per destination region and let local consumers read from the regional copy, rather than replicating per-consumer.
- **Independent audit-by-counting**: verify end-to-end delivery by comparing message counts at each pipeline tier, since per-hop acks can't detect loss further downstream.
