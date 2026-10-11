# How Google's Chubby Lock Service Works

**Domain:** distributed coordination · **Source:** blog.acolyer.org summary of "The Chubby Lock Service for Loosely-Coupled Distributed Systems" (Google, OSDI 2006)

## Overview
A coarse-grained distributed lock service that gives loosely-coupled systems primary election, name service, and small shared-config storage over a familiar filesystem-like API, instead of every team building ad-hoc consensus.

## Scale
Tens of thousands of client processes per Chubby instance · motivating load case: jobs with thousands of processes doing quadratic DNS lookups demanded ~150K lookups/sec against 60-second TTL DNS, which Chubby's explicit-invalidation caching was built to replace.

## Architecture
- **5-replica cell** per instance, using **Paxos** to elect and maintain a master
- **Filesystem-style namespace**: hierarchical files/directories double as lock handles and small data blobs
- **Sessions + leases**: clients hold a session with the master; ephemeral files auto-delete when the session closes, giving free failure detection
- **Client-side caching** of file data and lock state, kept consistent via master-driven invalidation rather than push-update
- **Grace period on master failover**: lease timers pause during re-election so client sessions survive a brief master outage instead of expiring

## Key decisions
- Coarse-grained locks instead of fine-grained: a lock held for hours/days puts far less request load on the lock service than one acquired per-operation, so a modest 5-node Paxos cell can serve tens of thousands of clients - fine-grained locking at that load would have required scaling the lock service itself.
- Exposed as a filesystem API with advisory (not mandatory) locks, because engineers already understood files and mutexes - adoption mattered more than exposing "correct" distributed semantics, even though it meant some clients would misuse locks in ways a purpose-built API might have prevented.
- Ran Paxos inside a dedicated service rather than as a client-linked library: consensus needs a quorum of independently-failing replicas, which a per-process embedded library can't provide - so coordination was centralized into a service other systems call into.
- Cache-invalidate-on-change instead of cache-update-on-change: avoids flooding all cache holders with every write, at the cost of a round-trip on next read - the right trade-off when writes are rare relative to reads (the assumption coarse-grained locking implies).

## Reusable patterns
- **Session + ephemeral-node liveness**: tie a lock/registration's lifetime to a heartbeated session rather than an explicit unlock call, so a crashed client's locks release automatically without a separate failure-detection mechanism.
- **Coarse-grained-by-design load shedding**: when a shared coordination service must serve many clients cheaply, deliberately push clients toward infrequent, long-held operations (locks, leader election) instead of accommodating fine-grained high-frequency ones.
