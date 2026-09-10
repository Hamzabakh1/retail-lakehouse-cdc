# Retail Lakehouse with CDC

Private portfolio project for production-style incremental data engineering.

## Outcome

Ingest sales, products, inventory and customers through batch and change-data-capture paths into Bronze, Silver and Gold layers.

## Deliverables

- Source contracts, incremental watermarking and CDC merge logic
- Raw immutable Bronze storage and quarantined invalid records
- Validated Silver entities and dimensional Gold marts
- Orchestration with retries, alerting, run audit and idempotency
- Cost and freshness observability dashboard
- Power BI sales, inventory and margin semantic model

## Architecture

`POS / ERP / CRM -> CDC + batch ingestion -> Bronze -> Silver -> Gold warehouse -> semantic model -> Power BI`

## Acceptance criteria

A source change is processed once, late events are handled deterministically, failed records are recoverable, and Gold reconciliation matches source totals.

## Build plan

1. Create synthetic retail sources and CDC event stream.
2. Implement Python ingestion and medallion transforms.
3. Add dbt-style tests and reconciliation checks.
4. Orchestrate with Azure Data Factory or Airflow.
5. Provision Azure resources with IaC and validate through CI.
