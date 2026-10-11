# How Spotify Works

**Domain:** media streaming delivery · **Source:** newsletter.systemdesign.one/p/spotify-system-design

## Overview
Music streaming for 500K+ users across 30M songs, optimized for fast playback start, minimal rebuffering, and cheap storage at scale.

## Scale
90TB raw audio (2-3x with replication) · 3MB/song standard quality · 3-4MB/stream at 128-160kbps · 10-15 songs/user/day · formats: Ogg/AAC at 64/128/320kbps.

## Architecture
- **Stateless API layer**: JWT auth, circuit breakers against cascading failures, pooled DB connections
- **Blob storage** (S3-like), hierarchical layout, **signed URLs** that expire after hours
- **HTTP adaptive streaming** (HLS/DASH): automatic bitrate switching on network conditions
- **Client-side caching** of recently played tracks; retry logic for network blips
- **Load balancer** with 30s health checks, zero-downtime instance rotation
- **Async analytics pipeline**: play events tracked via separate POST path, off the playback hot path

## Key decisions
- Signed, time-limited URLs instead of direct storage credentials - bounds exposure without adding an auth round-trip per chunk.
- Metadata queries and audio bytes are fully separate paths: clients stream audio straight from blob storage, so API servers never become a streaming bottleneck.
- Adaptive bitrate over fixed quality - trades quality for zero rebuffering under variable bandwidth.

## Reusable patterns
- **Signed URL pattern** for any time-limited resource access: downloads, file sharing, temp credentials.
- **Health-check-based LB rotation** for any service needing zero-downtime deploys without manual intervention.
