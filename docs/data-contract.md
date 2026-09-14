# Sales-change contract

| Field | Type | Rule |
| --- | --- | --- |
| `event_id` | string | Unique immutable change identifier. |
| `occurred_at` | ISO-8601 timestamp | Business timestamp in UTC. |
| `operation` | string | Currently `upsert`. |
| `store_id` | string | Non-empty source-store identifier. |
| `sale_amount` | decimal | Strictly greater than zero. |

Bad records are routed to quarantine with a stable reason code. Replays must use the original `event_id` to maintain idempotency.
