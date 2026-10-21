# M4 results (CI)

Full per-item output of every run: branch `m4-results` (`runs/<run>.md`, `latest.md`), artifact `m4-<run>` (with
all logs, 7 days). This file keeps the summary per run. Workflow and checks: `docs/M4-CI.md` §4, §7.

## 2026-10-21, run 39658484728 — series `4a9848e-fl80f999` (first run), checks 1–5

| # | Result | Failures |
|---|---|---|
| 1 | 13/15 | `c_ubigint` shown as DECIMAL(20,0) (harness expected LARGEINT; the server itself reports decimal128(20,0)) |
| 2 | 37/49 | UInt64 values wrapped negative; pre-1970 timestamps with a fraction garbage (`Y222-05-09 N5:25:11…`, BE converter); harness: float32, UUID, non-ASCII JSON normalisation |
| 3 | 19/21 | 2.3 in result mode partial: server rejects `CAST(sum(..)) AS alias` (Binder Error); 2.5 harness rounding |
| 4 | 32/44 | q06/q15/q18/q20 same `CAST(sum)` error; q22 `substring(x FROM a FOR b)` not StarRocks syntax (harness rewrite); q01 harness rounding |
| 5 | 22/26 | same `CAST(sum)` error (3); harness rounding (1) |
| log masking | PASS | |

Fixes: 0004 renders `sum(CAST(x AS T))` (integer sums only in result mode complete), 0003 floors Arrow timestamps
(upstream converter), harness normalisation. New series `4a9848e-fla2cd40` (FE 39660196425 with the 7 Flight test
classes, BE 39660201177, be-ut 39660205090 19/19).

## 2026-10-21, run 39661743301 — series `4a9848e-fla2cd40`, checks 1–9

| # | Check | Result |
|---|---|---|
| 1 | catalog, SHOW, DESC, masking | 13/15: only the `c_ubigint` type expectation (harness now accepts DECIMAL(20,0)) |
| 2 | types tables, every column | 45/49: UInt64 values wrapped (open), `c_ts_ns` −1 ns: BE floors to …59.999999, DuckDB's Python conversion truncates (harness now floors) |
| 3 | M4-TESTS §1–2, both result modes, session switches, catalog switch | **PASS 21/21** |
| 4 | TPC-H SF1 q01–q22, topn default and 0 | **PASS 44/44** (0.4–3.1 s per query on the shared runner) |
| 5 | sr-cases (26) on SF1 | **PASS 26/26** |
| 6 | failover | aborted: cluster servers were started one after another, each waits 60 s for the other (harness fixed) |
| 7 | KILL QUERY | **PASS**: query ended within 2 s of KILL, server log shows `backpressure=cancelled` |
| 8 | token / basic / TLS | **PASS 10/10** (right/wrong/missing token, basic user:token, password masked, TLS trusted / wrong host / untrusted / verify=false / plain vs TLS) |
| 9 | memory limit | **PASS 3/3**: clean memory-limit error, BE alive, next query works |
| log masking | dummy catalog token and server token in no log | **PASS** |

## 2026-10-21, run 39663221891 — series `4a9848e-fla2cd40`, checks 1, 2, 6

1 **PASS 15/15**; 6 **PASS 4/4** (servers now started together); 2: 47/49, UInt64 still wrapped. Diagnosis (ADBC
straight to the server): GetTables and result mode `complete` give `decimal128(20,0)` with correct values, result
mode `partial` streams `uint64` → the BE converter wrapped values ≥ 2^63. Fix in 0003: UInt64 arrays are widened
to decimal128(20,0) for DECIMAL slots (+ be-ut case). New series `4a9848e-fl598360` (FE 39664615702 forced,
BE 39664594320, be-ut 39664598409 20/20).

## 2026-10-21, run 39665941130 — series `4a9848e-fl598360`, checks 1–9: **all PASS**

| # | Check | Result |
|---|---|---|
| 1 | catalog, SHOW, DESC, masking | PASS 15/15 |
| 2 | types tables, every column (49 columns, 5000 rows each) | PASS 49/49 (hidden as designed: TIME, INTERVAL) |
| 3 | M4-TESTS §1–2, result modes partial + complete, session and catalog switches | PASS 21/21 |
| 4 | TPC-H SF1 q01–q22, `cbo_push_down_topn_limit` default and 0 | PASS 44/44 (45 s in total) |
| 5 | sr-cases (26) | PASS 26/26 |
| 6 | failover, 2-server cluster: before / during a read | PASS 4/4 (stop before: 11.5 s via backups; kill 1.5 s into a 2.7 s read: correct result) |
| 7 | KILL QUERY | PASS (ends < 2 s, server stream cancelled) |
| 8 | token / basic / TLS | PASS 10/10 |
| 9 | memory limit | PASS 3/3 |
| log masking | tokens in fe.log / be.INFO / be.WARNING / container logs | PASS |

## 2026-10-21, run 39670612956 — series `4a9848e-fl598360`, checks 1, 3, 4 with `ref_catalog=flight_c`

Harness test for the local final check (`m4.py --ref-catalog`): 1 PASS 15/15, 3 PASS 21/21, 4 **PASS 88/88**
(44 against `reference/sf1`, 44 against the same query on catalog `flight_c`, result mode complete).
