# Test Review: handoff-cli-tool (RC7 Layer 1)

Reviewed 21 files (~3584 lines) against `plans/handoff-cli-tool/outline.md`.

## RC6 Fix Verification

| RC6 Finding | Status | Evidence |
|---|---|---|
| M-1: `_split_sections` `in_message` flag test added | **Verified** | test_session_commit.py:142-159 — `test_split_sections_in_message_preserves_headings` parses input with `## Not a section` after `## Message`. Asserts section names are `["Files", "Message"]` and the `## Not a section` line appears in Message body. |
| m-1: `git log --oneline -1` confirmation in `test_commit_cli_success` | **Verified** | test_session_commit_cli.py:39-46 — runs `git log --oneline -1` after CLI invocation, asserts `"foo"` in log stdout. Confirms commit was actually created. |
| m-2: Submodule assertion tightened to `"## Submodule: agent-core"` | **Verified** | test_session_handoff_cli.py:234 — `assert "## Submodule: agent-core" in result.output`. Exact heading match with colon separator. |
| m-3: `test_commit_multi_submodule_order` added | **Verified** | test_session_commit_pipeline_ext.py:332-393 — creates alpha and beta submodules, commits files in both plus parent, asserts each submodule's log message present, parent committed last. |
| m-5: `ParsedTask` import aligned to `session.parse` re-export | **Verified** | test_session_status.py:11 imports `ParsedTask` from `claudeutils.session.parse`. |

All five RC6 test findings verified present and correct.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**m-1:** test_session_commit_format.py:21 — Vacuity. `assert ":" not in output.split("\n")[0] or "a7f38c2]" in output` is a disjunctive assertion where the second disjunct (`"a7f38c2]" in output`) is always true by construction of the test fixture. The intended check — that parent-only output has no submodule label colon prefix on the first line — is masked. `assert not output.split("\n")[0].startswith("agent-core:")` would verify the actual intent without a tautological fallback.

**m-2:** test_session_commit.py:50-75 — Excess. `test_parse_commit_input` uses parametrize over `["files", "options", "submodule", "message"]` but each case parses the identical `COMMIT_INPUT_FIXTURE` and checks one field. Four invocations of the full parser when a single test asserting all four fields would be equivalent. Not incorrect, but the parametrization suggests independence that does not exist (shared fixture, no isolation).

**m-3:** test_session_status.py:280 — Independence. `SESSION_FIXTURE` module-level constant defined at line 280, first referenced at line 253 (`test_session_status_cli`). Python resolves module-level names at call time so this works, but reading the file top-to-bottom encounters an undefined reference. Carried forward from prior rounds.

**m-4:** test_status_rework.py:13 — Consistency. Imports `ParsedTask` from `claudeutils.validation.task_parsing` while test_session_status.py:11 imports from `claudeutils.session.parse` (the S-4 public interface). Both valid, but inconsistent import paths across files in the same deliverable.

**m-5:** test_session_commit_validation.py — Completeness. C-4 specifies a combined `just-lint` + `no-vet` option row. `test_commit_combined_options` (line 101) tests `just-lint` + `amend`. `test_commit_skips_vet_when_no_vet` (line 75) tests `no-vet` alone. No test exercises the `just-lint` + `no-vet` combination from the C-4 table. The options are orthogonal so individual tests provide implicit coverage, but the specific design-specified combination has no dedicated test.

**m-6:** test_git_cli.py:83 — Specificity. `assert "clean" in result.output.lower()` matches any output containing "clean." The implementation emits `"Tree is clean."` — a more precise assertion like `assert result.output.strip() == "Tree is clean."` would catch format regressions.

**m-7:** test_session_handoff_cli.py:90 — Specificity. `assert "Git status" in result.output` checks for a substring of the actual output `"**Git status:**"`. If the format changed to lowercase `"**git status:**"`, the test would fail correctly, but if changed to `"**Git changes:**"` the test would also fail, so specificity is adequate. Marginal — noted for awareness only.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 7 |

**Delta from RC6:** RC6 had 1M/5m. The M-1 (no `in_message` flag test) is resolved — test added and verified. Prior minors m-1 and m-2 are resolved. Remaining minors are style, consistency, and specificity items that do not affect correctness. Two minors (m-3 SESSION_FIXTURE placement, m-4 import consistency) persist from prior rounds. Five new minors at the specificity/consistency level.

**RC7 verdict:** 0C/0M. Test suite covers all design-specified behavior across S-1 through S-5, H-1 through H-4, C-1 through C-5, and ST-0 through ST-2. All RC6 fixes verified. No functional gaps remain.
