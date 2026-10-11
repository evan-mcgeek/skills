# PayPal's Hera: Scaling Database Access to 100s of Billions of Queries/Day

**Domain:** database connection gateway · **Source:** medium.com/paypal-engineering (Scaling Database Access for 100s of Billions of Queries per Day: PayPal Introducing Hera)

## Overview
Hera is PayPal's proxy layer between microservices and Oracle databases, evolved since the late 1990s from a simple connection pooler into a query-aware multiplexing router that shields databases from application-tier connection sprawl.

## Scale
Hundreds of billions of SQL queries/day · tens of thousands of applications · thousands of database instances · hundreds of Hera pools · major architecture revisions in 2011, 2012, 2013, 2015.

## Architecture
- **Client library** embedded in each application host, thin by design, talks to the proxy
- **Centralized proxy service** with Router, Parser, and Query Rewriting modules - does the real work of connection multiplexing and SQL-aware routing
- **Worker processes** hold the actual DB connections and speak to the database on the proxy's behalf
- **Surge queue** (CoDel algorithm) backlogs requests under saturation instead of failing immediately; **Bouncer** hard-rejects once queue and connections are both exhausted
- **Transparent failover** reroutes read traffic away from failed replicas automatically

## Key decisions
- Multiplexing (2012): collapsed many idle, per-app pooled connections into a small number of active DB connections - microservices adoption multiplied the number of independent connection pools hitting the same databases, so the fix had to happen at the gateway, not per service.
- Read/write splitting (2013) by parsing SQL rather than requiring app-side annotation, to cut Oracle RAC inter-node chatter caused by write traffic without pushing routing logic into every client.
- Sharding (2015) added only once shared-storage RAC scaling hit its ceiling - horizontal partitioning was the last resort after pooling, multiplexing, and read/write splitting had each been exhausted.
- Kept the client library thin and put routing/parsing/protection intelligence in the centralized proxy, so protective features (surge queue, bouncer, failover) ship once in the gateway instead of being reimplemented per language/client.

## Reusable patterns
- **Multiplex before you shard**: when connection count, not query volume, is the bottleneck, collapsing many idle app-side connections into few active DB-side ones buys years before sharding is needed.
- **Centralize intelligence at the gateway, keep clients thin**: routing, parsing, and backpressure logic belongs in one shared proxy layer so it protects every caller uniformly and evolves without touching client code.
- **Bidirectional protection**: a data-access gateway should shield the database from application traffic spikes (surge queue/bouncer) *and* shield applications from database failures (transparent failover) - not just one direction.
