# Item 1.10 / Slice 8 — code review (and final review of Item 1.10)

Reviewed `scripts/check_line_limits.sh` as committed in `542ff17c`, read whole
rather than as a slice diff. Verdict: slice 8 is genuinely proven — the
mutation reds the new test and nothing else. One defect found and fixed: a
failed `mktemp` exited **1**, the overage code. One comment tightened off
history. Nothing committed.

## 1. Mutation — slice 8 is proven

Restored the process-substitution form for the `docs`/`plugin` markdown walk
(`done < <(find "$dir" -type f -name "*.md" -print0)`, `walk` call dropped),
applied with a `python3` heredoc asserting a unique match on both hunks.

```
tests/test_line_limits.py::test_line_limits_fails_when_find_cannot_walk FAILED
tests/test_line_limits.py:300: in test_line_limits_fails_when_find_cannot_walk
    assert result.returncode == 2, result.stdout + result.stderr
E   AssertionError: find: ‘docs/locked’: Permission denied
E   assert 0 == 2
E    +  where 0 = CompletedProcess(..., returncode=0, stdout='',
E        stderr='find: ‘docs/locked’: Permission denied\n').returncode
```

11/12 passed, the one failure being the slice's own test, failing on its
contract line. Restored via `git checkout --`; post-restore sha256
`df1bf402d5c479678a107c3b69d160d92e6877dcccc0f9a7bc06650567895339`, identical
to the pre-mutation copy. `git status --porcelain` empty afterwards.

## 2. The `walk` helper

**Exit from a function (pass).** `exit 2` inside `walk`, called from the top
level, exits the script — not the function. Confirmed by the precedence probe
below, which never reaches the root-level `*.md` walk.

**`WALK_LIST` definition order (pass).** Assigned after `walk`'s definition but
before any call; bash resolves the global at call time.

**Trap coverage (pass).** `trap 'rm -f "$WALK_LIST"' EXIT` is installed
immediately after the assignment, so no window exists where the file exists
untrapped. Probed with a private `TMPDIR` and counted leftovers after each
exit-2 path:

```
find-failure path:      exit=2, leftover files in tmpdir: 0
check_cap unread path:  exit=2, leftover files in tmpdir: 0
```

That an EXIT trap also fires on a `set -e` abort is bash-documented and
probed directly rather than assumed:

```
$ bash -c 'set -euo pipefail; t=$(mktemp); trap "rm -f \"$t\"; echo TRAP-RAN >&2" EXIT; false; echo unreachable'
TRAP-RAN
exit=1
```

### Finding S8-C1 — a failed `mktemp` exited 1, not 2 (Major, fixed)

`WALK_LIST="$(mktemp)"` is a simple command: under `set -e` its failure aborts
the script with `mktemp`'s own status, **1** — the interface's *overage* code,
for a run in which nothing was checked. Exactly the class the 1-2 review fixed
for an unreadable file and the 3-7 review fixed for `--allowlist` arity, missed
on the newest line.

Measured on `542ff17c`:

```
$ TMPDIR=/nonexistent-dir-xyz scripts/check_line_limits.sh <tree>
mktemp: failed to create file via template ‘/nonexistent-dir-xyz/tmp.XXXXXXXXXX’: No such file or directory
exit=1
```

Fixed with an explicit guard (`if ! WALK_LIST="$(mktemp)"` — `set -e` is
inactive in an `if` condition, and the status is `mktemp`'s):

```
$ TMPDIR=/nonexistent-dir-xyz scripts/check_line_limits.sh <tree>
mktemp: failed to create file via template ‘/nonexistent-dir-xyz/tmp.XXXXXXXXXX’: No such file or directory
check_line_limits: cannot create the walk list temp file
exit=2
```

`mktemp`'s own diagnostic is not suppressed, so both lines show. No test pins
this; the fix is behaviour-only and the suite stays 12/12.

### Finding S8-C2 — `walk`'s comment narrated history (Minor, fixed)

It read "…which is how a partial walk … *used to* leave the gate green: `find`
failed, but nothing downstream ever saw it" — the defect's biography, not the
present reason. Rewritten present-tense, and the rejected alternatives the
dispatch names are now recorded in the same place rather than lost: a pipeline
loses `EXIT_CODE` to the subshell, `mapfile -d ''` is bash 4.4, so a temp file
is the bash-3.2-safe form.

### Is a temp file necessary? — yes, given the constraints

- `find … -print0 | while …` puts the loop in a subshell, so `EXIT_CODE=1` set
  inside it is discarded (`shopt -s lastpipe` is bash 4.2 and off in
  non-interactive shells by default).
- A sentinel appended to the NUL stream works but needs a second channel for
  `find`'s status and an in-band value no path can contain.
- `mapfile -d ''` is bash 4.4; the script's stated contract is bash 3.2.

**Portability check on the bare `mktemp`** (no template): grounded against the
macOS mktemp(1) man page rather than assumed — "If no arguments are passed or
if only the `-d` flag is passed `mktemp` behaves as if `-t tmp` was supplied",
and `-t` honours `TMPDIR`. Safe on both BSD/macOS and GNU. No change.

## 3. Exit-precedence probe (the gap the test review recorded)

Tree: `plugin/big.md` at 401 lines (over cap, walked first, sets `EXIT_CODE=1`)
plus `docs/locked/` at mode 000.

```
oversized-file: plugin/big.md: 401 lines > 400
find: ‘docs/locked’: Permission denied
check_line_limits: find failed under docs
exit=2
```

Exit 2 wins over an already-set `EXIT_CODE=1`, as the interface requires: the
`exit 2` in `walk` leaves immediately and `exit "$EXIT_CODE"` is never reached.
The overage line already printed is left standing — deliberate, and
deliberately unasserted by the suite (test review's Finding S8-1). Still
unpinned by a test; the runbook has no slice for it and I did not add one
(tests are out of scope for this dispatch).

## 4. Whole-script pass (all eight slices in)

Checked, no change needed:

- **Dead code** — none from earlier slices. `ALLOWLIST=""` at the top is
  strictly redundant (both branches assign it) but is a `set -u` declaration
  next to its siblings; kept.
- **`--allowlist` arity** — explicit `[ "$#" -lt 2 ]` check ahead of the
  assignment, exit 2 with a message. Re-probed: `--allowlist` alone → exit 2.
- **Exit-code discipline** — only 0, 1 and 2 reachable. Every failure-to-run
  path exits 2: bad option, missing/absent allowlist, non-integer ceiling, bad
  ROOT (`cd … || exit 2`), unreadable file, failed walk, and now failed
  `mktemp`. `EXIT_CODE` only ever takes 1.
- **Quoting** — every expansion quoted, including `"${ALLOWLIST_PATHS[$i]}"`,
  `"$WALK_LIST"` inside the trap string, and `find "$@"`. All three read loops
  are `while IFS= read -r -d ''` over `-print0`, so spaced paths are safe (two
  tests pin it).
- **`[ ]` / `[[ ]]`** — mixed: `[[ ]]` at the arg loop and the `=~` ceiling
  check (which requires it), `[ ]` everywhere else. Neither is wrong; left, per
  the dispatch.
- **Header** — usage line, cap table, markdown scope, allowlist format and
  resolution order, ratchet-down maintenance rule and exit codes all re-read
  against the code; all still true. No bash-4 claim remains; the bash-3.2
  rationale sits on `lookup_ceiling`, where the constraint bites.
- **No suppression** — `grep -n '2>/dev/null\|>/dev/null\||| true'` returns
  nothing.
- **Length** — 185 lines.

Noted, not changed (outside the slice and harmless): a second positional
argument silently overwrites `ROOT` rather than erroring. No caller passes one.

## 5. Real-tree run

From `$TMPDIR`, absolute script path, absolute ROOT:

```
$ scripts/check_line_limits.sh /Users/david/code/edify
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
exit=1
```

Seven lines, root-relative paths, exit 1 not 2 — the walk completes cleanly on
the real tree. Unchanged from the GREEN report; the allowlist sidecar is Item
1.11 and was not created.

## 6. Final verification

```
$ shellcheck scripts/check_line_limits.sh
(clean)

$ pytest tests/test_line_limits.py -v
**Summary:** 12/12 passed

$ pytest -q
**Summary:** 316/332 passed, 16 skipped
```

## Diff

```
 scripts/check_line_limits.sh | 23 ++++++++++++++---------
 1 file changed, 14 insertions(+), 9 deletions(-)
```

Uncommitted, as instructed. `git status --porcelain` shows
` M scripts/check_line_limits.sh` and nothing else; `tests/test_line_limits.py`
untouched and the mutation restored.

## For the orchestrator

- **Exit-2-over-exit-1 precedence is correct but still untested.** Recorded by
  the test review as a gap, confirmed here by probe. One fixture would pin it
  (an over-cap file in `plugin/` plus an unreadable dir under `docs/`, assert
  exit 2); it needs a test owner.
- **Item 1.11 unchanged:** the header states the ratchet-down rule, so each
  allowlist entry should record its measured post-reflow count as its ceiling.
