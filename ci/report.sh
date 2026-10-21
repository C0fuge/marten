#!/usr/bin/env bash
# Writes a Markdown report of recent CI runs to stdout (used by .github/workflows/ci-report.yml).
# Needs GH_TOKEN and GITHUB_REPOSITORY. The cloud dev session cannot call the Actions API, so this report is
# pushed to branch `ci-status` (file STATUS-CI.md) where it can be read with git.
set -uo pipefail
R=$GITHUB_REPOSITORY
echo "# CI status"
echo
echo "Generated $(date -u +%Y-%m-%dT%H:%MZ) by ci-report (trigger: ${REPORT_TRIGGER:-manual})."
echo
echo "## Runs (newest first)"
echo
echo "| run id | workflow | branch | sha | event | status | conclusion | created | updated | title |"
echo "|---|---|---|---|---|---|---|---|---|---|"
gh run list -R "$R" -L 20 --json databaseId,workflowName,headBranch,headSha,event,status,conclusion,createdAt,updatedAt,displayTitle \
  --jq '.[] | "| \(.databaseId) | \(.workflowName) | \(.headBranch) | \(.headSha[0:9]) | \(.event) | \(.status) | \(.conclusion) | \(.createdAt) | \(.updatedAt) | \(.displayTitle[0:60]) |"'
echo
for id in $(gh run list -R "$R" -L 8 --json databaseId,workflowName --jq '.[] | select(.workflowName=="fe" or .workflowName=="be" or .workflowName=="be-ut") | .databaseId'); do
  echo "## Run $id jobs"
  echo
  gh run view "$id" -R "$R" --json jobs --jq '.jobs[] | "- \(.name): \(.status) \(.conclusion) \(.startedAt) → \(.completedAt)"'
  echo
  if [ "$(gh run view "$id" -R "$R" --json conclusion --jq .conclusion)" = "failure" ]; then
    echo "### Run $id failed steps (last 200 lines)"
    echo
    echo '```'
    gh run view "$id" -R "$R" --log-failed 2>&1 | tail -200 | cut -c1-400
    echo '```'
    echo
  fi
done
echo "## Artifacts"
echo
gh api "repos/$R/actions/artifacts?per_page=20" --jq '.artifacts[] | "- \(.name): \(.size_in_bytes/1048576|floor) MB, run \(.workflow_run.id), expired=\(.expired), created \(.created_at)"'
echo
echo "## Caches (build outputs and ccache)"
echo
gh cache list -R "$R" -L 30 --json key,sizeInBytes,createdAt,ref --jq '.[] | "- \(.key) (\(.sizeInBytes/1048576|floor) MB, \(.ref), \(.createdAt))"'
echo
echo "## Actions minutes"
echo
# Per-workflow billable minutes of the current billing cycle (private repo; ~2000 min/month, see CLAUDE.md).
gh api "repos/$R/actions/workflows" --jq '.workflows[] | "\(.id) \(.name)"' | while read -r w name; do
  gh api "repos/$R/actions/workflows/$w/timing" --jq "\"- $name ($w): \((.billable.UBUNTU.total_ms // 0) / 60000 | floor) billable min this cycle\"" 2>/dev/null
done
