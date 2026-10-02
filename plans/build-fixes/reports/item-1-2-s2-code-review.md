# Review: Item 1.2 slice 2 — code review (exempt paths committed in the run are dropped)

**Scope**: `plugin/skills/build/scripts/exempt-paths.sh`, `verify-step.sh`, `changed-files.sh` as of HEAD (`✨ Item 1.2/2 — exempt paths committed in the run are dropped`). Tests out of scope (already test-reviewed).
**Date**: 2026-10-02
**Mode**: review + fix

## Summary

The slice moves the exempt alternation into a sourced `exempt-paths.sh`. `verify-step.sh` composes its porcelain pattern from it. `changed-files.sh` drops matching paths inside its NUL-delimited read loop using an anchored, grouped `=~`. The composed `verify-step.sh` pattern is byte-identical to the old literal, the anchoring is correct, and the tests are green.

The review found and fixed four issues:
- A sourced file that leaves the variable unset gave exit 1, which is a verdict code in both scripts.
- A comment wrongly claimed the scripts are always invoked by absolute path. `/build` invokes `verify-step.sh` by a relative path.
- The shellcheck `source=` directive pointed at the wrong place and never resolved.
- Two comments were laid out badly.

**Overall Assessment**: Ready

## Verification of the scoped checks

- **Verdicts unchanged.** A bash probe evaluated the composed string `'^[^RC][^RC] "?('"${EXEMPT_PATHS_ALTERNATION}"')"?$'` after sourcing `exempt-paths.sh`. It printed `IDENTICAL` against the HEAD~1 literal `^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$`. The end anchor, the optional quotes and the R/C exclusion are all unchanged. `tests/test_verify_step.py` is green (8/8, run together with `test_changed_files.py`: 10/10).
- **changed-files anchoring.** `exempt_re='^('"${EXEMPT_PATHS_ALTERNATION}"')$'` groups the top-level `|` alternatives before anchoring. bash's `=~` compiles without `REG_NEWLINE`, so `^`/`$` anchor at the ends of the whole string: `memory<LF>x` does not match. The regex sits unquoted in a variable on the right of `[[ =~ ]]`, which is the bash-3.2-safe form (3.2 treats a quoted RHS as a literal).
- **Mutated-SUT run (once).** I mutated `changed-files.sh` in place to the ungrouped `exempt_re='^'"${EXEMPT_PATHS_ALTERNATION}"'$'` and `test_exempt_paths_committed_in_the_run_are_dropped` went red (1/2 passed). The `docs/inbox/x.md` and `memoryx.txt` decoys catch the lost anchoring. I restored it with the inverse exact-string Edit. Proof: `grep -n '^exempt_re='` shows line 52 grouped, `git diff --stat` was empty, and the run was green again at 2/2.
- **Sourcing idiom.** I probed a scratch copy of the three scripts in a directory whose name contains a space:
  - absolute path: CLEAN
  - relative invocation (`../dir with space/verify-step.sh`): CLEAN
  - `bash verify-step.sh` from the script directory (`script_dir="."`): CLEAN
  - path through a symlinked directory: CLEAN
  - `changed-files.sh` invoked relatively from a repo subdirectory: correct `BASE:` and list, because the source runs before `cd "$top"`
  - symlink to the script file itself: `ERROR:` exit 2. This fails closed. No production path symlinks these scripts (`find plugin -type l` finds only `plugin/.claude/skills`).
  - missing `exempt-paths.sh` or a syntax error in it: exit 2.
  - variable unset: exit 1. Defect, issue 1 below.
- **bash 3.2.** `${BASH_SOURCE[0]%/*}`, `if ! source …`, `[[ -z ${V:-} ]]` and unquoted-variable `=~` are all bash-3.2 constructs, and there are no BSD/GNU tool dependencies (no `dirname`, `sed`, `readlink`). I did not run bash 3.2 itself: no 3.2 binary on this host.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A sourced file that leaves the variable unset exits 1, a verdict code**
   - Location: `verify-step.sh:29-33`, `changed-files.sh:48-52` (HEAD)
   - Problem: `source … || { exit 2; }` catches only a source that fails. If `exempt-paths.sh` loads but leaves `EXEMPT_PATHS_ALTERNATION` unset (a rename in one file, a truncated edit), the next line's expansion trips `set -u`. Bash then exits 1 with `unbound variable`. I reproduced this: `verify-step.sh` rc=1. Exit 1 is DIRTY in `verify-step.sh`, which the orchestrator remediates against. In `changed-files.sh` it is the `NO-BASE:` code (interface). The scope requires that a source failure be exit 2, never a verdict.
   - Fix: `if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]; then echo "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"; exit 2; fi` in both scripts. Re-probed: unset gives rc=2 in both, a missing file gives rc=2, and the normal paths still pass.
   - **Status**: FIXED

2. **Comment claims an always-absolute invocation; production is relative**
   - Location: `verify-step.sh:21-23`, `changed-files.sh:39-42` (HEAD)
   - Problem: "`BASH_SOURCE[0]`, which the harness always invokes by absolute path" is false. `plugin/skills/build/SKILL.md` §2 and `references/finishing.md` run `plugin/skills/build/scripts/verify-step.sh` relative to the repo root. The idiom works for relative paths only because nothing changes directory before the source. The comment hid that load-bearing ordering, which matters most in `changed-files.sh`, where a `cd "$top"` follows.
   - Fix: `verify-step.sh` now says that `BASH_SOURCE[0]` is absolute or CWD-relative and names the production relative call. It also says that nothing changes directory before the source, and it states the symlink residual bound (exit 2). `changed-files.sh` points to that explanation and says why its source must precede the `cd` below. The idiom is now explained once.
   - **Status**: FIXED

### Minor Issues

1. **shellcheck `source=` directive never resolves**
   - Location: `verify-step.sh:28`, `changed-files.sh:47` (HEAD)
   - Problem: `# shellcheck source=exempt-paths.sh` is resolved against shellcheck's CWD. `shellcheck -x` from the repo root (and from `/`, as the PostToolBatch hook runs it) reports `SC1091 … exempt-paths.sh: openBinaryFile: does not exist`, so the directive never let shellcheck follow the file.
   - Fix: `# shellcheck source=SCRIPTDIR/exempt-paths.sh` in both. `shellcheck -x` on all three files from `/` now exits 0.
   - **Status**: FIXED

2. **`verify-step.sh` comment layout separates the pattern from its explanation**
   - Location: `verify-step.sh:5-33` (HEAD)
   - Problem: The sourcing comment and code sat between the long porcelain-pattern explanation and `exempt=`, the line that explanation describes. The slice also dropped the `(KD-7)` citation from the safety argument that the citation labels. The outline's KD-7 addendum depends on "the script comment already says so".
   - Fix: The source block now comes first and the pattern explanation sits directly above `exempt=`. "sourced below" was dropped, since the source now precedes it, and `(KD-7)` was restored on "Safe to exempt".
   - **Status**: FIXED

3. **Code span split across comment lines in `exempt-paths.sh`**
   - Location: `exempt-paths.sh:10-11` (HEAD)
   - Problem: `` `.claude/handoff-`` ended one line and `*.md`` began the next, so the one path a reader must recognise read as two fragments.
   - Fix: Reflowed so `` `.claude/handoff-*.md` `` sits on one line.
   - **Status**: FIXED

## Fixes Applied

- `plugin/skills/build/scripts/verify-step.sh:5-21`: the source block moved above the pattern explanation, an unset-variable guard was added (exit 2), the comment now covers relative invocation and the symlink bound, and the directive is `source=SCRIPTDIR/…`.
- `plugin/skills/build/scripts/verify-step.sh:23-25`: "sourced below" dropped and `(KD-7)` restored.
- `plugin/skills/build/scripts/changed-files.sh:39-52`: the comment points to `verify-step.sh`'s explanation and states the ordering before the `cd`, an unset-variable guard was added (exit 2), and the directive is `source=SCRIPTDIR/…`.
- `plugin/skills/build/scripts/exempt-paths.sh:9-12`: comment reflowed so the `.claude/handoff-*.md` code span is not split.

After the fixes: `tests/test_verify_step.py` and `tests/test_changed_files.py` pass 10/10, `shellcheck -x` exits 0, and `just precommit` printed `Precommit OK` (371/372, 1 xfail). The `oversized-file` lines for three `plugin/agents/*.md` files predate this change.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Slice 2: run-committed `inbox/x.md`, `.claude/handoff-task.md`, `memory` absent from list | Satisfied | `changed-files.sh:85-87`; test green; ungrouped-anchor mutant red |
| Interface: paths read from NUL-delimited diff, never split on whitespace | Satisfied | `git diff --name-only -z` + `read -r -d ''`; exempt match inside the same loop |
| Interface: exit 2 `ERROR:` on failure | Satisfied (after fix) | Source and unset-variable failures now exit 2 |
| `verify-step.sh` verdicts unchanged, pattern composed from `exempt-paths.sh` | Satisfied | Composed pattern byte-identical to the HEAD~1 literal; `test_verify_step.py` green |
| KD-6: one sourced file holds the alternation | Satisfied | `exempt-paths.sh`; both scripts source it |
| Slice 3 `NO-BASE:` | DEFERRED | Scope OUT |

---

## Positive Observations

- The exempt match runs inside the existing NUL-delimited loop rather than in a second grep pass, so there is no second NUL-handling surface.
- The alternation is a bare, unanchored ERE, and each caller adds its own anchors and context. That keeps the porcelain prefix and quote allowance out of the shared file.
- `script_dir="."` covers `bash verify-step.sh` with no directory component.
- The test's decoys (`docs/inbox/x.md`, `memoryx.txt`) are exactly what an ungrouped `^a|b|c$` gets wrong. The mutant confirmed it.

## Recommendations

- No refactoring is needed. The five-line locate-and-source idiom is duplicated across the two scripts, but it cannot be shared without first sourcing something, so the duplication is inherent.
