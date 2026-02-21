# Step 4.1

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Step 4.1: learning-ages.py --summary Flag

**Objective:** Add `--summary` flag to `agent-core/bin/learning-ages.py` that outputs a single-line health status instead of the full markdown report. Used by both health scripts.

**Script Evaluation:** Small — detect flag in sys.argv, add conditional output path reusing existing variables.

**Execution Model:** Haiku

**Prerequisite:** Read `agent-core/bin/learning-ages.py` main() lines 156-220 — identify where `total_entries`, `entries_7plus`, and `staleness_days` are computed relative to the report generation section.

**Implementation:**

Add `--summary` detection AFTER the existing computation block (after line 193 where `entries_7plus` is computed, before the `print("# Learning Ages Report")` line). The flag branches the output path, not the computation:
```
# --summary: branch output after computation, reuse existing variables
if '--summary' in sys.argv:
    [print one-liner summary using total_entries, entries_7plus, staleness_days]
    sys.exit(0)

# Normal: full markdown report follows
print("# Learning Ages Report")
...
```

One-liner output format:
- If consolidation date known: `"{total_entries} entries ({entries_7plus} ≥7 days, consolidation {staleness_days}d ago)"`
- If no prior consolidation: `"{total_entries} entries ({entries_7plus} ≥7 days, no prior consolidation)"`

Note: `--summary` runs full git blame computation (same as normal report). Acceptable latency for a once-per-session hook.

Argument detection: `'--summary' in sys.argv` (no argparse needed — simple flag check, single flag).

**Expected Outcome:**
```bash
python3 agent-core/bin/learning-ages.py agents/learnings.md --summary
# Output (one line): "47 entries (12 ≥7 days, consolidation 8d ago)"
# Exit: 0
```

**Error Conditions:**
- File not found still exits 1 with error to stderr (unchanged)
- No learning entries still exits 1 with error (unchanged)
- `--summary` with git blame errors: tolerate gracefully — use `entries_with_ages` that were successfully retrieved

**Validation:**
```bash
# Verify one-liner output: exactly 1 line matching expected format
output=$(python3 agent-core/bin/learning-ages.py agents/learnings.md --summary)
lines=$(echo "$output" | wc -l | tr -d ' ')
echo "Lines: $lines"  # Expected: 1
echo "Content: $output"
# Expected format A (prior consolidation): "<N> entries (<M> ≥7 days, consolidation <D>d ago)"
# Expected format B (no prior consolidation): "<N> entries (<M> ≥7 days, no prior consolidation)"
echo "$output" | grep -E "^[0-9]+ entries \([0-9]+ ≥7 days" || echo "FAIL: format mismatch"

# Verify normal mode still works (no regression)
python3 agent-core/bin/learning-ages.py agents/learnings.md | head -5
# Expected: first line is "# Learning Ages Report" (unchanged behavior)
python3 agent-core/bin/learning-ages.py agents/learnings.md | head -1 | grep -q "# Learning Ages Report" && echo "✓ Normal mode unchanged"
```

---
