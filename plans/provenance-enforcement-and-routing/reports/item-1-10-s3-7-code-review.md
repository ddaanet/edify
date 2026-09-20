# Item 1.10/3-7 — code review

Reviewed `scripts/check_line_limits.sh` as committed in `f74d9527`. Verdict:
slices 4 and 5 are genuinely proven; slice 7's exact-match guard is **not** —
the suite's exact-match test does not discriminate a basename-matching GREEN,
though a direct probe confirms the script matches exactly. Two defects found
and fixed in the working tree (not committed): a reintroduced silent-exit-1
argument path, and the gate's first bash-4 dependency.

## Mutation results

One mutation at a time, applied with a `python3` heredoc asserting a unique
match. Each was run against the **fixed** script (and, where noted, against
`f74d9527` as committed — the outcome was identical).

| # | Mutation | Expected | Observed |
|---|----------|----------|----------|
| A | allowlisted file never fails regardless of ceiling (`[ -z "$CEILING" ] \|\| [ … -gt … ]` → `[ -z "$CEILING" ]`) | slice 5 reds | 10/11, `test_line_limits_fails_allowlisted_file_over_ceiling` FAILED (`assert 0 == 1`) |
| B | allowlisted files silent (print guarded by `[ -n "$CEILING" ] \|\|`) | slice 4 reds | 7/11, four FAILED: `reports_allowlisted_without_failing`, `fails_allowlisted_file_over_ceiling`, `allowlists_a_spaced_path`, `matches_allowlist_paths_exactly` |
| C | allowlist path matched by basename | exact-match test reds | **11/11 passed — mutation survives** |

Restored byte-for-byte after each; `git diff --stat scripts/check_line_limits.sh`
empty between runs, and the final tree carries only the review's own fixes.

### Finding C — `test_line_limits_matches_allowlist_paths_exactly` does not discriminate basename matching (Major, test-side, not fixed — tests are out of scope)

The test's docstring claims `docs/sub/notes.md` "would be caught by a basename
comparison". Measured: it is not. The fixture allowlists `docs/notes.md` at
ceiling **401** and every decoy is **401 lines**. Under basename matching
`docs/sub/notes.md` inherits ceiling 401, and 401 ≤ 401 means it is reported
but does not fail — while `docs/my-notes.md` (basename not listed) still fails.
The aggregate assertions (`returncode == 1`, all three lines present) therefore
hold under both the correct and the mutant implementation.

The docstring's substring claim is wrong too: `docs/my-notes.md` does not
contain `docs/notes.md` as a substring, so an unanchored `case "$file" in
*$entry*)` would not match it either.

The script itself is correct. Direct probe — allowlist `docs/notes.md` at
ceiling **500**, tree holds only `docs/sub/notes.md` at 401 lines:

```
unmutated:        oversized-file: docs/sub/notes.md: 401 lines > 400   exit=1
basename mutant:  oversized-file: docs/sub/notes.md: 401 lines > 400   exit=0
```

A ceiling strictly above the decoy's line count is what makes the two
implementations diverge. The existing fixture would discriminate with one
change: give the allowlist entry a ceiling above 401 (e.g. 500) and drop
`docs/my-notes.md`'s claim on the exit code. Recorded for whoever owns the
test file; not applied here.

## bash version — measurement and decision

**Decision: replaced the associative array with a bash-3.2-safe linear scan.**

Measurement. Grepped `plugin/`, `scripts/`, `justfile` and
`plugin/portable.just` for `declare -A`, `mapfile`, `readarray`, `${var,,}` /
`${var^^}`, and `BASH_REMATCH`. Two hits:

```
plugin/bin/edify-review-range.sh:132:    prior_path="${BASH_REMATCH[1]}"
scripts/check_line_limits.sh:60:declare -A ALLOWLIST_CEILING
```

`BASH_REMATCH` and `[[ … =~ … ]]` are bash **3.0**, not 4 — so that hit is not
a bash-4 dependency. `declare -A` in this script was therefore the **first and
only** bash-4 dependency anywhere in the gate. The dispatch's condition for
replacing it is met.

Both call sites (`justfile:174`, `plugin/portable.just:74`) invoke the script
directly, and its shebang is `#!/usr/bin/env bash` — which on macOS resolves to
`/bin/bash`, version 3.2, unless Homebrew bash happens to be earlier on PATH.
The GREEN report's justification ("this repo's `/usr/bin/env bash` and Linux CI
both satisfy bash 4+") holds for Linux CI but not for a macOS developer running
`just precommit`, which is the gate's primary venue.

Replacement: two parallel indexed arrays plus an explicit `ALLOWLIST_COUNT`,
scanned by a `lookup_ceiling` helper that sets a global `CEILING`. Indexed
arrays, `for ((…))` and `local` are all bash 2.x–3.0 features. A count variable
rather than `${#arr[@]}` because bash < 4.4 errors on empty-array expansion
under `set -u`. A global rather than a command substitution so the hot path
does not fork once per scanned file.

Verified the zero-iteration case cannot abort under `set -e` — a C-style `for`
whose condition is false on entry exits 0:

```
$ bash -c 'set -euo pipefail; f(){ local i; C=""; for ((i=0;i<0;i++)); do C=x; done; }; f; echo "status=$?"'
status=0
```

and confirmed end-to-end: a tree with an empty allowlist and **two** over-cap
files reports **both**, so `lookup_ceiling` is not aborting after the first.

Construct inventory of the fixed script — no `declare -A`, `mapfile`,
`readarray`, `${var,,}`, `${var^^}`, `local -n`, `wait -n`, `coproc` or `&>>`
remain (the only textual hit is the explanatory comment).

**Caveat, stated rather than claimed:** no bash 3.2 binary exists in this
environment (`bash --version` → 5.2.37; no `/usr/local/bin/bash` or
`/opt/homebrew/bin/bash`), so the fix is verified by construct inventory and by
the suite passing under bash 5, not by executing under 3.2. Someone on a Mac
running `just precommit` closes that gap.

## Findings

### 1. `--allowlist` as the last argument: silent, exit 1 — Major, fixed

Slice 4 reintroduced the exact defect the 1-2 code review fixed (its finding
2). `ALLOWLIST="${2:-}"` followed by `shift 2` with `$# = 1`: `shift` fails,
`set -e` aborts, and the abort surfaces as **1** — the interface's *overage*
code — with nothing on stderr.

Measured on `f74d9527`:

```
$ ./scripts/check_line_limits.sh --allowlist
exit=1
```

Fixed with an explicit arity check ahead of the assignment:

```
$ ./scripts/check_line_limits.sh --allowlist
check_line_limits: --allowlist: missing FILE argument
exit=2
```

The `${2:-}` default is gone with it — it masked the arity problem without
solving it, since an empty `ALLOWLIST` then reached `no such file: ` anyway.

### 2. Header said nothing about maintaining ceilings — Minor, fixed

KD-7 says the ceiling "only ratchets down", which the script cannot enforce —
it is a rule for whoever edits the allowlist, and nothing stated it. Added two
sentences: lower an entry when its file shrinks and delete it once the file is
back under cap; a listed file growing past its ceiling is red by design, so
trim the file rather than raise the number. The bash-4 requirement sentence was
dropped (no longer true) and the TAB-in-path limitation added in its place.

### 3. `find` failure leaves part of the tree unchecked, exit 0 — Minor, reported only

`find` runs inside process substitution, so its exit status is unobservable and
a partial walk reads as a complete one. Measured on a clean tree whose only
over-cap file sits in a `chmod 000` directory:

```
find: ‘docs/locked’: Permission denied
exit=0
```

A 401-line file went unreported and the gate passed. This is the same class as
the unreadable-*file* path the 1-2 review fixed with an explicit guard, but the
fix is not analogous: recovering `find`'s status means a temp file plus a trap,
or a sentinel entry appended to the NUL stream — real machinery, no test pins
it, and `find`'s own stderr is at least loud. Left for the orchestrator to
rule on rather than fixed unasked.

### 4. Parse robustness — checked, three confirmations and one note

- **Last line without a trailing newline** — `|| [ -n "$entry_path" ]` handles
  it. Measured: `printf 'docs/notes.md\t401\tnote'` (no `\n`) is honoured, the
  file is reported and the run exits 0.
- **Path with no TAB** — ceiling is empty, the integer check fires:
  `check_line_limits: <file>: line 1: ceiling is not an integer: ` and exit 2.
  Loud, names the file and the line. Correct.
- **`#` comment and blank lines** — matched on `entry_path`; a comment line
  containing TABs still has its first field starting `#`. Correct.
- **Path containing a TAB** — inexpressible in the format. Noted in the header;
  no in-repo path contains one.
- **Trailing CR (a CRLF allowlist)** — **not fixed, noted.** A three-field line
  puts the CR in `_note`, harmless. A two-field line puts it in `ceiling` and
  the run dies with `ceiling is not an integer: 401` — a message whose
  invisible CR makes it read as a lie. It is exit 2 with the file and line
  named, so nothing fails silently; stripping CR would be new behaviour no test
  pins, on a sidecar this repo authors itself on a Unix checkout. Recorded
  rather than changed.

### 5. Exit codes and `set -e` — checked, sound after finding 1

Every failure-to-run path now exits 2, and only an overage exits 1. Measured
after the fix:

```
$ ./scripts/check_line_limits.sh --allowlist            → missing FILE argument            exit=2
$ ./scripts/check_line_limits.sh --allowlist /no/such . → no such file: /no/such           exit=2
$ ./scripts/check_line_limits.sh --oops                 → unknown option: --oops           exit=2
$ ./scripts/check_line_limits.sh /no/such/dir           → cd: …: No such file or directory exit=2
$ allowlist line with no TAB                            → ceiling is not an integer:       exit=2
```

`set -e` audit of every construct that could turn a failure into exit 1:

- `line_no=$((line_no + 1))` — arithmetic *expansion* in an assignment, never
  the `((…))` command; cannot return non-zero.
- `[ -z "$entry_path" ] && continue` — an and-list, not the last command in the
  loop body; `-e` does not fire on a false left side there.
- `case "$entry_path" in \#*) continue ;; esac` — a `case` with no matching
  pattern exits 0.
- `[ "$(basename "$file")" = "SKILL.md" ] && cap=200` — same and-list shape,
  already probed by the 1-2 review; unchanged.
- `check_cap`'s two `if` blocks — an `if` with no `else` exits 0 when its
  condition is false.
- `lookup_ceiling` — called as a bare command, so its status matters; verified
  0 on both the found and the zero-iteration paths (above).

stdout carries only `oversized-file:` lines; every diagnostic goes to stderr.

### 6. Style — checked, no change

Header is long and load-bearing (format, resolution order, maintenance rule,
exit codes) — kept. Nothing narrates. `lookup_ceiling` is defined immediately
above its only caller, as bash requires at runtime and as the file already does
for `check_cap`. Script is 159 lines.

## Final verification

```
$ shellcheck scripts/check_line_limits.sh
(clean)

$ pytest tests/test_line_limits.py
**Summary:** 11/11 passed

$ pytest -q
**Summary:** 315/331 passed, 16 skipped
```

Real-tree run, unchanged from the GREEN report's seven overages (the allowlist
sidecar is Item 1.11 and was not created):

```
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
exit=1
```

## Diff

```
 scripts/check_line_limits.sh | 47 +++++++++++++++++++++++++++++++++++---------
 1 file changed, 38 insertions(+), 9 deletions(-)
```

Uncommitted, as instructed. `git status --porcelain` shows
` M scripts/check_line_limits.sh` and nothing else — `tests/test_line_limits.py`
is untouched and every mutation was restored.

## For the orchestrator

- **Finding C is a test gap, not a script defect.** Slice 7's exact-match
  guard is weaker than its docstring claims. Fixing it costs one fixture edit
  (raise the allowlist ceiling above the decoys' line count); it needs a test
  owner, since this review may not edit the test file.
- **Finding 3** (`find` failure → exit 0) is unfixed and needs a ruling.
- **Item 1.11 note:** the header now states the ratchet-down maintenance rule,
  so populating the allowlist should record each file's *measured post-reflow*
  count as its ceiling, not a rounded-up one.
