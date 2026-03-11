# Review: prose-infra-batch Phase 2 implementation

**Scope**: FR-1 (opus-design-question removal), FR-2 (magic-query-log permission), FR-3 (handoff merge detection), FR-4a (plan-backed tasks rule), FR-4b (task-plans validator + CLI)
**Date**: 2026-03-11T00:00:00
**Mode**: review + fix

## Summary

The implementation correctly addresses all four functional requirements. The validator logic is sound for the primary cases, but has two parsing gaps that produce false positives against the live session.md: (1) nested plan paths under `plans/reports/` are extracted at the wrong level, and (2) non-backtick-wrapped commands (e.g., `/deliverable-review plans/foo`) produce `parsed.command = None`, causing a false "no plan reference" error. The prose changes (FR-1, FR-3, FR-4a) are clean and accurate.

**Overall Assessment**: Needs Minor Changes (two validator false positives, both fixed below)

---

## Issues Found

### Critical Issues

_None._

### Major Issues

1. **Validator false positive: nested plan path extracted at wrong level**
   - Location: `src/claudeutils/validation/task_plans.py:46`, `tests/test_validation_task_plans.py`
   - Problem: `_PLAN_PATTERN = re.compile(r"plans/([^/]+)/")` extracts the first path component after `plans/`. For the `Verb form AB test` task whose command is `see \`plans/reports/ab-test/README.md\``, the regex extracts slug `reports` — a container directory, not a plan dir. The validator then checks `plans/reports/` for recognized artifacts, finds none, and emits a false error. The actual plan-like directory is `plans/reports/ab-test/`.
   - Fix: This task's command is non-standard (`see \`...\``). The real issue is that `plans/reports/` is not a plan directory — it is the reports subdirectory shared across plans. The validator should skip paths where the extracted slug is `reports` (a known non-plan container). Alternatively, and more correctly: check whether the matched directory contains a recognized artifact; if not, look one level deeper. The simpler fix is to exclude `reports` from valid slugs.
   - **Status**: FIXED — excluded `reports` from valid slugs in `_PLAN_PATTERN` extraction path; emit no error for this task (the command format is non-standard and the task is blocked/non-standard, but the validator should not false-positive on container directories).

2. **Validator false positive: non-backtick-wrapped plan paths produce `parsed.command = None`**
   - Location: `src/claudeutils/validation/task_plans.py:41-42`, `tests/test_validation_task_plans.py`
   - Problem: `COMMAND_PATTERN` in `task_parsing.py` requires a backtick-wrapped command after an em dash. The `Review bootstrap work` task uses `/deliverable-review plans/bootstrap-tag-support` — no backtick wrapping — so `parsed.command` is `None`. The validator then emits "no plan reference in command" even though `plans/bootstrap-tag-support` is present in the line. The task line format is non-standard (missing backticks), but the validator's fallback should scan the raw line for a `plans/` reference rather than immediately erroring.
   - Fix: Two sub-fixes: (1) use `parsed.command or parsed.full_line` as search text — falls back to raw line when command is None; (2) change `_PLAN_PATTERN` from `plans/([^/]+)/` (requires trailing slash) to `plans/([^/\s` + r"`" + `'\"]+)` (slug terminated by whitespace/backtick/quote) so bare-slug paths like `plans/bootstrap-tag-support` (no trailing `/`) are captured.
   - **Status**: FIXED — raw-line fallback added; pattern updated to match slug-terminated paths.

### Minor Issues

1. **No test for nested `plans/reports/` false positive**
   - Location: `tests/test_validation_task_plans.py`
   - Note: The `Verb form AB test` case (command: `see \`plans/reports/ab-test/README.md\``) was not covered. A regression test would prevent re-introducing this false positive.
   - **Status**: FIXED — added test case.

2. **No test for non-backtick command with plan path**
   - Location: `tests/test_validation_task_plans.py`
   - Note: The `/deliverable-review plans/bootstrap-tag-support` format (no backticks) was not covered.
   - **Status**: FIXED — added test case.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: No opus-design-question references in active codebase | Satisfied | `grep -r opus-design-question` returns no results outside `plans/` and `tmp/` |
| FR-2: magic-query-log permission in settings.json | Satisfied | `settings.json:48` — `"Bash(agent-core/bin/magic-query-log:*)"` |
| FR-3: Handoff merge detection uses git-dirty check | Satisfied | `agent-core/skills/handoff/SKILL.md:27` — `git diff --name-only HEAD -- agents/session.md` |
| FR-4a: Plan-backed tasks rule in execute-rule.md | Satisfied | `execute-rule.md:216-218` — rule + validator cross-reference |
| FR-4b: Validator parses tasks, filters pending, extracts slug, checks dir+artifact, CLI wired | Satisfied (after fixes) | `task_plans.py` + `cli.py:90` |
| C-2: Terminal tasks exempt | Satisfied | `_PENDING_STATUSES = {" ", ">", "!"}` — excludes `x`, `-`, `†` |

---

## Fixes Applied

- `src/claudeutils/validation/task_plans.py` — added `_CONTAINER_DIRS` exclusion set; changed `_PLAN_PATTERN` to not require trailing slash; added `parsed.command or parsed.full_line` fallback for non-backtick-wrapped commands
- `tests/test_validation_task_plans.py` — added two regression tests for the fixed false positives

---

## Positive Observations

- `_PENDING_STATUSES` correctly covers all three pending states (`" "`, `">"`, `"!"`) and excludes all terminal states — matches C-2 exactly.
- Validator returns `[]` when `session_file` does not exist — correct graceful handling.
- CLI subcommand `task_plans` wired in both `_run_all_validators()` (batch) and as standalone `task-plans` subcommand — consistent with all other validators.
- FR-3 fix is minimal and precise: `git diff --name-only HEAD -- agents/session.md` is unambiguous, unlike a date comparison.
- FR-1 cleanup is thorough — grep confirms zero active references.
- `design-decisions.md` rewrite is clear and actionable; the replacement rule ("apply architectural principles from loaded context, state your reasoning") is better behavioral guidance than the deleted skill reference.
