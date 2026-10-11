# Airflow: Workflow Management Platform at Airbnb

**Domain:** batch job scheduling / data pipeline orchestration · **Source:** medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8

## Overview
Airbnb replaced a patchwork of cron jobs, vendor schedulers, and scripts-calling-scripts with Airflow, a platform for authoring, scheduling, and monitoring DAGs of interdependent batch jobs - later open-sourced and now the industry-standard workflow orchestrator.

## Scale
No throughput/job-count metrics published in the source; adoption spanned Airbnb's data warehousing, growth analytics, A/B testing, email targeting, sessionization, and search ranking metrics pipelines.

## Architecture
- **Job definitions as Python source**, checked into source control, not YAML/JSON config
- **Scheduler process** parses DAGs and fires task instances once their upstream dependencies are satisfied
- **Workers** execute task instances, pluggable via **Executors**: SequentialExecutor (single process), LocalExecutor (local parallelism), CeleryExecutor (distributed, backed by a Celery message queue)
- **Metadata repository** (MySQL/Postgres) tracks task/DAG run state
- **Web application** (Flask) for DAG visualization, run history, and manual triggering
- **CLI** for testing, backfilling, and describing DAGs
- **Hooks** abstract connections to external systems (databases, APIs) behind a centralized connection registry; **Operators** (action/transfer/sensor) subclass a common BaseOperator to define one unit of work

## Key decisions
- Pipelines as Python code instead of declarative config, because DAGs needed to be dynamically generated (e.g., one DAG per table-partition) and to reuse shared logic via imports/subclassing - something a static YAML file can't express.
- Pluggable executor abstraction (sequential → local → Celery) so the same DAG definitions scale from a laptop to a distributed worker fleet without being rewritten - the execution backend is swappable, the DAG isn't.
- Centralized Hooks/Operators layer instead of each pipeline hand-rolling its own connection logic, so credentials and retry/connection-pooling behavior live in one place per external system, not duplicated per DAG author.

## Reusable patterns
- **DAG-as-code**: express pipeline dependencies as a directed acyclic graph in a general-purpose language, not a config format, when pipelines need to be generated dynamically or share logic.
- **Swappable executor behind a stable scheduling API**: let the same orchestration layer target different execution backends (in-process, local workers, distributed queue) so scaling up doesn't require redesigning pipeline definitions.
