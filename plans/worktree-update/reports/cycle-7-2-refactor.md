# Cycle 7-2 Refactoring Analysis

## Current State

**File:** `src/claudeutils/worktree/cli.py`
**Line count:** 448 lines (48 over 400-line limit)
**Cause:** Cycle 7-2 added THEIRS clean tree validation (+49 lines)
**Prior refactor:** Cycle 7-1 removed 31 lines (430→399) via helper extraction

## Line Distribution Analysis

```
Lines 1-29:    Imports + _git() helper (29 lines)
Lines 31-46:   wt_path() (16 lines)
Lines 48-55:   derive_slug() (8 lines)
Lines 57-76:   _filter_section() (20 lines)
Lines 78-99:   focus_session() (22 lines)
Lines 101-115: add_sandbox_dir() (15 lines)
Lines 117-133: initialize_environment() (17 lines)
Lines 135-138: worktree() group decorator (4 lines)
Lines 140-159: _parse_worktree_list() (20 lines)
Lines 161-168: ls() command (8 lines)
Lines 170-195: _create_session_commit() (26 lines)
Lines 197-219: _create_parent_worktree() (23 lines)
Lines 221-243: _create_submodule_worktree() (23 lines)
Lines 245-259: _setup_worktree() (15 lines)
Lines 261-280: clean_tree() command (20 lines)
Lines 282-313: new() command (32 lines)
Lines 315-324: add_commit() command (10 lines)
Lines 326-335: _probe_registrations() (10 lines)
Lines 337-354: _remove_worktrees() (18 lines)
Lines 356-373: _check_merge_clean() (18 lines)      <-- OURS validation
Lines 375-404: _check_worktree_clean() (30 lines)   <-- THEIRS validation (NEW)
Lines 406-415: merge() command (10 lines)
Lines 417-449: rm() command (33 lines)
```

**Pattern:** Merge validation split into two helpers (OURS + THEIRS) totaling 48 lines.

## Refactoring Strategy

**Goal:** Remove 48+ lines to reach ≤400 target.

### Option 1: Merge Validation Consolidation (Recommended)

Consolidate `_check_merge_clean()` (OURS) and `_check_worktree_clean()` (THEIRS) into single helper with parameters.

**Current structure:**
- `_check_merge_clean(exempt_paths)` - 18 lines
- `_check_worktree_clean(worktree_path)` - 30 lines
- Total: 48 lines

**Refactored structure:**
```python
def _check_clean_for_merge(
    path: Path | None = None,
    exempt_paths: set[str] | None = None,
    strict: bool = False,
    label: str = "main"
) -> None:
    """Verify clean tree for merge.

    Args:
        path: Directory to check (None = current directory)
        exempt_paths: Paths to exempt (ignored if strict=True)
        strict: If True, no exemptions (THEIRS mode)
        label: Location label for error messages
    """
    parent_cmd = ["git"]
    if path:
        parent_cmd.extend(["-C", str(path)])
    parent_cmd.extend(["status", "--porcelain", "--untracked-files=no"])

    parent = _git(*parent_cmd[1:], check=False)
    if not strict and exempt_paths:
        dirty = [line for line in parent.split("\n")
                 if line and not any(p in line for p in exempt_paths)]
    else:
        dirty = [line for line in parent.split("\n") if line.strip()]

    if dirty:
        click.echo(f"Clean tree required for merge ({label})")
        raise SystemExit(1)

    # Check submodule
    submodule_path = path / "agent-core" if path else Path("agent-core")
    if submodule_path.exists() and (submodule_path / ".git").exists():
        sub_cmd = ["-C", str(submodule_path), "status", "--porcelain", "--untracked-files=no"]
        submodule = _git(*sub_cmd, check=False)
        if submodule.strip():
            click.echo(f"Clean tree required for merge ({label} submodule)")
            raise SystemExit(1)
```

**Estimated size:** ~30 lines consolidated (saves 18 lines)

**merge() command updated:**
```python
@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Prepare for merge: verify OURS and THEIRS clean tree."""
    _check_clean_for_merge(
        exempt_paths={"agents/session.md", "agents/jobs.md", "agents/learnings.md", "agent-core"},
        label="main"
    )
    worktree_path = wt_path(slug)
    _check_clean_for_merge(path=worktree_path, strict=True, label="worktree")
```

**Estimated total reduction:** 18 lines

### Option 2: Deslop Pass

Apply deslop principles across the file:

1. **focus_session() (lines 78-99):** 22 lines
   - Remove intermediate variables where used once
   - Inline `plan_dir` extraction into conditional
   - Estimated: 19 lines (-3)

2. **_create_session_commit() (lines 170-195):** 26 lines
   - Consolidate env dict creation
   - Inline blob variable
   - Estimated: 23 lines (-3)

3. **_setup_worktree() (lines 245-259):** 15 lines
   - Inline `container` variable (used once)
   - Estimated: 14 lines (-1)

4. **new() command (lines 282-313):** 32 lines
   - Consolidate error handling
   - Inline `worktree_path` in setup call
   - Estimated: 29 lines (-3)

5. **rm() command (lines 417-449):** 33 lines
   - Inline single-use variables
   - Consolidate branch deletion logic
   - Estimated: 30 lines (-3)

**Estimated total reduction:** 13 lines

### Option 3: Module Split (Escalate to Opus)

Split merge-specific logic into separate module:
- `src/claudeutils/worktree/merge.py`
- Extract: `_check_merge_clean()`, `_check_worktree_clean()`, `merge()` command
- Total extracted: ~60 lines
- Import overhead: ~2 lines

**Issue:** Would create 60-line merge.py module, which seems over-engineered for current scope. Merge logic is cohesive with worktree operations.

**Escalation needed:** Architectural change (new module) requires opus design decision.

## Recommended Approach

**Tier 2 refactoring:** Option 1 + Option 2 in sequence.

1. **Consolidate merge validation** (Option 1): Remove 18 lines via helper unification
2. **Deslop pass** (Option 2): Remove 13 lines via code compression
3. **Total reduction:** 31 lines (448→417, well under 400-line limit)

**Rationale:**
- Option 1 addresses the root cause (merge validation duplication)
- Option 2 provides buffer (17-line cushion)
- No architectural changes needed (no escalation)
- Maintains test coverage (behavior unchanged)
- Single refactoring session (Tier 2 execution)

## Execution Plan

**Tier 2 execution (direct implementation):**

### Step 1: Consolidate merge validation helpers
- Replace `_check_merge_clean()` and `_check_worktree_clean()` with single `_check_clean_for_merge()`
- Update `merge()` command to use new helper with different parameters
- Estimated: 448→430 lines

### Step 2: Deslop pass
- Apply deslop principles to 5 functions identified above
- Focus on single-use variables and unnecessary intermediates
- Estimated: 430→417 lines

### Step 3: Verify
```bash
pytest tests/test_worktree_commands.py -v
just precommit
```

### Step 4: Commit
```bash
git add src/claudeutils/worktree/cli.py
git commit -m "♻️ Refactor: Consolidate merge validation + deslop (448→417 lines)"
```

## Risk Assessment

**Low risk:**
- Consolidation preserves behavior (same logic, different structure)
- Deslop removes only intermediate variables (no logic change)
- Test coverage validates behavior preservation
- No new abstractions or architectural changes

**Mitigation:**
- Run tests after each step
- If tests fail, rollback step and analyze
- Precommit gate ensures quality

## Conclusion

**ESCALATE: Line limit conflict with linting requirements**

Attempted refactoring achieved 396 lines (4-line buffer) but breaks precommit due to linting conflicts:
- Ruff E501 (line length) enforcement requires multi-line formatting
- Multi-line formatting adds lines back, pushing file above 400 limit
- Trade-off: either violate line limit (416 lines with proper formatting) or violate linting (396 lines with noqa suppressions)

**Current state:** 416 lines with proper formatting, all tests passing, precommit has linting warnings (TRY003 cosmetic, E501 structural).

**Architectural decision needed:**
1. Accept 416 lines (raise limit to 420 for this file)?
2. Module split (extract merge validation to separate module)?
3. Suppress E501 on specific long lines (noqa pragmas)?

Recommend: Option 1 (raise limit to 420). Merge validation consolidation removed 18 lines of duplication. Remaining overage (16 lines) is formatter-driven, not structural bloat.
