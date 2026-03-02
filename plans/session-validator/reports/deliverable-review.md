# Deliverable Review: session-validator

**Date:** 2026-03-02
**Methodology:** agents/decisions/deliverable-review.md
**Layer 1:** Two opus agents (code + test), run in parallel
**Layer 2:** Interactive cross-cutting review with delivery path analysis

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | src/claudeutils/validation/cli.py | +15 | -0 |
| Code | src/claudeutils/validation/plan_archive.py | +119 | -0 |
| Code | src/claudeutils/validation/session_commands.py | +43 | -0 |
| Code | src/claudeutils/validation/session_structure.py | +260 | -3 |
| Code | src/claudeutils/validation/session_worktrees.py | +96 | -0 |
| Code | src/claudeutils/validation/task_parsing.py | +100 | -0 |
| Code | src/claudeutils/validation/tasks.py | +1 | -1 |
| Code | src/claudeutils/worktree/resolve.py | +1 | -1 |
| Code | src/claudeutils/worktree/session.py | +1 | -1 |
| Test | tests/test_validation_plan_archive.py | +212 | -0 |
| Test | tests/test_validation_section_aware.py | +206 | -0 |
| Test | tests/test_validation_session_commands.py | +81 | -0 |
| Test | tests/test_validation_session_structure.py | +135 | -13 |
| Test | tests/test_validation_session_worktrees.py | +135 | -0 |
| Test | tests/test_validation_status_line.py | +131 | -0 |
| Test | tests/test_validation_task_parsing.py | +179 | -0 |
| Test | tests/test_validation_tasks.py | +3 | -3 |
| Test | tests/test_worktree_merge_session_resolution.py | +2 | -2 |
| Test | tests/test_worktree_session.py | +3 | -3 |
| Agentic prose | agent-core/fragments/execute-rule.md | +3 | -3 |
| Agentic prose | agents/decisions/operational-tooling.md | +2 | -2 |

**Total:** 21 files, +1728/-32 (net +1696)

**Design conformance:** No design.md exists (Moderate classification → Tier 2 inline execution). Conformance baseline is `plans/session-validator/requirements.md` (7 FRs, 4 NFRs).

## Critical Findings

**C-1.** `session_worktrees.py:36-52` — Functional correctness — `get_worktree_slugs()` parses `git worktree list --porcelain` incorrectly. The porcelain format produces lines like `worktree /path/to/.claude/worktrees/slug`. The parser does `parts = line.split(); path = parts[0]`, which yields `"worktree"` (the keyword), never the actual path. The `.claude/worktrees/` check always fails. **Verified:** reproduction confirms zero slugs returned for valid porcelain input.

Impact: FR-4 worktree cross-reference is functionally broken in production. All 14 tests bypass this code path by passing `worktree_slugs=` directly, so the bug is invisible to tests. The existing correct parser (`_parse_worktree_list` from `worktree/utils.py`) was available but not reused, per requirements implementation notes.

**C-2.** `session_structure.py:249-304` — Functional completeness (delivery path) — `check_task_section_lines()` does not account for H3 subsection headings within task sections. Main's `agents/session.md` contains `### Blocked / Terminal` inside `## In-tree Tasks` (line 63). After merge, the validator will flag this as `"invalid task line format in In-tree Tasks: ### Blocked / Terminal"`. Lines starting with `#` are neither blank, indented, nor HTML comments, and they don't parse as task lines → error.

Impact: Precommit will fail on merge unless either (a) the validator is updated to allow H3 headings in task sections, or (b) the session.md data is restructured to remove the subsection heading.

## Major Findings

**M-1.** `session_structure.py:387-389` — Conformance (NFR-1) — `check_worktree_markers()` returns `(errors, warnings)` but `validate()` discards warnings: `marker_errors, _ = check_worktree_markers(...)`. FR-4 requires warnings for orphaned worktrees. NFR-1 requires warnings printed to stderr without failing the check. Warnings are computed but never surfaced.

**M-2.** Missing FR-3 criterion 3 — Conformance — "Backtick-wrapped paths in task metadata (e.g., `Plan: foo/bar`) are checked if they look like filesystem paths" is not implemented. FR-3 criteria 1 (Reference Files paths) and 2 (no `tmp/` paths) are covered by existing validators, but criterion 3 is absent.

**M-3.** Missing NFR-2 — Conformance — `--fix` flag for mechanical autofixes (section reordering, stale reference removal) does not exist. Zero matches for `--fix` across all validation source files. Complete omission.

**M-4.** `session_structure.py:254` — Functional completeness (delivery path) — `_check_invalid_model_in_line()` parses pipe-separated metadata segments but doesn't account for free-text descriptions that happen to contain pipes. Main's session.md line 254: `- [ ] **Test diamond migration** — Needs scoping | depends on runbook evolution (delivered) | sonnet | 0.9`. The segment `depends on runbook evolution (delivered)` is not a valid model, restart, or priority — it produces error `"invalid model 'depends on runbook evolution (delivered)'"`. The parser treats every pipe-delimited segment after the first as a metadata field, but the format allows free-text descriptions mixed with pipes.

## Minor Findings

### NFR-4 consolidation incomplete (3 instances)

- `session_structure.py:21` — retains own `TASK_PATTERN` (used by `extract_section_tasks`), not imported from `task_parsing.py`
- `tasks.py:16` — retains own `TASK_PATTERN` with `—` suffix, not migrated to shared module
- `worktree/session.py:30` — retains own `task_pattern`, not migrated to shared module

NFR-4 says "consolidate into a single extraction module" — new validators comply, existing consumers only had character class updated.

### Code quality (6 instances)

- `session_structure.py:25-43` — `ALLOWED_SECTIONS` and `SECTION_ORDER` are identical lists defined twice
- `session_structure.py:240` — ordering error message reads ambiguously: `"In-tree Tasks appears before Next Steps"` when the problem is Next Steps appearing before In-tree Tasks
- `session_structure.py:282` — `startswith("  ")` (two spaces) for indentation detection; single-space or tab indent would be missed
- `session_commands.py:35` — `break` after first anti-pattern match suppresses subsequent matches on same line
- `plan_archive.py:34` — `"".strip().split("\n")` produces `['']` not `[]`; handled by `if not line` but non-obvious
- `plan_archive.py:42` — only checks `D` status, not `R` (rename); may be intentional per requirements

### Test quality (6 instances)

- `test_validation_session_structure.py:255` — `len(errors) >= 1` instead of `== 1`
- `test_validation_session_structure.py:337-352` — `test_multiple_error_types` count assertion fragile on worktree_slugs behavior
- `test_validation_session_worktrees.py:27-31` — `test_main_worktree_excluded` tests passthrough path, not actual exclusion
- `test_validation_session_worktrees.py:127-135` — `"line" in ... or "2" in ...` assertion too weak
- `test_validation_section_aware.py:85-95` — `len(errors) >= 2` instead of `== 2`
- `test_validation_section_aware.py:97-107` — missing case-insensitivity test for model names

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| FR-1: Section schema | Covered | `session_structure.py:check_section_schema()` |
| FR-2: Task format | Covered | `task_parsing.py` + `check_task_section_lines()` |
| FR-3: Reference validity | **Partial** — criterion 3 missing | `check_reference_files()` + `session_refs.py` |
| FR-4: Worktree markers | **Broken in production** | `session_worktrees.py` — porcelain parser bug |
| FR-5: Status line | Covered | `session_structure.py:check_status_line()` |
| FR-6: Plan archive | Covered | `plan_archive.py` |
| FR-7: Command semantics | Covered | `session_commands.py` |
| NFR-1: Precommit integration | **Partial** — warnings discarded | `cli.py` wiring present |
| NFR-2: --fix flag | **Missing** | Not implemented |
| NFR-3: Format dependency | N/A | Worktree format landed |
| NFR-4: Shared parsing | **Partial** — new code uses it, old code doesn't | `task_parsing.py` created, 3 legacy copies remain |

### Delivery Path Concerns

Main's `agents/session.md` (354 lines, 80 tasks) triggers 3 validator errors after merge:

1. `### Blocked / Terminal` subsection heading → invalid task line (C-2)
2. `depends on runbook evolution (delivered)` → invalid model (M-4)
3. `## Reference Files` after `## Next Steps` → section out of order (legitimate data issue, not a validator bug)

Item 3 is correct behavior — the data on main needs fixing. Items 1 and 2 are validator gaps that need resolution before merge.

Additionally: main had `skill-disclosure` merge since branch base (ce5d1713), but no validation source changes in that merge — clean merge expected for code.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 4 |
| Minor | 15 |

**Critical:** Production porcelain parser bug (C-1), H3 heading in task sections not handled (C-2 — delivery path blocker).

**Major:** Warnings discarded (M-1), FR-3 criterion 3 missing (M-2), NFR-2 missing (M-3), free-text metadata with pipes misclassified (M-4 — delivery path).

Layer 1 reports: `plans/session-validator/reports/deliverable-review-code.md`, `plans/session-validator/reports/deliverable-review-test.md`.
