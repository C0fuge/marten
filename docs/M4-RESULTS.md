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
