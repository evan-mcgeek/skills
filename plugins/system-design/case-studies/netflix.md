# How Netflix's Architecture Works

**Domain:** video streaming / microservices at scale · **Source:** bytebytego.com/guides (Netflix's Overall Architecture, 4 Ways Netflix Uses Caching, How Netflix Scales Push Messaging, Netflix Tech Stack - Databases)

## Overview
Global video streaming platform (220M+ users) built as hundreds of microservices spanning mobile/web clients, an API gateway layer, polyglot storage, and a dedicated CDN for video delivery.

## Scale
220M users across iOS, Android, smart TVs, Roku, FireStick, and web · EVCache running in production 10+ years · user attention span design target of ~90 seconds (drives caching latency budget).

## Architecture
- **Zuul** as API gateway/routing, **Eureka** for service discovery, **Spring Boot** for services
- **GraphQL** for client-to-server communication (replacing older REST layer)
- **EVCache** (Memcached-based distributed KV store) as the primary caching layer in front of Cassandra and backend services
- **Cassandra** as default wide-column store for video/actor metadata, user profiles, device info, viewing history
- **MySQL** for billing, subscriptions, tax, revenue; **CockroachDB** for multi-region active-active/distributed transactions
- **Kafka + Flink/Spark** for streaming and batch data processing; **Redshift/Druid** for analytics; **Atlas** (in-house) for time-series metrics
- **S3 + Open Connect** (Netflix's own CDN) for video storage/delivery
- **Push messaging**: event management engine routes clock/user/system-triggered events by priority into a processing cluster, persists payloads in Cassandra, then fans out via FCM (Android), APNs (Apple), and an in-house "Zuul Push" for web/TV/streaming devices
- **CI/CD**: Jenkins, Spinnaker, Gradle, Chaos Monkey, Atlas, PagerDuty

## Key decisions
- One cache (EVCache) serving four distinct roles - lookaside cache, transient session store, precomputed-homepage primary store, and high-volume read-mostly data (UI strings/translations) - instead of separate caching systems per use case, because all four share the same latency requirement (keep interaction under the ~90s attention span).
- Nightly batch precompute of personalized homepages written directly into EVCache, so the online path only ever does a cache read, never a live recommendation computation.
- Platform-native push delivery (FCM/APNs) instead of a single custom protocol for every device, because mobile OSes already provide the most reliable low-power delivery path - Netflix only builds its own (Zuul Push) where no native option exists (web/TV/streaming sticks).
- Database choice by workload shape, not one default: relational (MySQL/CockroachDB) for money and multi-region consistency, wide-column (Cassandra) for high-write denormalized metadata, columnar (Redshift/Druid) for analytics, time-series (Atlas) for metrics - avoids forcing incompatible access patterns onto one engine.

## Reusable patterns
- **Cache-as-precompute-sink**: run expensive personalization/ranking as an offline batch job and write results straight into the cache, so the serving path is a pure read with no compute in the request loop.
- **Platform-native fan-out for last-mile delivery**: delegate to OS-level push services per platform and only build custom delivery for platforms without one.
