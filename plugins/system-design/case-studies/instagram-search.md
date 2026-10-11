# Instagram's Search Architecture

**Domain:** unified entity search / social-graph-aware ranking · **Source:** instagram-engineering.com/search-architecture-eeb34a936d3a

## Overview
Instagram's search moved from a purpose-built, database-driven lookup to Facebook's Unicorn - a social-graph-aware search engine - so a single query could span accounts, hashtags, places, and media while factoring in the viewer's follow graph.

## Scale
65% increase in search traffic and 12% more users searching per session after the redesign · millions of requests/sec · media index spans billions of posts indexed by trillions of likes · 20% increase in hashtag clicks after unifying ranking across entity types.

## Architecture
- **Slipstream**: Thrift-encoded event pipeline that enriches sparse database rows with contextual data as they're written
- **Firehose**: async pub/sub on Facebook's Scribe carrying those events to indexers - best-effort delivery, eventual consistency, tolerates data loss
- **Nightly batch reconciliation**: PostgreSQL snapshots scraped into Hive; periodic "base builds" reconstruct documents from Hive and merge against Slipstream deltas to correct any drift the streaming path missed
- **Unicorn** (adopted from Facebook): denormalized store of documents (users, hashtags, places, media) grouped into sets queried via AND/OR/NOT set operations; queries compile to S-expressions like `(and user:maxime (apply followed_by: followed_by:me))`
- **Two-step retrieval**: candidate generation via reverse index intersection, then ranking via feature lookup (visual - CNN image classifiers, face detection; metadata - captions/hashtags/location; author - verification, follower count)
- **Per-query-type ranking**: machine-learned models for Explore-style discovery, hand-tuned scoring functions for direct hashtag/location search
- **Unified cross-entity blending**: a classifier merges ranked results across accounts/hashtags/places into one result set, using per-country query-log aggregation to disambiguate intent

## Key decisions
- Adopted Unicorn instead of building a bespoke graph-aware search engine, because Facebook had already solved graph-relationship queries (e.g., "media from accounts I follow taken in New York") at a scale Instagram would eventually need - reuse over reinvention once the parent company had the infrastructure.
- Kept a streaming (Slipstream/Firehose) path for low-latency freshness but paired it with nightly batch reconciliation, accepting eventual consistency on the fast path because a periodic base-build sweep bounds how long any index drift can persist.
- Split ranking strategy by query type instead of one universal model - ML scoring where enough behavioral signal exists (Explore), hand-tuned functions where it doesn't (raw hashtag/location search) - rather than forcing a single ranking approach to fit both regimes.

## Reusable patterns
- **Enrich-at-write via async pipeline + periodic batch reconciliation**: stream contextual enrichment for freshness, then run a scheduled full rebuild from the source of truth to bound eventual-consistency drift, instead of trying to make the streaming path fully consistent.
- **Compile queries to set algebra**: model heterogeneous entity search as documents grouped into sets with AND/OR/NOT operators - lets one query language span accounts, hashtags, places, and graph relationships without per-entity-type query code.
