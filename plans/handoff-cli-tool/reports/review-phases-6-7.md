# Runbook Review: Phase 6 + Phase 7

**Artifact**: `plans/handoff-cli-tool/runbook-phase-6.md`, `plans/handoff-cli-tool/runbook-phase-7.md`
**Date**: 2026-03-07T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (Phase 6: 6 cycles, Phase 7: 4 cycles)

## Summary

Phase 6 had four fixable issues: a behavioral vacuity caused by 6.1 GREEN over-specifying validation dispatch (making 6.4 RED unable to fail), two prescriptive GREEN phases (6.4 and 6.6), a prescriptive function signature in 6.5 GREEN, and a vague 6.6 RED assertion. Phase 7 had one minor ambiguity in the 7.3 integration test setup instruction. All issues fixed.

**Overall Assessment**: Ready

---

## Findings

### Critical Issues

1. **Behavioral vacuity — Cycle 6.4 RED cannot fail against 6.1 GREEN**
   - Location: Cycle 6.1 GREEN, Cycle 6.4 RED
   - Problem: 6.1 GREEN described validation dispatch: "Run validation: `just precommit` (default) or `just lint` (if `just-lint` in options)". This means the 6.1 implementation already handles `just-lint` dispatch. 6.4 RED's "Expected failure: Options not affecting validation behavior / Why it fails: No option dispatch" would not hold — the test would pass immediately. Behavioral vacuity: 6.4 adds no new constraint beyond 6.1.
   - Fix: Removed option dispatch from 6.1 GREEN (minimal implementation: always runs `just precommit`, defers dispatch to 6.4). Added cross-reference note in 6.1 GREEN: "validation level dispatch added in Cycle 6.4". Removed `just-lint` mention from 6.1 RED assertions.
   - **Status**: FIXED

### Major Issues

2. **Prescriptive code in Cycle 6.4 GREEN**
   - Location: Cycle 6.4 GREEN, Behavior section
   - Problem: `subprocess.run(["just", "lint"])` prescribes the exact call, bypassing the established `_git()`/subprocess wrapper abstraction. The implementation should dispatch to the correct validation command, but the exact call form is implementation detail.
   - Fix: Replaced with behavioral description: "run `just lint` instead of `just precommit`" without prescribing the exact subprocess invocation.
   - **Status**: FIXED

3. **Prescriptive registration code in Cycle 6.6 GREEN**
   - Location: Cycle 6.6 GREEN, Changes section for `session/cli.py`
   - Problem: `from claudeutils.session.commit.cli import commit; session_group.add_command(commit)` is exact implementation code, not behavioral guidance. Agent becomes a copier rather than an implementer.
   - Fix: Replaced with behavioral instruction referencing the established pattern: "Import and register the commit command with the session group (same pattern as worktree subcommand registration in main cli.py)".
   - **Status**: FIXED

4. **Prescriptive function signature in Cycle 6.5 GREEN**
   - Location: Cycle 6.5 GREEN, Behavior section
   - Problem: `format_commit_output(submodule_outputs: dict[str, str], parent_output: str, warnings: list[str]) -> str` prescribes the exact signature with type annotations. The behavior (separate submodule outputs, parent output, warnings) should be described, not the exact parameter names and types.
   - Fix: Replaced with behavioral description: "Extract output formatting to a dedicated function that accepts submodule outputs (keyed by path), parent output string, and any warning messages."
   - **Status**: FIXED

### Minor Issues

5. **Vague RED assertion in Cycle 6.6**
   - Location: Cycle 6.6 RED, first assertion
   - Problem: "stdout contains git commit output" does not constrain what "git commit output" means. An executor could write a test asserting any non-empty stdout and satisfy this description.
   - Fix: Replaced with specific format: "stdout contains `[branch hash] message` format line". Added "real git repo via `tmp_path`, file staged" context to clarify test setup. Added specific error text for empty-stdin case: "stdout contains `**Error:**` and references missing required section".
   - **Status**: FIXED

6. **Ambiguous test setup instruction in Cycle 7.3 RED**
   - Location: Cycle 7.3 RED, "Assertions — parent-only" section
   - Problem: "Create dirty file in `tmp_path` repo, stage manually to verify" — ambiguous. "Stage manually to verify" could mean: stage the file before CLI invocation (which would bypass the CLI's staging logic), or verify staging via git status. The test intends to exercise CLI-driven staging.
   - Fix: Replaced with "Create modified file in `tmp_path` repo (uncommitted change, appears in `git status --porcelain`)" — unambiguous setup, no mention of pre-staging.
   - **Status**: FIXED

---

## Fixes Applied

- **6.1 GREEN Behavior**: Removed option dispatch mention; added cross-reference note pointing to 6.4
- **6.1 RED Assertions**: Removed `just-lint` option branch from assertion text
- **6.4 GREEN Behavior**: Replaced `subprocess.run(["just", "lint"])` with behavioral dispatch description
- **6.5 GREEN Behavior**: Replaced prescriptive function signature with behavioral description of inputs and outputs
- **6.6 GREEN Changes (session/cli.py)**: Replaced exact import/registration code with behavioral pattern reference
- **6.6 RED Assertions**: Added format specifics (`[branch hash] message`), added setup context, specified empty-stdin error text
- **7.3 RED Assertions (parent-only)**: Replaced ambiguous "stage manually to verify" with clear uncommitted-change setup description

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
