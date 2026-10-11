# How WhatsApp Works

**Domain:** real-time messaging · **Source:** newsletter.systemdesign.one/p/whatsapp-system-design

## Overview
Real-time chat for 2B+ users exchanging messages over unreliable mobile networks, with guaranteed delivery, offline queuing, and multi-device sync.

## Scale
500M DAU · 50M concurrent connections at peak · 350-500K msgs/sec peak · ~10B msgs/day · 400-500TB active storage (30-day retention).

## Architecture
- **WebSockets** for persistent bidirectional client connections (replaces polling overhead)
- **Chat servers** hold connections, route messages, track online status
- **Kafka/RabbitMQ** decouples message-received ack from async storage write
- **Cassandra** for high-throughput message storage, queried by user/conversation/timestamp
- **Redis** as connection registry: which user is on which server, presence with sub-second lookup
- **Consul** for service discovery - ephemeral chat servers register/deregister with health checks

## Key decisions
- WebSockets over polling: eliminates repeated handshake/bandwidth waste of "any new messages?" requests.
- Ack/storage separation via queue: sender gets instant feedback while persistence happens async, so storage never blocks responsiveness.
- Service discovery over static config: servers scale/crash without manual reconfiguration.

## Reusable patterns
- **Heartbeat + timeout**: client pings every 30s, server closes after 60s silence - kills zombie connections cheaply.
- **Hot/cold storage split**: Redis for latency-critical presence, Cassandra for durable history.
