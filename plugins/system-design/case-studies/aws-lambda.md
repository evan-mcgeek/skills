# How AWS Lambda Works

**Domain:** multi-tenant compute isolation / cold starts · **Source:** newsletter.systemdesign.one/p/how-does-aws-lambda-work

## Overview
Serverless compute abstracting server provisioning by running tenant code in lightweight isolated microVMs across a distributed worker fleet, at 10 trillion requests/month.

## Scale
10 trillion requests/month · 99% of invocations are warm-start · cold-start latency cut ~90% via snapshotting.

## Architecture
- **Service decomposition**: Invoke service (routing) → Assignment service (worker allocation) → Placement service (worker lifecycle)
- **Firecracker microVMs**: lightweight virtualization, many isolated tenants multiplexed per physical EC2 host
- **Warm vs cold start**: reuse an existing microVM for sub-100ms invocation; new microVM creation is slower but is only 1% of traffic
- **Snapshot restoration**: pre-initialized microVM state restored from disk instead of bootstrapping code from scratch - this is *the* fix for cold starts
- **Lazy-loaded container images**: only the needed image chunks download on demand, shared layers optimized for bandwidth
- **Durable journal logging** of worker metadata for failover resilience
- **Health monitoring** drives placement/scaling decisions on worker fleet

## Key decisions
- MicroVMs over full VMs or bare containers: tenant isolation with much lower overhead - critical for the multi-tenant economics of serverless.
- Snapshots over cold bootstrapping: eliminated the #1 friction point for serverless adoption by delivering an already-running process, not code to initialize.
- Lazy image loading: most of a container image's bytes aren't needed to start handling requests.

## Reusable patterns
- **Lightweight-hypervisor multiplexing** (KVM-based, e.g. Firecracker) packs many isolated workloads per host cheaper than full VMs.
- **Process/state snapshotting for fast recovery** generalizes beyond serverless - applies to databases, caches, any app server with expensive cold init.
