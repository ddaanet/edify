# Step 1.3

**Plan**: `plans/recall-tool-anchoring/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.3: Write recall-diff.sh

**Objective:** Show what changed in plan directory since last artifact update.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-diff.sh`
- Shebang + `set -euo pipefail`
- Accept `<job-name>` argument
- Find `plans/<job-name>/recall-artifact.md` — if missing, report and exit 1
- Get artifact's last-modified time
- Use `git log --since="<mtime>" --name-only --pretty=format: -- "plans/<job-name>/"` to list files changed since artifact mtime
- Exclude `recall-artifact.md` itself from output
- Output changed file list to stdout (one per line)
- If no changes found, output nothing, exit 0

**Expected Outcome:** Write-side gates use this to see what exploration/discussion changed since last artifact update.

**Error Conditions:**
- Missing argument → usage message, exit 1
- Not in git repo → stderr diagnostic, exit 1
- Artifact missing → stderr diagnostic, exit 1

**Validation:** Run against this plan. After modifying a file in `plans/recall-tool-anchoring/`, re-run — should show the modified file.

---
