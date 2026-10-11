# How Airbnb Works

**Domain:** booking consistency at moderate write-scale · **Source:** newsletter.systemdesign.one/p/airbnb-system-design

## Overview
Hotel/room booking system where the core risk is double-booking. Read-heavy search traffic and write-light reservation traffic get deliberately different treatment - and the design explicitly rejects distributed-transaction machinery it doesn't need at this scale.

## Scale
1.1B room-nights/year, 550M bookings/year · ~17 booking TPS avg, ~1,000 read QPS (5:1 read:write) · ~4.3M rooms, 620M inventory rows, 500GB+ storage.

## Architecture
- **Service separation with shared transactional data**: Hotel/Rate/Reservation/Payment/Notification/Search are independent services, but inventory+reservation share one PostgreSQL DB to avoid distributed transactions on the booking path
- **Elasticsearch** for geospatial search/filtering; hotel metadata cached in **Redis**
- **Local ACID transactions** prevent double-booking - no saga, no 2PC
- **Idempotency keys**: frontend-generated unique ID per reservation attempt, dedupes retries
- **CDN** for static assets, Redis for hot pricing/availability
- **API gateway**: single entry point for auth, rate limiting, load balancing

## Key decisions
- Shared Postgres over per-service DBs for the inventory+reservation path: at 17 write TPS, distributed transactions add latency and failure modes with no proportional benefit - local ACID is simpler and safer.
- Rejected sagas (eventual consistency is dangerous for a booking) and 2PC (blocking, coordinator failure risk) - not justified at this traffic level.
- Services still split for independent scaling (Hotel/Search gets 10 instances, low-write Reservation gets 3).

## Reusable patterns
- **Read:write ratio analysis** should drive the caching/consistency strategy, not a default microservices-everywhere posture.
- **Don't reach for saga/2PC by default** - match consistency machinery to actual traffic and actual risk, not to what's fashionable.
- **Idempotency keys from the client** eliminate accidental duplicate writes under retry/concurrency.
