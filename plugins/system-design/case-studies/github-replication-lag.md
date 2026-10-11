# How GitHub Mitigates Replication Lag with Freno

**Domain:** database replication / write throttling · **Source:** github.blog/2017-10-13-mitigating-replication-lag-and-reducing-read-load-with-freno

## Overview
GitHub's MySQL master-replica setup suffered stale reads whenever large batch writes (100K+ rows) pushed replication lag past target thresholds; throttling logic was duplicated ad hoc across Ruby, Perl, and Go codebases with no coordination. Freno centralizes lag monitoring into one HTTP-polled throttling service every app cooperates with voluntarily.

## Scale
Sub-second target replication lag · large batch jobs of 100,000+ rows · ~800 req/s initially hitting Freno's check endpoint, cut to ~50 req/s from the main app via a 20ms memcached TTL on client-side caching · ~30% of web/API reads shifted off the master, ~11% of indexing-job reads eliminated via delayed queuing · deferred jobs hit <600ms added latency 95% of the time.

## Architecture
- **Freno**: standalone service that asynchronously and continuously polls replica lag across clusters, independent of any app request path
- **HTTP check endpoint** (`GET /check/<app>/mysql/<cluster>`): returns 200 when safe to proceed, a throttle signal otherwise - apps poll this before writing/reading, they aren't proxied through it
- **Raft-based HA**: multiple Freno nodes agree on a single source of truth for lag state so a node failure doesn't blind the fleet
- **Cluster-name abstraction**: callers address a cluster, never an individual replica host, so topology changes don't require caller changes
- **Client-side cache** (20ms TTL via memcached) in front of the check call, to keep Freno's own request volume low under high-frequency callers

## Key decisions
- Polling replica lag continuously and out-of-band, instead of checking lag synchronously inside each request, so throttling decisions never add latency to the write/read path itself.
- Made cooperation voluntary (an HTTP check apps opt into) rather than an inline proxy - kept Freno decoupled from the data path, so it can fail closed/open independently without becoming a new single point of failure for every query.
- Centralized the throttling logic that had been duplicated per-language, because scattered logic meant no one could coordinate a global slowdown when one app's batch job threatened every other app's replicas.
- Added a short client-side cache TTL once check-call volume itself became a load problem - a 20ms cache is cheap because lag doesn't change meaningfully within tens of milliseconds, but it cut Freno's incoming rate by ~16x.

## Reusable patterns
- **Batch + checkpoint**: break large writes into small segments (50-100 rows) and re-check lag between segments, instead of running one giant transaction that can blow past the lag budget before anyone notices.
- **Lag-aware read routing**: compare "time since my write" against "current max replica lag" to decide master-vs-replica per read, rather than a fixed replica-read delay for everyone.
- **Deferred-write timestamping**: stamp async job payloads with their originating write time and hold execution until replicas catch up to that timestamp - turns a synchronous consistency wait into an async queue delay.
