# Evolving Distributed Tracing at Uber (Jaeger)

**Domain:** observability / distributed tracing · **Source:** uber.com/blog/distributed-tracing

## Overview
As Uber's architecture exploded from a monolith to 2,000+ microservices, metrics and logs alone couldn't explain cross-service request behavior. Uber built Jaeger, a purpose-built distributed tracing system, after existing tooling (Zipkin, their own pull-based Merckx prototype) hit structural limits.

## Scale
500 microservices (fall 2015) → 2,000+ microservices (early 2017) · thousands of traces/sec by 2016 · hundreds of services instrumented · 4 primary languages (Node.js, Python, Go, Java) plus a proprietary RPC protocol (TChannel).

## Architecture
- **TChannel protocol** carries tracing fields (`spanid`, `parentid`, `traceid`, `traceflags`) natively in its binary spec - trace context propagation is a first-class protocol feature, not bolted on
- **Push architecture**: client libraries emit spans over UDP to a local **jaeger-agent** sidecar, which handles routing without coupling services to service-discovery
- **Backend-driven sampling**: collectors compute sampling rates from observed traffic and push the rate back down to clients, instead of each service guessing a fixed probabilistic rate in isolation
- **Storage evolution**: Riak/Solr prototype (didn't scale) → Cassandra with a Zipkin-compatible wire format (to reuse Zipkin's UI) → custom Go collectors + dedicated query service + React UI once the data model outgrew Zipkin's

## Key decisions
- Moved off the pull model (reading spans out of Kafka) because async frameworks like Tornado don't hold thread-local context across concurrent requests - pull couldn't represent async control flow, so the fix was architectural (switch to push), not a Kafka tuning problem.
- Built Jaeger instead of adopting Zipkin outright because Zipkin's gaps were structural, not superficial: no interoperable client libraries across languages, no TChannel transport support, and a tree-only data model that couldn't express the DAGs and key-value span logging OpenTracing needed.
- Made sampling rate a backend-computed, push-down value rather than a per-service config, because an individual service has no visibility into its aggregate impact on the tracing backend's total traffic.
- Kept the Zipkin-compatible storage format during the transition specifically to reuse its UI - decoupling the storage-format migration from the UI-rewrite so the two didn't have to ship together.

## Reusable patterns
- **Sidecar agent for cross-cutting infra concerns**: put span emission/routing in a local agent process instead of an in-process client SDK, so service code stays free of discovery/routing logic.
- **Backend-computed sampling, pushed to clients**: centralize the traffic-vs-cost tradeoff where the aggregate view exists, rather than asking each caller to self-throttle blind.
- **Interoperability-by-CI**: a cross-language conformance test suite (Uber's "crossdock") run on every PR catches wire-format drift across the many client libraries a polyglot tracing system requires.
