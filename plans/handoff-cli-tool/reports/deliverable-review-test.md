# Test Review: handoff-cli-tool (Round 2)

## Fix Verification

**C#5 — amend+no-edit pipeline test:** FIXED
`test_commit_pipeline_errors.py:155` (`test_commit_amend_no_edit`). Integration test with real git repo: creates commit with "Original message", calls `commit_pipeline` with `options={"amend", "no-edit"}` and `message=None`, verifies `result.success is True` and git log preserves original message. Exercises the real `_git_commit` path with `--amend --no-edit` flags. Only precommit mocked.

**M#13 — no-vet skip test:** FIXED
`test_session_commit_validation.py:97` (`test_commit_skips_vet_when_no_vet`). Constructs `CommitInput` with `options={"no-vet"}`, mocks `vet_check`, asserts `vet_check.assert_not_called()`. Companion test `test_commit_default_calls_vet` (line 70) verifies the default path calls vet. Both directions now tested. Original `test_commit_no_vet` renamed for clarity.

**M#14 — strengthen `_git changes` assertion:** FIXED
`test_git_cli.py:101-107`. Assertions are now separate `assert` statements (conjunction): `"## Parent"`, `"README.md"`, `"modified content"`, and `"diff"` all verified independently. No `or` disjunction.

**M#15 — H-2 committed detection append mode:** FIXED
`test_session_handoff.py:217` (`test_write_completed_with_accumulated_content`) and `:234` (`test_write_completed_overwrites_not_appends`). First test pre-populates section with mixed old+new content, verifies old content replaced. Second test calls `write_completed` twice, verifies first write's content replaced by second (no accumulation). Both confirm the simplified implementation (all H-2 modes collapse to overwrite) works correctly.

**M#16 — `_validate` dispatch edge cases:** FIXED
`test_session_commit_validation.py:176` (`test_validate_stale_vet_failure`): mocks `vet_check` returning `passed=False, reason="stale", stale_info="report is 3 days old"`. Verifies `result.success is False`, output contains "stale" and "3 days old". Line 208 (`test_validate_unknown_reason`): mocks `vet_check` returning `reason=None`. Verifies output contains "unknown". Both exercise `_validate` through `commit_pipeline` (the real dispatch path).

**m-4 — fix weak CLI assertion:** FIXED
`test_session_commit_cli.py:102-104`. Assertions are separate `assert` statements: `result.exit_code == 1`, `"unreviewed" in result.output.lower()`, `"Vet" in result.output`. All must hold (conjunction). No `or` disjunction.

## New Findings

No new defects introduced by the rework.

Pre-existing issues noted (not introduced by rework, not in scope for this review):

- `test_session_commit_pipeline.py:65` and `:100` contain `or`-disjunction assertions (same class as the fixed M#14/m-4 findings, but in pre-existing tests not targeted by the rework)
- `_init_repo` helper duplication across 6 test files (deferred m-1 from round 1; notably `test_commit_pipeline_errors.py` now uses the shared `pytest_helpers.init_repo_at` while others still use local copies)

## Summary

- **Fix verification:** 6/6 FIXED (C#5, M#13, M#14, M#15, M#16, m-4)
- **New rework-introduced issues:** 0
- **Pre-existing issues noted:** 2 (deferred from round 1, not blocking)
