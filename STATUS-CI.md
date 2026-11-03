# CI status

Generated 2026-11-03T08:46Z by ci-report (trigger: workflow_run fe cancelled).

## Runs (newest first)

| run id | workflow | branch | sha | event | status | conclusion | created | updated | title |
|---|---|---|---|---|---|---|---|---|---|
| 41605708311 | ci-report | main | 972c547ff | workflow_run | in_progress |  | 2026-11-03T08:45:55Z | 2026-11-03T08:46:09Z | ci-report |
| 41605520176 | be | main | 2a23272bc | workflow_dispatch | in_progress |  | 2026-11-03T08:44:27Z | 2026-11-03T08:44:51Z | be |
| 41605517022 | fe | main | 2a23272bc | workflow_dispatch | in_progress |  | 2026-11-03T08:44:25Z | 2026-11-03T08:45:55Z | fe |
| 41605509133 | ci-report | main | 2a23272bc | workflow_run | completed | success | 2026-11-03T08:44:21Z | 2026-11-03T08:44:37Z | ci-report |
| 41605501560 | fe | main | 2a23272bc | push | completed | cancelled | 2026-11-03T08:44:18Z | 2026-11-03T08:45:52Z | fe: join-key IN list up to 50000 keys (q19 at SF10 needs ~21 |
| 41605501548 | dispatch | main | 2a23272bc | push | completed | success | 2026-11-03T08:44:18Z | 2026-11-03T08:44:30Z | fe: join-key IN list up to 50000 keys (q19 at SF10 needs ~21 |
| 41598906259 | compare | main | bc7b54b50 | workflow_dispatch | completed | success | 2026-11-03T07:49:47Z | 2026-11-03T08:03:32Z | compare |
| 41598894621 | dispatch | main | bc7b54b50 | push | completed | success | 2026-11-03T07:49:41Z | 2026-11-03T07:49:50Z | STATUS: join-key fix (series fla21c2a; FE 41591877770, m4 41 |
| 41593206366 | compare | main | a62e09d9a | workflow_dispatch | completed | success | 2026-11-03T06:58:06Z | 2026-11-03T07:48:04Z | compare |
| 41593203647 | m4 | main | a62e09d9a | workflow_dispatch | completed | success | 2026-11-03T06:58:05Z | 2026-11-03T07:16:36Z | m4 |
| 41593063533 | dispatch | main | a62e09d9a | push | completed | success | 2026-11-03T06:56:40Z | 2026-11-03T06:58:10Z | dispatch m4 checks 1-9 and compare sf=10 ours,up for series  |
| 41592037472 | ci-report | main | 58a09952f | workflow_run | completed | success | 2026-11-03T06:46:45Z | 2026-11-03T06:47:05Z | ci-report |
| 41591880762 | be | main | 58a09952f | workflow_dispatch | completed | success | 2026-11-03T06:45:17Z | 2026-11-03T06:50:18Z | be |
| 41591877770 | fe | main | 58a09952f | workflow_dispatch | completed | success | 2026-11-03T06:45:15Z | 2026-11-03T06:54:12Z | fe |
| 41591865880 | ci-report | main | 58a09952f | workflow_run | completed | success | 2026-11-03T06:45:09Z | 2026-11-03T06:45:21Z | ci-report |
| 41591861878 | dispatch | main | 58a09952f | push | completed | success | 2026-11-03T06:45:06Z | 2026-11-03T06:45:20Z | fe: join-key pushdown only from a smaller source table, no i |
| 41591861551 | fe | main | 58a09952f | push | completed | cancelled | 2026-11-03T06:45:06Z | 2026-11-03T06:46:42Z | fe: join-key pushdown only from a smaller source table, no i |
| 41582285095 | compare | main | e262ea96e | workflow_dispatch | completed | success | 2026-11-03T05:10:00Z | 2026-11-03T05:48:39Z | compare |
| 41582274557 | dispatch | main | e262ea96e | push | completed | success | 2026-11-03T05:09:54Z | 2026-11-03T05:10:04Z | dispatch compare sf=10 ours,up for series flded1b0 (m4 41580 |
| 41580201961 | compare | main | 17fe96c00 | workflow_dispatch | completed | success | 2026-11-03T04:48:05Z | 2026-11-03T05:23:12Z | compare |

## Run 41605520176 jobs

- plan: completed success 2026-11-03T08:44:30Z → 2026-11-03T08:44:48Z
- part1 / build (part 1): in_progress  2026-11-03T08:44:51Z → 0001-01-01T00:00:00Z

## Run 41605517022 jobs

- build: in_progress  2026-11-03T08:45:54Z → 0001-01-01T00:00:00Z

## Run 41605501560 jobs

- build: completed cancelled 2026-11-03T08:44:21Z → 2026-11-03T08:45:51Z

## Artifacts

- compare-41593206366: 3 MB, run 41593206366, expired=false, created 2026-11-03T07:47:59Z
- compare-41598906259: 2 MB, run 41598906259, expired=false, created 2026-11-03T08:03:26Z
- m4-41593203647: 0 MB, run 41593203647, expired=false, created 2026-11-03T07:16:31Z
- fe-jars-5689f2b8df8e7f28: 28 MB, run 41591877770, expired=false, created 2026-11-03T06:54:06Z
- starrocks_be-56fc72cd9e2c1877: 97 MB, run 41591880762, expired=false, created 2026-11-03T06:50:15Z
- compare-41582285095: 2 MB, run 41582285095, expired=false, created 2026-11-03T05:48:33Z
- compare-41580201961: 2 MB, run 41580201961, expired=false, created 2026-11-03T05:22:56Z
- m4-41580199568: 0 MB, run 41580199568, expired=false, created 2026-11-03T05:09:01Z
- starrocks_be-56fc72cd9e2c1877: 97 MB, run 41579557200, expired=false, created 2026-11-03T04:45:37Z
- fe-jars-71ce9ff6ed9dae61: 28 MB, run 41578204766, expired=false, created 2026-11-03T04:35:44Z
- compare-41466074590: 4 MB, run 41466074590, expired=false, created 2026-11-02T15:38:17Z
- compare-41466070831: 4 MB, run 41466070831, expired=false, created 2026-11-02T15:08:39Z
- up-starrocks_be-cb8256824cbed984: 93 MB, run 41446753059, expired=false, created 2026-11-02T14:04:33Z
- compare-41451137029: 0 MB, run 41451137029, expired=false, created 2026-11-02T13:45:18Z
- compare-41447501206: 0 MB, run 41447501206, expired=false, created 2026-11-02T13:12:25Z
- up-fe-256a379552744d18: 672 MB, run 41446749737, expired=false, created 2026-11-02T12:46:25Z
- m4-40696414078: 0 MB, run 40696414078, expired=false, created 2026-10-28T13:38:24Z
- m4-40696410403: 0 MB, run 40696410403, expired=false, created 2026-10-28T13:33:05Z
- m4-40694418153: 0 MB, run 40694418153, expired=false, created 2026-10-28T13:25:47Z
- m4-40692973807: 0 MB, run 40692973807, expired=false, created 2026-10-28T13:11:35Z

## Caches (build outputs and ccache)

- be-out-56fc72cd9e2c1877 (97 MB, refs/heads/main, 2026-11-03T06:50:13.909772Z)
- up-fe-out-256a379552744d18 (664 MB, refs/heads/main, 2026-11-02T12:46:19.906464Z)
- fe-out-5689f2b8df8e7f28 (28 MB, refs/heads/main, 2026-11-03T06:54:03.727242Z)
- m4-assets-v18 (4255 MB, refs/heads/main, 2026-10-28T13:16:36.297547Z)
- ccache-be-41591880762-1-1 (535 MB, refs/heads/main, 2026-11-03T06:50:00.185981Z)
- m2-2ebb4f6fdf2a7a28 (791 MB, refs/heads/main, 2026-10-28T10:10:04.780509Z)
- fe-out-71ce9ff6ed9dae61 (28 MB, refs/heads/main, 2026-11-03T04:35:41.925694Z)
- fe-out-4cb407b8728cef4a (28 MB, refs/heads/main, 2026-11-03T03:46:56.925883Z)
- fe-out-c5f3778cbd7fe588 (28 MB, refs/heads/main, 2026-10-28T10:10:06.538742Z)
- up-be-out-cb8256824cbed984 (93 MB, refs/heads/main, 2026-11-02T14:04:31.805783Z)
- ccache-up-41446753059-1-1 (148 MB, refs/heads/main, 2026-11-02T14:04:22.917904Z)
- up-m2-256a379552744d18 (974 MB, refs/heads/main, 2026-11-02T12:46:11.94264Z)
- be-out-9dba754829d38a31 (97 MB, refs/heads/main, 2026-10-26T04:07:50.895891Z)
- fe-out-953a5b852c105901 (28 MB, refs/heads/main, 2026-10-26T03:56:23.201463Z)

## Actions minutes

- be-part (395334860): 0 billable min this cycle
- be-ut (395334861): 0 billable min this cycle
- be (395334863): 0 billable min this cycle
- ci-report (395334865): 0 billable min this cycle
- compare (404510413): 0 billable min this cycle
- dispatch (395334869): 0 billable min this cycle
- fe (395334870): 0 billable min this cycle
- m4 (395334871): 0 billable min this cycle
- release (395334873): 0 billable min this cycle
- up-be-part (404504967): 0 billable min this cycle
- up-be (404504968): 0 billable min this cycle
- up-fe (404504970): 0 billable min this cycle
