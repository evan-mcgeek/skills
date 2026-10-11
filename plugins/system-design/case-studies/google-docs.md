# How Google Docs Works

**Domain:** real-time collaborative editing · **Source:** newsletter.systemdesign.one/p/how-does-google-docs-work

## Overview
Real-time collaborative editing via Operational Transformation (OT): documents are revision logs of discrete operations, not a single locked file, so concurrent edits merge without a central lock.

## Scale
Cross-Earth network round-trip: ~200ms - the constraint the whole design compensates for.

## Architecture
- **OT algorithm**: shows changes without waiting on high-latency round-trips; transforms concurrent operations so they converge to the same end state
- **Local document copy** per client: edits apply instantly locally (latency hiding), then propagate
- **Revision log model**: document state = replay of an operation event log, not a stored final blob
- **Event-based sync**: only operation deltas travel over the network, not full snapshots
- **Optimistic concurrency**: multiple clients write simultaneously; conflicts resolved algorithmically, not via lock queues
- **Offline tolerance**: local ops queue until reconnect

## Key decisions
- Rejected pessimistic locking (single writer) - kills real-time collaboration and offline editing.
- Rejected last-write-wins - silently drops concurrent edits under latency.
- Rejected raw diff-sync - diffing complicates conflict resolution and costs more compute than operation-based replication.
- Chose OT: local execution for responsiveness, algorithmic convergence for consistency, no user-facing conflict UI.

## Reusable patterns
- **Latency hiding**: keep a local state copy, execute immediately, propagate async - applies to any collaborative or high-latency-network system.
- **Operation-based replication**: model changes as an immutable append-only event log rather than mutating shared state; enables deterministic replay and conflict resolution.
