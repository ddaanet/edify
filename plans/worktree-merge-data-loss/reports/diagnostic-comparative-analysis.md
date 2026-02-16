# Diagnostic: Comparative Analysis of Three-Agent Runbook Review

**Date:** 2026-02-16
**Runbook:** worktree-merge-data-loss (Phase 1: 13 TDD cycles, Phase 2: 1 general step)

## Method

Three independent review passes ran in parallel:
- **Opus plan-reviewer** — Phase 1 + Phase 2 diagnostic second pass (fix-all)
- **Haiku quiet-explore** — Independent exploration against source files
- **Sonnet inline** — Orchestrator RCA during idle context (source code reads)

## Findings Matrix

| Finding | Opus | Haiku | Sonnet | Real? |
|---------|------|-------|--------|-------|
| `_git()` returns str, not returncode (C1.1) | ✅ Fixed silently | ❌ Missed | ✅ Found | **Yes — critical** |
| Orphan guard message untested (C1.4) | ✅ Major, fixed | ❌ Not found | Not checked | Yes |
| `-d`/`-D` flag unverifiable in integration tests (C1.5/1.6) | ✅ Minor, fixed | Not found | Not checked | Yes |
| Skip ambiguity "silently" vs "commit only" (C1.11) | ✅ Minor, fixed | Not found | Identified in reasoning | Yes |
| Mock reference contradicts testing strategy (C1.7) | ✅ Minor, fixed | ✅ Major (same) | Not checked | Yes |
| Conditional RED failure (C1.8) | ✅ Minor, fixed | ✅ Minor (same) | Not checked | Yes |
| `removal_type` variable threading (C1.6) | ✅ Fixed inline | ✅ Major (same) | Not checked | Yes |
| Phase 2 design ref line range 158-163→164 | ✅ Minor, fixed | Not found | Not checked | Yes |
| Line number misalignment "before line 351" (C1.4) | Not found | ✅ "Critical" | Not checked | **No — false positive** |
| Import order C1.9 before C1.1 GREEN | Not found | ✅ "Major" | Not checked | **No — false positive** |
| Phase 2 prerequisites missing Phase 1 dep | Not found | ✅ Minor | Not checked | Marginal (ordering enforces) |

## False Positive Analysis

**Haiku Finding 1 (line numbers):** "before line 351" means *before the statement at line 351* (after docstring, before `worktree_path = wt_path(slug)`). The haiku agent misread this as "before the function." The placement is correct — guard goes inside the function, after docstring.

**Haiku Finding 4 (import order):** Cycles execute sequentially within a phase. Cycle 1.1 GREEN completes before Cycle 1.9 RED starts. The runbook already states "Dependencies: Requires Cycle 1.1" in Cycle 1.9 header. The concern about execution order is unfounded.

## Quality Assessment

| Metric | Opus | Haiku | Sonnet |
|--------|------|-------|--------|
| Real findings | 8 (5 reported + 3 silent fixes) | 4 (overlapping with opus) | 1 (unique) |
| False positives | 0 | 2 (1 "critical", 1 "major") | 0 |
| Unique findings | 5 | 0 | 1 |
| Severity accuracy | High (calibrated ratings) | Low (inflated: "critical" for non-issue) | N/A (1 finding) |
| Source verification | Verified all line refs | Verified line refs but misinterpreted | Verified _git() return type |

**Key observation:** Opus found and fixed the `_git()` return type issue without reporting it as a separate finding — it just corrected line 39 as part of fix-all. This silent fix pattern is efficient but makes the review report incomplete as a diagnostic record.

## Conclusions

- **Opus review** is the only pass that found all real issues and produced zero noise
- **Haiku exploration** has value for coverage (found 4 real issues) but generates false positives at elevated severity — cannot be trusted for critical/major ratings without human validation
- **Sonnet inline RCA** caught the single most impactful issue (`_git()` return type) that would have caused broken code at execution time — narrow scope but high signal
- **Three-agent approach** has diminishing returns: opus alone would have caught everything; haiku added noise requiring triage; sonnet found nothing opus didn't also fix

## Applied Changes

All fixes from opus review are in the git diff (8 changes across Phase 1, 1 change in Phase 2). No additional fixes needed — opus covered all real issues including the `_git()` fix I identified independently.
