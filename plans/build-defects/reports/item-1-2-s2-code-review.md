# Review: Item 1.2 / Slice 2 — code review (SUT as of 4a24c0fe)

**Scope**: every line of `plugin/skills/build/scripts/verify-step.sh` as
committed. Commit 2c35c093 changed no SUT line; the last SUT change is
4a24c0fe. The review checks three things: that 4a24c0fe matches the slice 1
review's F-1/F-2 text, that F-2 is correct, and that the script is portable to
bash 3.2 and BSD grep. `tests/test_verify_step.py` is OUT of scope. The
comment's commit-premise sentence (lines 8–10) is KNOWN and is not raised here.
**Date**: 2026-09-25
**Mode**: review + fix. The one fix is NOT APPLIED — routed. It exists as a
patched copy at `tmp/patched/verify-step.sh`. The tracked script has no diff.

## Summary

4a24c0fe applies F-1 and F-2 exactly as written. F-2 is correct, and it draws
the exit-2 line in the right place. Every construct is portable to bash 3.2 and
BSD `grep -E`. One defect predates this slice and the slice 1 review missed it.
The grep filter reads its input from a here-string. When bash cannot create
the here-string's temp file, the redirection fails with exit 1. The script
reads that 1 as grep's "every line filtered out" and prints `CLEAN`, exit 0,
on a dirty tree. On bash 3.2, the macOS target, every here-string goes through
a temp file.

**Overall Assessment**: Needs Minor Changes. One major fix is written out and
verified on a copy but NOT APPLIED, because the classifier refuses edits to
`plugin/` shell scripts. Nothing is UNFIXABLE.

## F-1 / F-2 conformance (4a24c0fe)

- **F-1**: `git show 4a24c0fe` replaces the block with text identical,
  line for line, to the F-1 "new" block in `item-1-2-s1-code-review.md`. That
  covers the comment lines 10–13, the `exempt=` pattern
  `^[^RC][^RC] "?(…)"?$`, and the `git status … || { echo "ERROR: git status
  failed"; exit 2; }` guard.
- **F-2**: the `command -v just >/dev/null || { echo "ERROR: just not found on
  PATH"; exit 2; }` block before `just precommit` is identical to the F-2
  "new" text.
- `tmp/mutants/pre-f1.sh` is byte-identical to `git show
  31fe4a16:…/verify-step.sh`, and `tmp/mutants/current.sh` to the tracked
  script (`diff`, `cmp`).

## F-2 correctness

F-2 was never checked on a copy in slice 1. It has been checked now:

- Control run (`MUTANT=tmp/mutants/current.sh`, rebind): 5/5 pass, including
  `test_missing_just_exits_2`. The test review's `m-just.sh` (F-2 removed)
  turns exactly that test red, with exit 1 and `PRECOMMIT: validation failed`.
- In a non-interactive bash, `command -v` resolves only executable `PATH`
  entries, functions and builtins. It prints nothing and returns 1 when
  `just` is absent, and `>/dev/null` discards only the resolved path. The
  `||` list keeps it out of `set -e`.
- The exit-2 line sits in the right place. SKILL.md §2 and escalation.md
  §Post-item remediation treat exit 1 as remediable ("Fix and commit") and
  exit 2 as "no verdict, stop". A dispatch cannot remove the `just` binary,
  so exit 2 fits. It can break the justfile or delete the `precommit`
  recipe, and `just` then exits non-zero. That case stays on the exit-1
  `PRECOMMIT:` path, which is correct because remediation is what should
  happen. Extending F-2 to `just --show precommit` would turn a
  dispatch-caused breakage into a "no verdict" stop, so I do not recommend it.
- Order: a dirty tree with no `just` exits 1 with `DIRTY:` before the `just`
  check runs. That is a valid verdict, because the tree check needs no `just`.

## Portability (bash 3.2, BSD grep)

- Syntax: `<<<`, `[[ ]]`, `set -o pipefail` and `$(…) || { … }` all exist in
  bash 3.2. `$?` in the `elif` is the status of the `if` condition (POSIX).
  An assignment's status is its command substitution's status.
- ERE: the pattern uses only bracket expressions (`[^RC]`, `[^/]`), `?`, `+`,
  alternation in one group and `\.`, with no backreferences or `\s`/`\w`.
  POSIX ERE, so BSD `grep -E` handles it.
- `bash -n` passes and default `shellcheck` is clean. `--enable=all` adds
  only SC2250 (brace style), which is linter territory and not raised.
- The here-string is not portable in failure behaviour. See Major 1.

## Evidence gathered

I ran the committed script against throwaway repos in `$TMPDIR` with a stub
`just` and git config insulated (git 2.47.3, bash 5.2.37, GNU grep 3.11):

| Porcelain | Verdict | Note |
|---|---|---|
| ` R inbox/a.md -> notes.md` (intent-to-add worktree rename) | DIRTY, 1 | Y-column guard needed and working |
| `C  inbox/a.md -> copy.md` (`status.renames=copies`, modified source) | DIRTY, 1 | the `C` half matters: `inbox/[^/]+\.md$` would match `a.md -> copy.md` |
| `MM .claude/handoff-task.md` | CLEAN, 0 | |
| `D  inbox/a.md` + `?? inbox/a.md` | CLEAN, 0 | |
| `?? inbox/résumé.md` (`core.quotePath=false`) | CLEAN, 0 | |
| `?? "inbox/r\\x.md"`, `?? "inbox/tab\tx.md"` | CLEAN, 0 | escapes stay inside `[^/]+` |
| submodule `memory`: untracked content, modified content, new commit | ` M memory` → CLEAN, 0 | porcelain v1 shows ` M`, not `m`/`?` |
| submodule `memory` staged bump | `MM memory` → CLEAN, 0 | |
| `UU .claude/handoff-task.md` mid-merge | CLEAN, 0 | see Recommendations |
| 1501 untracked `stray-*.txt`, here-string temp file cannot be written | **CLEAN, 0** | Major 1 |

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A failed here-string reads as "every line filtered out", so a dirty
   tree passes as CLEAN**
   - Location: `verify-step.sh:23`,
     `if status=$(grep -vE "$exempt" <<<"$porcelain"); then`
   - Problem: bash feeds a here-string through a temp file. Before 5.1 it
     always does. From 5.1 it does so only when the text exceeds the pipe
     buffer, and uses a pipe below that. If the temp file cannot be created
     or written (disk or quota full, file-size limit, no writable temp dir),
     bash prints `cannot create temp file for here-document` and fails the
     redirection with exit 1. grep never runs. The `elif [[ $? -eq 1 ]]`
     branch cannot tell that 1 apart from grep's no-lines-selected result, so
     `status=""` and the script reports `CLEAN`. This is the one failure the
     comment at lines 16–17 says it tolerates nothing but ("only grep's exit
     1 … tolerate that one code and nothing else"). A false CLEAN is the
     direction the gate exists to prevent. Reproduced on bash 5.2 with a
     1501-entry dirty tree (100906 bytes of porcelain, above the pipe size)
     and `ulimit -f 1`:
     ```
     …/verify-step.sh: line 23: cannot create temp file for here-document: No space left on device
     CLEAN: tree clean, just precommit passed
     rc=0
     ```
     On macOS bash 3.2 a one-line status takes the same path. When no temp
     dir is usable, bash also falls back to writing `sh-thd.*` into the CWD,
     which here is the repo root. I observed this at
     `/proc/self/fd/0 → …/edify/sh-thd.e2xsZK (deleted)`. The file is
     unlinked at once, so no dirt is left behind.
   - Fix: feed grep through a `printf` pipe. The pipeline's status, under
     `pipefail`, is then grep's own, apart from a `printf` write error, which
     can only follow a grep failure. The comment is there so the line is not
     "simplified" back to `<<<`. Exact text is under Fixes Routed, F-3.
   - **Status**: NOT APPLIED — routed (the classifier refuses edits to
     `plugin/` shell scripts). Verified on `tmp/patched/verify-step.sh`: the
     same forced failure gives DIRTY, exit 1. The normal 1501-entry run gives
     exit 1 and 1502 lines. `bash -n` passes, `shellcheck` is clean, and the
     rebind run is 5/5 green.

### Minor Issues

None.

## Fixes Routed (NOT APPLIED — routed to my human partner)

**F-3** (Major 1), one replacement in
`plugin/skills/build/scripts/verify-step.sh`, line 23:

old:
```
if status=$(grep -vE "$exempt" <<<"$porcelain"); then
```

new:
```
# A pipe, not a here-string: bash writes a here-string to a temp file (always
# before 5.1, above the pipe size after), and a failure to create it also
# exits 1, which would read as "every line filtered out".
if status=$(printf '%s\n' "$porcelain" | grep -vE "$exempt"); then
```

The patched copy is `tmp/patched/verify-step.sh`. I built it from
`cp plugin/skills/build/scripts/verify-step.sh` and a Python exact-string
replacement that asserts `count(old) == 1`. `diff -u` against the tracked file
shows only the hunk above. Checks run:

- `bash -n tmp/patched/verify-step.sh`: OK. `shellcheck`: clean. The
  executable bit is kept.
- `MUTANT=tmp/patched/verify-step.sh PYTHONPATH=tmp/mutants pytest -p rebind
  tests/test_verify_step.py -v`: **5/5 passed**.
- Empty porcelain behaves as before: `printf '%s\n' ""` emits one newline,
  just as `<<<""` did. grep then exits 0 with an empty line, and `status` is
  empty.
- `printf` is a builtin and `pipefail` is already set. Both are bash 3.2.

## Fixes Applied

None to tracked files. `git status --porcelain` shows no entry for
`plugin/skills/build/scripts/verify-step.sh`. The only artifact written
besides this report is `tmp/patched/verify-step.sh` (gitignored). Scratch
repos under `$TMPDIR` were removed.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| orch m5 / KD-7: any change is dirt | Partial | Holds whenever the here-string succeeds. A temp-file failure turns any dirt CLEAN (Major 1) |
| KD-7: three exemptions in any porcelain state | Satisfied | Evidence table: XY states, submodule states, quoted and escaped paths |
| KD-7: status under `--untracked-files=all` | Satisfied | `verify-step.sh:19` |
| F-1 applied as written | Satisfied | 4a24c0fe diff equals the F-1 "new" text |
| F-2 applied as written and correct | Satisfied | Identical text; control 5/5; `m-just.sh` reds; boundary analysis above |
| Exit 2 = no verdict (SKILL.md §2, escalation.md) | Satisfied for `git status`, grep exit ≥ 2 and missing `just` | Major 1 is a failure that produces a *verdict* (0) rather than 2 |
| bash 3.2 / BSD grep portability | Syntax satisfied; failure behaviour not (Major 1) | Portability section |

## Positive Observations

- The `[^RC]` guard covers both columns. That is needed: an intent-to-add
  worktree rename appears as ` R` in the Y column, and the guard catches it.
- Porcelain v1 without `-z` escapes newlines, tabs, quotes and backslashes
  inside a quoted path. Line-oriented `grep -v` is therefore sound: one entry
  per line, and an escape cannot reach outside `[^/]+`.
- Every `ERROR:` line is printed after git's own `fatal:` text (stderr is
  merged at line 2), so the exit-2 report carries its cause.

## Recommendations

- **`C` half of the guard is unpinned.** The test review already noted this.
  The table above confirms a `C` line is reachable (`status.renames=copies`
  with a modified source) and that dropping `C` would make it CLEAN. The test
  file is OUT here. Pinning it belongs in a later slice.
- **Unmerged exempt paths pass.** `UU .claude/handoff-task.md` mid-merge is
  CLEAN, and so are `AA`/`DD` on exempt paths. Not raised as a finding: KD-7
  says "in any porcelain state", and the failure is loud. Any later
  `git commit`, with or without `-- <paths>`, refuses during a merge with
  unmerged files. Verified in a scratch repo: `fatal: cannot do a partial
  commit during a merge.` (rc 128) and `Committing is not possible because
  you have unmerged files.` (rc 128). If KD-7 is revisited, `U` could join the excluded
  characters. That is a design call, not a regex fix.
- **`"?…"?` accepts an unbalanced quote.** Git never emits one: a path
  holding `"` is quoted and escaped as `\"`, and the `\.md"?$` tail then fails
  to match. No behaviour depends on the imbalance, so this is not a finding.
- `echo "$status"` (line 36) prints porcelain data that can hold backslashes.
  Under bash's default `xpg_echo` off, which is how the shebang's `bash` runs
  on Linux and macOS, it prints verbatim. Only an exported
  `BASHOPTS=xpg_echo` changes that. Not raised.
