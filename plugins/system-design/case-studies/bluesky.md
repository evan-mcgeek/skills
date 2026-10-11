# How Bluesky Works

**Domain:** decentralized/federated social network · **Source:** newsletter.systemdesign.one/p/how-does-bluesky-work

## Overview
Built on AT Protocol: independent servers ("PDS") each own a slice of user data and federate over HTTP/WebSocket, similar in spirit to email federation - no single central database of all content.

## Scale
6M user repos on a single data server at ~$150/month · 50K+ custom feeds · video up to 90s.

## Architecture
- **Federated model**: independent Personal Data Servers (PDS) host user repositories, communicate via HTTP webhooks + WebSocket subscriptions
- **Per-user repository**: a SQLite DB of CBOR-encoded records - portable, like moving a git repo between hosts
- **Firehose/crawler**: subscribes to every PDS's real-time updates over WebSocket, producing one unified event stream
- **Index server** (Go + ScyllaDB): turns raw repo data into consumable feeds, caches results in Redis for read-heavy access
- **Moderation as labels**: metadata labels attached by a moderation service; visibility policy lives on the user's own data server (decentralized enforcement)
- **Roaring Bitmaps** compress follower sets, switching representation (bitmap/sorted array/RLE) by data density

## Key decisions
- **DIDs, not handles, as the identity primitive** - immutable IDs decouple identity from a mutable display name, so a handle change doesn't break post history.
- **Actions (likes/comments) live only in the actor's own repo**, never pushed to every follower - index servers aggregate by crawling instead of fanning out on write.
- Cursor-based pagination (timestamp as offset) instead of offset-limit, to avoid full scans.

## Reusable patterns
- **Roaring bitmap set intersection** is ~100x faster than naive set ops for social-graph overlap queries - applies anywhere you compute graph intersections at scale.
- **Write-to-owner-only + crawl-to-aggregate** avoids fanout-on-write entirely; trades write simplicity for read-side aggregation cost (contrast with Twitter's fanout-on-write).
