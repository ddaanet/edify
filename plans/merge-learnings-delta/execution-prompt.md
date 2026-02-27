# Merge Learnings Delta — Tier 2 TDD Execution

Paste this prompt to start execution. Do NOT use `/design` or `/runbook` — planning is complete.

## Phase 1: Context Loading

1. Read `agents/session.md` — task metadata, cycle descriptions, reference files
2. Read `plans/merge-learnings-delta/requirements.md` — FR-1 (6 test scenarios), FR-2 (reporting)
3. Read `plans/merge-learnings-delta/recall-artifact.md` — 9 entry keys

## Phase 2: Recall

Resolve these keys (single batch call). Output stays in your context — do not write to file.

```bash
agent-core/bin/when-resolve.py \
  "when preferring e2e over mocked subprocess" \
  "when test setup steps fail" \
  "when detecting vacuous assertions from skipped RED" \
  "when tests simulate merge workflows" \
  "when testing presentation vs behavior" \
  "when green phase verification includes lint" \
  "when fixture shadowing creates dead code" \
  "when test corpus defines correct behavior" \
  "when tdd cycles grow shared test file"
```

## Phase 3: Source Familiarization

Read these files (batch):
- `src/claudeutils/worktree/resolve.py` — `diff3_merge_segments()`, `_resolve_heading()`, `_resolve_one_sided_deletion()`
- `src/claudeutils/worktree/remerge.py` — `remerge_learnings_md()` (FR-2 modification target)
- `src/claudeutils/validation/learnings.py` — `parse_segments()`
- `tests/test_learnings_diff3.py` — existing pure-function tests (322 lines — do NOT add to this file)
- `tests/test_worktree_merge_learnings.py` — existing integration tests (150 lines)
- `tests/test_worktree_remerge_session.py` — pattern reference for `remerge_*` integration tests
- `tests/fixtures_worktree.py` — `init_repo`, `repo_with_submodule`, `mock_precommit`, `BranchSpec`

## Phase 4: Ping-Pong TDD Execution

### Protocol

Two specialized resumable agents alternate:

- **Agent R** — writes tests ONLY. Gate: `just red-lint` (lint passes, test fails on assertion). Must NOT write production code.
- **Agent G** — implements ONLY. Gate: `just lint` (lint passes, all tests pass). Must NOT write new tests.

Resume agents incrementally — R accumulates test-writing context, G accumulates implementation context.

### Gates

After each agent returns, verify the gate before proceeding:

```bash
# After Agent R:
just red-lint    # must pass (lint clean + test fails)

# After Agent G:
just lint        # must pass (lint clean + tests pass)
```

If gate fails, resume the same agent with the failure output.

### Recall Keys for Agent Prompts

Include these resolved entries (from Phase 2) in agent prompts as constraint-format rules:

**All cycles:**
- DO use real git repos with `tmp_path` fixtures, not mocked subprocess
- DO verify assertion strength when RED passes unexpectedly — mutate expected value, confirm failure
- DO NOT shadow pytest fixtures with local function definitions
- GREEN verification: `just check && just lint` (not just pytest)

**Cycle 6 additionally:**
- Branch must be the merged parent, not created at HEAD — `when tests simulate merge workflows`

**Cycle 7 additionally:**
- Test conditional output logic (behavior), not exact format string (presentation) — `when testing presentation vs behavior`

### Cycle Execution

**New file for ALL cycles:** `tests/test_learnings_consolidation.py`

#### Cycles 1-5: Characterization Batch (Single Agent R)

These test EXISTING behavior — `diff3_merge_segments()` already handles consolidation correctly. Tests will pass immediately. Agent R writes all 5 tests, verifies each passes, verifies assertion strength (mutate expected → confirm failure).

No Agent G needed — no production code changes.

Launch Agent R (sonnet, test-driver):

```
Write 5 pure-function tests in tests/test_learnings_consolidation.py in a class TestConsolidationScenarios.

Import diff3_merge_segments from claudeutils.worktree.resolve.

Each test calls diff3_merge_segments(base, ours, theirs) with segment dicts. Segment keys are heading strings (e.g., "When analyzing X"), values are body line lists (e.g., ["- bullet"]).

Include a preamble segment (key "") in all three dicts: ["# Learnings", "", "---"].

Test 1 — consolidation_with_new_entries:
  base: preamble + A, B, C (3 entries)
  ours: preamble + C only (A,B consolidated away)
  theirs: preamble + A, B, C, E (pre-consolidation + new E)
  Assert: merged has C and E only. A and B absent. No conflicts.

Test 2 — consolidation_no_new_entries:
  base: preamble + A, B, C
  ours: preamble + C only
  theirs: preamble + A, B, C (unchanged from base)
  Assert: merged has C only. A and B absent. No conflicts.

Test 3 — modified_consolidated_away_entry:
  base: preamble + A, B
  ours: preamble + B only (A consolidated)
  theirs: preamble + A-modified-body, B
  Assert: "When A" (or whatever heading) in conflicts list.

Test 4 — modified_surviving_entry:
  base: preamble + A, B
  ours: preamble + B only (A consolidated)
  theirs: preamble + A, B-modified-body
  Assert: merged has B with modified body. A absent. No conflicts.

Test 5 — no_consolidation_both_added:
  base: preamble + A
  ours: preamble + A, B (added B)
  theirs: preamble + A, C (added C)
  Assert: merged has A, B, C. No conflicts.

These tests exercise EXISTING behavior — they WILL pass immediately. After writing each test:
1. Run pytest tests/test_learnings_consolidation.py -x -q
2. Verify it passes
3. Verify assertion strength: temporarily change an expected value, confirm test fails, revert

After all 5: run just red-lint — should PASS (all tests pass, lint clean).
Wait — these are characterization tests that pass. red-lint expects a failing test.
Instead: run just check to verify lint. Then run pytest on the file to verify all pass.

[Recall constraints — include resolved content from Phase 2 recall here]
```

After Agent R returns, verify: `just check && pytest tests/test_learnings_consolidation.py -x -q`

Commit: `/commit --test` (WIP checkpoint)

#### Cycle 6: Integration — Both Merge Directions (Ping-Pong)

**Agent R** (resume from cycles 1-5):

```
Add two integration tests to tests/test_learnings_consolidation.py in a new class TestConsolidationIntegration.

Use init_repo fixture from tests/fixtures_worktree.py (import the fixture — pytest discovers it from fixtures_worktree.py which is a conftest-like module).

Pattern reference: tests/test_worktree_remerge_session.py — shows how to set up real git repos with branches, merge --no-commit, and call remerge functions.

Test 6a — branch_to_main_consolidation:
  Setup real git repo (tmp_path + init_repo fixture).
  1. Commit learnings.md with 3 entries (A, B, C) on main
  2. Create branch, diverge
  3. On main: consolidate — rewrite learnings.md with C only (remove A, B)
  4. On branch: add new entry E (learnings has A, B, C, E)
  5. git merge --no-commit --no-ff branch (from main)
  6. monkeypatch.chdir(repo), call remerge_learnings_md()
  7. Assert: result has C and E only. A, B absent. File staged.

Test 6b — main_to_branch_consolidation:
  Same setup but reversed:
  1. Commit learnings.md with A, B, C on main
  2. Create branch with A, B, C
  3. On main: consolidate to C only
  4. On branch: add E (has A, B, C, E)
  5. From branch: git merge --no-commit --no-ff main
  6. Call remerge_learnings_md()
  7. Assert: result has C and E only. A, B absent.

These test remerge_learnings_md from remerge.py — import it.
These are characterization tests (code works). Verify they pass + assertion strength.

Import: from claudeutils.worktree.remerge import remerge_learnings_md

[Recall constraints — include resolved content]
```

Gate: `just check && pytest tests/test_learnings_consolidation.py -x -q`

Commit: `/commit --test`

#### Cycle 7: FR-2 Reporting (Genuine Ping-Pong)

**Agent R** (resume):

```
Add reporting tests to tests/test_learnings_consolidation.py in a new class TestMergeReporting.

Test 7a — reports_counts_when_segments_change:
  Setup real git repo with consolidation scenario (reuse pattern from cycle 6a).
  After remerge_learnings_md(), capture click output.
  Assert output contains: "learnings.md: kept N + appended M new (dropped K consolidated)"
  With correct counts for the scenario.

  To capture click output: use click.testing.CliRunner or monkeypatch click.echo,
  or since remerge_learnings_md uses click.echo, capture via capsys or
  redirect. Check how existing tests capture click output.

Test 7b — silent_on_noop:
  Setup repo where learnings.md is identical on both sides (no divergence).
  After remerge_learnings_md(), assert NO output produced (no click.echo call).

These tests MUST FAIL (RED) — the reporting code doesn't exist yet.
Run: just red-lint — must pass (lint clean, tests fail on assertion).

[Recall constraints — include resolved content]
```

Gate: `just red-lint` — must pass.

**Agent G** (new agent, sonnet):

```
Make the failing tests in tests/test_learnings_consolidation.py::TestMergeReporting pass.

Read the test file to understand what's expected.
Read src/claudeutils/worktree/remerge.py — modify remerge_learnings_md().

Add reporting logic after the merge succeeds (after writing merged content, before git add):
1. Count segments (excluding preamble key ""):
   - kept: entries in merged that were also in ours_segs
   - appended: entries in merged that were NOT in ours_segs
   - dropped: entries in theirs_segs that are NOT in merged (and were in base — consolidation removed)
2. If any change (appended > 0 or dropped > 0):
   click.echo(f"learnings.md: kept {kept} + appended {appended} new (dropped {dropped} consolidated)")
3. If no change: no output

Gate: just lint (all tests pass, lint clean)

[Recall constraints — include resolved content]
```

Gate: `just lint` — must pass.

Commit: `/commit --test`

## Phase 5: Final Validation + Commit

```bash
just precommit
```

If passing: `/commit` (full commit, not WIP).

Then: `/handoff --commit` to update session.md and commit.
