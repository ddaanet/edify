# Deliverable Review: handoff-cli-tool

**Date:** 2026-03-21
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 25 | +1573 | -62 | +1511 |
| Test | 15 | +2506 | -6 | +2500 |
| Agentic prose | 1 | +5 | -1 | +4 |
| Configuration | 1 | +9 | -1 | +8 |
| **Total** | **42** | **+4093** | **-70** | **+4023** |

**Review methodology:** Layer 1 (three opus agents: code, test, prose+config) + Layer 2 (interactive cross-cutting).

**Design conformance summary:** Core parsing (commit, handoff, session.md), git extraction (S-2, S-5), and commit gates (C-1, C-3, C-5) are well-implemented. Handoff pipeline (H-1 through H-4) works correctly. Status subcommand has significant functional completeness gaps against the outline. Commit pipeline has two critical error-handling issues.

## Critical Findings

### 1. SKILL.md allowed-tools blocks Step 7 precommit gate

- **File:** `agent-core/skills/handoff/SKILL.md:4`
- **Axis:** Functional correctness
- **Design req:** Coupled skill update — "Handoff skill must add `just precommit` as a pre-handoff gate"
- **Impact:** Step 7 instructs agent to run `just precommit`. Frontmatter declares `allowed-tools: Read, Write, Edit, Bash(wc:*), Task, Skill`. The `Bash(wc:*)` pattern restricts Bash to `wc` commands only — `just precommit` is blocked. The precommit gate cannot execute.
- **Source:** Prose Layer 1

### 2. `_git_commit` ignores non-zero exit code

- **File:** `src/claudeutils/session/commit_pipeline.py:77-84`
- **Axis:** Robustness, error signaling
- **Design req:** S-3 — exit code carries semantic signal
- **Impact:** `_git_commit()` uses `check=False` and returns `result.stdout.strip()` without checking `result.returncode`. `commit_pipeline()` unconditionally wraps this in `CommitResult(success=True)`. Git commit failures (hook rejection, lock contention, nothing staged after validation) are silently reported as success. Same issue in `_commit_submodule()` (line 134-148).
- **Source:** Code Layer 1 (CR-1)

### 3. Submodule committed before validation gate

- **File:** `src/claudeutils/session/commit_pipeline.py:254-273`
- **Axis:** Conformance, robustness
- **Design req:** Pipeline ordering — "validate → vet check → precommit → stage → submodule commit → parent commit"
- **Impact:** Implementation commits submodules (line 256-264) and stages parent files (line 267-268) before running the validation gate (line 271). If precommit or vet check fails after submodule commit, submodule has an irrevocable commit but parent doesn't — inconsistent state requiring manual recovery.
- **Source:** Code Layer 1 (CR-2), Layer 2

### 4. Exit code semantics: clean-file error returns exit 1, design says exit 2

- **File:** `src/claudeutils/session/cli.py:31-32`
- **Axis:** Conformance, error signaling
- **Design req:** S-3 — "0=success, 1=pipeline error, 2=input validation." Design output example: "Clean-files error (exit 2)"
- **Impact:** `CleanFileError` from `commit_pipeline` returns `CommitResult(success=False)`. CLI line 32 exits 1 for all `success=False` results. Clean-file errors are input validation (caller listed files with no changes) and should exit 2 per design. The calling agent uses exit codes to distinguish retryable errors from malformed input.
- **Source:** Test Layer 1 (C-1)

### 5. No test for amend+no-edit pipeline path

- **File:** `tests/test_session_commit_pipeline_ext.py`
- **Axis:** Functional completeness
- **Design req:** C-5 — "`no-edit` keeps existing commit message — `## Message` section omitted"
- **Impact:** Parser test validates `amend+no-edit` parses without `## Message`. No pipeline test exercises the actual `git commit --amend --no-edit` path through `commit_pipeline`. The `_git_commit` function's `--no-edit` flag has zero integration coverage.
- **Source:** Test Layer 1 (C-2)

## Major Findings

### 6. `handoff/context.py` is dead code

- **File:** `src/claudeutils/session/handoff/context.py` (all 45 lines)
- **Axis:** Vacuity, excess
- **Impact:** `PrecommitResult` and `format_diagnostics()` are defined and tested (`test_session_handoff.py:291-330`) but never imported by production code. Handoff CLI runs git status/diff inline (cli.py:57-72). Written for an earlier design where CLI ran precommit internally, removed during checkpoint-4 review.
- **Source:** Code Layer 1 (MJ-4), Test Layer 1 (M-7), Layer 2

### 7. Status: plan state discovery not implemented

- **File:** `src/claudeutils/session/status/cli.py:31-34, 55-60`
- **Axis:** Functional completeness
- **Design req:** Status pipeline step 2 — "claudeutils _worktree ls for plan states and worktree info"
- **Impact:** `plan_states` populated with empty strings (line 34). `render_unscheduled({}, ...)` always receives empty dict. Rendered output shows `Status: ` (blank). Plan lifecycle states never read from filesystem. Comment says "Plan discovery deferred to Phase 4+" but no such phase exists in the runbook.
- **Source:** Code Layer 1 (MJ-2), Test Layer 1 (M-6), Layer 2

### 8. Status: session continuation header missing

- **File:** `src/claudeutils/session/status/cli.py`, `src/claudeutils/session/status/render.py`
- **Axis:** Functional completeness
- **Design req:** "When git tree is dirty, prepend `Session: uncommitted changes — /handoff, /commit`. If any plan-associated task has status review-pending, append `/deliverable-review plans/<name>`."
- **Impact:** Feature entirely absent. Status never checks git dirty state or renders the continuation header.
- **Source:** Code Layer 1 (MJ-1), Test Layer 1 (M-2), Layer 2

### 9. Status: output format diverges from design

- **File:** `src/claudeutils/session/status/render.py:8-31, 34-57`
- **Axis:** Conformance
- **Design req:** "Next-task metadata merged into the in-tree item with ▶ marker. Suppress Next: section when it duplicates the first in-tree task."
- **Impact:** Implementation renders separate `Next:` section (always, even single-task) using `Next: <name>` format without `▶`. `render_pending` uses `- <name>` for all tasks without distinguishing first. Also: restart metadata omitted from In-tree listing (only shown in Next section).
- **Source:** Code Layer 1 (MJ-3, MN-4), Layer 2

### 10. `git_status()` corrupts first porcelain line

- **File:** `src/claudeutils/git.py:84-98`
- **Axis:** Functional correctness
- **Design req:** S-5 — mechanical git queries
- **Impact:** Returns `result.stdout.strip()` — removes leading space from first porcelain line. ` M file.py` becomes `M file.py`, corrupting the XY status code. Consumer `_prefix_status_lines()` in `git_cli.py` parses `line[:3]` as status — corrupted first line yields wrong status+path. Same bug class documented in learnings.md ("When parsing git status porcelain format"). `commit_gate.py:_dirty_files()` correctly uses raw `result.stdout.splitlines()`.
- **Source:** Code Layer 1 (MJ-5)

### 11. Handoff diagnostics don't use `_git changes` utility

- **File:** `src/claudeutils/session/handoff/cli.py:57-72`
- **Axis:** Conformance
- **Design req:** S-5 — "Consumers: commit skill (input construction), handoff CLI (H-3 diagnostics)"
- **Impact:** Handoff CLI uses inline `subprocess.run` for git status/diff. Doesn't use the `_git changes` utility which provides submodule-aware output. If submodule changes exist, handoff diagnostics won't show them.
- **Source:** Layer 2

### 12. Status: old format enforcement missing

- **File:** `src/claudeutils/session/status/cli.py`, `src/claudeutils/session/parse.py`
- **Axis:** Conformance
- **Design req:** ST-2 — "Old format (no metadata) → fatal error (exit 2). Mandatory metadata enforces plan-backed task rule."
- **Impact:** Parser silently skips unparseable task lines (returns `None`, filtered out). Status CLI never validates that parsed tasks have required metadata. Old-format sessions render without error.
- **Source:** Test Layer 1 (M-8), Layer 2

### 13. `test_commit_no_vet` tests wrong direction

- **File:** `tests/test_session_commit_validation.py:70-92`
- **Axis:** Specificity, vacuity
- **Design req:** C-4 — `no-vet` option skips vet check
- **Impact:** Docstring says "Default pipeline calls vet_check." Tests that vet IS called when `no-vet` is NOT in options. No test verifies that when `no-vet` IS in options, `vet_check` is NOT called. The `no-vet` path from C-4 has no pipeline-level test.
- **Source:** Test Layer 1 (M-1)

### 14. `_git changes` test uses weak assertion

- **File:** `tests/test_git_cli.py:106`
- **Axis:** Specificity
- **Design req:** S-5 — output "includes both the file list and the diff"
- **Impact:** Assertion uses `or`: `assert "modified content" in result.output or "diff" in result.output.lower()`. Design says output includes both status and diff — test should verify both are present, not either/or.
- **Source:** Test Layer 1 (M-3)

### 15. H-2 committed detection modes not fully tested

- **File:** `tests/test_session_handoff.py`
- **Axis:** Functional completeness
- **Design req:** H-2 — three modes based on diff against HEAD
- **Impact:** Mode 1 (overwrite) tested. Mode 3 (auto-strip) partially tested. Mode 2 (append after agent cleared old) untested. Implementation delegates all to single overwrite, which is a valid simplification, but the append scenario is not verified.
- **Source:** Test Layer 1 (M-4)

### 16. No test for `_validate` dispatch edge cases

- **File:** `tests/test_session_commit_validation.py`
- **Axis:** Coverage
- **Design req:** C-4 — validation levels
- **Impact:** `_validate()` function's vet failure paths (stale reason formatting, unknown reason) have no direct test coverage.
- **Source:** Test Layer 1 (M-5)

## Minor Findings

**Code (5):**
- **MN-1:** Uncaught `CalledProcessError` from `_stage_files` (check=True) — unhandled traceback instead of structured `CommitResult`. Same for `_commit_submodule` git add. (`commit_pipeline.py:52-59, 267-268`)
- **MN-2:** `_fail` duplicated in `git.py` and `worktree/cli.py`. Pre-existing; extraction was opportunity to remove. (`git.py:33-39`)
- **MN-3:** `_strip_hints` only filters `hint:` prefix. Low risk — covers common case. (`commit_pipeline.py:187-189`)
- **MN-5:** Plan status renders `Status: ` (empty value) when plan discovery is deferred. Should omit or show placeholder. (`render.py:54-56`)
- **No ANSI coloring:** Design says "ANSI-colored structured text." No colors in render.py.

**Test (5):**
- **m-1:** `_init_repo` helper duplicated across 6 test files. Should use shared `pytest_helpers.init_repo_at`.
- **m-2:** `_build_dependency_edges` blocker matching joins all text; two unrelated blockers mentioning different tasks would falsely create dependency. (`test_session_status.py:263-271`)
- **m-3:** `SESSION_FIXTURE` defined after first use at line 281, definition at line 308. (`test_session_status.py`)
- **m-4:** Weak disjunction in vet check CLI test assertion. (`test_session_commit_cli.py:103`)
- **m-5:** `test_commit_amend_parent` uses `len(commits) == 2` without explaining init commit. (`test_session_commit_pipeline_ext.py:282`)

**Prose+Config (2):**
- **settings.local.json** not a plan deliverable — incidental environmental change.
- **Pre-existing:** Missing `Bash(git diff:*)` in SKILL.md for Step 1 prior-handoff detection. Not introduced by this deliverable.

## Gap Analysis

| Design Requirement | Status | Reference |
|--------------------|--------|-----------|
| `_handoff` command | Covered | `session/handoff/cli.py` |
| `_commit` command | Covered (with Critical issues #2, #3, #4) | `session/cli.py`, `commit_pipeline.py` |
| `_status` command | Partial (Major gaps #7, #8, #9, #12) | `session/status/cli.py` |
| S-2: `_git()` extraction | Covered | `git.py` |
| S-3: Output/error conventions | Partial (Critical #4: exit code semantics) | `cli.py`, `git.py` |
| S-4: Session.md parser | Covered | `session/parse.py` |
| S-5: `_git changes` utility | Covered (Major #10: `git_status()` strip bug) | `git_cli.py` |
| H-1: Domain boundaries | Covered | |
| H-2: Completed section write mode | Covered (simplified) | `handoff/pipeline.py` |
| H-3: Diagnostic output | Partial (Major #11: doesn't use `_git changes`) | `handoff/cli.py` |
| H-4: State caching | Covered | `handoff/pipeline.py` |
| C-1: Scripted vet check | Covered | `commit_gate.py` |
| C-2: Submodule coordination | Covered (Critical #3: ordering) | `commit_pipeline.py` |
| C-3: Input validation | Covered | `commit_gate.py` |
| C-4: Validation levels | Covered | `commit_pipeline.py` |
| C-5: Amend semantics | Covered (Critical #5: no test) | `commit_pipeline.py` |
| ST-0: Worktree-destined tasks | Covered | `render.py` |
| ST-1: Parallel detection | Covered | `render.py` |
| ST-2: Preconditions/degradation | Partial (Major #12: old format not enforced) | `status/cli.py` |
| Coupled skill update | Broken (Critical #1: allowed-tools) | `SKILL.md` |
| Registration in `cli.py` | Covered | `cli.py:155-158` |
| Tests | Covered (with gaps per Major #13-16) | 15 test files |

**Missing deliverables:** None (all specified deliverables produced).
**Unspecified deliverables:** `handoff/context.py` (Major #6 — dead code), `pytest_helpers.py` additions (justified — shared test infrastructure).

## Summary

| Severity | Count |
|----------|-------|
| Critical | 5 |
| Major | 11 |
| Minor | 12 |

Core infrastructure (git helpers, parsers, commit gates, handoff pipeline) is solid. Issues concentrate in two areas: (1) commit pipeline error handling and ordering — three Critical findings affect correctness; (2) status subcommand functional completeness — four Major findings for unimplemented design features. The SKILL.md allowed-tools gap prevents the precommit gate from executing.
