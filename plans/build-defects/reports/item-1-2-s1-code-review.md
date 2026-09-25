# Review: Item 1.2 / Slice 1 — code review (GREEN 31fe4a16)

**Scope**: `plugin/skills/build/scripts/verify-step.sh` (every line, not only
the diff) and the `justfile` `run-pytest` sentinel line added in 31fe4a16.
**Date**: 2026-09-25
**Mode**: review + fix. Fixes to both files are routed to my human partner:
the one permitted `Edit` on `verify-step.sh` was refused by the auto-mode
classifier ("gave no verdict … Don't retry it"). It was not retried and no
sed or Bash rewrite was used. `git diff` on both files is empty after the
review.

## Summary

The KD-7 exemption works for the cases the slice pins, and the real-repo
dogfood run agrees. Two problems remain. First, the `^.. ` prefix accepts
rename lines, so a staged rename *out of* `inbox/` or `.claude/handoff-*`
passes as clean. Second, a `git status` failure exits 128, which is outside
the documented 0/1/2 contract. Both fixes were checked on a copy of the
script and are given below as exact text. Separately, KD-7's own safety
argument does not hold for *staged* exempt dirt, which the slice
deliberately exempts. That needs a design decision (UNFIXABLE, U-DESIGN).

**Overall Assessment**: Needs Significant Changes. One UNFIXABLE finding
needs a decision. Two major fixes and one minor fix are written out below
but NOT APPLIED.

## Evidence gathered

I ran the committed script unmodified against a throwaway repo in
`$TMPDIR`, with a stub `just` and git config insulated:

| Porcelain line | Script verdict | Intended |
|---|---|---|
| (empty) | CLEAN, 0 | yes |
| `R  inbox/a.md -> notes.md` | **CLEAN, 0** | no: `notes.md` is a staged non-exempt path |
| `R  inbox/a.md -> inbox/b.md` | DIRTY, 1 | acceptable (conservative) |
| `?? "inbox/my brief.md"` | **DIRTY, 1** | no: it is an `inbox/*.md` |
| `?? "inbox/r\303\251sum\303\251.md"` | **DIRTY, 1** | no: same |
| `?? "inbox/q\"x.md"` | **DIRTY, 1** | no: same |
| `?? inbox/sub/x.md` | DIRTY, 1 | yes (`*` does not cross `/`) |
| `?? .claude/handoff-foo.md` | CLEAN, 0 | yes |
| not a git repo | **exit 128**, git's `fatal:` text only | no: 2 per SKILL.md §2 |

Git's porcelain v1 wraps a path in quotes when it contains a space, a
quote, a backslash or a non-ASCII byte (the default `core.quotePath`). This
repo leaves `core.quotePath` unset.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A rename out of an exempt path is judged as one exempt path**
   - Location: `verify-step.sh:16`
   - Problem: a v1 rename or copy line reads `XY old -> new`. With
     `inbox/a.md -> notes.md`, `inbox/[^/]+\.md$` matches `a.md -> notes.md`,
     so the line is filtered out. `.claude/handoff-x.md -> y.md` behaves the
     same way (observed CLEAN on the unfixed pattern). The result is that a
     staged addition of a non-exempt root-level `*.md` is reported CLEAN.
     KD-7 did not intend this: its exemptions name paths, not destinations.
     The comment's claim "the XY status may hold anything" is what lets it
     through.
   - Fix: reject rename and copy lines outright. Porcelain v1 uses `R` and
     `C` only for those. A rename *within* `inbox/` was already DIRTY
     (because of the second `/`), so every rename now gets the same
     conservative treatment. Exact text is under Fixes Routed, F-1.
   - **Status**: NOT APPLIED — routed to my human partner (classifier
     refused the Edit). Checked on a copy: the slice test stays green,
     shellcheck is clean, and both rename probes turn DIRTY, 1.

2. **`git status` failure exits 128, outside the 0/1/2 contract**
   - Location: `verify-step.sh:17`. The line was modified in this diff, and
     line 14's comment claims "`git status` must succeed".
   - Problem: under `set -e` a failing `porcelain=$(git status …)` exits
     with git's own code (128 outside a repo), and no `ERROR:` line is
     printed. SKILL.md §2 routes only exits 0, 1 and 2, with exit 2 meaning
     "no verdict". §4.4 sends "anything else" to `escalation.md`, whose
     §Post-item remediation also handles only 1 and 2. A 128 therefore
     falls through every routing table. The grep branch already maps
     failure to 2; the `git status` step does not.
   - Fix: add `|| { echo "ERROR: git status failed"; exit 2; }`. Exact text
     is in F-1, which covers both major fixes because the lines are
     adjacent.
   - **Status**: NOT APPLIED — routed to my human partner. Checked on a
     copy: outside a repo it prints git's `fatal:`, then
     `ERROR: git status failed`, and exits 2.

### Minor Issues

1. **Quoted exempt paths are reported as dirt**
   - Location: `verify-step.sh:16`
   - Problem: an `inbox/*.md` brief whose name holds a space, a quote or a
     non-ASCII byte gets quoted by git, and the `^.. inbox/` anchor misses
     it. The error is in the safe direction (false DIRTY, not a false
     CLEAN), but the downstream effect is bad. `escalation.md` §Post-item
     remediation tells the agent to "Fix and commit". The artisan could
     then commit another session's brief, which is exactly the outcome
     KD-7's inbox exemption exists to prevent. Brief names are kebab-case by
     convention, so this is unlikely in practice.
   - Fix: allow one optional pair of quotes around the path group. Quotes
     only become safe to allow once the `R`/`C` guard from Major 1 is in
     place: without it, `"inbox/a b.md" -> "x y.md"` would match. That is
     why both changes are in the single F-1 text.
   - **Status**: NOT APPLIED — routed (part of F-1). Checked on a copy:
     space, non-ASCII and quote-character briefs are CLEAN, 0, while
     `"inbox/my brief.txt"` stays DIRTY.

2. **A missing `just` is reported as a precommit failure** (pre-existing,
   lines 36–39, not touched by 31fe4a16; reported because the dispatch asked
   for the whole script to be audited)
   - Problem: if `just` is not on `PATH`, it exits 127, the `||` branch
     prints `PRECOMMIT: validation failed` and exits 1. The caller then
     tries to repair a "precommit failure" that is really a missing tool.
     That is an environment fault with no verdict, and the script's own
     convention for that is exit 2.
   - Fix (F-2, optional):
     ```
     old:
     just precommit || {
     new:
     command -v just >/dev/null || {
         echo "ERROR: just not found on PATH"
         exit 2
     }
     just precommit || {
     ```
     `command -v … >/dev/null` discards only the resolved path, not an
     error, so it does not break the no-suppression rule.
   - **Status**: NOT APPLIED — routed to my human partner. Not checked on a
     copy.

### UNFIXABLE

1. **KD-7's safety argument fails for staged exempt dirt**
   - Location: `verify-step.sh:8–10` (the comment copies KD-7's argument),
     `plans/build-defects/outline.md` KD-7. The slice test requires a
     staged `MM .claude/handoff-task.md` to be CLEAN.
   - Problem: the comment and KD-7 say exempt dirt "never enters a commit"
     because commits stage by name. That is true of unstaged and untracked
     exempt dirt. It is false of exempt dirt that is already *staged*: a
     pathspec-less `git commit` records the whole index. I reproduced this
     in a throwaway repo. With `.claude/handoff-task.md` staged, running
     `git add src.py && git commit -m …` committed both files. Every
     committing dispatch commits this way (`test-driver.md` step 6,
     `refactor.md:181–182`, `dispatch-composition.md:34–35`). None uses
     `git commit -- <paths>` or `--only`. `.claude/handoff-task.md` and
     `.claude/handoff-todo.md` are tracked here, and KD-7 names "staged" as
     an expected handoff state, so the leak path is real. `M  memory` (a
     staged submodule bump) and `A  inbox/x.md` belong to the same class.
     Before this change, only ` M memory` (unstaged) was exempt, so the
     change introduced this gap.
   - **Status**: UNFIXABLE (U-DESIGN)
   - **Investigation:**
     1. Scope OUT: not listed. It is not the sandbox-mask item or any other
        OUT bullet.
     2. Design deferral: KD-7 does not defer it. KD-7 asserts the premise.
     3. Codebase patterns: `rg` found no `git commit --` or `--only` use in
        `plugin/`. Nothing in the pipeline scopes commits to their paths.
     4. Conclusion: there are two valid fixes, and each has consequences
        outside this item. (a) Make every committing dispatch commit with
        `git commit -- <its paths>`. That touches `dispatch-composition.md`,
        `test-driver.md` and `refactor.md` (Item 2.x or other jobs) and
        keeps KD-7 as written. (b) Exempt only unstaged or untracked states
        (X column ` ` or `?`), so staged exempt dirt is DIRTY. That
        contradicts KD-7's "in any porcelain state" and the slice test's
        staged handoff, and it would stop `/build` after every `/precompact`
        that stages the handoff. The choice belongs to my human partner.
        Until it is made, the comment at lines 8–10 overstates the
        guarantee.

## Fixes Routed (NOT APPLIED — routed to my human partner)

**F-1** (Major 1, Major 2, Minor 1), one contiguous replacement in
`plugin/skills/build/scripts/verify-step.sh`, lines 10–17:

old:
```
# exempt dirt never enters a commit. The two-column XY status may hold
# anything, so the pattern matches only the path after it.
# `--untracked-files=all` explodes an untracked `inbox/` into its files, since
# a collapsed `?? inbox/` line is not a path the exemption can judge.
# `git status` must succeed; only grep's exit 1 (every line filtered out) is
# a result rather than a failure, so tolerate that one code and nothing else.
exempt='^.. (memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)$'
porcelain=$(git status --porcelain --untracked-files=all)
```

new:
```
# exempt dirt never enters a commit. The two-column XY status may hold any
# state but a rename or copy: an `R`/`C` line's `old -> new` is two paths, and
# `inbox/a.md -> b.md` would pass as one exempt path. Git quotes a path holding
# a space or a non-ASCII byte, so the pattern allows the quotes.
# `--untracked-files=all` explodes an untracked `inbox/` into its files, since
# a collapsed `?? inbox/` line is not a path the exemption can judge.
# `git status` must succeed; only grep's exit 1 (every line filtered out) is
# a result rather than a failure, so tolerate that one code and nothing else.
exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'
porcelain=$(git status --porcelain --untracked-files=all) || {
    echo "ERROR: git status failed"
    exit 2
}
```

I applied this exact old→new text by string replacement to a copy in
`$TMPDIR` (`count(old) == 1` asserted) and checked it:

- `test_conventional_dirt_is_clean_and_other_dirt_is_not` passes against the
  copy. I imported the test module and rebound only `SCRIPT`; the test file
  was not relocated.
- `shellcheck` is clean and `bash -n` passes.
- The probe table above gives the intended verdict on every row.

Every construct is portable to bash 3.2 and BSD `grep -E` (POSIX ERE
bracket expressions, `?`, and alternation, with no backreferences). If the
UNFIXABLE item resolves toward option (b), the text at lines 8–10 changes
again. Line 16's `^[^RC][^RC]` would then become an X column restricted to
` ` or `?`.

**F-2** (Minor 2): the text is in Minor 2 above.

## Fixes Applied

None. The one `Edit` attempt (F-1) was refused by the classifier, and
`git diff -- plugin/skills/build/scripts/verify-step.sh justfile` is empty.

## Mutated-SUT run

The test ran once per mutant against a mutated **copy** of the SUT, with
the test module's `SCRIPT` rebound. I did not mutate the file in place: if
the classifier refused the restoring `Edit`, the tracked SUT would have been
left mutated.

| Mutant | Result |
|---|---|
| unmodified copy (control) | green |
| drop `--untracked-files=all` | **red** |
| `inbox/[^/]+\.md` → `inbox/.*` | **red** |
| `\.claude/handoff-[^/]+\.md` → `\.claude/handoff-.*` | **red** |
| `^.. (` → `^ M (` (single-column status) | **red** |
| F-1 proposed text | green |

Every forbidden mutant turned the test red. The rename-escape and
quoted-path behaviours are not pinned by any test. The test file is OUT of
scope here; see Recommendations.

## justfile sentinel line

The line is correct and needed. `tests/test_verify_step.py` executes
`plugin/skills/build/scripts/verify-step.sh`. Before this line, no hashed
path covered it, so an edit to the script alone left `Tests cached` green:
the gap `gate-cache-must-cover-every-check.md` describes. Widening is the
right fix under that memory, because the test exists to read this tree.
`git ls-files -z --cached --others --exclude-standard
plugin/skills/build/scripts/` lists exactly `verify-step.sh`, so its
contents now enter the `cksum`. The GREEN report independently recomputed
the stored sentinel against the widened list. I checked the other paths the
suite reads: the only other `plugin/` inputs, `plugin/bin/` and
`plugin/hooks/`, were already hashed. `plugin/portable.just` appears only
in a docstring. No finding.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| orch m5 / KD-7: any change is dirt | Satisfied | `?? stray.txt` and decoys DIRTY (slice test) |
| KD-7: `memory`, `.claude/handoff-*.md`, `inbox/*.md` exempt in any state | Partial | Unquoted paths are exempt in any XY state. Quoted paths are not (Minor 1). Renames out of an exempt path wrongly pass (Major 1) |
| KD-7: status under `--untracked-files=all` | Satisfied | `verify-step.sh:17`; the mutant without it goes red |
| KD-7: masks neither filtered nor gitignored | Satisfied | No mask names in the pattern |
| KD-7: "exempt dirt cannot enter a commit" | Not satisfied for staged states | UNFIXABLE 1 |
| Exit 2 = no verdict (SKILL.md §2) | Partial | grep failure → 2; `git status` failure → 128 (Major 2) |

## Positive Observations

- A single `grep -vE` with the exemption anchored on the path after the
  status columns handles `MM`, `M `, ` M` and `??` uniformly, and the slice
  test's `MM` fixture pins that.
- `--untracked-files=all` also overrides a user's
  `status.showUntrackedFiles=no`, which previously could have hidden
  untracked dirt entirely.
- The grep exit-code handling is precise: 0 → listing, 1 → empty, anything
  else → exit 2 with an `ERROR:` line, and the comment says why.
- The DIRTY listing echoes the raw porcelain lines, which is what KD-7
  needs for the `sandbox-lies` annotation to be readable.

## Recommendations

- Once F-1 lands, add a slice that pins `R  inbox/a.md -> notes.md` as DIRTY
  and `?? "inbox/my brief.md"` as CLEAN, plus a non-repo CWD giving exit 2.
  No current test detects any of the three.
- Resolve UNFIXABLE 1 before Item 2.1 writes the §2 DIRTY bullet, which
  names the KD-7 exemptions and would carry the same premise.
