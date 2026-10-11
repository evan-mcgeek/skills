# How Etsy Caches: Consistent Hashing and Cache Smearing

**Domain:** caching / hot-key mitigation · **Source:** codeascraft.com/2017/11/30/how-etsy-caches (Etsy Engineering)

## Overview
Etsy caches database queries and expensive computations in Memcached, and internal HTTP responses in Varnish, routing keys to hosts via consistent hashing (Ketama) - with a targeted technique ("cache smearing") to fix the subset of keys popular enough to saturate a single cache host.

## Scale
Not disclosed in the source beyond qualitative framing: some keys are hit frequently enough, and store large enough values, that read traffic alone saturates one cache host's network interface - i.e. read demand for a single key exceeds what one machine can serve.

## Architecture
- **Memcached** for DB query results and computed values; **Varnish** for internal HTTP request caching
- **Consistent hashing (Ketama)** as the client-side routing algorithm: each key maps deterministically to one cache host, so adding/removing hosts only reshuffles a small fraction of keys
- **Cache smearing** for identified hot keys: append a small random integer (e.g. in `[0, 5)`) to the key on every read and write. Consistent hashing then spreads the resulting N key variants - all holding identical data - across N different hosts
- Applied at two layers: Memcached keys get the entropy appended directly to the key string; Varnish keys get it added as a query parameter

## Key decisions
- Kept plain consistent hashing as the default for all keys, and applied smearing only to the specific keys identified as hot - smearing trades cache-space efficiency (N copies of the same value) for read throughput, so it's only worth paying for where a single host's network/CPU is actually the bottleneck.
- Solved a hot-key problem at the client/key-naming layer instead of over-provisioning cache hosts or forcing all traffic through a single bigger machine - one key value multiplied across several hosts turns a single-host hotspot into a distributed one that scales with N.
- Used a small, bounded entropy range rather than fully randomizing placement, since the goal is spreading one key across a handful of hosts, not redistributing the whole keyspace.

## Reusable patterns
- **Cache smearing (fan-out replication of a single hot key)**: append bounded random entropy to a hot key's name on both read and write paths so a consistent-hash router spreads it across multiple hosts as identical copies - apply selectively, not globally, since it costs cache space proportional to the entropy range.
- **Consistent hashing as the default routing layer**, reserving special-case techniques (like smearing) for the specific keys that measurement shows need them, rather than redesigning the whole caching layer around the worst case.
