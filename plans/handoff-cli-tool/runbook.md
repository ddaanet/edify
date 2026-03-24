# RC8 Fix Runbook: handoff-cli-tool

**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (0C/0M/6m)
**Date:** 2026-03-24
**Tier:** 2 — Lightweight Delegation

## Recall

- `when testing CLI tools` — Click CliRunner, in-process, isolated filesystem
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path, mock only for error injection

## Findings Summary

| # | Finding | Type | Location |
|---|---------|------|----------|
| m-1 | Bare pytest.raises without match | Simple | tests/test_session_commit.py:101 |
| m-2 | Heading format not verified | Simple | tests/test_session_handoff.py:45-46 |
| m-3 | Empty Files section not rejected | Moderate (TDD) | src/claudeutils/session/commit.py |
| m-4 | ci.message or "" masks unreachable state | Moderate (general) | src/claudeutils/session/commit_pipeline.py:336 |
| m-5 | _strip_hints fragile continuation | Moderate (TDD) | src/claudeutils/session/commit_pipeline.py:204 |
| m-6 | ParsedTask import bypasses S-4 | Simple | src/claudeutils/session/status/render.py:7 |

---

## Phase 1: Simple fixes batch (type: general)

**Files:** tests/test_session_commit.py, tests/test_session_handoff.py, src/claudeutils/session/status/render.py

**m-1 fix (test_session_commit.py:101):**
```python
# Current:
with pytest.raises(CommitInputError):
# Fix:
with pytest.raises(CommitInputError, match="no-edit contradicts"):
```

**m-2 fix (test_session_handoff.py:45-46):**
After existing assertions, add:
```python
assert any("### " in line and "Handoff CLI tool design" in line for line in result.completed_lines)
```
The fixture has `**Handoff CLI tool design (Phase A):**` — check what H-1/H-2 actually specify before writing the assertion to ensure the fixture's heading format matches.

**m-6 fix (render.py:7):**
```python
# Current:
from claudeutils.validation.task_parsing import ParsedTask
# Fix:
from claudeutils.session.parse import ParsedTask
```

Verify `from claudeutils.session.parse import ParsedTask` exports ParsedTask (check session/parse.py re-exports).

**Verify:** `just precommit` passes after batch.

---

## Phase 2: Empty files validation (type: tdd)

**Files:** tests/test_session_commit.py (RED), src/claudeutils/session/commit.py (GREEN)

**RED — test_parse_commit_empty_files (test_session_commit.py):**
```python
def test_parse_commit_empty_files_raises() -> None:
    """## Files section with no entries raises CommitInputError."""
    with pytest.raises(CommitInputError, match="empty"):
        parse_commit_input("## Files\n\n## Message\n> msg\n")
```
Run `just test tests/test_session_commit.py` — must FAIL (currently returns CommitInput with files=[]).

**GREEN — add empty check in commit.py `_validate` (after `if files is None` guard):**
```python
if not files:
    msg = "## Files section is empty"
    raise CommitInputError(msg)
```
Insert after line 114 (after `raise CommitInputError("Missing required section: ## Files")`).

**Verify:** `just test tests/test_session_commit.py` passes. `just precommit` passes.

---

## Phase 3: Message assertion (type: general)

**File:** src/claudeutils/session/commit_pipeline.py:334-337

**Context:** `_validate_inputs` at line 262 guarantees `ci.message is not None` when `no_edit is False`. The `or ""` fallback is dead code when `no_edit is False`, and the message is unused when `no_edit is True`.

**Fix:** Replace the `or ""` fallback with an explicit assertion:
```python
assert ci.message is not None or no_edit
parent_output = _git_commit(
    ci.message or "", amend=amend, no_edit=no_edit, cwd=cwd
)
```

Note: The `or ""` in `_git_commit` call can remain since it's harmless when `no_edit=True` (message unused) and dead when `no_edit=False` (ci.message guaranteed non-None by assert).

**Verify:** `just test tests/test_session_commit_pipeline.py` passes. `just precommit` passes.

---

## Phase 4: Strip hints fix (type: tdd)

**Files:** tests/test_session_commit_pipeline.py (RED), src/claudeutils/session/commit_pipeline.py (GREEN)

**Current code (commit_pipeline.py:199-211):**
```python
for line in lines:
    is_hint = line.startswith(("hint:", "advice:"))
    if is_hint:
        prev_was_hint = True
    elif prev_was_hint and line and line[0] in (" ", "\t"):
        if line[0] == "\t" or (line[0] == " " and len(line) > 1 and line[1] == " "):
            prev_was_hint = True
        else:
            prev_was_hint = False
            result.append(line)
    else:
        prev_was_hint = False
        result.append(line)
```

**Bug:** When a single-space-indented line follows a hint, it enters the elif branch, takes the inner-else (resets `prev_was_hint = False`, appends line). Subsequent double-space continuation lines then fall to outer-else (appended — incorrectly included in output).

**RED — test in test_session_commit_pipeline.py:**
```python
def test_strip_hints_single_space_then_double() -> None:
    """Lines after hint filtered even after single-space-prefixed line."""
    text = "hint: do this\n single\n  continuation\nnormal"
    result = _strip_hints(text)
    assert "single" not in result
    assert "continuation" not in result
    assert "normal" in result
```
Run `just test tests/test_session_commit_pipeline.py -k strip_hints` — must FAIL (single and continuation currently appear in output).

Note: Need to import `_strip_hints` from `claudeutils.session.commit_pipeline` in the test file (check if already imported; if not, add to imports).

**GREEN — simplify inner condition:**
```python
for line in lines:
    is_hint = line.startswith(("hint:", "advice:"))
    if is_hint:
        prev_was_hint = True
    elif prev_was_hint and line and line[0] in (" ", "\t"):
        prev_was_hint = True  # all indented lines after hint are continuation
    else:
        prev_was_hint = False
        result.append(line)
```
Remove the inner if-else entirely. All indented lines (space or tab) after a hint are treated as continuation and filtered.

**Verify:** `just test tests/test_session_commit_pipeline.py` passes. `just precommit` passes.

---

## Phase 5: Final verification (type: general)

Run `just precommit` — all tests pass, lint clean.
