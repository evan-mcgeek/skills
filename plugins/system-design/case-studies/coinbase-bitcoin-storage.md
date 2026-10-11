# How Coinbase Secures Bitcoin in Cloud Infrastructure

**Domain:** crypto custody / key management · **Source:** coinbase.com/blog (How Coinbase Builds Secure Infrastructure To Store Bitcoin In The Cloud)

## Overview
Coinbase custodies customer bitcoin private keys mostly offline, using secret-sharing and geographically distributed quorums so no single compromised location, device, or person can move funds.

## Scale
98%+ of customer bitcoin held in cold storage · disaster-recovery environment retains action logs for a 10-year minimum.

## Architecture
- **Cold storage (majority of funds)**: private keys generated offline, split via Shamir's Secret Sharing into N pieces with a threshold scheme (e.g. 2-of-3) so a subset reconstructs the key
- **Geographically distributed key holders**: shard custodians located in different regions; a signing ceremony protocol verifies holder identity and ceremony integrity before any reconstruction
- **Warm storage**: a smaller working balance signed by threshold keys, kept available for withdrawals processable within minutes
- **Institutional cold storage**: Hardware Security Modules (HSMs) generate and guard keys in tamper-resistant hardware for higher-assurance custody tiers
- **Immutable audit logging**: every action logged to a separate disaster-recovery environment, retained 10+ years

## Key decisions
- Split custody by liquidity need (cold vs. warm) instead of one storage tier for everything - the 98%+ that doesn't need same-day movement stays fully offline and unreachable by any online attacker; only the small operational balance is reachable, bounding blast radius of any breach.
- Threshold secret-sharing (2-of-3, etc.) instead of a single key or single-signer control - eliminates the single point of failure both for a leaked/stolen key and for one holder being unavailable or compromised.
- Geographic distribution of key-holders - a single physical breach (site compromise, coercion, disaster) can't recover a key alone since the ceremony requires holders assembling from separate locations.
- Immutable, long-retention logging as a distinct system from the signing infrastructure - a forensic trail that's provably untamperable is only useful if it isn't reachable by whoever might tamper with the signing path itself.

## Reusable patterns
- **Threshold secret-sharing for high-value secrets**: split a key/credential across N holders with a k-of-N reconstruction threshold, so no single compromised party is sufficient and no single unavailable party is a bottleneck.
- **Tier custody by liquidity/access-frequency**: keep the large majority of an asset in a tier that's structurally unreachable by online attackers, and only expose the minimum needed for operational velocity.
