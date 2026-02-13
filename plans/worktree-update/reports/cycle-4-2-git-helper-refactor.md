# Cycle 4.2: Git Helper Refactor

## Summary

Introduced `_git()` helper function and replaced all 24 subprocess.run git calls with helper invocations.

## Changes

**Added:**
- `_git()` helper function (lines 14-29)
  - Parameters: `*args`, `check=True`, `env=None`, `input_data=None`
  - Returns stripped stdout
  - Explicit parameter passing to avoid ruff PLW1510 autofix conflicts

**Replaced:**
- 24 subprocess.run(["git", ...]) patterns → 25 `_git()` calls
- Returncode checks → try/except subprocess.CalledProcessError patterns

**Results:**
- Line count: 413 → 336 (77 line reduction, 18.6%)
- Target: ≤400 lines ✓
- All tests pass: 765/766 passed, 1 xfail ✓

## Key Decisions

**Explicit parameter passing:**
- Initial attempt used `**kwargs` pattern
- Ruff PLW1510 autofix added `check=False` despite kwargs containing `check`
- Changed to explicit parameters (`capture_output=True, text=True, check=check, env=env, input=input_data`)
- Avoids "multiple values for keyword argument 'check'" error

**Returncode pattern replacement:**
- Before: `result.returncode == 0` checks
- After: try/except subprocess.CalledProcessError
- Examples:
  - Branch existence: `_git("rev-parse", "--verify", slug)` → exception = doesn't exist
  - Staged changes: `_git("diff", "--quiet", "--cached")` → exception = has changes
  - Branch deletion: `_git("branch", "-D", slug)` → catch exception, check stderr

**Parameter naming:**
- `input_data` parameter (not `input`) to avoid shadowing builtin
- `env` parameter for GIT_INDEX_FILE in session commit creation

## Verification

```bash
just dev
```

**Output:**
- 765/766 passed, 1 xfail
- Precommit OK

**Coverage:**
- All git subprocess calls replaced
- Only one subprocess.run remains (inside _git helper)
- All 25 _git() calls verified working

## fixed

Refactored cli.py with _git() helper: 413→336 lines (77 line reduction), all 24 subprocess.run git calls replaced, all tests pass.
