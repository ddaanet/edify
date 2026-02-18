# Deliverable Review: Prose + Config Partition

**Scope**: SKILL.md Mode C (exit code 3 handling) + cli.py (stderr-to-stdout migration)
**Design ref**: `plans/worktree-merge-resilience/outline.md`
**Requirements ref**: `plans/worktree-merge-resilience/requirements.md`
**Date**: 2026-02-18

## Summary

SKILL.md Mode C is well-structured with clear exit code semantics and deterministic action paths. The exit code 3 separation from exit 1 is clean — agents get an unambiguous signal for "conflicts need resolution" vs "error/precommit failure." The cli.py change is a single-line `err=True` removal, correctly scoped to the merge command only. Two issues found: one major (precommit diagnostic output dropped) and one minor.

**Overall Assessment**: Needs Minor Changes

---

## agent-core/skills/worktree/SKILL.md

### Major: Precommit failure output may be incomplete (implementation gap)

**Location**: SKILL.md:99-105 (step 5) / merge.py:302-314
**Axis**: Conformance, Actionability
**Design ref**: D-8, C-2
**Finding**: Step 5 instructs the agent to "Review the failed precommit checks in stdout." The implementation (merge.py:313) echoes `precommit_result.stderr` to stdout but drops `precommit_result.stdout`. Many lint/check tools (ruff, mypy, pytest) write diagnostic output to stdout, not stderr. An agent following step 5 would see "Precommit failed after merge" and whatever precommit wrote to stderr, but miss stdout-based diagnostics. This makes step 5.1 ("Review the failed precommit checks in stdout") potentially insufficient — the agent may not have enough information to fix the issue.

This is an implementation bug in merge.py (should echo both `.stdout` and `.stderr`), not a SKILL.md prose issue. But SKILL.md conformance depends on the implementation actually forwarding complete output. Flagged here because the deliverable review axis is conformance between skill and implementation.

### Positive Observations

- **Exit code 3 separation is clean.** Old SKILL.md conflated conflicts and precommit failure under exit 1, requiring the agent to parse stderr to distinguish. New structure: exit 3 = conflicts (resolve + re-run), exit 1 = error (fix + amend). Each exit code has exactly one action path.

- **Idempotent resume instruction is precise.** Step 4.3 says "re-run: `claudeutils _worktree merge <slug>` with `dangerouslyDisableSandbox: true` (idempotent — resumes from current state, skips already-completed phases)." This matches the state machine behavior: after conflict resolution, re-run detects `parent_resolved` and proceeds to Phase 4.

- **Session file auto-resolution framing is correct.** "Report as bug if they appear in the conflict list" matches implementation — `resolve_session_md` and `resolve_learnings_md` remove these files from the conflict list before the exit-3 report. If they appear, something broke in auto-resolution.

- **stdout-only framing is consistent throughout.** All three exit code steps say "Read stdout for..." — no residual stderr references. Matches D-8 decision.

- **Sandbox bypass annotation added to step 5.6** (re-run after precommit fix). The old SKILL.md omitted `dangerouslyDisableSandbox: true` from the exit-1 re-run command. Fixed.

- **No vacuous instructions.** Every numbered step has a concrete action. The "Common issues" list under exit code 2 is actionable (specific git commands to diagnose).

- **Determinism is strong.** Given any exit code (0, 1, 2, 3), the skill produces exactly one action path. No branching within exit code handlers — the old "If conflicts detected / If precommit failure" branching under exit 1 is eliminated.

- **Scope boundaries are correct.** Mode C describes what auto-resolves (session, learnings, agent-core pointer) vs what needs manual resolution (source files). Matches implementation in `_phase3_merge_parent`.

---

## src/claudeutils/worktree/cli.py

### Minor: Remaining `err=True` in non-merge functions (by design, not a defect)

**Location**: cli.py:76,136,229,235,289,299,308,361,368
**Axis**: Completeness
**Design ref**: D-8
**Finding**: Nine `err=True` calls remain in cli.py, all in non-merge functions (`new`, `rm`, `_guard_branch_removal`, `_initialize_environment`, `_create_parent_worktree`, `_check_confirm`). D-8 scope is "merge output to stdout." The Phase 5 review (review-phase-5.md) explicitly confirmed the scope: "merge.py: all matches; cli.py: merge command only." Non-merge `err=True` is intentionally preserved. Not a defect — documented here for completeness.

### Positive Observations

- **Single-line change, correctly scoped.** Only the `merge` CLI wrapper's error handler was changed (line 262). No behavioral change beyond output stream.

- **No functional side effects.** The `SystemExit` codes from `merge_impl` propagate through click unchanged. The try/except only catches `CalledProcessError` (unexpected git failures not already handled inside `merge_impl`).

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-1 (exit code 3) | Satisfied | SKILL.md step 4: exit 3 = "conflicts, merge paused" with resolve+re-run workflow |
| FR-2 (conflicts need resolution) | Satisfied | SKILL.md step 4 describes Edit + git add + re-run cycle |
| FR-4 (conflict context) | Satisfied | SKILL.md step 4: "conflicted file list with conflict type, per-file diff stats, branch divergence summary, and a hint command" |
| FR-5 (idempotent resume) | Satisfied | SKILL.md step 4.3: "idempotent — resumes from current state, skips already-completed phases" |
| NFR-2 (no data loss) | Satisfied | No abort instructions in SKILL.md. Exit 3 preserves merge state. |
| C-1 (skill contract) | Satisfied | SKILL.md Mode C updated with all 4 exit codes (0, 1, 2, 3) |
| C-2 (non-interactive) | Satisfied | All instructions use Edit + Bash, no interactive resolution |
| D-8 (stdout only) | Satisfied | SKILL.md says "Read stdout" for all exit codes. cli.py merge handler: `err=True` removed. |

**Gaps**: None.

---

## Recommendations

- Fix merge.py:313 to echo both `precommit_result.stdout` and `precommit_result.stderr` — ensures agents get complete precommit diagnostic output per SKILL.md step 5's instruction. This is a follow-up implementation fix, not a SKILL.md prose fix.

## Next Steps

- Address precommit output issue in merge.py (major finding)
