# Fix Plan: Deliverable Review Majors (Diamond TDD)

## Structure

```
Phase 1: RED — 4 integration tests demonstrating bugs (all fail)
Phase 2: FIX — apply code changes (#4 → #2 → #1 → #3, trivial first)
Phase 3: GREEN — all 4 tests pass + full regression suite
```

## Phase 1: RED Tests

### Test A: parent_conflicts auto-resolves session.md

**File:** `tests/test_worktree_merge_routing.py`
**Bug:** merge.py:327-333 — `parent_conflicts` branch lists conflicts and exits 3 without running auto-resolution (resolve_session_md, resolve_learnings_md, agent-core --ours)
**Existing related test:** `test_merge_reports_and_exits_3_when_parent_conflicts` (line 237) — conflicts on src/feature.py only, no session.md

**Setup:**
- `repo_with_submodule` fixture
- Branch: modify `agents/session.md` (add task) + modify `src/conflict.py`
- Main: modify `agents/session.md` differently (add different task) + modify `src/conflict.py` differently
- `git merge --no-commit --no-ff branch` → conflicts on both files
- Leave both unresolved (state = `parent_conflicts`)

**RED assertion:**
```python
result = runner.invoke(worktree, ["merge", slug])
assert result.exit_code == 3
# BUG: session.md appears in conflict report (not auto-resolved)
assert "session.md" not in result.output  # FAILS — this is the bug
assert "conflict.py" in result.output     # only real conflict remains
```

**Why integration:** Exercises full `merge()` → `_detect_merge_state()` → `parent_conflicts` branch → auto-resolution pipeline.

### Test B: precommit failure forwards stdout

**File:** `tests/test_worktree_merge_correctness.py` (or new: `tests/test_worktree_merge_output.py`)
**Bug:** merge.py:313 — echoes `precommit_result.stderr` but drops `.stdout`
**Existing fixture:** `mock_precommit` always succeeds — need a failing variant

**Setup:**
- `repo_with_submodule` fixture
- Simple diverged branch (no conflicts)
- Replace `mock_precommit` with `mock_precommit_failure` that returns:
  - `returncode=1`, `stdout="LINT: unused import in merge.py\n"`, `stderr="precommit failed\n"`

**RED assertion:**
```python
result = runner.invoke(worktree, ["merge", slug])
assert result.exit_code == 1
assert "LINT: unused import" in result.output  # FAILS — stdout dropped
assert "precommit failed" in result.output     # passes (stderr already echoed)
```

**Why integration:** Tests the full merge → commit → precommit → output pipeline.

### Test C: submodule MERGE_HEAD not orphaned after clean parent merge

**File:** `tests/test_worktree_merge_submodule.py`
**Bug:** merge.py:131-181 — Phase 2 submodule merge fails, leaves MERGE_HEAD. Phase 3+4 succeed, exit 0. MERGE_HEAD persists.
**Existing related test:** `test_merge_continues_to_phase3_when_submodule_conflicts` (routing.py:138) — accepts `exit_code in (0, 3)` documenting the bug

**Setup:**
- `repo_with_submodule` fixture
- Branch: commit file to agent-core (creating submodule divergence) + commit non-conflicting file to parent
- Main: commit CONFLICTING file to agent-core (same path, different content) + commit non-conflicting file to parent
- No parent source conflicts — only agent-core conflicts

**RED assertion:**
```python
result = runner.invoke(worktree, ["merge", slug])
# BUG: exits 0 with orphaned MERGE_HEAD
agent_core = repo / "agent-core"
has_merge_head = subprocess.run(
    ["git", "-C", str(agent_core), "rev-parse", "--verify", "MERGE_HEAD"],
    capture_output=True, check=False,
).returncode == 0
assert not has_merge_head  # FAILS — MERGE_HEAD persists
```

**Design micro-decision (exit code):**
When parent merge is clean but submodule has unresolved MERGE_HEAD:
- Exit 3 (conflicts exist). SKILL.md Mode C already instructs "resolve and re-run."
- State machine: detected as `submodule_conflicts` on re-run, which routes to Phase 3+4.
- Fix approach: after Phase 4 commit succeeds, check agent-core for MERGE_HEAD. If present, emit conflict info and exit 3.

### Test D: resolve.py outputs to stdout not stderr

**File:** `tests/test_worktree_merge_session_resolution.py`
**Bug:** resolve.py:99,105 — `click.echo(..., err=True)` sends merge-path output to stderr
**Nature:** Unit test (triggering git-add failure in integration is fragile)

**Setup:**
- Mock `_git` to raise `CalledProcessError` on `("add", "agents/session.md")` call
- Call `resolve_session_md(["agents/session.md"], slug="test")`
- Capture stdout vs stderr

**RED assertion:**
```python
# BUG: message goes to stderr
assert "hash-object" in captured.out  # FAILS — went to stderr instead
```

**Alternative (simpler):** Since fix is 2 chars, verify via grep:
```python
import ast, inspect
source = inspect.getsource(resolve_session_md)
assert "err=True" not in source  # FAILS
```

Source inspection is brittle. Prefer the mock approach — it tests behavior.

## Phase 2: Fixes (trivial first)

### Fix #4: resolve.py err=True (2 chars)
- resolve.py:99 — delete `, err=True`
- resolve.py:105 — delete `, err=True`

### Fix #2: precommit stdout forwarding (~3 lines)
- merge.py:312-313 — add `click.echo(precommit_result.stdout)` before stderr line
- Consider: combine stdout+stderr, or emit stdout first (diagnostics before error label)

### Fix #1: parent_conflicts auto-resolution (~15 lines)
Extract auto-resolution from `_phase3_merge_parent:228-234` into helper, call from `parent_conflicts` branch at :327-333.

```python
# Extract helper
def _auto_resolve_known_conflicts(conflicts: list[str], slug: str) -> list[str]:
    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]
    conflicts = resolve_session_md(conflicts, slug=slug)
    conflicts = resolve_learnings_md(conflicts)
    return conflicts

# In parent_conflicts branch:
elif state == "parent_conflicts":
    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]
    conflicts = _auto_resolve_known_conflicts(conflicts, slug)
    if conflicts:
        click.echo(_format_conflict_report(conflicts, slug))
        raise SystemExit(3)
    # All conflicts auto-resolved — continue to commit
    _phase4_merge_commit_and_precommit(slug)
```

**Note:** If ALL conflicts are auto-resolvable, the branch should proceed to Phase 4 (commit), not exit 3. This is new behavior — needs a RED test variant.

### Fix #3: submodule MERGE_HEAD lifecycle (~15 lines)
After Phase 4 commit, check for agent-core MERGE_HEAD. If present, report and exit 3.

```python
# In _phase4_merge_commit_and_precommit, after _validate_merge_result:
submodule_path = Path("agent-core")
if submodule_path.exists() and (submodule_path / ".git").exists():
    sub_merge_head = subprocess.run(
        ["git", "-C", "agent-core", "rev-parse", "--verify", "MERGE_HEAD"],
        capture_output=True, check=False,
    )
    if sub_merge_head.returncode == 0:
        click.echo("Submodule agent-core has unresolved merge conflict")
        click.echo("Resolve in agent-core/, then re-run merge")
        raise SystemExit(3)
```

**Placement:** After precommit passes but as final check. The parent merge is committed; the submodule conflict is the remaining work.

## Phase 3: GREEN

1. Run all 4 new tests — all pass
2. `just test tests/test_worktree_merge_*.py` — full regression
3. `just precommit` — lint + format

## Interactions

- Fix #1 extracts helper from `_phase3_merge_parent` → refactor, not behavioral change to Phase 3 path
- Fix #3 adds check after Phase 4 → new behavior, doesn't change existing state routing
- Fixes #1 and #3 are independent: #1 changes `parent_conflicts` branch, #3 adds post-Phase-4 check
- Existing test `test_merge_continues_to_phase3_when_submodule_conflicts` (routing.py:138) currently accepts `exit_code in (0, 3)` — after Fix #3, tighten to assert specific exit code

## Model / Execution

- Sonnet session, single commit
- Vet the batch (>5 lines, behavioral changes)
- Update session.md pending tasks on completion
