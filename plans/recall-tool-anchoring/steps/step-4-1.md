# Step 4.1

**Plan**: `plans/recall-tool-anchoring/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Step 4.1: Write pretooluse-recall-check.py

**Objective:** Soft enforcement at Task delegation boundary — warn when recall artifact missing.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/hooks/pretooluse-recall-check.py`
- Follow `pretooluse-recipe-redirect.py` pattern: read JSON from stdin, check tool_input, output JSON with additionalContext
- Parse `tool_input.prompt` for `plans/<job>/` path pattern (regex: `plans/([^/]+)/`)
- Extract first match as job name
- Check if `plans/<job>/recall-artifact.md` exists (os.path.exists, not subprocess)
- If missing → output additionalContext: "⚠️ No recall-artifact.md for plans/<job>/. Consider /recall or generating artifact before delegation."
- If present or no plans/ path detected → exit 0 (no output, no interference)
- Shebang: `#!/usr/bin/env python3`

**Expected Outcome:** Task delegations referencing a plan directory get a soft reminder if recall artifact is missing. Does not block.

**Error Conditions:**
- Malformed hook input → exit 0 silently (defensive — hook must not break delegation)
- Multiple plans/ matches → use first match

**Validation:** Test with mock JSON input containing plans/ path and missing artifact. Verify additionalContext in output.

---
