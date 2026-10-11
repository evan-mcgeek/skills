# System Design Pattern Index

Shared reference for the system-design plugin's `create`, `analyze`, and `add-case-study` skills. All paths below are relative to the plugin root.

| Problem | Pattern | See |
|---|---|---|
| Real-time push delivery | Persistent WebSocket connections + heartbeat/timeout | [whatsapp](case-studies/whatsapp.md), [slack](case-studies/slack.md), [tinder](case-studies/tinder.md), [zoom](case-studies/zoom.md) |
| "Nearby X" / proximity queries | Hierarchical geospatial indexing (S2 / H3, hex or Hilbert-curve cells) | [tinder](case-studies/tinder.md) (S2), [uber-nearby-drivers](case-studies/uber-nearby-drivers.md) (H3) |
| Feed / timeline generation | Precompute+cache vs. write-to-owner-and-crawl vs. client-side virtualization | [reddit](case-studies/reddit.md), [bluesky](case-studies/bluesky.md), [twitter-timeline](case-studies/twitter-timeline.md) |
| Large file upload | Presigned URLs direct to blob storage, bypassing app servers | [youtube](case-studies/youtube.md), [spotify](case-studies/spotify.md) |
| Adaptive media delivery | Adaptive bitrate / layered (SVC) streaming, encode once serve many | [youtube](case-studies/youtube.md), [spotify](case-studies/spotify.md), [zoom](case-studies/zoom.md) |
| Payment / money correctness | Idempotency keys + append-only double-entry ledger + transactional outbox | [stripe-payments](case-studies/stripe-payments.md), [airbnb](case-studies/airbnb.md) |
| Collaborative editing / conflict resolution | Operational Transformation over an append-only operation log | [google-docs](case-studies/google-docs.md) |
| Multi-tenant DB resource isolation | Proxy-layer connection pooling + RTT-based congestion control | [cloudflare-postgres](case-studies/cloudflare-postgres.md) |
| Serverless / cold-start mitigation | Pre-warmed snapshots, pre-pushed images, backpressure-based throttling | [aws-lambda](case-studies/aws-lambda.md), [meta-serverless](case-studies/meta-serverless.md) |
| Global data placement | Region-local clusters + access-pattern-driven migration | [instagram](case-studies/instagram.md), [slack](case-studies/slack.md) (channel sharding) |
| Write/read decoupling under load | Async job queue on the write path + precomputed read cache | [reddit](case-studies/reddit.md), [whatsapp](case-studies/whatsapp.md) (ack/storage split) |
| Pagination at scale | Cursor-based (ID/timestamp) pagination over offset-limit | [slack](case-studies/slack.md), [bluesky](case-studies/bluesky.md), [youtube](case-studies/youtube.md), [twitter-timeline](case-studies/twitter-timeline.md) |
| Low-power / opportunistic networking | Public-key broadcast + crowdsourced relay, zero-knowledge server | [apple-airtags](case-studies/apple-airtags.md) |
| LLM inference serving | Token streaming + RAG grounding + stateless request design | [chatgpt-llm-serving](case-studies/chatgpt-llm-serving.md) |
| Polyglot storage by workload shape | Relational for money/consistency, wide-column for high-write metadata, columnar for analytics, in-house TSDB for metrics | [netflix](case-studies/netflix.md) |
| Database engine ceiling (GC pauses, compaction) | Swap to a wire-compatible engine (e.g. ScyllaDB) instead of tuning the old one further | [discord](case-studies/discord.md) |
| Single-DB scaling under runaway growth | Ordered escalation: vertical scale → connection pooling → vertical partition → horizontal partition + routing proxy | [figma-postgres-scaling](case-studies/figma-postgres-scaling.md) |
| CI pipeline silently slow at scale | Profile what the step actually transfers before architecting around it - often a one-line config fix (e.g. missing git refspec) | [pinterest-clone-time](case-studies/pinterest-clone-time.md) |
| Exabyte-scale immutable object storage, cost/durability tradeoff | Single soft-state coordinator per shard/cell + relational metadata + commodity spinning disks, avoid quorum protocols | [dropbox-magic-pocket](case-studies/dropbox-magic-pocket.md) |
| Runaway cloud infra cost under linear-scaling traffic | Line-item billing audit + partition/key-level hot-spot diagnosis before just raising provisioned throughput | [segment-dynamodb-cost](case-studies/segment-dynamodb-cost.md) |
| Zero-downtime rewrite of critical infrastructure | Shadow proxy + dual-execution diff on reads, offline integration tests on writes, before cutover | [uber-schemaless](case-studies/uber-schemaless.md) |
| DB connection sprawl from microservices | Centralized proxy gateway: connection multiplexing + SQL-aware read/write routing before sharding | [paypal-hera](case-studies/paypal-hera.md) |
| Single-tenant-DB monolith hitting VACUUM/TXID-wraparound limits | Shard by the dominant query boundary (tenant ID) + double-write/backfill/dark-read migration | [notion-sharding-postgres](case-studies/notion-sharding-postgres.md) |
| Cross-datacenter log/event replication at massive throughput | Per-DC local clusters mirrored once into aggregate clusters + independent audit-by-counting | [linkedin-kafka](case-studies/linkedin-kafka.md) |
| Hot key saturates a single cache host | Consistent hashing (Ketama) + selective "cache smearing" - bounded random entropy spreads reads/writes across N hosts | [etsy-caching](case-studies/etsy-caching.md) |
| Single-domain write pressure on a monolithic DB | Replica-promotion split: eliminate cross-joins, then promote a read replica to independent master, accepting brief downtime | [airbnb-database-partitioning](case-studies/airbnb-database-partitioning.md) |
| Polyglot workloads forced onto one storage system | Shared control-plane core (routing/replication/conflict-resolution) + pluggable per-workload storage engines | [twitter-manhattan](case-studies/twitter-manhattan.md) |
| High-value credential/key custody | Threshold secret-sharing (k-of-N) + liquidity-tiered cold/warm storage | [coinbase-bitcoin-storage](case-studies/coinbase-bitcoin-storage.md) |
| Duplicate events at ingest scale | Shard-scoped read-time dedup (flag at compaction, filter at query) instead of a dedicated ingest-time dedup store | [mixpanel-dedup](case-studies/mixpanel-dedup.md) |
| Replica read staleness under batch write load | Centralized lag-polling throttle service with voluntary HTTP check-before-write/read | [github-replication-lag](case-studies/github-replication-lag.md) |
| Ad hoc cron/script sprawl for interdependent batch jobs | DAG-as-code (Python) + pluggable executor abstraction (sequential/local/Celery) | [airbnb-airflow](case-studies/airbnb-airflow.md) |
| Atomic operations spanning independently-consistent shards | Modified 2PC: external transaction record + copy-on-write staging table, scoped only to the minority of cross-shard ops | [dropbox-cross-shard-transactions](case-studies/dropbox-cross-shard-transactions.md) |
| Cross-service visibility gap at 1000s of polyglot microservices | Sidecar push-based span emission + backend-driven sampling rate pushed to clients | [uber-distributed-tracing](case-studies/uber-distributed-tracing.md) |
| Automated primary-DB failover without split-brain or stale-client writes | Raft-consensus failure detection + Consul (not DNS) primary discovery + forced connection cutover | [github-mysql-ha](case-studies/github-mysql-ha.md) |
| Distributed coordination (locking, leader election, small config) at scale | Paxos-replicated lock service + session/lease-based ephemeral nodes + filesystem-style API | [google-chubby](case-studies/google-chubby.md) |
| Rate limiting across millions of tenants at billions of req/day | Approximate sliding-window counter (decay-weighted, O(1) memory) + async increments | [cloudflare-rate-limiting](case-studies/cloudflare-rate-limiting.md) |
| Enterprise search across siloed tenant data | Per-tenant index isolation for access control + two-stage retrieval → learned re-rank | [slack-search](case-studies/slack-search.md) |
| API overload from distinct failure modes (abuse, contention, fleet exhaustion) | Layer independent limiters per failure mode instead of one global limiter | [stripe-rate-limiters](case-studies/stripe-rate-limiters.md) |
| High-cardinality time-series metrics at massive ingest rate | Immutable-model TSDB + ingestion-time downsampling + lazy column-at-a-time query evaluation | [uber-m3-metrics](case-studies/uber-m3-metrics.md) |
| Graph-shaped read-heavy workload outgrowing generic KV caching | Graph-native object/association API + leader/follower cache tiers per region, read-your-own-writes consistency | [facebook-tao](case-studies/facebook-tao.md) |
| Cascading failure from slow/failing dependencies | Per-dependency thread-pool/semaphore bulkheads + circuit breaker + network-free fallback (Hystrix) | [netflix-fault-tolerance](case-studies/netflix-fault-tolerance.md) |
| Search spanning heterogeneous entity types + social-graph relevance | Denormalized documents grouped into sets queried via AND/OR/NOT set algebra, ranked per-query-type | [instagram-search](case-studies/instagram-search.md) |

## Case studies

47 case studies distilled from [systemdesign.one](https://newsletter.systemdesign.one), [bytebytego.com/guides](https://bytebytego.com/guides), and company engineering blogs (via [awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)), at `case-studies/`: whatsapp, youtube, instagram, instagram-search, stripe-payments, stripe-rate-limiters, google-docs, cloudflare-postgres, cloudflare-rate-limiting, meta-serverless, airbnb, airbnb-database-partitioning, airbnb-airflow, spotify, slack, slack-search, reddit, bluesky, tinder, twitter-timeline, twitter-manhattan, uber-nearby-drivers, uber-schemaless, uber-distributed-tracing, uber-m3-metrics, aws-lambda, zoom, apple-airtags, chatgpt-llm-serving, netflix, netflix-fault-tolerance, discord, figma-postgres-scaling, pinterest-clone-time, dropbox-magic-pocket, dropbox-cross-shard-transactions, segment-dynamodb-cost, paypal-hera, notion-sharding-postgres, linkedin-kafka, etsy-caching, coinbase-bitcoin-storage, mixpanel-dedup, github-replication-lag, github-mysql-ha, google-chubby, facebook-tao. Each file: overview, scale numbers, architecture components, key decisions + rationale, and reusable patterns.
