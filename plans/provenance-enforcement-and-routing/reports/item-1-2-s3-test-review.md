# Item 1.2 slice 3 — test review

Verdict: **test proven by mutation**. No fixes applied; the test file is
unchanged from what RED left.

The mutation proof was reproduced independently — four mutations of my own
choosing, none of them the RED report's (which inserted an unconditional
`RANGE:` emission ahead of the compare). Two kill the test, two do not; both
survivors are outside this slice's contract and are recorded as findings
without a fix.

## Unmutated run

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 3/3 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
- tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict
```

A pristine copy of the SUT was taken before any mutation:

```
$ shasum $TMPDIR/edify-review-range.sh.pristine plugin/bin/edify-review-range.sh
5b8b93c2fde6a5d8a3b4dc4e90fa8be047576f6d  /tmp/claude-1000/edify-review-range.sh.pristine
5b8b93c2fde6a5d8a3b4dc4e90fa8be047576f6d  plugin/bin/edify-review-range.sh
```

## Mutation A — swap `<a>` and `<b>` in the CONFLICT line (KILLED)

```diff
     printf 'CONFLICT: base %s != %s inherited from %s\n' \
-        "$resolved_base" "$prior_base" "$prior_path"
+        "$prior_base" "$resolved_base" "$prior_path"
```

```
**Summary:** 2/3 passed, 1 failed

### tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict FAILED

tests/test_review_range.py:171: in test_second_pass_recomputed_base_is_conflict
    assert (
E   AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'CONFLICT: ba.../outline.md\n'
E     - CONFLICT: base 856d310… != 4cf8902… inherited from plans/prior-job/outline.md
E     + CONFLICT: base 4cf8902… != 856d310… inherited from plans/prior-job/outline.md
```

The test pins the operand order, not merely the presence of both shas. This is
the mutation the fixture is built for: the two shas are distinct commits taken
from `git rev-parse`, so swapping them is detectable.

## Mutation B — emit the prior's base as the range instead of conflicting (KILLED)

```diff
-    if [[ "$resolved_base" == "$prior_base" ]]; then
-        printf 'RANGE: %s..HEAD\n' "$resolved_base"
-        exit 0
-    fi
+    printf 'RANGE: %s..HEAD\n' "$prior_base"
+    exit 0
```

```
**Summary:** 2/3 passed, 1 failed

tests/test_review_range.py:170: in test_second_pass_recomputed_base_is_conflict
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError: RANGE: 32cf28ccb40b253ba7e5e5299570581e1bf9b74b..HEAD
E   assert 0 == 1
```

The "silently substitute the inherited base" failure mode KD-2 explicitly
rejects ("No substitution: a conflict means one of two artifacts is wrong, and
the script cannot know which") is caught on both exit code and stdout.

## Mutation C — prefix-only compare, full shas still emitted (SURVIVED)

```diff
-    if [[ "$resolved_base" == "$prior_base" ]]; then
+    if [[ "${resolved_base:0:7}" == "${prior_base:0:7}" ]]; then
```

```
**Summary:** 3/3 passed
```

Survives, and within contract. The slice asserts the `CONFLICT:` verdict with
full shas; two distinct commits differ in their first 7 characters, so a
prefix-only compare reaches the same branch and prints the same full-sha line.
This test cannot distinguish the two, and is not asked to — detecting a
prefix-only compare would need a fixture with two commits sharing a 7-char
prefix, which no slice in Item 1.2 specifies. **Disposition: noted, no fix.**

## Mutation D — two hops instead of one (SURVIVED, vacuously)

Follows the prior artifact's own `Derived from:` chain when it names a
superseding path, replacing `prior_path`/`prior_base` with the grandparent's:

```diff
+    # MUTATION D: hop a second time when the prior itself supersedes one.
+    prior_derived=$(sed -E 's/^- \*\*Derived from:\*\* *//' \
+        <<<"$(grep -m1 -- '\*\*Derived from:\*\*' <<<"$prior_provenance" || true)")
+    if [[ "$prior_derived" =~ $superseding_quoted ]] ||
+        [[ "$prior_derived" =~ $superseding_bare ]]; then
+        prior_path="${BASH_REMATCH[1]}"
+        prior="$root/$prior_path"
+        prior_base=$(base_value_of \
+            "$(grep -m1 -- '\*\*Base:\*\*' <<<"$(provenance_of "$prior")" || true)")
+    fi
+
     if [[ ! "$prior_base" =~ ^[0-9a-fA-F]{40}$ ]]; then
```

```
**Summary:** 3/3 passed
```

Survives **vacuously**: the fixture's prior artifact is written with
`Derived from: none`, so the chain never extends and the mutated branch never
fires. KD-2's "One hop only — each artifact in a chain was compared against
its predecessor at its own review" is therefore unexercised by any slice in
Item 1.2 (slices 4–8 add no multi-hop fixture either). **Disposition: noted,
no fix** — out of this slice's scope, and the outline's slice list does not
call for a chain fixture.

## Restore

```
$ git checkout -- plugin/bin/edify-review-range.sh
$ git diff --stat -- plugin/bin/edify-review-range.sh
(no output)
$ git status --porcelain
 M tests/test_review_range.py
?? plans/provenance-enforcement-and-routing/reports/item-1-2-s3-red.md
$ shasum $TMPDIR/edify-review-range.sh.pristine plugin/bin/edify-review-range.sh
5b8b93c2fde6a5d8a3b4dc4e90fa8be047576f6d  /tmp/claude-1000/edify-review-range.sh.pristine
5b8b93c2fde6a5d8a3b4dc4e90fa8be047576f6d  plugin/bin/edify-review-range.sh
```

Byte-for-byte identical to the pre-mutation copy; the only dirty tracked file
is the test, which is this slice's change. Restore was performed after each of
the four mutations, not only at the end.

## Wrong-reason hunt

- **Shas come from git, and in the right direction.** `first = _init_repo(repo)`
  is the seed commit's sha, `second = _run_git(repo, "rev-parse", "HEAD")` the
  second commit's. The artifact's `Base:` is `second`, the prior's is `first`,
  so "this `Base:` is a later commit than the prior's" holds as the slice
  states. Neither sha is a literal; both come from `git rev-parse` in the
  fixture, so the assertion cannot pass against a hard-coded string.
- **The assertion is the exact line.** `result.stdout ==
  f"CONFLICT: base {second} != {first} inherited from plans/prior-job/outline.md\n"`
  — full equality including the trailing newline, so extra stdout would fail
  it; plus `result.returncode == 1`. Mutation A proves the operand order is
  load-bearing.
- **`Derived from:` is the real wrapped shape.** The test calls
  `_second_pass_derived_from("plans/prior-job/outline.md")`, the same helper
  slice 2 uses — nothing after the label, the motivating report on the first
  continuation line, `` superseding `<path>` `` on the second. The `<path>` in
  the asserted line is therefore the repo-relative path the script echoes back
  out of the artifact text, not a value the test supplies twice.
- **Foreign CWD preserved.** `elsewhere` is created outside the repo and passed
  as CWD, matching slices 1–2 and the real invocation shape.
- **Slices 1–2's artifacts are untouched.** `git diff tests/test_review_range.py`
  is purely additive: 27 added lines at the end of the file, no change to
  `_init_repo`, `_write_artifact`, `_second_pass_derived_from`, `_run_git`,
  `_run_review_range`, or the two existing tests. The RED report's claim that
  no fixture change was needed is confirmed against the diff, not taken on
  trust.
- **Informational, no fix — this test does not discriminate a HEAD-recomputing
  script.** Its name says `recomputed_base`, but the artifact's `Base:` *is*
  HEAD in this fixture, so a script emitting `git rev-parse HEAD` in place of
  the artifact's value would produce the identical `CONFLICT:` line. That guard
  is slice 1's (`_init_repo` returns the first commit precisely so `Base:` is
  not HEAD there), and the review brief specifies Base = HEAD here. Recorded so
  the name is not read as evidence it is not.
- **stderr unasserted**, consistent with slices 1–2; it is attached to the
  `returncode` assertion's message, so a script failure surfaces in the report.

## Lint

```
$ ruff check tests/test_review_range.py
All checks passed!

$ mypy tests/test_review_range.py
(exit 0, no output)

$ docformatter -c tests/test_review_range.py
(exit 0, no output)
```

## Final run after restore

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 3/3 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
- tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict
```

Not committed, per the dispatch.
