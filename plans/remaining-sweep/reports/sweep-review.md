# Sweep review — uncommitted working tree against HEAD

Reviewed the whole uncommitted tree against HEAD. Scope excluded untracked
`.claude/*`, `inbox/` and `plans/skill-reviews/`. Reports under
`plans/remaining-sweep/reports/` were treated as claims and checked against the
diff; two of them assert mechanisms that do not hold (C1, C2 below).

Verdict: the sweep is sound. One critical defect in `plugin/portable.just`'s
`format` recipe was actively reverting work and hiding it; fixed. Nine fixes
applied in total — **one of them correcting a defect this review itself
introduced** (C3). Four findings left unfixed, with reasons. The owed docs
coupling (group 9) is added.

**Read the concurrency note first.** The tree kept changing under this review,
inside its scope and in five files outside it. Everything below is true as of
the final gate run; §"Concurrent modification" says what moved.

## Critical

### C1 — `just format` formatted docstrings, then reverted them

`plugin/portable.just`, recipe `format`, the `docformatter` line.
`pyproject.toml` `[tool.docformatter]` sets `in-place = true`, so `docformatter
--diff src tests` **rewrites the files** and then prints a `before/`→`after/`
diff, exiting 3. The line piped that diff into `patch-and-print -Rp1` — a
*reverse* apply, which undid the rewrite. Net effect per dirty file:
docformatter fixed it, `patch -R` put it back, the file was still listed under
"Reformatted files", and the following `docformatter -c` failed on it. `|| true`
hid all of it, so `just dev` reported a docformatter failure on code the user
had just formatted.

Reproduced against a faithful config copy. Old code, one dirty docstring:
listing says `src/doc.py`, file on disk byte-identical to the unformatted
original, `docformatter -c` exits 3.

Fixed: docformatter's in-place write now stands; the diff is read only for file
names (`sed -ne 's|^--- before/||p'`), exit 3 and 0 are both results, anything
else is a loud `fail`, and the `|| true` is gone. Verified on the same probe —
the docstring stays formatted, both files are listed accurately, and
`docformatter -c` and `ruff format --check` exit 0 afterwards.

This was the last `|| true` in either justfile, so the fix also closes an NFR-2
("errors never pass silently") violation rather than only a behaviour bug.

### C3 — this review introduced a copy-based mutation restore; corrected

`test-driver.md` §RED step 4; `tdd-slice.md` §Mutation proof and §(d). An
earlier pass of this review changed `test-driver.md` to verify a mutation
restore with "`cmp` against a copy saved before the first mutation". That is the
method `craft:test-discipline` measured and rejected —
`references/genuine-red.md` §"Restore by inverting the edit, never from a copy":
a `$TMPDIR` backup succeeded, the suite redded, and the restore one call later
read an empty `$TMPDIR`, leaving the mutation live in a tree holding uncommitted
work. It also rejects `${TMPDIR:-/tmp}` (same cross-call assumption) and `git
checkout`/`git stash` (they discard the checking session's own uncommitted
work). `tdd-slice.md` carried the defect independently ("a checksum against a
copy"), and its §(d) prescribed "save, mutate, run, restore" — `save` being the
copy.

All three now prescribe the grounded method: mutate by exact string replacement
with a string unique in the file, restore by applying it with the two strings
swapped, and prove the restore by grepping for the mutation text expecting no
hit, then the suite green — "the replacement exiting 0 is not the evidence."
This also dissolves what the bad fix was reaching for: grep works whether or not
the SUT is committed, so the uncommitted-stub case needs no special casing.

## Major

### C2 — `patch-and-print` mishandled quoted names; its comment is false

`plugin/portable.just`, `format` → `patch-and-print`. The new comment claims
"This GNU patch (2.8) prints `patching file PATH` unquoted, in both forward and
reverse mode (verified live)". GNU patch 2.8 on this box prints `patching file
'has space.txt'` — quoted — for a name needing it, in both directions. So the
new `s/^patching file //p` leaves the quotes on, and HEAD's version (which
matched *only* the quoted form) dropped unquoted names entirely. Neither form
was right.

Fixed to accept both: `s/^patching file '?([^']*)'?$/\1/p`, verified against
both inputs. The residual bound (a name containing a literal single quote comes
back with patch's own `'\''` escaping) is stated in the comment rather than
implied away.

Separately verified and now stated as a bound in `apply-ruff-diff`: ruff writes
a bare `--- PATH` header with no tab, so for a path containing a space `patch`
reads the name up to the space and the hunk fails. That is now a loud failure by
design (it was a silent skip under the old blanket `|| true`).

### `run-lint-checks` had no format check, so `just check` missed it

In `plugin/portable.just` and `justfile`: `run-checks` gained `ruff format
--check`; `run-lint-checks` did not. Of its four consumers, `lint`, `green` and
`red-lint` all declare `format` as a dependency, so for them the check is
redundant-but-free. `check:` declares no dependency and does not mutate — so
`just check` was the one checking recipe that could not notice unformatted code.
Added to both copies with the reason in a comment. This also makes D-22's `just
check && just test` verification actually cover format.

### Root `justfile` duplicates portable's `precommit` body — UNFIXABLE

`justfile`, recipe `precommit`. The override copies six body lines plus a
four-line `rumdl` comment verbatim from `plugin/portable.just`'s `precommit`,
adding only `run-design-links`. Any future check added to the portable
`precommit` will silently not reach this repo.

The clean alternative is a hook: `portable.just` ends its `precommit` with
`run-project-checks`, defines it as a no-op in its own `bash_prolog`, and the
root defines it as `run-design-links`; the root's override then disappears. Not
applied, because it is not safe from here — the root `bash_prolog` *overrides*
portable's wholesale, so any other consuming project that also overrides
`bash_prolog` would lose the no-op and get `run-project-checks: command not
found`. That is a contract change to the shipped module and belongs to whoever
owns its consumers. The ~100-line `bash_prolog` duplication already present is
the same problem and predates this change.

### `docs/changelog.md` is at 398/400 — no room for the next entry

The owed design-links entry fits (see group 9), but the file now has two lines
of headroom against a 400 cap it is not allowlisted for. The next
design-significant change cannot be recorded without a trim or split, and per
the convention a file parked at its cap has stopped emitting the signal.
Reporting rather than cramming or raising a ceiling; this needs its own job.

## Minor — fixed

- **`check_design_links.sh` could report a lie.** `cd "$ROOT" 2>/dev/null || {
  echo "no such directory" ...}` suppressed `cd`'s own diagnostic and then
  asserted the cause. A permission error was reported as a missing directory.
  Now `cd` prints its own reason and the script's message is neutral ("cannot
  enter").
- **Bare `mktemp` is a usage error on macOS.** Both gate scripts used it while
  `check_design_links.sh` explicitly claims macOS bash 3.2 portability; BSD
  `mktemp` has no default template. Both now use `mktemp
  "${TMPDIR:-/tmp}/<name>.XXXXXX"`, the portable form given in
  `shell-scripting:shell-gotchas` `references/portability.md` §mktemp.
- **`check_design_links.sh`'s header overstated its scope** — it claimed to
  check the hub `docs/design.md`, which it never reads. Corrected to say what it
  does check and why the hub is deliberately out, which is also why omitting
  `docs/design.md` from the sentinel is correct rather than an oversight.
- **`test-driver.md` carried a restore check that misreports.** RED item 4 gave
  only `git diff --quiet <sut>`, which reports a successful restore as a failure
  when the RED dispatch wrote the stub itself (k=1) — the stub is a diff against
  HEAD. The first attempt at this fix was wrong; see C3 for the grounded
  replacement that supersedes it.

## Concurrent modification — scope caveat on this review

At 01:59:25–01:59:30, after this review's first full gate run, three files
inside its scope were rewritten by something other than this review:
`plugin/agents/tdd-auditor.md`, `plugin/agents/test-driver.md`,
`plugin/skills/build/references/tdd-slice.md`. The wording is neither this
review's nor that of the consistency reviewer it dispatched. Two real defects,
present at HEAD and present when this review read the diff, were fixed there:

- `tdd-auditor.md` §Edge Cases at HEAD said "fall back to the dispatch's
  transcript under the session's `subagents/` directory" — which
  `memory/ddaanet/shared-claude.md` forbids outright, and which `finishing.md`
  had been edited this session to remove. It now returns `blocked: report
  missing for <dispatch name>`, and `grep -rn 'subagents/' plugin/` is empty.
- `tdd-slice.md` §(a) and `test-driver.md` §RED step 1 at HEAD said RED "does
  not touch the SUT" for k>1, contradicting the mutation proof the same sweep
  added. Both now carry an explicit exception for it.

Both were genuine findings this review had missed, and both were already fixed
on disk by the time it looked, so it verified rather than re-applied them. The
consistency reviewer reported them as live because it was quoting HEAD-era text.

Also modified after this review began and **outside the brief's groups —
unreviewed here**: `plugin/skills/formalize/SKILL.md`,
`plugin/skills/ground/SKILL.md`,
`plugin/skills/ground/references/grounding-criteria.md`. None appeared in the
session-start `git status`.

The writer left its files un-reflowed, so this review's final `just format` had
to rewrap seven files. A line count is only honest after the formatter has run.

**Ratchet owed, not applied:** `plugin/skills/design/SKILL.md` is now 277 lines
against a ceiling of 285, because the reflow shortened it. The allowlist's own
rule is that a ceiling follows a shrink down, so the entry should become 277.
Not applied — lowering it while a writer is active in `plugin/skills/` would
hand them a red gate for in-flight work. No ceiling was raised and nothing grew.

## Minor — not fixed

- **`check_design_links.sh` leaks one temp file** when the first `mktemp`
  succeeds and the second fails — the `EXIT` trap is installed after both.
  Trapping earlier needs an empty-value guard under `set -u`; not worth it.
- **`find` ordering makes violation-line order filesystem-dependent**, never
  their content; no test depends on ordering.
- **`plugin/fragments/token-economy.md` now conflicts on its face with 11 sites
  — contested, owner's call.** The fragment now says `path:line` belongs "only
  in a dated write-time record", and `runbook/SKILL.md` was changed to match (no
  line numbers in code-fix items). But `plugin/skills/review/SKILL.md` (3),
  `plugin/skills/deliverable-review/SKILL.md` (2) and
  `plugin/agents/corrector.md` (6) still prescribe `file:line` for findings.
  Either a review report *is* a dated write-time record — in which case the
  exception covers them and nothing changes — or it is not, and 11 sites need
  updating. The differential treatment the sweep applied (changed the
  prescriptive runbook, left the frozen report templates) suggests the former,
  but making that explicit means adding words to a fragment every consumer pays
  for, and deciding it is a design judgement rather than a defect. Not guessed.
- **`dispatch-composition.md` §Prompt contents says "Every dispatch prompt
  carries" but does not cover `tdd-audit`,** whose inputs are the slice reports
  and git alone (`finishing.md` §3, `tdd-auditor.md` §Inputs); D-85 names only
  `artisan` and `test-driver` as needing the skills fallback. The file's opening
  already bounds it ("from a runbook item, or from an ad-hoc task") and item 4
  carries a per-dispatch "Overrides" clause, so the looseness costs at most two
  redundant Reads, never a wrong result. The lighter fix is one clause on the
  "Every dispatch" line, not the agent-name enumeration the reviewer proposed,
  which would rot. Not applied — a wording nit in a concurrently-edited file.
- **`tdd-auditor.md` §Cross-Slice Checks "Scope compliance" names only later
  *items*, not a later slice of the same item.** A GREEN over-implementing
  within its own item (D-84) is caught indirectly by Per-Slice Check 1's
  mutation-proof accounting but not named here. An enhancement to audit
  coverage, and a judgement about what the auditor should catch. Reported for
  the owner.
- **`plugin/skills/design/SKILL.md` gained `Edit` in `allowed-tools`** with no
  recorded rationale. The reason is evident (revising an outline without a full
  rewrite) and `docs/references/project-configuration.md` governs frontmatter,
  but no decision line records it. Flagging, not fixing — it may be deliberate
  and too small to index.

## Verified clean — no findings

**Group 1, the test split is a pure move.** HEAD's `tests/test_review_range.py`
compared against the five new modules plus `tests/review_range_helpers.py` by
AST, per top-level definition: 17 old definitions, 18 new, **nothing dropped,
zero bodies differing**, no definition duplicated across modules. The single
addition is `test_one_hop_only_ignores_grandprior_mismatch`, as documented. All
module-level scaffolding (`REPO_ROOT`, `BIN_DIR`, the four `_write`/`_run`
helpers, the imports) is accounted for in the helper module, which contains no
`def test_` that would now go uncollected. 15 tests pass across the five modules
(12 definitions, 2 parametrized).

**Mutation check 1 — the new test is genuine.**
`plugin/bin/edify-review-range.sh` mutated to chase a second hop through the
prior artifact to its grandprior.
`test_one_hop_only_ignores_grandprior_mismatch` failed on its own assertion with
exactly the outcome its docstring predicts — `CONFLICT: base adc7ad1… !=
d73d108… inherited from plans/job-b/outline.md`, `assert 1 == 0`. Restored,
byte-identical, `git status --porcelain` empty for that path.

**Mutation check 2 — the CRLF gate is genuine.** With the carriage-return block
removed from `scripts/check_line_limits.sh`, both
`test_line_limits_rejects_crlf_on_full_entry_line` and
`…_on_two_field_entry_line` failed. Restored, byte-identical, 16/16 pass. These
two tests defend against a real false-pass: the allowlist's `tmp_path` is
embedded in the script's diagnostic and pytest derives that directory name from
the test's own name, which contains "crlf" — both strip it before the wording
assertion. The CR check is also correctly ordered *before* the integer check, so
a two-field CRLF line reports the carriage return rather than blaming the
ceiling. (Both checks used a `$TMPDIR` backup — see C3 on why that method is not
the one to prescribe.)

**Group 3, whitespace and read-loop safety.** The allowlist loop is `IFS=$'\t'
read -r … || [ -n "$entry_path" ]`, so a final line without a newline is not
dropped, and the CR test covers every field a CR can land in under that `IFS`.
Both gate scripts walk NUL-delimited throughout (`find -print0` spooled to a
temp file, `read -r -d ''`). `shellcheck` clean on all four changed shell files.

**Group 4, sentinel correctness.** `git ls-files --cached --others
--exclude-standard` is NUL-delimited end to end. The root copy's extra inputs
are justified: the suite executes both gate scripts (so `scripts/`), and
`tests/test_design_links.py:353` ends by running the design-links gate against
the real tree (so `docs/decisions.md` and `docs/references/`). `docs/design.md`
is correctly absent — no test reads it and the gate does not either.
`portable.just` adding only `scripts/` is right: a consuming project has no
design docs.

**Group 4, the `set -e` AND-list pattern.** Both gate scripts use `[ cond ] &&
continue` as a `for ((…))` body's first statement under `set -euo pipefail`.
Verified empirically that a failing left operand does not trigger `errexit`, so
neither aborts mid-scan and silently exits 1.

**Group 4, Python reformatting is semantics-free.** All nine ruff-reformatted
files (three under `src/edify/`, six under `tests/`) are **AST-identical** to
HEAD.

**Group 5, `verify-step.sh`.** `CLEAN: tree clean, just precommit passed`
accumulates as checks run; D-49 carries the same string and `build/SKILL.md`
updated both call sites.

**Group 7, the three new rules are consistent.** GREEN-scoping is stated in all
three places it has to act and agrees in all three — `dispatch-composition.md`
§Prompt contents item 3, `tdd-slice.md` §(c), `test-driver.md` §GREEN Mode: the
`Interfaces:` block goes in for structure, anything the slice's tests do not
reach is out. The mutation-proof rule agrees across `test-driver.md` RED step 4
and its escalation list, `tdd-slice.md` (both the proof and the test-review
reproduction with a *different* mutation), and `tdd-auditor.md` — including the
load-bearing "per named test, not per batch" in every one, and mutation framed
as fallback rather than route. This respects the convention against bundling a
red task into a green subagent: the proof replaces the red *evidence*, not the
separate dispatch. Recall skills-loading agrees across `recall/SKILL.md`,
`artisan.md`, `test-driver.md`, `write-outline.md` and
`fragments/delegation.md`, and the heading `## Skills to load before executing`
matches exactly between the template that writes it and the skill that reads it.

**The documented skill-resolution glob actually works.** `ls -dt
~/.claude/plugins/cache/*/<plugin>/*/skills/<name>/SKILL.md | head -1` resolves
against the real cache for two different plugins, so the instruction in
`artisan.md`, `test-driver.md` and `recall/SKILL.md` is grounded, not plausible.

**No stale removed-subsystem references.** The only `edify _recall` hits under
`plugin/` and `docs/` are in `CLAUDE.md` and `plugin/README.md`, both describing
it as removed. `grep -rn 'subagents/' plugin/ docs/references/` returns nothing.
No broken internal link found across the 13 prose files: every
`references/<x>.md` path, skill name and agent name resolves.

**Group 8, `docs/design.md` lost nothing.** Section headings identical to HEAD.
All 27 requirement ids and all referenced decision ids present on both sides.
Every FR/NFR statement, its §2 status and its full evidence list survive
verbatim in the new `**ID — statement.** Status; evidence` form, with the `·`
test separator preserved and now explained in the section lead-in. Ids sit
adjacent to their statements, so lookup by id still works. NFR-2's table-escaped
`\|\| true` is correctly de-escaped. FR-19/FR-20 were table rows on neither side
and remain recorded as dropped with ids not reused.

One content change outside the requirement sections: §5.1 dropped "— currently
`0.1.1`" from the version-lockstep sentence. Correct — it removes a volatile
currency claim, which is what the no-volatile-state convention asks for.

Both `docs/design.md` and the test split were independently re-verified by a
second agent by different methods, reaching the same conclusion. Its three
"differing bodies" against the AST comparison's zero is not a disagreement: all
three are line-wrapping changes leaving the AST identical.

**No allowlisted file grew**, and no ceiling was raised. One ratchet-down is
owed; see the concurrency note.

## Group 9 — owed docs coupling, added

- `docs/references/quality-gates.md`, D-46: `design links` added to the
  automated-checks enumeration, plus two paragraphs after the checklist — one
  naming what `check_design_links.sh` pins (every node-defined `D-<n>` indexed
  once, node conclusion a prefix of the index line's, every `Argued in` path
  resolving) and why the hub is deliberately unpinned; one on the sentinel
  hashing untracked files and carrying `scripts/` plus, root-only,
  `docs/decisions.md` and `docs/references/`, with `docs/design.md` absent for
  the same reason the gate skips it. D-46's bolded conclusion is untouched, so
  `docs/decisions.md` needs no matching edit and the gate stays green.
- `docs/references/testing.md`: **nothing owed.** It does not describe the
  sentinel — checked. Its D-22 (`just check && just test`) is strengthened
  rather than contradicted by the `run-lint-checks` fix.
- `docs/changelog.md`: one dated entry, `## 2026-09-21 — the design graph's
  crosslinks are checked mechanically`, six body lines after the reflow. See the
  Major finding on the file's remaining headroom.
- `scripts/check_design_links.sh` still passes: 85 decisions indexed, 8 nodes.

## Final gate

`just format` then `just precommit`, full output, exit 0:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 352 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 277 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
PRECOMMIT EXIT=0
```

Eight allowlisted lines, not the nine the brief expected: `proof/SKILL.md` fell
under its cap mid-review. `ruff check`, `ruff format --check`, `docformatter
-c`, `mypy` and `rumdl` printed nothing, which under `report` means each ran
clean. The suite was cached; it ran green in full (348/349 passed, 1 xfail)
earlier and every edit since has been prose the sentinel does not hash. Nothing
staged, nothing committed, no branch or worktree created; both mutated files
restored byte-identical against HEAD.

**This gate is a snapshot, not a standing result.** The tree was being written
continuously while it ran. The run before this one failed — `rumdl` wanted to
reflow `plugin/skills/runbook/SKILL.md`, which had been edited at 02:08:44,
between that run's `just format` and its `just precommit`. During the passing
run above, `plugin/skills/requirements/SKILL.md` was rewritten at 02:09:20 and
its count moved 357 → 352. Allowlisted counts have drifted repeatedly in twenty
minutes (`proof` 203 → 198, `design` 285 → 277, `requirements` 357 → 353), each
time because the writer's edits arrive un-reflowed and `just format` shortens
them.

So a green `just precommit` here means the tree was green at 02:09:25. `just
format && just precommit` must be re-run as one step once the writer stops:
running them separately is what produced the failure above. Further runs were
stopped deliberately rather than looped.

One reporting error of this review's own, for the record: the failing run was
first read through `| tail -3`, which showed a green-looking tail and an exit
code belonging to `tail`. That is the truncation anti-pattern `CLAUDE.md` names
under Validation Output Integrity, and it briefly turned a real failure into a
pass.
