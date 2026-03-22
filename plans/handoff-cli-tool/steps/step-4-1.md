# Step 4.1

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Step 4.1: Missing test coverage

**Findings:** C#5, M#13, M#14, M#15, M#16, m-4

**Prerequisite:** Read each test file and corresponding production code.

**Tasks (batch — all test-only, no production changes):**

1. **C#5 — amend+no-edit pipeline test** → `test_session_commit_pipeline_ext.py`
   Integration test: construct `CommitInput` with `options={"amend", "no-edit"}` and `message=None`. Exercise `commit_pipeline`. Verify git commit used `--amend --no-edit` flags. Verify existing commit message preserved.

2. **M#13 — no-vet skip test** → `test_session_commit_validation.py`
   Add `test_commit_skips_vet_when_no_vet`. Construct input with `options={"no-vet"}`. Mock `vet_check`. Assert `vet_check` not called. (Existing `test_commit_no_vet` tests default path — rename to `test_commit_default_calls_vet` for clarity.)

3. **M#14 — strengthen changes assertion** → `test_git_cli.py:106`
   Change `or` assertion to `and`: verify output includes BOTH status text AND diff text.

4. **M#15 — H-2 append mode test** → `test_session_handoff.py`
   Add test: pre-populate Completed section with old content, call `write_completed` with new content. Verify old content replaced (current simplified implementation overwrites — test confirms this is correct for mode 2).

5. **M#16 — _validate edge cases** → `test_session_commit_validation.py`
   Add `test_validate_stale_vet_failure`: mock `vet_check` returning `VetResult(passed=False, reason="stale", stale_info="...")`. Verify output contains `stale` and `stale_info`. Add `test_validate_unknown_reason`: mock returning `reason=None`. Verify output contains `unknown`.

6. **m-4 — fix weak CLI assertion** → `test_session_commit_cli.py:103`
   Change `or` to `and` — verify both conditions hold.

**Verify:** `just test`
