# Step 1.1

**Plan**: `plans/recall-tool-anchoring/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.1: Write recall-check.sh

**Objective:** Create existence/non-empty validator for recall artifacts.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-check.sh`
- Shebang + `set -euo pipefail`
- Accept `<job-name>` argument
- Check `plans/<job-name>/recall-artifact.md` exists and is non-empty
- Exit 0 with no output on success
- Exit 1 with diagnostic on stderr: "recall-artifact.md missing for <job>" or "recall-artifact.md empty for <job>"
- Make executable (`chmod +x`)

**Expected Outcome:** Script validates artifact existence. Used by PreToolUse hook (Phase 4) and available for ad-hoc checks.

**Error Conditions:** Missing argument → usage message to stderr, exit 1.

**Validation:** Run against this plan's artifact (should exit 0). Run against nonexistent job (should exit 1 with diagnostic).

---
