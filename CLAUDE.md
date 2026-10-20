# Working in this repository (instructions for Claude sessions)

Goal: StarRocks 4.1.4 with a native Arrow Flight SQL catalog, delivered as a patch series + build artifacts +
install guide. Design and decisions: `docs/PLAN.md` (§6 lists the user's decisions; do not reopen them).
Source facts: `docs/RESEARCH.md`. Current state and next steps: `docs/STATUS.md`. Read all three first.

## Session routine

This repo is developed by a recurring cloud session that starts from zero context every time.

1. **Lock.** `git fetch origin`. If `docs/LOCK` on the working branch holds a UTC time less than 110 minutes
   old, another session is working: stop without changes. Otherwise write the current UTC time
   (`date -u +%FT%TZ`) to `docs/LOCK`, commit `[skip ci] lock`, push. Remove the lock (empty the file) in the
   last commit of the session.
2. **Branch.** Work on `main`. If pushing to `main` is rejected, use the branch `claude/starrocks-dev` (create
   it from `main`) and keep using it; at session start continue from whichever of `origin/main` and
   `origin/claude/starrocks-dev` has the newer work. Never force-push `main`.
3. **CI state.** `git fetch origin ci-status && git show origin/ci-status:STATUS-CI.md`.
4. **Source.** `scripts/prepare-source.sh src` (shallow clone of tag 4.1.4 + `git am` of `patches/`; ~1 GB,
   git-ignored). Edit in `src/` on branch `flight`, one commit per patch (amend / fixup the right commit;
   subjects start with `thrift:`, `fe:`, `be:`). Then `scripts/export-patches.sh src`. Unchanged patches must
   stay byte-identical (the script ensures that) so only the affected CI build starts.
5. **Work** on the first open item of "Next steps" in `docs/STATUS.md`. Prefer finishing one step properly
   over starting several.
6. **Build/test only in CI.** Compiling StarRocks needs the official builder image; do not try to build it in
   the session. Push changed patches (triggers fe / be by file name), or request runs in `ci/dispatch.txt`
   (`fe force=true tests=Class1,Class2`, `be`, `report`) and push. You may wait in the session for a result
   (poll `ci-status` with `git fetch` every few minutes, up to ~40 min); otherwise leave it for the next session.
7. **Before ending** (aim for ≤ 90 min per session): export patches, update `docs/STATUS.md` (milestone table,
   patch table, a dated Log line with what was done and CI run ids, Next steps), release the lock, commit, push.
   Never leave work only in the session; uncommitted work is lost.

## Rules

- The repo is **public** (since 2026-10-20, so Actions minutes are free; it may become private again later).
  Everything you push is visible to anyone: double-check for secrets. Still keep builds lean — runners are slow
  (full BE build ≈ many hours) and each build delays feedback. Before pushing a thrift or BE patch change, check `STATUS-CI.md`: a push touching BE patches cancels a
  running BE build on the same branch. Batch BE changes; touch the thrift patch as rarely as possible. Don't use
  `force=true` without a reason. Never re-run a build that failed for the same reason without a fix.
- No secrets, credentials, personal data or other projects' code in the repo. No copy of StarRocks sources
  (only patches).
- Commit/push only to this repository. Don't open issues or PRs elsewhere.
- M4 (tests against a real Arrow Flight server and the bench data) is done by the maintainer locally. Cloud
  sessions do M1–M3 and M5 and FE unit tests; prepare M4 by writing the test SQL and expected results.
- Anything that needs the maintainer's decision goes to "Open questions for the maintainer" in `docs/STATUS.md`;
  meanwhile continue with work that does not depend on it.
- Write docs and commit messages in English.
