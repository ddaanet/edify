# Cycle 4.1

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.1: Conflict output — all FR-4 fields present

**Prerequisite:** Read `src/claudeutils/worktree/merge.py` (current state after Phases 1-3 are implemented) to identify both call sites where `_format_conflict_report` must be invoked: the `parent_conflicts` branch in `merge()` and the `if conflicts:` block in `_phase3_merge_parent`.

**RED Phase:**

**Test:** `test_conflict_output_contains_all_fields`
**File:** `tests/test_worktree_merge_conflicts.py`

**Assertions:**
- When merge produces a source file conflict and exits 3, output contains:
  - Conflicted filename (e.g., `src/feature.py`)
  - Conflict type label — at minimum one of: `UU` (both modified), `AU` (added by us), `DU` (deleted by us)
  - A line containing `|` indicating diff stat format (e.g., `src/feature.py | 3 +++`)
  - A line matching the divergence format: starts with `"Branch: "` followed by a digit (e.g., `"Branch: 1 commits ahead, Main: 0 commits ahead since merge-base"`)
  - Hint line containing: `"Resolve conflicts"` AND `"claudeutils _worktree merge"` AND the slug value

**Expected failure:** Current Phase 3 Cycle 3.1 implementation outputs a basic conflict list without any diff stats, divergence info, or hint → assertions for diff stat, divergence, and hint fields fail.

**Why it fails:** `_format_conflict_report` does not yet exist. After Phase 3 is implemented, the conflict exit path emits conflict file names and exits 3 — but no diff stats, divergence section, or hint. The test for those fields does not exist yet (collection error), then fails on missing fields once written.

**Verify RED:** `pytest tests/test_worktree_merge_conflicts.py::test_conflict_output_contains_all_fields -v`

**Test setup:**
1. Create repo, branch with a unique source file (`src/feature.py`), main with conflicting content in same file
2. Monkeypatch chdir. Use `mock_precommit` fixture.
3. Invoke `worktree merge slug` via CliRunner
4. Assert exit_code == 3
5. Assert all output field patterns in `result.output`

**Note:** The test captures `result.output` (stdout) from CliRunner. With D-8 (all output to stdout), this works without stderr capture. Phase 5 handles the full stdout migration; for Phase 4, the conflict report output should use `click.echo()` (stdout, default).

**GREEN Phase:**

**Implementation:** Add `_format_conflict_report(conflicts: list[str], slug: str) -> str` and call it from both conflict exit sites.

**Behavior:**
- Build output string with sections:
  - Header: "Conflicts in merge of `{slug}`:"
  - For each file in `conflicts`: get conflict type from `git status --short` (2-char status code), print as `  {type} {file}`
  - For each file: run `git diff --stat MERGE_HEAD -- {file}` and include the stat line(s) indented
  - Divergence section: run `git rev-list --count HEAD..{slug}` and `git rev-list --count {slug}..HEAD`, format as "Branch: N commits ahead, Main: M commits ahead since merge-base"
  - Hint line: `"Resolve conflicts, git add, then re-run: claudeutils _worktree merge {slug}"`
- Return the complete string
- Call sites: replace `click.echo(<conflict list>)` + `raise SystemExit(3)` with `click.echo(_format_conflict_report(conflicts, slug))` + `raise SystemExit(3)` at both locations

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `_format_conflict_report(conflicts: list[str], slug: str) -> str` function. Update both call sites (`_phase3_merge_parent` and `parent_conflicts` branch in `merge()`) to call it.
  Location hint: Place function after `_format_git_error` (near top of file, with other formatting helpers). Call sites: `_phase3_merge_parent` if-conflicts block, and `parent_conflicts` case in `merge()` dispatch.

**Verify GREEN:**
- `pytest tests/test_worktree_merge_conflicts.py::test_conflict_output_contains_all_fields -v`
- `pytest tests/ -k "merge" -v`

---

**Phase 4 STOP conditions:**
- `git diff --stat MERGE_HEAD -- <file>` returns empty → STOP, MERGE_HEAD not present at this point (verify state machine routing)
- `git rev-list --count HEAD..{slug}` fails → STOP, slug branch may not be reachable (check branch exists)
- Both call sites not updated → STOP, one path omits the formatted report (grep for `SystemExit(3)` in merge.py, verify both use `_format_conflict_report`)
