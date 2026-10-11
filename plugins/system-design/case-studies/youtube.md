# How YouTube Works

**Domain:** video upload/streaming at scale · **Source:** newsletter.systemdesign.one/p/youtube-system-design

## Overview
Video platform processing 500+ hours of uploads/minute, transcoding raw uploads into dozens of formats for adaptive playback across devices.

## Scale
1M uploads/day · 100M DAU · 100:1 read:write ratio · max 256GB file size · target <500ms first-frame latency.

## Architecture
- **Pre-signed URLs**: client uploads directly to blob storage (S3-like), bypassing app servers entirely
- **Multipart chunking**: resumable uploads, chunk-level retry for huge files
- **Async transcoding pipeline**: fans out to 6+ resolutions × hundreds of segments without blocking the uploader
- **Adaptive Bitrate Streaming (ABR)**: manifest files (HLS/DASH-style) let clients switch quality by network condition
- **CDN** serves segments/manifests globally
- **DynamoDB** for high-write watch-progress tracking
- **Cursor-based pagination** for search/browse at high cardinality

## Key decisions
- App servers handle only metadata; blob storage + CDN carry the actual bytes - keeps app tier stateless and cheap to scale.
- Eventual consistency for new uploads (10-30 min processing lag is acceptable) buys availability under CAP pressure.
- Watch-progress writes are fire-and-forget: throughput over immediate confirmation.

## Reusable patterns
- **Presigned URL upload**: any large-file service should let clients write directly to blob storage instead of proxying bytes through app servers.
- **Manifest-based adaptive streaming**: separates metadata delivery from bulk data transfer, letting each scale independently.
