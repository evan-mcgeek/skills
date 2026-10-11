# Dropbox's Magic Pocket: In-House Exabyte Storage

**Domain:** object/block storage · **Source:** dropbox.tech/infrastructure/inside-the-magic-pocket

## Overview
Dropbox's proprietary immutable block storage system for file content, replacing S3, storing encrypted 4MB chunks that are never modified after write - mutability is handled by a separate FileJournal layer above it.

## Scale
Multi-exabyte capacity, grew from double-digit petabytes to exabyte scale in ~6 months · 4MB blocks aggregated into 1GB buckets · cells ~50PB raw each (capped by single-master coordination) · OSDs >1PB/machine, >8PB/rack · cross-zone replication within 1 second of upload · repair triggers after 15 min OSD downtime.

## Architecture
- **Frontends**: accept storage requests, decide placement, issue reads/writes
- **Block Index**: sharded MySQL mapping hash → cell/bucket/checksum, behind an RPC layer
- **Cells**: independent ~50PB clusters spread across racks for physical diversity
  - **OSDs**: "dumb" storage nodes doing caching/scheduling/validation only - no distributed protocol participation
  - **Replication Table** (MySQL): maps buckets → volumes/OSDs, tracks open/closed state + generation numbers
  - **Master**: single soft-state coordinator per cell - watches OSD health, triggers repair, creates/merges buckets, drives garbage collection
  - **Volume Managers**: execute Master commands (move volumes, erasure-code cold data)
- **Cross-zone replication daemon**: async-replicates writes across ≥2 of the western/central/eastern US zones

## Key decisions
- Single Master per cell instead of a distributed consensus protocol - centralizes complex placement decisions without quorum-protocol complexity; the cost is a ~100PB cap per cell, accepted because cells scale horizontally instead.
- MySQL for the Block Index and Replication Table rather than a newer KV store - reliable, expressive data model, and Dropbox already had deep MySQL operational expertise; no need to adopt something new just because it's trendier.
- Spinning disks, not SSDs, for bulk storage - SSDs reserved for databases/caches where latency matters; cold block storage optimizes for cost/density instead.
- Retry-based access with careful timeout tuning instead of a quorum protocol - quorum gives lower tail latency at the cost of much greater complexity; Dropbox judged the complexity not worth it for this workload.
- Open/closed volume lifecycle - closing a volume before repair/garbage-collection touches it means live traffic and background maintenance never interleave, which keeps the consistency protocol simple.
- Immutable blocks with mutation pushed to FileJournal - keeps the storage layer's contract trivial (write-once, read-many) and moves all versioning/mutation complexity to a layer designed for it.

## Reusable patterns
- **Soft-state coordinator**: the Master holds no persistent state itself - all authoritative data lives in the Replication Table - so it can restart freely without a recovery protocol.
- **Staged durability by data temperature**: high replication for hot/recent data, erasure coding for cold data, instead of one durability scheme for everything.
- **Spread-thin repair**: place thousands of volumes per OSD across hundreds of peer machines so a failure's reconstruction traffic fans out across hundreds of network links/disks instead of hammering a few.
