# TAO: Facebook's Distributed Data Store for the Social Graph

**Domain:** graph data store / caching architecture · **Source:** usenix.org/system/files/conference/atc13/atc13-bronson.pdf, micahlerner.com/2021/10/13/tao-facebooks-distributed-data-store-for-the-social-graph

## Overview
TAO replaced Facebook's MySQL + look-aside Memcache stack with a purpose-built graph cache/store that models the social graph natively as objects and typed associations (edges), serving a read-dominated workload across thousands of machines worldwide.

## Scale
Billions of reads and millions of writes per second across the fleet · petabytes of data · thousands of machines · read:write ratio heavily skewed toward reads (Facebook's workload).

## Architecture
- **Data model**: objects (typed nodes, e.g. a user or a check-in) and associations (typed, timestamped edges between objects, e.g. "friend-of" or "checked-in-at") - a fixed, graph-shaped API instead of generic key-value gets/sets
- **Storage**: MySQL, sharded - each shard is one database server; one table for all object types, one table for all association types
- **Caching tier**: dedicated cache servers own a set of shards, LRU eviction, fill-on-demand; the cache tier - not the client - owns invalidation and query logic
- **Leader/follower cache tiers per region**: followers serve local reads and forward cache misses/writes up to a leader tier; the leader talks to the database and asynchronously propagates updates back down to followers
- **Multi-region**: one region's database is master, others are read replicas; a slave region's leader tier forwards writes to the master region's leader before updating its own local followers

## Key decisions
- Replaced generic key-value Memcache with a graph-native API (objects + associations) because Memcache's key-value model made association-list operations (fetch all of a user's friends, paginate by time) require expensive client-side fan-out instead of one query.
- Moved cache invalidation and access-control logic into the cache tier itself instead of the client, because look-aside caching left every client independently responsible for correct invalidation - a misbehaving or buggy client could corrupt cache state for everyone.
- Chose eventual consistency with read-after-write only within a region, not global strong consistency, because Facebook's workload tolerates a stale friend-count for a few hundred milliseconds globally but never tolerates a user failing to see their own just-made write - so the guarantee is scoped to exactly the case that matters.
- Leader/follower split per region (not full mesh) so read traffic never leaves the region while write consistency still funnels through one authoritative path (the master region's leader) - avoids cross-region write coordination on the hot path.

## Reusable patterns
- **Cache the shape of your queries, not just your keys**: when the dominant workload is "give me all edges of type X from node Y," model that as a first-class server-side API instead of layering it on generic KV gets, so the cache can serve it in one hop.
- **Scope your consistency guarantee to the actual user-visible requirement**: "read-your-own-writes" is far cheaper to provide than global strong consistency and covers the case users actually notice.
