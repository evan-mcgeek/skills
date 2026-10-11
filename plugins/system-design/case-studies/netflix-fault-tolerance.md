# Netflix's Fault Tolerance in a High-Volume Distributed System (Hystrix)

**Domain:** resilience / cascading-failure prevention · **Source:** techblog.netflix.com/2012/02/fault-tolerance-in-high-volume (via github.com/Netflix/Hystrix/wiki)

## Overview
Netflix wraps every network-bound dependency call in a `HystrixCommand` that isolates it with timeouts, thread-pool or semaphore bulkheads, and a circuit breaker, so that one misbehaving downstream service can't cascade into an outage of the whole API tier.

## Scale
40+ thread pools with 5-20 threads each (most set to 10) across API instances · 10+ billion Hystrix command executions per day · ~350 threaded executions/sec/server · thread-pool overhead: ~0ms at median, ~3ms p90, ~9ms p99 · semaphore isolation sustains 5000+ rps with a pool of only 1-2.

## Architecture
- **HystrixCommand** wraps every remote call (network dependency, 3rd-party library); its `run()`/`construct()` is where the actual call happens
- **Thread-pool isolation (bulkhead)**: each dependency gets its own dedicated thread pool, so a saturated/slow dependency fills only its own pool, not the shared request-handling threads
- **Semaphore isolation**: a lighter-weight alternative that limits concurrency without a dedicated thread pool - no ability to time out and walk away from a stuck call, so used only for low-latency in-process calls
- **Circuit breaker**: three states - Closed (normal, tracking error rate) → Open (once error % and request volume both cross thresholds, short-circuits all calls immediately) → Half-Open (after a sleep window, lets one probe request through; success closes the circuit, failure reopens it)
- **Fallback**: runs on the calling thread (not the command's pool) whenever the command fails, times out, or is rejected by the bulkhead/circuit breaker; must be a network-free in-memory/static response, any further network call has to be its own separate HystrixCommand
- **Request cache**: deduplicates concurrent calls with identical cache keys within one request context, so N callers get one underlying execution
- **Request collapser**: batches many concurrent single-item calls (e.g. 300 simultaneous video-attribute lookups) into one batched backend call within a short window (~10ms), trading a small median latency increase for far fewer backend calls

## Key decisions
- Chose per-dependency thread pools over a single shared pool or semaphores-everywhere, because client libraries change constantly and are often opaque - a thread boundary is the only way to forcibly "walk away" from a call that won't respect its own timeout, since Hystrix can interrupt a thread but can't force a socket to close.
- Accepted a measured ~3-9ms tail-latency cost for thread isolation as a deliberate trade: bounded, well-understood overhead beats the unbounded blast radius of one dependency's latency spike consuming every request-handling thread in the service.
- Restricted fallbacks to network-free logic on purpose - a fallback that itself calls out over the network reintroduces the exact failure mode (cascading latency) the pattern exists to prevent, so any such call must be wrapped in its own isolated command.
- Circuit breaker requires both an error-rate threshold and a minimum request-volume threshold before tripping, avoiding false trips from a handful of failures during low traffic.

## Reusable patterns
- **Per-dependency bulkhead**: isolate each external dependency in its own concurrency-limited pool so failure/latency in one dependency can't starve resources needed by unrelated calls.
- **Fallback must be network-free**: a fallback path that makes its own remote call isn't a fallback, it's a second failure surface - keep fallbacks to in-memory/static data only.
- **Collapse-then-batch for read-heavy hotspots**: when many callers request the same class of small item concurrently, batch them into one backend round-trip inside a short time window instead of one call per caller.
