# Step 1.2

**Plan**: `plans/recall-tool-anchoring/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.2: Write recall-resolve.sh

**Objective:** Create reference manifest resolver — parse manifest, feed triggers to when-resolve.py.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-resolve.sh`
- Shebang + `set -euo pipefail`
- Accept `<artifact-path>` argument
- Read file, strip `—` annotations (everything after ` — ` on each line), trim whitespace
- Skip blank lines and comment lines (starting with `#`)
- Collect trigger phrases as arguments to `agent-core/bin/when-resolve.py`
- Pass all triggers in a single invocation: `agent-core/bin/when-resolve.py "when <trigger1>" "how <trigger2>" ...`
- Each manifest line's first word determines prefix: lines starting with `when` or `how` use that prefix as-is; other lines default to `when` prefix
- Output resolved content to stdout

**Expected Outcome:** Manifest references expand to full decision file content via when-resolve.py.

**Error Conditions:**
- Missing/unreadable artifact → stderr diagnostic, exit 1
- when-resolve.py fails → propagate exit code
- Empty manifest (no triggers after parsing) → stderr warning, exit 0

**Validation:** Run against this plan's artifact after Phase 2 conversion. Verify stdout contains resolved decision content.

---
