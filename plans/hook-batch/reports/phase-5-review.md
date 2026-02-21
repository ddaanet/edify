# Runbook Review: hook-batch Phase 5

**Artifact**: `plans/hook-batch/runbook-phase-5.md`
**Date**: 2026-02-21T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (4 steps)

## Summary

Phase 5 covers Hook Infrastructure: hooks.json creation, sync-hooks-config.py merge helper, justfile update, and sync execution. The phase is well-structured with prerequisites, implementation guidance, and validation commands. Four issues found — one critical (sandbox note missing from Step 5.2 validation), two major (Step 5.3 placement ambiguity and cross-step atomic write discrepancy), and one minor (missing PostToolUse Bash preservation note in Step 5.1 + missing verification in Step 5.4). All issues fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

1. **Step 5.2 validation commands blocked by sandbox — no dangerouslyDisableSandbox note**
   - Location: Step 5.2, Validation section
   - Problem: All validation commands call `python3` directly (`python3 -c 'import ast...'`, `python3 agent-core/bin/sync-hooks-config.py`). The deny list contains `Bash(python3:*)`, which blocks these without `dangerouslyDisableSandbox: true`. The phase-level prerequisite mentions the requirement applies to "Step 5.2 and 5.3/5.4" but Step 5.2 has no per-step note, unlike Step 5.4 which has an explicit `**Note:**`. An executor following steps sequentially could fail Step 5.2 validation silently.
   - Fix: Added explicit `**Note:** This step requires dangerouslyDisableSandbox: true` before the Validation block in Step 5.2.
   - **Status**: FIXED

### Major Issues

1. **Step 5.3 placement instruction ambiguous given existing hooks section in justfile**
   - Location: Step 5.3, Implementation
   - Problem: Step 5.3 says "Append to end of sync-to-parent recipe body (before the next recipe definition)". The recipe body already contains a full hooks sync section (lines 63-91 of agent-core/justfile). The instruction doesn't indicate that this section exists, so "end of recipe body" is ambiguous — executor might insert before the hooks section or after `echo "Sync complete!"`. The sync-hooks-config.py call must come after the hooks section (which symlinks hooks.json) and before `echo "Sync complete!"`.
   - Fix: Replaced placement instruction with "Insert before `echo "Sync complete!"` at the end of the `sync-to-parent` recipe body (after the hooks section, before the closing echo)". Added note explaining the hooks section already exists.
   - **Status**: FIXED

2. **Step 5.3 error condition references atomic write not described in Step 5.2**
   - Location: Step 5.3, Error Conditions
   - Problem: Step 5.3 Error Conditions says "Ensure sync-hooks-config.py writes atomically (write to temp file, rename)" as if this is already implemented. Step 5.2 implementation guidance (the step that creates sync-hooks-config.py) contains no mention of atomic write. The executor implementing Step 5.2 has no instruction to include this pattern; the Step 5.3 error condition would then be a false assertion about a property that doesn't exist.
   - Fix: Revised Step 5.3 error condition to frame atomic write as a verification requirement against Step 5.2's implementation ("verify this is implemented in sync-hooks-config.py before running") rather than an assertion it exists.
   - **Status**: FIXED

### Minor Issues

1. **Step 5.1 Notes omit PostToolUse Bash preservation requirement; Step 5.4 verification missing PostToolUse Bash check**
   - Location: Step 5.1 Notes; Step 5.4 Verification
   - Problem: `settings.json` contains a PostToolUse Bash entry with submodule-safety.py. Step 5.1 Notes correctly describe how to handle PostToolUse Write|Edit (new entry) but don't mention that the existing PostToolUse Bash entry must also be preserved during merge. Step 5.4 verifies PreToolUse Bash, PreToolUse Write|Edit, and UserPromptSubmit dedup, but has no check that PostToolUse Bash (submodule-safety.py) survived the merge alongside the new PostToolUse Write|Edit entry.
   - Fix: Added note in Step 5.1 Notes clarifying PostToolUse Bash must be preserved. Added verification block in Step 5.4 checking both PostToolUse matchers (Bash + Write|Edit) with expected values.
   - **Status**: FIXED

## Fixes Applied

- Step 5.1 Notes: Added "PostToolUse Bash matcher already exists (submodule-safety.py) — merge must preserve it; sync-hooks-config.py adds Write|Edit entry alongside existing Bash entry"
- Step 5.2 Validation: Added `**Note:** This step requires dangerouslyDisableSandbox: true` before validation commands
- Step 5.3 Implementation: Changed placement instruction from "Append to end of recipe body" to "Insert before `echo "Sync complete!"` … after the existing hooks section"; added note that hooks section already exists
- Step 5.3 Error Conditions: Reframed atomic write from assertion to verification requirement against Step 5.2 implementation
- Step 5.4 Verification: Added PostToolUse Bash + Write|Edit preservation check with expected output comments

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
