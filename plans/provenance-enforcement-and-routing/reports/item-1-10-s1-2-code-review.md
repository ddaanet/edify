# Item 1.10/1-2 — code review

Reviewed `scripts/check_line_limits.sh` as committed in `66e32fad`. Verdict:
the two slices are genuinely proven by the tests, and four failure-mode
defects were found and fixed in the working tree (not committed).

## Mutation results

Each mutation was applied to `scripts/check_line_limits.sh` alone, the suite
run, then the script restored from git. Final restore verified with
`git diff --exit-code`.

| # | Mutation | Expected | Observed |
|---|----------|----------|----------|
| A | `-gt "$cap"` → `-ge "$cap"` | slice 2 still passes | 2/2 passed |
| A' | same, direct probe on a 400-line `docs/notes.md` | mutant reports it, original does not | mutant: `oversized-file: docs/notes.md: 400 lines > 400`, exit 1; original: no output, exit 0 |
| B | markdown default `cap=400` → `cap=500` | slice 2 reds | 1/2 passed, 1 failed |
| C | drop `$file` from the message | slice 2 reds | 1/2 passed, 1 failed |
| D | `for dir in plugin docs` → `for dir in plugin` | slice 2 reds, slice 1 passes | 1/2 passed, 1 failed |
| E | markdown `cap=400` → `cap=0` | slice 1 reds (false-positive direction) | 0/2 passed, 2 failed |

Reading: slice 2 pins the cap value, the message format including the path,
and the `docs/` walk. Slice 1 has force only against a mutation that makes
the script report a clean tree (E) — which is what a clean-tree contract test
is for. The off-by-one (A) survives both slices: neither fixture sits at
exactly 400 lines, so the boundary is unpinned. That is a gap in the slice
list, not a defect in the script — the script's `-gt` is correct, and A' shows
the mutant does change behaviour at the boundary. Flagged for slice 3, which
already tests a 201-line `SKILL.md` against a 200 cap and could pin `200`
itself at no extra cost.

## Real-tree run from an outside CWD

```
$ cd /Users/david && /Users/david/code/edify/scripts/check_line_limits.sh /Users/david/code/edify
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
EXIT=1
```

Every path is root-relative: no `./` prefix, no absolute path, despite the
CWD being outside the checkout. The `${file#./}` strip is needed only on the
root loop (`find .`); the `plugin`/`docs` loops pass `find` a bare directory
name and so emit `plugin/…` and `docs/…` directly. Confirmed by this output —
no other loop can produce `./`.

**Two consequences for the orchestrator, neither a defect here:**

- `just precommit` is red on this repo as of `66e32fad`, and was already red
  before this review's fixes. KD-7 anticipates exactly this ("red on its
  first run"); it clears when slice 4's allowlist lands and Item 1.11 runs
  the reflow. Stated because the gate is a live dependency of every
  subsequent commit in this job.
- KD-7 says "six files are over today". The measured count is **seven** —
  `docs/design.md` at 1213 lines is the extra. Item 1.11 populates the
  allowlist from measured post-reflow counts, so it will pick this up, but
  KD-7's parenthetical is stale.

## Findings

### 1. `--allowlist FILE` was accepted and silently discarded — Major, fixed

`--allowlist) shift 2 ;;` consumed the option and its argument and did
nothing. Measured before the fix: `check_line_limits.sh --allowlist al.txt
ROOT` scanned `ROOT` normally, reported the overage and exited 1 — a caller
supplying an allowlist got a full hard gate with no indication the allowlist
was ignored. That is the silent-failure class `CLAUDE.md` §Error Handling
rules out.

Fixed by rejecting the option: stderr `check_line_limits: --allowlist: not
implemented`, exit 2. Chosen over dropping the arm because with the arm gone
`--allowlist` falls through to the `*)` case and becomes `ROOT`, which is
silently wrong in a different way. Slice 4 replaces the arm's two-line body
with the real parse and deletes the disclaimer from the header comment —
nothing to undo.

### 2. `shift 2` with no following argument — Major, fixed by the same change

Measured before the fix: `check_line_limits.sh --allowlist` (option last)
printed **nothing at all** and exited **1**. Under `set -e`, `shift 2` with
`$# = 1` fails, aborting the script; exit 1 is the interface's *overage*
code, so a usage error was indistinguishable from "one file is over cap",
with no diagnostic. The rejection arm in finding 1 removes the `shift`
entirely, so this path now prints the same diagnostic and exits 2.

### 3. Failure paths exited 1, colliding with the overage code — Major, fixed

The interface reserves 1 for an overage. Three paths violated it:

| Path | Before | After |
|------|--------|-------|
| `--allowlist` with no argument | silent, exit 1 | diagnostic, exit 2 |
| nonexistent `ROOT` | bash's `cd` error, exit 1 | bash's `cd` error, exit 2 |
| unreadable file under scope | bash's redirect error, exit 1, scan abandoned mid-way | explicit `cannot read <path>` + exit 2 |

No path exits 0 on a failure — the `set -e` abort was at least loud in that
direction. The fixes are `cd "$ROOT" || exit 2` and an explicit
`if ! line_count=$(wc -l <"$file")` guard in `check_cap` that names the file
before exiting 2. The guard also converts an opaque bash redirect message
into one that says which file and which script.

Unknown options were a fourth case, mostly by accident: `--oops` fell to
`*)`, became `ROOT`, and produced `cd: --: invalid option` with exit 2 — the
right code with a misleading message. A `-*)` arm now rejects it by name.

Note for Item 1.11: `portable.just`'s `report-end-safe` treats any non-zero
as "failed", so 1 and 2 are indistinguishable at the recipe level. Worth
separating there if the distinction is to be usable; out of scope here.

### 4. `find` stderr no longer silenced — verified, no action

The pre-existing `2>/dev/null` on both `find` calls is gone in `66e32fad`,
replaced by `[ -d "$dir" ] || continue` guards. This also completes half of
Item 1.11's "delete the dead `agents/decisions` loop and its `2>/dev/null`"
— that loop and its suppression are both already gone, so Item 1.11's
instruction is satisfied in advance. Flagged so Item 1.11 does not go looking
for code that no longer exists.

### 5. Scope fidelity vs KD-8 — checked, no change needed

- `plugin/` holds `README.md`, `agents`, `bin`, `fragments`, `hooks`,
  `justfile`, `portable.just`, `scripts`, `skills`. No vendored or generated
  subtree. The only generated directory anywhere under it is
  `plugin/bin/__pycache__`, which holds no `*.md` and so cannot reach the
  markdown walk.
- There is **no** `plugin-dev/` vendored subtree in this repo, at the root or
  under `plugin/` (`find . -maxdepth 3 -name plugin-dev` is empty). The
  shared-conventions rule about `<consumer>/plugin-dev/` being read-only
  generated content has no subject here, so no exclusion was added — adding
  one now would be an exclusion for a path that does not exist.
- `node_modules/` is at the repo root only. The root loop is
  `find . -maxdepth 1`, so it never descends into it. Not reachable, no
  exclusion needed.
- `memory/` is a submodule and is not in any loop's scope. Correct per KD-8.
- The `docs/superpowers/plans/*` and `docs/superpowers/specs/*` exclusions
  match on `find`'s output prefix (`docs/…`) and are correct as written.

**Latent, for whoever adds a vendored subtree later:** if `plugin-dev/` or
similar ever lands under `plugin/`, both this script *and* KD-8's reflow
scope need the same exclusion, and neither currently has a mechanism that
would notice. Recorded rather than pre-built.

### 6. `set -e` and the `&&` cap assignment — checked, sound

`[ "$(basename "$file")" = "SKILL.md" ] && cap=200` returns 1 for every
non-`SKILL.md` file. Probed under `set -euo pipefail` inside a function: the
and-list does not trigger the `-e` exit, and execution continues. It is also
not the last command in the loop body, so it cannot leak a non-zero status.
No change.

### 7. Style — checked, no change

Helpers before use, as bash requires at runtime and as the house style in
this repo's scripts has it. Comments state what and why, no narration; the
two added comments follow the same shape. Mixed `[ ]` and `[[ ]]` left alone
as instructed.

## Final verification

```
$ shellcheck scripts/check_line_limits.sh
shellcheck clean

$ pytest tests/test_line_limits.py -v
**Summary:** 2/2 passed
- tests/test_line_limits.py::test_line_limits_passes_clean_tree
- tests/test_line_limits.py::test_line_limits_fails_markdown_over_400
```

Post-fix probes of every path touched:

```
$ check_line_limits.sh --allowlist al.txt ROOT
check_line_limits: --allowlist: not implemented           exit=2
$ check_line_limits.sh --allowlist
check_line_limits: --allowlist: not implemented           exit=2
$ check_line_limits.sh --oops
check_line_limits: unknown option: --oops                 exit=2
$ check_line_limits.sh /no/such/dir
…: cd: /no/such/dir: No such file or directory            exit=2
$ check_line_limits.sh ROOT          # ROOT holds a chmod-000 docs/secret.md
oversized-file: docs/notes.md: 401 lines > 400
…: docs/secret.md: Permission denied
check_line_limits: cannot read docs/secret.md             exit=2
```

Both in-repo callers (`justfile:174`, `plugin/portable.just:74`) invoke the
script bare with no options, so the new `-*` rejection cannot affect them.

## Diff

```
 scripts/check_line_limits.sh | 23 +++++++++++++++++++----
 1 file changed, 19 insertions(+), 4 deletions(-)
```

Uncommitted, as instructed. `git status --porcelain` shows
` M scripts/check_line_limits.sh` and nothing else — the mutation runs were
all restored.
