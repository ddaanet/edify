# Fix Runbook: RC9 Findings

**Source:** plans/handoff-cli-tool/reports/deliverable-review.md
**Classification:** Mixed — Simple (m-1..m-7, m-9) + Moderate (M-1, m-10)
**Tier:** 2 (Lightweight Delegation)

## Pending Task Before Start

m-8 (`_AGENT_CORE_PATTERNS` hardcoded submodule name) is a design-level deferral per outline.md C-1. Do NOT fix inline. Create a pending task entry:
- "Submodule vet config" plan already exists at `plans/submodule-vet-config/brief.md` — no new task needed; m-8 is already tracked there.

---

## Phase 1: TDD — M-1 vet_check cwd path fix (type: tdd)

**Bug:** `commit_gate.py:159` — `Path(f).exists()` resolves against process cwd, ignoring the `cwd` parameter. Every other call site in the function correctly threads `cwd`. When process cwd differs from `cwd`, `matched_paths` is empty → `vet_check` returns `passed=True` silently.

**Fix:** `(Path(cwd or ".") / f).exists()`

### Cycle 1.1: RED — test vet_check respects explicit cwd

**Target file:** `tests/test_session_commit.py` (append after existing vet_check tests, before any other section)

**Test description:**
```
def test_vet_check_stale_with_explicit_cwd(tmp_path: Path) -> None:
    """vet_check with explicit cwd detects stale even without monkeypatch.chdir."""
```

**Setup:**
1. Write `pyproject.toml` with `require-review = ["src/**/*.py"]` in `tmp_path`
2. Create `plans/bar/reports/vet-review.md` in `tmp_path`, set mtime 10s in the past
3. Create `tmp_path/src/foo.py` (newer mtime — source is stale)
4. **Do NOT call `monkeypatch.chdir`** — process cwd is NOT `tmp_path`

**Call:** `vet_check(["src/foo.py"], cwd=tmp_path)`

**Assertions:** `result.passed is False` and `result.reason == "stale"`

**Expected RED:** Without fix, `Path("src/foo.py").exists()` resolves against process cwd → returns `False` → `matched_paths = []` → function returns `passed=True` → test fails.

**Verify RED:** `just test tests/test_session_commit.py::test_vet_check_stale_with_explicit_cwd` fails.

### Cycle 1.1: GREEN — fix path resolution in vet_check

**Target file:** `src/claudeutils/session/commit_gate.py`, line 159

**Change:**
```python
# Before:
matched_paths = [Path(f) for f in matched if Path(f).exists()]
# After:
matched_paths = [Path(cwd or ".") / f for f in matched if (Path(cwd or ".") / f).exists()]
```

Note: `matched_paths` is passed to `_newest_file` which calls `.stat().st_mtime` — paths must be absolute or correctly rooted. Using `Path(cwd or ".") / f` ensures resolution against repo root.

**Verify GREEN:** `just check && just test tests/test_session_commit.py` — all pass.

---

## Phase 2: TDD — m-10 parent_output empty guard (type: tdd)

**Bug:** `commit_pipeline.py:234` — `parts.append(_strip_hints(parent_output))` unconditional. When `parent_output=""` with submodule outputs present, appends an empty string → `"\n".join(parts)` ends with spurious `"\n"`.

**Fix:** `if parent_output: parts.append(_strip_hints(parent_output))`

### Cycle 2.1: RED — test empty parent_output with submodule

**Target file:** `tests/test_session_commit_format.py` (append after existing tests)

**Test description:**
```
def test_format_empty_parent_with_submodule() -> None:
    """Empty parent_output with submodule output → no trailing newline."""
```

**Call:** `format_commit_output(submodule_outputs={"agent-core": "commit msg"}, parent_output="")`

**Assertion:** `not output.endswith("\n")`

**Expected RED:** Without fix, parts ends with `""` → `"\n".join(...)` ends with `"\n"` → fails.

**Verify RED:** `just test tests/test_session_commit_format.py::test_format_empty_parent_with_submodule` fails.

### Cycle 2.1: GREEN — add conditional guard

**Target file:** `src/claudeutils/session/commit_pipeline.py`, line 234

**Change:**
```python
# Before:
    parts.append(_strip_hints(parent_output))
# After:
    if parent_output:
        parts.append(_strip_hints(parent_output))
```

**Verify GREEN:** `just check && just test tests/test_session_commit_format.py` — all pass.

---

## Phase 3: General fixes (type: general)

All changes in this phase are non-behavioral. Executor reads each target file before editing.

### Step 3.1: Test specificity — add match= to bare pytest.raises (m-1, m-2, m-3)

**Files:**
- `tests/test_session_commit.py:257` — `pytest.raises(CleanFileError)`
- `tests/test_session_parser.py:147` — `pytest.raises(SessionFileError)`
- `tests/test_commit_pipeline_errors.py:26` — `pytest.raises(subprocess.CalledProcessError)`

**Changes:**

m-1 (`test_validate_files_amend`, line 257):
```python
# Before:
    with pytest.raises(CleanFileError):
# After:
    with pytest.raises(CleanFileError, match="no uncommitted changes"):
```

m-2 (`test_parse_session_missing_file`, line 147):
```python
# Before:
    with pytest.raises(SessionFileError):
# After:
    with pytest.raises(SessionFileError, match="not found"):
```

m-3 (`test_git_commit_raises_on_failure`, line 26):
```python
# Before:
    with pytest.raises(subprocess.CalledProcessError):
# After:
    with pytest.raises(subprocess.CalledProcessError, match="non-zero exit status"):
```

**Verify:** `just check && just test tests/test_session_commit.py tests/test_session_parser.py tests/test_commit_pipeline_errors.py`

### Step 3.2: Test vacuity — remove redundant len > 0 assertions (m-4, m-5)

**Files:**
- `tests/test_session_handoff.py:45` — `assert len(result.completed_lines) > 0`
- `tests/test_session_parser.py:57` — `assert len(lines) > 0`

Remove the redundant `len(...)  > 0` assertion lines. The `any(...)` assertions on the following lines already imply non-empty.

**Verify:** `just check && just test tests/test_session_handoff.py tests/test_session_parser.py`

### Step 3.3: Fixture format conformance — fix bold-colon to ### heading (m-6)

**File:** `tests/test_session_handoff.py:31`

**Change:** Update `HANDOFF_INPUT_FIXTURE` to use `### ` heading format per outline.md:75 spec.

```python
# Before:
**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent

# After:
### Handoff CLI tool design (Phase A)
- Produced outline
- Review by outline-review-agent
```

Also update the test assertion at line 47 which checks for `"**Handoff CLI tool design"` — update to check for `"### Handoff CLI tool design"` instead.

**Verify:** `just check && just test tests/test_session_handoff.py`

### Step 3.4: Dead code removal — remove step_reached field (m-7)

**File:** `src/claudeutils/session/handoff/pipeline.py`

`HandoffState.step_reached` (line 20) is set but never read. The resume path re-runs the full pipeline. Remove:
1. The `step_reached: str = "write_session"` field from `HandoffState`
2. Any sites that set `step_reached` (check with `grep -rn "step_reached"`)

**Search first:** `grep -rn "step_reached" src/ tests/` to find all usages before editing.

**Verify:** `just check && just test tests/` — ensure HandoffState-related tests still pass.

### Step 3.5: Docstring warning — _git_output porcelain safety (m-9)

**File:** `src/claudeutils/session/commit_gate.py`, function `_git_output` (lines 31-43)

Add a docstring warning that `.strip()` destroys porcelain format. Current docstring: `"""Run git command and return stdout."""`

Update to:
```python
def _git_output(
    *args: str,
    cwd: Path | None = None,
) -> str:
    """Run git command and return stripped stdout.

    Warning: `.strip()` on return value destroys leading spaces in
    porcelain XY format — do not use for `git status --porcelain`.
    Use raw `result.stdout.splitlines()` for porcelain output instead.
    """
```

Check docstring summary length: "Run git command and return stripped stdout." = 43 chars ≤ 70 limit. Safe from docformatter wrap.

**Verify:** `just check && just test tests/test_session_commit.py`

---

## Final Verification

After all phases complete:

```bash
just precommit
```

All checks must pass. If failures exist, fix before considering task done.

## Recall Entries (for executor context)

- `when docstring formatting conflicts` — docformatter wraps at 80 chars; summary must be ≤70 content chars to avoid D205
- `when green phase verification includes lint` — GREEN verification is `just check && just test`, not just `just test`
- `when detecting vacuous assertions from skipped RED` — verify RED fails before implementing GREEN
