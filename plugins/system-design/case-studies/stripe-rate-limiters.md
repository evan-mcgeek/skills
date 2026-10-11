# How Stripe Scales Its API with Rate Limiters

**Domain:** API resilience / traffic shedding · **Source:** stripe.com/blog/rate-limiters

## Overview
Stripe protects its API from abusive traffic, resource contention, and cascading overload with four independent, layered rate limiters - each catching a different failure mode the others miss.

## Scale
Request rate limiter: millions of requests/month rejected (mostly runaway test-mode scripts) · concurrent-requests limiter: ~12,000 rejections/month, eliminated CPU contention on expensive endpoints · worker-utilization shedder: ~100 rejections/month, but has prevented full outages · fleet load shedder reserves 20% capacity for critical requests (e.g. charge creation).

## Architecture
- **Request rate limiter** (primary layer): token bucket per user in Redis (self-managed or ElastiCache) - remove a token per request, refill continuously, reject when empty; tuned to allow short bursts above the steady-state cap for legitimate traffic spikes (e.g. flash sales)
- **Concurrent requests limiter**: caps simultaneous in-flight requests per user instead of requests/sec, targeting endpoints where clients retry while still waiting, compounding load on an already-strained backend
- **Fleet usage load shedder**: splits traffic into critical (e.g. charge creation) vs. non-critical (e.g. list charges) and reserves a fixed capacity percentage for critical traffic; non-critical requests get HTTP 503 once their share is exhausted
- **Worker utilization load shedder** (last resort, emergency-only): sheds traffic in priority order - test mode traffic first, then GET, then POST, then critical methods last - with gradual shed/recovery to avoid flapping

## Key decisions
- Four separate limiters instead of one global one, because each protects against a distinct failure mode: abusive per-user volume, per-endpoint resource contention, fleet-wide capacity exhaustion, and near-outage overload - a single limiter tuned for one case leaves the others exposed.
- Concurrency limiting instead of only rate limiting for expensive endpoints, because the failure mode there is retry amplification (clients re-requesting while still waiting), which a requests/sec cap doesn't address.
- Fail-open on limiter bugs or Redis failure - the rate limiter must never be the thing that takes the API down, so errors in the limiting path are caught and traffic passes through rather than being blocked.
- Dark-launch before enforcing: observe what traffic *would* be rejected, tune thresholds, and only then flip to active rejection, to avoid breaking real customer workflows on rollout.
- Rolled out in a fixed order - request limiter, then concurrency limiter, then load shedders - because each layer is only worth adding once the simpler layer above it stops being sufficient.

## Reusable patterns
- **Layer rate limiting by failure mode, not by a single global knob**: volume abuse, resource contention, and fleet-wide overload each need a purpose-built limiter; stacking them beats tuning one limiter to cover all three.
- **Gradual shed/recovery to avoid flapping**: when a load shedder trips, ramp its effect up and down smoothly rather than binary on/off, so recovery doesn't immediately re-trigger the same overload.
