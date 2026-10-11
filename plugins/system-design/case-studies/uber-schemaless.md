# Rewriting the Sharding Layer of Uber's Schemaless Datastore

**Domain:** zero-downtime infrastructure migration · **Source:** eng.uber.com/schemaless-rewrite (Frontless project)

## Overview
Uber rewrote the process-per-request Python sharding layer in front of its Schemaless datastore into a goroutine-based Go service ("Frontless") while the system stayed in production, validating correctness by running old and new code in parallel before cutting traffic over.

## Scale
40+ Schemaless instances, thousands of storage worker nodes (2016) · core trip-data datastore since Oct 2014 · after rewrite: 85% median latency reduction, 70% p99 reduction, 85%+ CPU utilization drop, enabling worker node consolidation across all instances.

## Architecture
- **Legacy layer**: Flask inside uWSGI, one OS process per in-flight request - concurrency scaled only by spawning more heavyweight Linux processes
- **Frontless (new)**: Go service using goroutines for lightweight per-request concurrency, replacing the process-per-request model
- **Migration proxy**: Frontless first deployed as a pure proxy forwarding every request to the legacy Python backend, so it could go live with zero behavior change
- **Per-endpoint cutover**: each read endpoint reimplemented in Go one at a time; both implementations executed for every read request, responses diffed for correctness before traffic fully moved
- **Writes**: single-execution only (can't dual-run mutations safely), instead validated via automated integration tests comparing both implementations offline

## Key decisions
- Proved the approach on one experimental high-traffic endpoint first (85% latency win) before committing to a full rewrite - de-risked the goroutine bet with real production data before the multi-endpoint migration.
- Went proxy-first rather than big-bang cutover: Frontless shipped to production forwarding 100% of traffic to the old system, so the new service's own stability was validated under real load before any business logic moved into it.
- Split validation strategy by request type: dual-execute-and-diff for idempotent reads (safe to run twice), but offline integration tests for writes (unsafe to run twice against a live datastore) - matched the validation technique to what's safe to execute twice.

## Reusable patterns
- **Shadow/dual-execution migration**: run old and new implementations side by side on real traffic, diff outputs, and only promote the new path once outputs match - turns a risky infrastructure rewrite into a series of low-risk, individually-verified endpoint swaps.
- **Match validation strategy to operation safety**: dual-execute in production only for reads/idempotent operations; fall back to offline replay/integration tests for anything with a side effect that can't run twice.
