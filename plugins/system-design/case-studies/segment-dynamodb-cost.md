# Segment's Million-Dollar AWS Cost Cut

**Domain:** infra cost optimization / DynamoDB throughput · **Source:** segment.com/blog/the-million-dollar-eng-problem (2016-era, via web.archive.org)

## Overview
Segment's AWS bill grew linearly with customer traffic (unlike typical SaaS margins), reaching two-thirds of COGS by Q3 2016. A 3-month, line-by-line cost audit ("project benjamin") cut annual AWS spend by over $1M, with three fixes accounting for 60% of the savings.

## Scale
DynamoDB hot shards fix: $300K/year saved · service auto-scaling: $60K/year · bin-packing/instance consolidation: $240K/year · remaining long tail: $400K/year · 647 partitions on the affected DynamoDB table · 100-200 containers packed per instance post-fix (up from a handful) · absorbed a 4x API volume increase with fewer instances than before.

## Architecture
- **DynamoDB** behind an ingestion pipeline of unpartitioned queues (NSQ at the time) feeding multiple consumer writers
- **AWS Detailed Billing** exported to S3, loaded into **Redshift** via Heroku's AWSBilling worker, for line-item cost analysis
- **ECS** for container orchestration with **Terraform**-managed infrastructure modules ("Clusters", "Services", "Workers") giving efficient-by-default primitives to every new service
- Migrated from classic **ELB** (one host-port per container, no bin-packing) to **ALB** (dynamic per-container ports, mesh routing) to allow dense container packing per instance

## Key decisions
- Treated DynamoDB's pricing model as partition-count-based, not throughput-based - provisioned capacity determines partition count (10GB/3000 RCU/1000 WCU per partition), so a handful of hot keys saturating one partition throttles the whole table even with "enough" total provisioned throughput; the fix was identifying and isolating hot keys, not just raising capacity.
- Diagnosed hot keys by logging every throttled key during induced throttling (temporarily lowering provisioned capacity) rather than guessing - DynamoDB's partition heatmap showed *which* partition was hot but not *which key*, so they built their own key-level instrumentation on top of it.
- Blocklisted a small set of bad keys (test traffic hard-coding literal `"user_id"` as the actual ID) instead of re-architecting the whole pipeline immediately - a cheap, targeted fix (4x capacity reduction) bought time for the real structural fix (moving ingestion to Kafka for proper upstream partitioning).
- Switched ELB→ALB specifically to unblock bin-packing (one port-per-container was the blocker to running multiple containers per host), then consolidated onto fewer, larger reserved instances (~40% cheaper) once density was possible - sequenced as "unblock the constraint, then exploit it."
- Encoded the fixes into reusable Terraform modules instead of relying on one-time manual cleanup, because untracked infra costs a rewrite every 6 months without a "narrow path" that's efficient by default.

## Reusable patterns
- **Diagnose hot-partition/hot-key problems by inducing and logging the failure**, not just reading the platform's own aggregate metrics - the heatmap Amazon provided was necessary but not sufficient; per-key instrumentation on top of it found the actual root cause.
- **Make the efficient path the only path**: bake cost/perf best practices into shared infra modules (Terraform, in this case) so new services inherit them for free instead of relying on tribal knowledge or periodic audits.
