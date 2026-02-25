# Step 1.3 Execution Report

**Step:** Write recall-diff.sh
**Status:** Complete

## Implementation

Created `/Users/david/code/claudeutils-wt/recall-tool-anchoring/agent-core/bin/recall-diff.sh` (28 lines).

**Behavior:**
- Accepts `<job-name>` argument
- Locates `plans/<job-name>/recall-artifact.md`; exits 1 with diagnostic if missing
- Gets artifact mtime via `date -r`
- Runs `git log --since=<mtime> --name-only` over the plan directory
- Strips blank lines, excludes `recall-artifact.md` itself, deduplicates via `sort -u`
- Exits 0 with no output when no changes found

**Error conditions handled:**
- Missing argument → usage to stderr, exit 1
- Artifact missing → diagnostic to stderr, exit 1
- Not in git repo → diagnostic to stderr, exit 1

## Validation

Run against `recall-tool-anchoring` plan — output showed 10 files changed since artifact was last modified:
```
plans/recall-tool-anchoring/orchestrator-plan.md
plans/recall-tool-anchoring/reports/step-1-1-execution.md
plans/recall-tool-anchoring/reports/step-1-2-execution.md
plans/recall-tool-anchoring/runbook-outline.md
plans/recall-tool-anchoring/runbook.md
plans/recall-tool-anchoring/steps/step-1-1.md
plans/recall-tool-anchoring/steps/step-1-2.md
plans/recall-tool-anchoring/steps/step-1-3.md
plans/recall-tool-anchoring/steps/step-4-1.md
plans/recall-tool-anchoring/steps/step-4-2.md
```

All error conditions verified (missing arg, missing artifact).

## Commit

Submodule commit: `c36a2df` — "Add recall-diff.sh — show plan files changed since artifact update"
