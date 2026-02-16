# Deeper RCA: Why the Quality Gap Between Review Tiers

**Date:** 2026-02-16
**Context:** Three-agent diagnostic on worktree-merge-data-loss runbook

## Root Cause 1: Structural vs Semantic Analysis

**Haiku performed structural verification. Opus performed semantic verification.**

Haiku checked:
- Do referenced files exist? ✅
- Do line numbers match? ✅ (but misinterpreted placement)
- Are import paths valid? ✅
- Is git command syntax correct? ✅

Haiku missed:
- Does `_git(check=False)` achieve the intended boolean check? (No — returns `str`, not returncode)
- Can you verify `-d` vs `-D` flags in integration tests without mocking? (No)
- Does "before line 351" mean "before the function" or "before the statement"? (Misread as "before function")

**The `_git()` miss is diagnostic:** Haiku read utils.py, confirmed the function exists, confirmed the import path — but never asked "what does `_git()` return, and can the caller use that return value to determine merge status?" That's a semantic question about API contract compatibility.

Opus read the same code and silently corrected the runbook because it understood that `_git()` → `str` and `merge-base --is-ancestor` → exit-code-only are incompatible interfaces.

## Root Cause 2: Severity Inflation from Confidence Miscalibration

Haiku rated a false positive as CRITICAL and a non-issue as MAJOR. Pattern:

- **"Before line 351" → CRITICAL misplacement risk.** Haiku saw ambiguity and escalated to maximum severity. The ambiguity was in haiku's interpretation, not in the runbook. A reader familiar with runbook conventions (location hints point within functions) would read "before line 351" correctly.

- **Import order C1.9 before C1.1 → MAJOR dependency risk.** Haiku didn't know that cycles execute sequentially. This is workflow-level context not stated in the phase file itself. Without that context, the concern is rational — but the conclusion (reorder cycles or add dependency) is wrong.

**Pattern:** Haiku detects possible ambiguity → lacks context to resolve it → escalates severity as a hedge. This produces false signal at elevated severity, which is worse than missing the issue entirely (forces triage work on the orchestrator).

## Root Cause 3: Silent Fix vs Reported Fix

Opus fixed `_git()` return type without listing it as a finding. Two interpretations:

1. **Efficient:** The fix was obvious, no judgment required, just corrected inline
2. **Incomplete audit trail:** The diagnostic report undercounts real issues found

For runbook correctness: efficient (the fix landed). For understanding review quality: incomplete (we only know opus fixed it because the diff shows the change and I independently found the same issue).

**Implication:** Fix-all agents may undercount their work when the fix is obvious. The review report measures diagnostic difficulty, not total corrections applied.

## Root Cause 4: Orchestrator Idle Context RCA

Sonnet (me) found the single most impactful issue while reading source code during agent wait time. This worked because:

- **Narrow scope:** I targeted one specific concern (`_git()` API compatibility) rather than sweeping all 13 cycles
- **Cross-file reasoning:** Required understanding `_git()` signature in utils.py AND its usage context in Cycle 1.1
- **Motivated search:** I read utils.py specifically to verify runbook accuracy, not for general exploration

This suggests orchestrator idle time is best used for targeted hypothesis testing, not broad review (which the delegated agents already cover).

## Actionable Conclusions

| Conclusion | Evidence | Implication |
|------------|----------|-------------|
| Opus alone is sufficient for runbook review | 8 real fixes, 0 false positives | Don't parallelize review agents — single opus pass is higher quality than multi-tier |
| Haiku exploration adds triage cost | 2 false positives at elevated severity | Use haiku for structural checks only (file exists, fixture available), not judgment calls |
| Sonnet inline RCA has high signal density | 1 finding in 4 reads vs haiku's 4 findings in 13 reads | Orchestrator idle context best for targeted verification, not broad sweeps |
| Review reports undercount silent fixes | `_git()` fix not in opus findings but in diff | Diff-based analysis more complete than report-based for measuring review value |

## Decision

No workflow change needed — the existing pattern (opus plan-reviewer) already catches everything. The three-agent diagnostic was useful as a one-time calibration exercise, not as a repeatable process.
