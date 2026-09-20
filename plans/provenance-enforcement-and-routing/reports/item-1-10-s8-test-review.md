# Item 1.10 / Slice 8 — test review

Scope: `tests/test_line_limits.py` (the slice's whole diff). SUT
`scripts/check_line_limits.sh` touched only via mutate–run–restore; the
delivered diff leaves it untouched. Fixes applied directly, not committed.

Verdict: **RED confirmed.**

## 1. Mechanical run

`pytest tests/test_line_limits.py -v`, as delivered:

```
Summary: 11/12 passed, 1 failed

tests/test_line_limits.py::test_line_limits_fails_when_find_cannot_walk FAILED
tests/test_line_limits.py:294: in test_line_limits_fails_when_find_cannot_walk
    assert result.returncode == 2, result.stdout + result.stderr
E   AssertionError: find: 'docs/locked': Permission denied
E   assert 0 == 2
E    +  where 0 = CompletedProcess(..., returncode=0, stdout='',
E        stderr="find: 'docs/locked': Permission denied\n").returncode
```

An `AssertionError` on the slice's own contract line, not a collection or
fixture `ERROR`, and the only failure in the file. The red matches Finding 3
exactly: `find` fails inside process substitution, `set -e` cannot see it,
the gate exits 0 with the 401-line file never checked.

## 2. The new test — findings and disposition

**Teardown (pass).** `locked_dir.chmod(0o700)` is in a `finally`, so it runs
on the assertion path too; the observed failing run left `tmp_path` cleanup
clean. Root is skipped with a stated reason (`os.geteuid() == 0`).

**Discrimination (pass).** A script that exited 2 on every run would fail
`test_line_limits_passes_clean_tree` (pins 0) and the five tests pinning 1,
so exit 2 here is not free.

**Finding S8-1 — the "no `oversized-file:` line" assertion was vacuous
(fixed).** The fixture's only readable markdown is `docs/notes.md` at 10
lines; the 401-line file is inside the unwalkable directory. Nothing is
printable under *any* implementation, correct or broken, so the assertion
could never fail — decoration, not evidence, and the docstring's "nothing
reported" overclaimed what the fixture proves.

Ruling applied (the orchestrator's): exit 2 is the contract; a partial report
before the failure is permitted but must not be relied on. Dropped the stdout
assertion and the redundant bare `assert result.stderr` (subsumed by the
`"docs/locked" in result.stderr` check), and rewrote the docstring to state
that what a partial walk printed is deliberately unasserted. Retained
assertions: `returncode == 2` and `"docs/locked" in result.stderr` — the
latter portable across GNU and BSD `find`, whose messages differ in quoting
but both contain the path.

Deliberately **not** changed: raising `docs/notes.md` to 401 lines would make
the test additionally pin that a run failure outranks an overage (exit 2 wins
over exit 1). That is real and currently uncovered, but it is a different
contract from this slice's, and it would destroy the fixture's demonstration
of Finding 3's actual symptom — a tree that goes *green* while hiding an
overage. **Gap recorded for the orchestrator:** no test pins exit-2 precedence
over exit-1 when both conditions hold.

## 3. Finding C fix — reproduced independently

Pre-mutation `sha256 scripts/check_line_limits.sh`:
`826da029474e759a985c72cf1d3d7fb1cf8ea243d82881f94e7a580375fb02e6`.

Mutation applied by `python3` heredoc asserting a unique match, line 107:

```bash
-        if [ "${ALLOWLIST_PATHS[$i]}" = "$1" ]; then
+        if [ "$(basename "${ALLOWLIST_PATHS[$i]}")" = "$(basename "$1")" ]; then
```

Corrected fixture against the mutant — **killed**:

```
tests/test_line_limits.py::test_line_limits_matches_allowlist_paths_exactly FAILED
    assert result.returncode == 1
E   assert 0 == 1  (both files still reported; exit wrongly 0)
```

Pre-fix fixture against the same mutant — **survives**, confirming Finding C
was real rather than taken on the report's word. Ran `git show
HEAD:tests/test_line_limits.py` from a scratch copy under a path whose
`parents[1]` is the checkout, so `SCRIPT` still resolved:

```
tmp/test_old_line_limits.py::test_line_limits_matches_allowlist_paths_exactly PASSED
```

Scratch copy deleted. Restore: `git checkout -- scripts/check_line_limits.sh`;
post-restore sha256 `826da029474e759a985c72cf1d3d7fb1cf8ea243d82881f94e7a580375fb02e6`
— byte-for-byte identical. `git status --porcelain` afterwards showed only
`M tests/test_line_limits.py` and the untracked slice reports.

**Finding S8-2 — exact-match docstring still overclaimed (fixed).** It read
"a wrongly-matching decoy would be reported but not failed, while the correct
exact match still fails it", which conflates the decoy with the entry and
leaves unsaid why 500 rather than 401 is load-bearing. Rewritten to name the
ceiling-above-401 as the thing that makes the implementations diverge, and to
state that both files are reported either way so the exit code carries the
whole signal.

## 4. Lint bar

- `ruff check tests/test_line_limits.py` — All checks passed!
- `ruff format --check` — 1 file already formatted
- `mypy tests/test_line_limits.py` — rc=0, no diagnostics
- `docformatter --diff tests/test_line_limits.py` — no diff, rc=0
- `wc -l` — 314 lines (cap 400)
- Whitespace safety — no new splitting; the new test's paths are fixed
  literals, and the file's existing spaced-path tests are untouched.

## 5. Post-fix run

`pytest tests/test_line_limits.py -v`: 11/12 passed, 1 failed — still only
`test_line_limits_fails_when_find_cannot_walk`, failing on
`assert result.returncode == 2` with observed 0. The corrected
`test_line_limits_matches_allowlist_paths_exactly` passes against the
unmutated script.

RED confirmed; GREEN owns making the unwalkable-directory case exit 2.
No commit made.
