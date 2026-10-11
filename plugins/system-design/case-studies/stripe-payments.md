# How Stripe Payment Integration Works

**Domain:** payments / financial correctness · **Source:** newsletter.systemdesign.one/p/design-a-payment-system

## Overview
A payment backend integrating a PSP (Stripe) across authorize/capture/settle phases. The hard problem isn't throughput, it's correctness under partial failure - never double-charge, never lose track of money mid-transaction. Consistency is prioritized over availability; SQL/ACID is the backbone.

## Scale
~100K payments/day → 500K-1M webhook events/day · Stripe limits: 100 req/s/account, 25 req/s/endpoint · target <5s end-to-end, <100ms internal · 99.999% uptime target.

## Architecture
- **Payment API**: validates idempotency key, creates PaymentIntent, returns client secret immediately - no blocking on downstream work
- **PSP integration layer**: adapter isolating Stripe-specific calls, error mapping, idempotency keys on every POST, timeout handling
- **Payment DB**: mutable current-state table + append-only audit log, updated atomically in one transaction
- **Webhook receiver**: verifies HMAC-SHA256 signature, stores raw event, returns 200 fast; all real logic deferred to async workers
- **Queue** (Kafka/SQS): at-least-once delivery; transactional outbox decouples DB write from queue publish
- **Background workers**: webhook processing, PSP retries with exponential backoff, daily reconciliation, stuck-payment detection
- **Double-entry ledger**: every money movement as balanced debit/credit pairs; corrections are new reversing entries, never edits

## Key decisions
- Idempotency keys at every hop (client→backend, backend→PSP, webhook processing) turn "at-least-once delivery" into effectively-exactly-once processing.
- Sync API path only queues work; async workers do the slow/PSP-dependent part - customer requests never wait on PSP latency.
- Audit log is append-only and immutable - current-state table is a derived read optimization, not the source of truth.

## Reusable patterns
- **Transactional outbox**: write state change + queue message in the same DB transaction, relay async - prevents lost events on crash-between-steps.
- **State machine enforced at the DB layer**: valid transitions as constraints, webhooks trigger the state machine rather than writing state directly.
