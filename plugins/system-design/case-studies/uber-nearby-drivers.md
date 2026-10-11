# How Uber Finds Nearby Drivers

**Domain:** geospatial indexing at high QPS · **Source:** newsletter.systemdesign.one/p/how-does-uber-find-nearby-drivers

## Overview
Converts raw GPS into a hierarchical hexagonal grid (H3) to answer "who's nearby" at 1M requests/sec without scanning all drivers.

## Scale
1M req/sec for proximity queries · H3 supports 16 resolution levels down to ~1m² · 122 base cells globally (12 pentagons) · drivers report GPS every few seconds.

## Architecture
- **H3 geospatial index**: divides the globe into hex cells, each a 64-bit ID; hierarchical, 7:1 parent:child ratio
- **Hexagonal cells**: every neighbor is equidistant from center - no direction-dependent distance coefficients like squares/triangles need
- **Map matching**: raw noisy GPS snapped onto actual road segments for accuracy
- **Redis** buffers recent driver locations for fast reads + map-matching context
- **Cassandra** as the write-optimized backend for long-term location history
- **kRing function** finds neighboring cells efficiently for radius search; resolution changes via bitwise truncation of the cell ID

## Key decisions
- Hexagons over squares/triangles: uniform neighbor distance simplifies "nearby" math, no directional correction needed.
- Hierarchical resolution: dense urban areas get fine-grained cells, rural/sparse areas get coarse ones - storage cost matches actual data density.
- Redis in front of Cassandra: writes (constant GPS pings) go to the write-optimized store; reads (proximity queries) hit the cache, shielding Cassandra.
- H3 cell ID doubles as the partition key - deterministic, predictable data distribution across nodes.

## Reusable patterns
- **Hierarchical geospatial indexing (H3/S2)** turns O(n) proximity scanning into near-O(log n) lookups for any location-based service (see also Tinder's S2 case study - compare the two libraries' tradeoffs).
- **Write-optimized store + read cache split** generalizes to any high-throughput system with an asymmetric read/write pattern.
