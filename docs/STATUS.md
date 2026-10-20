# Status

Kept up to date with every milestone so the work can be resumed from this repository alone.
Design: StarRocks 4.1.4 + native Arrow Flight SQL catalog, variant B (FE metadata/planning in Java, BE scan in
C++ with Arrow Flight DoGet). Decisions: catalog-level token (v1), partial result mode + location failover on by
default, nested types exposed (`flight.nested_types=hide|json` to change), pushdown of projection, filters, LIMIT,
count(*) and GROUP BY aggregation, TOP-N optimizer fix as a separate patch.

## Milestones

| M | Content | State |
|---|---|---|
| M0 | CI builds unmodified 4.1.4 FE + BE; artifacts downloadable | in progress |
| M1 | FE catalog `flight`: schemas, tables, type mapping, secret masking | in progress (code) |
| M2 | BE native scanner (partial mode, location failover, cancellation), Arrow → Chunk | todo |
| M3 | Pushdown: projection, filters (BE re-check), LIMIT, count(*), GROUP BY aggregation; TOP-N fix | todo |
| M4 | Bench tests on the local stand | todo |
| M5 | Package: patch series + artifacts + install guide | todo |

## CI

- `fe.yml`: FE jars. `be.yml`: `starrocks_be`, split into chained jobs `part1..part4` (each < 6 h, ccache carried
  between them through actions/cache); if 4 parts are not enough the run re-dispatches itself and the next run
  resumes from the newest ccache. A started build therefore finishes without anyone watching.
- Builds are skipped when an output for the same input hash is cached (`fe-out-<hash>`, `be-out-<hash>`).
- Push-triggered builds react only to their patch areas (`*-thrift-*`, `*-fe-*`, `*-be-*`).

## Next steps

1. Finish M0 (full unmodified BE build) and record times / minutes.
2. FE connector + optimizer patches, FE CI build.
3. BE connector patch; the first BE build after the Thrift patch is close to a full rebuild.
