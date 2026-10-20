# M4 test SQL (run on the maintainer's local stand)

Prepared by the cloud sessions; M4 itself runs locally (PLAN.md §5, M4). Names below assume the bench catalogs
`flight` (this connector) and `jdbc` (the existing JDBC catalog on the same server) and the TPC-H schema `tpch`;
adjust if the bench uses other names. Every query result must equal the JDBC catalog result (or the truth
checksums of the bench). No credentials in this file: put the token in the catalog statement on the stand only.

```sql
CREATE EXTERNAL CATALOG flight PROPERTIES (
  "type" = "flight",
  "flight.uri" = "grpc://<host>:<port>",      -- grpc+tls://… for the TLS run
  "flight.token" = "<token>"
);
SHOW CREATE CATALOG flight;                    -- token masked
SHOW DATABASES FROM flight;
SHOW TABLES FROM flight.tpch;
DESC flight.tpch.lineitem;
```

## 1. Projection, filters, LIMIT (EXPLAIN shows `REMOTE SQL:`)

| # | Query | Expected `REMOTE SQL` |
|---|---|---|
| 1.1 | `SELECT l_orderkey, l_quantity FROM flight.tpch.lineitem WHERE l_shipdate >= DATE '1998-09-01' AND l_returnflag = 'R'` | `SELECT "l_orderkey", "l_quantity", … FROM "tpch"."lineitem" WHERE (…>= DATE '1998-09-01') AND (… = 'R')` |
| 1.2 | `SELECT * FROM flight.tpch.nation LIMIT 5` | `… FROM "tpch"."nation" LIMIT 5` |
| 1.3 | `SELECT * FROM flight.tpch.nation WHERE n_name LIKE 'A%' LIMIT 3` | `WHERE ("n_name" LIKE 'A%') LIMIT 3` |
| 1.4 | `SELECT count(*) FROM flight.tpch.customer WHERE c_comment LIKE '%a\\_b%'` | no WHERE for the backslash pattern, no LIMIT; result still correct (BE re-check) |
| 1.5 | `SET flight_filter_pushdown = false;` then 1.1 | no WHERE in `REMOTE SQL`; same result |

## 2. Aggregation pushdown (`FlightAggregationPushdownRule`)

| # | Query | Expected |
|---|---|---|
| 2.1 | `SELECT count(*) FROM flight.tpch.lineitem` | `REMOTE SQL: SELECT count(*) AS "__flight_agg_0" FROM "tpch"."lineitem"`; result = JDBC; time well under 1 s |
| 2.2 | `SELECT count(*) FROM flight.tpch.lineitem WHERE l_quantity > 45` | same with `WHERE ("l_quantity" > 45)` (decimal literal as plain number) |
| 2.3 | `SELECT l_returnflag, l_linestatus, sum(l_quantity), min(l_shipdate), max(l_discount), count(*) FROM flight.tpch.lineitem GROUP BY 1, 2 ORDER BY 1, 2` | `SELECT "l_returnflag", "l_linestatus", CAST(sum("l_quantity") AS DECIMAL(38,2)) AS "__flight_agg_0", min("l_shipdate") …, count(*) … GROUP BY "l_returnflag", "l_linestatus"` |
| 2.4 | `SELECT DISTINCT n_regionkey FROM flight.tpch.nation` | `SELECT "n_regionkey" FROM … GROUP BY "n_regionkey"` |
| 2.5 | `SELECT avg(l_quantity) FROM flight.tpch.lineitem` | not pushed (avg): plain scan of `l_quantity` |
| 2.6 | `SELECT count(DISTINCT l_suppkey) FROM flight.tpch.lineitem` | not pushed |
| 2.7 | `SELECT o_orderpriority, count(*) FROM flight.tpch.orders WHERE o_comment LIKE '%a\\_b%' GROUP BY 1` | not pushed (a conjunct cannot be rendered) |
| 2.8 | `SELECT count(*) FROM flight.tpch.nation WHERE n_nationkey < 0` | 0 (not NULL) |
| 2.9 | `SELECT l_returnflag, count(*) c FROM flight.tpch.lineitem GROUP BY 1 HAVING count(*) > 1000` | pushed; HAVING applied after the merge; result = JDBC |
| 2.10 | `SET flight_aggregate_pushdown = false;` then 2.3 | plain scan; same result |
| 2.11 | `ALTER CATALOG flight SET ("flight.pushdown.aggregate" = "false")` (or a second catalog) then 2.3 | plain scan |

Also compare 2.1–2.4 and 2.9 in both `flight.result_mode` = `partial` (several endpoints: partial groups merged
by StarRocks) and `complete`.

## 3. TPC-H SF10

All 22 queries against `flight.tpch` with `cbo_push_down_topn_limit` at its default and at 0; checksums against
the truth and the JDBC catalog; record timings Flight vs JDBC vs Trino plugin (PLAN.md §5 M4).
