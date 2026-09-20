# Item 1.10 / Slice 8 — RED report

Mode: RED. Scope: `tests/test_line_limits.py` only. SUT
(`scripts/check_line_limits.sh`) touched only via mutate-run-restore for
step 2, never modified in the delivered diff.

## 1. New test: `test_line_limits_fails_when_find_cannot_walk`

```python
def test_line_limits_fails_when_find_cannot_walk(tmp_path: Path) -> None:
    """A directory `find` cannot read is a failure to run, not a clean pass.

    `docs/locked/` is chmod 0o000: `find` hits it mid-walk, prints
    `Permission denied` to stderr and exits non-zero — but the script reads
    that `find` from a process substitution, whose exit status `set -e`
    cannot see. Slices 3-7's code review (Finding 3) found this leaves the
    gate green: exit 0, no overage reported, the locked file never checked.
    This asserts the fix: exit 2, nothing reported, the failure surfaced on
    stderr.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions; chmod 0o000 has no effect")

    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 10)
    locked_dir = root / "docs" / "locked"
    _write_lines(locked_dir / "hidden.md", 401)
    locked_dir.chmod(0o000)
    try:
        result = _run_check_line_limits(root)
    finally:
        locked_dir.chmod(0o700)

    assert result.returncode == 2, result.stdout + result.stderr
    assert not any(
        line.startswith("oversized-file:") for line in result.stdout.splitlines()
    ), result.stdout
    assert result.stderr, "expected find's Permission denied on stderr"
    assert "docs/locked" in result.stderr, result.stderr
```

`import os` and `import pytest` added to the module.

### Red run (today's script, unmodified)

```
tests/test_line_limits.py::test_line_limits_fails_when_find_cannot_walk FAILED
AssertionError: find: ‘docs/locked’: Permission denied

assert 0 == 2
 +  where 0 = CompletedProcess(..., returncode=0,
     stdout='', stderr='find: ‘docs/locked’: Permission denied\n').returncode
```

Confirms Finding 3 exactly: `find`'s permission-denied failure inside the
process-substitution loop is invisible to `set -e` — exit 0, empty stdout
(the locked file is silently never reported), the failure landing only on
stderr. GREEN must make this exit 2.

## 2. Finding C fixture correction

`test_line_limits_matches_allowlist_paths_exactly` originally allowlisted
`docs/notes.md` at ceiling 401 — equal to every decoy's line count — so a
basename-matching mutant and the correct exact-match implementation produced
identical observable output (both report all three files, both exit 1 via
`docs/my-notes.md`, which is allowlist-independent). The docstring's claim
that `docs/my-notes.md` is a substring case was also false: `docs/my-notes.md`
does not contain `docs/notes.md` as a substring.

Fix applied: dropped `docs/my-notes.md` (an unconditional-failure confound
that swallowed the basename-mutant signal in the aggregate exit code
regardless of allowlist behaviour) and raised the allowlisted ceiling to
500 — strictly above the two remaining files' 401 lines. Fixture now:
`docs/notes.md` (401, allowlisted at ceiling 500) and `docs/sub/notes.md`
(401, decoy sharing the allowlisted entry's basename). Under exact-path
matching, `docs/notes.md` is allowlisted-under-ceiling (reported, not
failed) while `docs/sub/notes.md` is not allowlisted at all (reported and
failed) — exit 1. Under basename matching, `docs/sub/notes.md` wrongly
inherits the 500 ceiling and stops failing — exit 0. Docstring rewritten to
state only what the fixture proves.

### Proof: unmutated script passes

```
tests/test_line_limits.py::test_line_limits_matches_allowlist_paths_exactly PASSED
```

### Proof: basename mutant fails

Mutated `scripts/check_line_limits.sh` line 107 from

```bash
if [ "${ALLOWLIST_PATHS[$i]}" = "$1" ]; then
```

to

```bash
if [ "$(basename "${ALLOWLIST_PATHS[$i]}")" = "$(basename "$1")" ]; then
```

Result:

```
tests/test_line_limits.py::test_line_limits_matches_allowlist_paths_exactly FAILED
AssertionError: oversized-file: docs/sub/notes.md: 401 lines > 400
  oversized-file: docs/notes.md: 401 lines > 400

assert 0 == 1
 +  where 0 = CompletedProcess(..., returncode=0,
     stdout='oversized-file: docs/sub/notes.md: 401 lines > 400\n'
            'oversized-file: docs/notes.md: 401 lines > 400\n',
     stderr='').returncode
```

Both files are still reported (the mutant doesn't change what's printed),
but the run wrongly exits 0 instead of 1 — the fixture now discriminates.

### Restore

```
git checkout -- scripts/check_line_limits.sh
git diff --stat scripts/check_line_limits.sh   # empty
```

Confirmed byte-for-byte identical to the committed version.

## 3. Full-file run and lint

`pytest tests/test_line_limits.py -v`: 11/12 passed, 1 failed — only
`test_line_limits_fails_when_find_cannot_walk` (the new RED test); every
pre-existing test, including the corrected
`test_line_limits_matches_allowlist_paths_exactly`, passes.

- `ruff check tests/test_line_limits.py` — all checks passed.
- `mypy tests/test_line_limits.py` — no output (clean).
- `docformatter --diff tests/test_line_limits.py` — no output (clean).
- `wc -l tests/test_line_limits.py` — 312 lines (cap 400).

`git status --porcelain`: only `tests/test_line_limits.py` modified.

## Commit

None made, per instruction.
