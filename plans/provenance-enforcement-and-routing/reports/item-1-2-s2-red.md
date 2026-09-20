# Item 1.2 slice 2 — RED

Slice: `test_second_pass_matching_base_emits_range` — prior artifact carries
the same `Base:`; asserts exit 0 and the `RANGE:` line.

Scope: `tests/test_review_range.py` only. `plugin/bin/edify-review-range.sh`
was read (not edited); `git status --porcelain` confirms it is untouched.

## Fixture change

No new fixture function was needed to write *two* artifacts — `_write_artifact`
already takes an arbitrary `path`, so the test calls it twice, once for the
prior and once for the artifact under test. What was added:

1. `_write_artifact`'s docstring now notes `derived_from` may itself span
   lines with a leading-space continuation — no code change, since it already
   interpolates the string verbatim via f-string.
2. A new helper `_second_pass_derived_from(prior_path)` builds the `Derived
   from:` *value* in the real wrapped shape the outline's own `##
   Provenance` section uses: the motivating report path on the bullet line,
   then an indented continuation line carrying `` superseding `<prior_path>` ``:

   ```python
   def _second_pass_derived_from(prior_path: str) -> str:
       """Build a `Derived from:` value in the real wrapped second-pass shape.

       Report path on the bullet line, ``superseding `<prior_path>` `` on an
       indented continuation line — the shape
       ``plans/provenance-enforcement-and-routing/outline.md``'s own
       ``## Provenance`` section uses.
       """
       return (
           "`plans/prior-job/reports/deliverable-review.md`,\n"
           f"  superseding `{prior_path}`"
       )
   ```

Slice 1's `test_first_pass_emits_range` is unchanged and still passes.

## Test body

```python
def test_second_pass_matching_base_emits_range(tmp_path: Path) -> None:
    """A prior artifact with the same `Base:` emits `RANGE: <base>..HEAD`."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", sha)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        sha,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
```

The prior artifact is written at `plans/prior-job/outline.md` with `Derived
from: none` and `Base: <sha>` (the same first commit `_init_repo` returns).
The artifact under test is written at `plans/job/outline.md` with its
`Derived from:` value in the wrapped second-pass shape naming the prior by
its repo-relative path, and the same `Base:` sha — the "inherited match"
case the slice specifies. Invocation is by bare name with `plugin/bin` on
`PATH` and `cwd` outside the repo, unchanged from slice 1's helper.

## Pytest output (verbatim)

```
# Test Report

**Summary:** 1/2 passed, 1 failed

## Failures

### tests/test_review_range.py::test_second_pass_matching_base_emits_range FAILED

```python
tests/test_review_range.py:141: in test_second_pass_matching_base_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PRIOR: plans/prior-job/outline.md
E     
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-480/test_second_pass_matching_base0/repo/plans/job/outline.md'], returncode=1, stdout='NO-PRIOR: plans/prior-job/outline.md\n', stderr='').returncode

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
```
```

Fails on the assertion, not an error: the script reaches its `superseding`
arm (per slice 1's fix), extracts the prior path correctly, and emits its
current skeleton verdict `NO-PRIOR: plans/prior-job/outline.md`, exit 1 —
exactly what the brief specified the current script would do. Slice 1's test
still passes.

## Lint

```
$ ruff check tests/test_review_range.py
All checks passed!

$ mypy tests/test_review_range.py
Success: no issues found in 1 source file

$ docformatter -c tests/test_review_range.py
(exit 0)
```

One docformatter round-trip: the first docstring for the new test,
`"""A prior artifact carrying the same \`Base:\` emits \`RANGE:
<base>..HEAD\`."""`, was 81 columns and docformatter wanted to wrap it across
two lines. Shortened to `"""A prior artifact with the same \`Base:\` emits
\`RANGE: <base>..HEAD\`."""` (79 columns), which docformatter accepts as-is.

## Scope

Touched `tests/test_review_range.py` only.
`plugin/bin/edify-review-range.sh` is byte-identical to its state at the
start of this slice. `git status --porcelain`:

```
 M tests/test_review_range.py
```

Nothing committed.
