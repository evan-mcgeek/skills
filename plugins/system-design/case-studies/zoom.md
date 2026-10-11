# How Zoom Works

**Domain:** real-time video routing · **Source:** newsletter.systemdesign.one/p/zoom-architecture

## Overview
Handles 300M calls/day by pushing encode/decode/mixing work to clients and keeping servers focused purely on routing, not media processing.

## Scale
300M video calls/day, designed around unreliable mobile networks.

## Architecture
- **Scalable Video Coding (SVC)**: one hierarchical layered stream encoded once; each client decodes only the layers it needs - no per-device re-encoding
- **Client-side processing**: frame encode/decode/composition happens on the client; servers just move bytes
- **No server-side mixing**: every participant's stream stays independent; the receiving client composes the grid itself
- **Custom multimedia routers** optimize network paths between participants for low latency
- **Peer-to-peer for 1:1 calls**: bypasses servers entirely when there are only two participants
- **Client-side QoS monitoring**: measures packet loss/latency, adjusts stream via proprietary algorithm
- **UDP primary, TCP/HTTPS fallback** for resilience across network conditions
- **Meeting zones + zone controllers**: organizational grouping of servers per meeting

## Key decisions
- SVC over multiple parallel encodings: avoids the transcoding cost of serving every resolution/device combo from a re-encoded stream.
- No server-side mixing: composing video is cheap on a modern client and expensive at server scale - push it to the edge.
- P2P for the most common case (1:1 calls) removes server load and latency for the majority of traffic.

## Reusable patterns
- **Hierarchical/layered streaming**: encode once, let each client pick its own quality tier - applies to any adaptive media system, not just video calls.
- **Offload processing to clients when they have the headroom**: this is the general form of "don't do on the server what the client can do for free."
