# Architecture and operating model

## Data flow

1. CDC and batch records land unchanged in Bronze.
2. The pipeline removes replayed event IDs and validates the remaining records.
3. Invalid records are retained in quarantine, preserving evidence for correction and replay.
4. Valid records form the Silver sales entity; Gold aggregates it by business date and store.
5. A run audit captures row counts, watermark and reconciliation status.

## Operational controls

- Use an orchestration retry only after checking the last successful watermark.
- Alert when quarantine rate exceeds an agreed threshold.
- Reconcile Gold revenue to Silver revenue on every run.
- Keep Bronze immutable and restrict write access to ingestion identities.
