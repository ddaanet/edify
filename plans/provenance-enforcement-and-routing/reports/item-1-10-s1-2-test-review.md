# Item 1.10, slices 1-2 — test review

Reviewed `tests/test_line_limits.py` (new, uncommitted) against the slice
texts in `plans/provenance-enforcement-and-routing/outline.md` (KD-7,
Item 1.10) and the RED report
`plans/provenance-enforcement-and-routing/reports/item-1-10-s1-2-red.md`.

Verdict: **RED confirmed.**

## Run before fixes

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_line_limits.py -v

Summary: 1/2 passed, 1 failed

tests/test_line_limits.py::test_line_limits_fails_markdown_over_400 FAILED
tests/test_line_limits.py:61: in test_line_limits_fails_markdown_over_400
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 1
E    +  where 0 = CompletedProcess(args=['/Users/david/code/edify/scripts/check_line_limits.sh',
E        '/tmp/claude-1000/pytest-of-david/pytest-525/test_line_limits_fails_markdow0/root'],
E        returncode=0, stdout='', stderr='').returncode

Passes:
tests/test_line_limits.py::test_line_limits_passes_clean_tree
```

Slice 2 fails on an assertion, not an ERROR — the fixture builds, the script
runs, and the failure is the exit code the contract demands. Slice 1 passes,
vacuously, as the list revision predicted.

## Mutation proof of slice 1

`scripts/check_line_limits.sh` replaced in place by an unconditional failure:

```bash
#!/usr/bin/env bash
set -euo pipefail
echo "oversized-file: x: 10 lines > 400"
exit 1
```

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_line_limits.py -v

Summary: 0/2 passed, 2 failed

tests/test_line_limits.py::test_line_limits_passes_clean_tree FAILED
tests/test_line_limits.py:43: in test_line_limits_passes_clean_tree
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: oversized-file: x: 10 lines > 400
E   assert 1 == 0

tests/test_line_limits.py::test_line_limits_fails_markdown_over_400 FAILED
tests/test_line_limits.py:62: in test_line_limits_fails_markdown_over_400
    assert result.stdout.splitlines() == [
E   At index 0 diff: 'oversized-file: x: 10 lines > 400'
E                 != 'oversized-file: docs/notes.md: 401 lines > 400'
```

Slice 1 is a real test: it goes red the moment the script reports an overage
on a clean tree. Slice 2 additionally proves it is not exit-code-only — under
the mutation it fails on the stdout line, which is the assertion that carries
the path and count.

The mutation was re-run after the fixes below, with the same result
(`0/2 passed`, slice 1 failing on `assert 1 == 0`).

Restore, both times:

```
$ git checkout -- scripts/check_line_limits.sh
$ git diff --quiet scripts/check_line_limits.sh   # rc=0
$ git status --porcelain
?? plans/provenance-enforcement-and-routing/reports/item-1-10-s1-2-red.md
?? tests/test_line_limits.py
```

The SUT is byte-for-byte as committed; the only untracked files are the RED
report and the test file (this review report makes a third).

## Findings

1. **`_write_lines` docstring did not pin the line-count convention** and
   ended in a garbled clause ("relative to itself"). The convention matters:
   slice 2's `401 lines` is only true under `wc -l` semantics, and a file
   without a trailing newline counts one fewer. *Fixed* — the docstring now
   states that the file always ends in a newline, that `wc -l` therefore
   reports exactly `count` for `count >= 1`, and that `path` may contain
   spaces.

   Verified empirically rather than by reading: the helper was driven for
   counts 10, 200, 201, 400, 401 and each file gave `wc -l` equal to `count`
   with a trailing newline; `sub dir/my notes.md` at 401 gave `wc -l = 401`.

2. **Slice 1's negative assertion was weaker than it needed to be.** It
   tested `line.startswith("oversized-file:")` per split line, so a report
   emitted with leading whitespace would have slipped through. *Fixed* —
   replaced with `assert "oversized-file:" not in result.stdout`, which is
   both stricter and shorter.

3. **`ROOT` is genuinely under test.** `cwd=root.parent` (`tmp_path`) is
   outside the checkout, confirmed in the `CompletedProcess` args above. Note
   that a script which ignored `ROOT` and walked `cwd` recursively would
   still *find* `root/docs/notes.md`; what rules that implementation out is
   slice 2's exact-equality assertion, which demands the root-relative
   `docs/notes.md` and not `root/docs/notes.md`. No change — the assertion
   already closes the hole.

4. **Whitespace safety: clean.** Every path is built with `Path.__truediv__`,
   never string concatenation; the subprocess is invoked with an argument
   list, so no shell splitting occurs. Slice 7's `my notes.md` needs no
   helper change (verified above).

5. **Scope realism: the fixture expresses the later slices.** The tree
   mirrors the real scope (`plugin/skills/x/SKILL.md`, `docs/notes.md`), so
   slice 3 varies the cap by path with no new machinery, slice 6 adds
   `docs/superpowers/plans/x.md`, and the existing Python gate is reachable
   as `_write_lines(root / "src" / "x.py", n)`. Nothing here blocks them. No
   change: slices 1 and 2 hold to their verbatim fixture text, so `src/x.py`
   is not added now — the Python gate is pinned by whichever later slice
   claims it, and Item 1.10 should not land without one doing so.

6. **Style matches the sibling contract suite.** `REPO_ROOT` / `SCRIPT` at
   module top, `_`-prefixed helpers, `check=False` with stdout+stderr as the
   assertion message — the same shape as `tests/test_review_range.py` from
   Item 1.2.

## Run after fixes

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_line_limits.py -v

Summary: 1/2 passed, 1 failed

tests/test_line_limits.py::test_line_limits_fails_markdown_over_400 FAILED
tests/test_line_limits.py:64: in test_line_limits_fails_markdown_over_400
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 1

Passes:
tests/test_line_limits.py::test_line_limits_passes_clean_tree
```

Unchanged in kind: slice 2 still red on its assertion, slice 1 still passing.

Lint, all clean:

```
$ ruff check tests/test_line_limits.py
All checks passed!
$ mypy tests/test_line_limits.py
(no output)
$ docformatter --diff tests/test_line_limits.py
(no output, rc=0)
```

## Note for GREEN

Slice 2 asserts `result.stdout.splitlines()` equals exactly the one
`oversized-file:` line. Any additional stdout — a summary, a count, a
progress line — fails it. That is the interface as written ("one
`oversized-file:` line per over-cap file"); diagnostics belong on stderr.

## Scope

Touched: `tests/test_line_limits.py` (the two fixes above) and this report.
`scripts/check_line_limits.sh` was mutated and restored, twice, and is
byte-for-byte as committed. Nothing committed.
