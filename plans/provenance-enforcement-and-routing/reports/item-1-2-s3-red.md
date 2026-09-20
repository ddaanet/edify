# Item 1.2 slice 3 — RED

Scope: `tests/test_review_range.py` only. The deviation stated in the
dispatch applies: slice 2's code review (`item-1-2-s2-code-review.md`) already
probed this exact verdict against the unchanged script (its P1 row). This
test is written exactly as if it were red, run, and reported as passing —
then proven real by mutation, not by an unimplemented-behaviour red.

## Test added

```python
def test_second_pass_recomputed_base_is_conflict(tmp_path: Path) -> None:
    """A `Base:` later than the prior's emits `CONFLICT:` naming both shas."""
    repo = tmp_path / "repo"
    first = _init_repo(repo)
    second = _run_git(repo, "rev-parse", "HEAD").strip()
    prior = repo / "plans" / "prior-job" / "outline.md"
    _write_artifact(prior, "none", first)
    artifact = repo / "plans" / "job" / "outline.md"
    _write_artifact(
        artifact,
        _second_pass_derived_from("plans/prior-job/outline.md"),
        second,
    )

    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    result = _run_review_range(artifact, elsewhere)

    assert result.returncode == 1, result.stdout + result.stderr
    assert (
        result.stdout
        == f"CONFLICT: base {second} != {first} inherited from "
        "plans/prior-job/outline.md\n"
    )
```

No fixture change was needed: `_init_repo` already returns the first commit's
sha, and the second (HEAD) is read directly with the existing `_run_git`
helper, so `_init_repo` itself is untouched.

## Unmutated run (all three, expect PASS)

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 3/3 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
- tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict
```

As the dispatch predicted: the new test passes against the unchanged script.

## Mutation applied

Edited `plugin/bin/edify-review-range.sh` directly (a pristine copy was kept
under `$TMPDIR/mutation-work/edify-review-range.sh.orig` for the
before/after diff), inserting an unconditional `RANGE:` emission ahead of the
base compare so the inheritance check is skipped entirely:

```diff
     prior_provenance=$(provenance_of "$prior")
     prior_base_line=$(grep -m1 -- '\*\*Base:\*\*' <<<"$prior_provenance" || true)
     prior_base=$(base_value_of "$prior_base_line")
 
     if [[ ! "$prior_base" =~ ^[0-9a-fA-F]{40}$ ]]; then
         echo "NO-PRIOR: $prior_path"
         exit 1
     fi
 
+    # MUTATION: skip the compare entirely, emit RANGE unconditionally.
+    printf 'RANGE: %s..HEAD\n' "$resolved_base"
+    exit 0
+
     if [[ "$resolved_base" == "$prior_base" ]]; then
         printf 'RANGE: %s..HEAD\n' "$resolved_base"
         exit 0
     fi
```

## Mutated run

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 2/3 passed, 1 failed

## Failures

### tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict FAILED

    tests/test_review_range.py:170: in test_second_pass_recomputed_base_is_conflict
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError: RANGE: ad6e45c52d5d204678ca98df3b3cace1f72d0d48..HEAD
    E
    E   assert 0 == 1
    E    +  where 0 = CompletedProcess(args=['edify-review-range.sh', '/tmp/.../repo/plans/job/outline.md'], returncode=0, stdout='RANGE: ad6e45c52d5d204678ca98df3b3cace1f72d0d48..HEAD\n', stderr='').returncode

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
```

The new test fails on its assertion under mutation (`returncode` 0 vs
expected 1, wrong stdout line); the other two stay green — they never
reach the inherited-compare branch's `CONFLICT:` path in a way this mutation
disturbs (slice 2's matching-base test still gets `RANGE:`, which is what
the unconditional emission also produces).

## Restore

```
$ git checkout -- plugin/bin/edify-review-range.sh
$ git status --porcelain -- plugin/bin/edify-review-range.sh
$ git diff --stat -- plugin/bin/edify-review-range.sh
```

Both commands produced no output (clean). Byte-for-byte check against the
pre-mutation copy:

```
$ diff /tmp/claude-1000/mutation-work/edify-review-range.sh.orig plugin/bin/edify-review-range.sh
$ echo $?
0
```

## Re-run after restore (expect all three PASS again)

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 3/3 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
- tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict
```

## Lint

```
$ ruff check tests/test_review_range.py
All checks passed!

$ mypy tests/test_review_range.py
(exit 0, no output)

$ docformatter -c tests/test_review_range.py
(exit 0, no output)
```

## Scope check

```
$ git status --porcelain
 M tests/test_review_range.py
```

Only the test file is dirty; the SUT (`plugin/bin/edify-review-range.sh`) is
untouched, confirmed above by both `git status --porcelain` and the
byte-for-byte diff against the pre-mutation copy.

## Commit

Not committed, per the dispatch ("Commit nothing. Stop.").
