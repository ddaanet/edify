# Review gate — code, tests, config

Group: `.rumdl.toml`, `plugin/bin/edify-review-range.sh`, `plugin/portable.just`,
`pyproject.toml`, `uv.lock`, `scripts/check_line_limits.sh`,
`scripts/check_line_limits.allow`, `tests/test_review_range.py`,
`tests/test_line_limits.py`. Baseline `1f54633b`.

Requirements M-4 (KD-2) and m-5 (KD-7, KD-8).

**Verdict: one Minor fixed. No critical or major defect in the group.** Two
design questions remain open from the slice reviews; both need a KD amendment
rather than a code change, and both are listed in §Open-items ledger. The
tree is red at the time of writing, for a cause outside this group — see
§Concurrent commit.

## 1. Fixed — the line-limit gate was the only check not wrapped in `report`

`run-line-limits` called `./scripts/check_line_limits.sh` bare, in both
`plugin/portable.just` and the root `justfile` (whose `bash_prolog` overrides
the portable one, so both copies had to change to take effect).

Two consequences, both created by Item 1.11 making the check live — before the
reflow the script only walked Python, found nothing, and printed nothing:

- **Ten unlabelled lines on every green run.** An allowlisted file is reported
  and does not fail (KD-7), so `just precommit` printed ten `oversized-file:`
  lines with no header saying what produced them. Every other check in the
  recipe goes through `report`, which prints `# <header>` whenever the command
  produced output.
- **An overage aborted the recipe before the summary.** Unwrapped and under
  `set -euo pipefail`, a non-zero exit killed `precommit` at that line, so
  `report-end-safe "Precommit"` never ran and no `✗ Precommit failed` was
  printed. This contradicts the shared convention that a quiet gate signs off
  with the checks that passed and fails legibly.

Fix, applied identically to `plugin/portable.just:73` and `justfile:173`:

```bash
run-line-limits() {
    # Wrapped like every other check: `safe` so an overage reaches
    # `report-end-safe` instead of aborting the recipe under `set -e`, and a
    # header so the `oversized-file:` lines an allowlisted file prints on
    # every green run say what produced them.
    report "line limits" ./scripts/check_line_limits.sh
}
```

`report` uses `safe`, which sets `status=false`; `report-end-safe` ends in
`end-safe`, so the recipe still exits non-zero on an overage. Measured on the
red path below: header present, `✗ Line limits failed`, exit 1.

**Note for the orchestrator:** the root `justfile` was not in this group's file
list. It had to change because it carries its own `bash_prolog` copy that
overrides the portable module's; changing only `plugin/portable.just` would have
left the two prologs divergent and had no effect in this repo. Drop the
`justfile` hunk if that is unwanted — but then drop the `portable.just` hunk
with it.

## 2. Measurements

### KD-8 — `.rumdl.toml` against `memory/ddaanet/markdown-formatter-choice.md`

Every shipped setting matches the memory's measured findings: `enable =
["MD013"]`, `line-length = 80`, `reflow = true`, `reflow-mode = "normalize"`,
`headings`/`code-blocks`/`tables = false`, `--no-cache` at every call site.
`reflow-mode = "normalize"` is the one the memory says a line-count cap has to
be measured against; it is set.

**`/*.md` anchoring — claim verified, not taken on trust.** Throwaway tree under
`$TMPDIR` with `root.md`, `sub/a.md`, `sub/deep/b.md`, `plans/c.md`:

| config `include` | files rumdl walked |
|---|---|
| `["*.md"]` | 4 |
| `["/*.md"]` | 1 |

`*` crosses `/`; the anchored form is required and is what ships.

**Scope matches the line guard exactly.** `rumdl check --no-cache .` reports
`5/57 files`; `find plugin docs -name '*.md'` minus the two frozen
`docs/superpowers/` trees, plus root-level `*.md`, is **57**. Identical.

**The 5 `rumdl check` issues are genuinely unreflowable**, which is the whole
argument for `fmt --check` over `check` in the gate. All five are a single
unbreakable code span:

```
plugin/skills/design/SKILL.md:75        `Skill(skill: "edify:recall", args: "plans/<job> — decisions …")`
plugin/skills/runbook/SKILL.md:56       `Skill(skill: "edify:recall", args: "plans/<job> — implementation patterns …")`
plugin/agents/runbook-corrector.md:65   `Skill(skill: "edify:recall", args: "plans/<job> — phase-structure …")`
plugin/agents/design-corrector.md:105   `Skill(skill: "edify:recall", args: "plans/<job-name> — architectural …")`
plugin/agents/outline-corrector.md:61   `Skill(skill: "edify:recall", args: "plans/<job> — design conventions …")`
```

`rumdl check` would leave the gate permanently red on these with no action that
clears it. `rumdl fmt --check -q --no-cache` exits **0** on them. Item 1.11's
report cites two such lines; there are five now, because commits after the
reflow added three. The conclusion is unchanged and the choice is vindicated by
the growth.

### The precommit formatter step

| tree | `rumdl fmt --check -q --no-cache` |
|---|---|
| repo, clean (before `d4e0a2b5`) | exit 0, **prints nothing** |
| scratch `docs/over.md`, one 200-char paragraph | exit 1, prints the unified diff it would apply |

`-q` suppresses the summary but not the diff, so the failure is diagnostic
rather than bare. Placement is correct per KD-8 — after `run-pytest`,
immediately ahead of `run-line-limits`.

### The `format` recipe's changed-files listing

`just format` on the clean tree: **no output, exit 0.** End-to-end with a
scratch `docs/zz-scratch-review.md` holding a 200-char paragraph (created, run,
removed; tree returned clean):

```
**Reformatted files:**
  - docs/zz-scratch-review.md
```

The `sed -Ene '/\[fixed\]$/s/^([^:]+):.*$/\1/p'` extraction was checked against
`rumdl fmt -q`'s real output shape (`path:line:col: [MD013] … [fixed]`) and
against a two-fix-one-file input; `sort --unique` collapses the repeat as the
comment claims.

No `|| true` on the rumdl line, unlike the `ruff`/`docformatter` lines above it.
That is correct: those need it because `patch` exits non-zero on an empty diff,
whereas `rumdl fmt` exits 0 when it fixes and when it leaves unwrappable lines.
A real rumdl failure should fail `format`, per the project's error-handling rule.

### The allowlist — every entry re-measured

`wc -l` on each of the ten listed paths against its recorded ceiling:

```
ok docs/design.md 1221
ok docs/superpowers/design/plugin-transition-evaluation.md 403
ok plugin/agents/corrector.md 682
ok plugin/agents/design-corrector.md 460
ok plugin/agents/outline-corrector.md 450
ok plugin/skills/build/SKILL.md 218
ok plugin/skills/design/SKILL.md 285
ok plugin/skills/proof/SKILL.md 203
ok plugin/skills/requirements/SKILL.md 357
ok plugin/skills/review/SKILL.md 231
```

Ten for ten at the time of measurement, and the script reported exactly those
ten files and exited 0 — no over-cap file is missing from the list, no listed
file is under cap. `design/SKILL.md` has since moved to 286; see §Concurrent
commit.

The allowlist header's maintenance rule ("only ratchet down… trim the file
rather than raising the number") is **word-for-word consistent** with
`check_line_limits.sh:25-28`. The duplication is right — the sidecar has to be
self-describing to whoever edits it.

### `rumdl` pinning

`rumdl>=0.2.74` in the dev group, resolved in `uv.lock` to 0.2.74 with wheels
for all seven platforms and hashes. A floor rather than a pin, matching every
other dev dependency in the file (`ruff>=0.14.9`, `pytest-mock>=3.15.1`, …).
Consistent; nothing to change. `uv.lock` is generated — not hand-edited, and it
shows only the additive rumdl entry plus the two dependency-list insertions.

## 3. The two scripts as a whole

Checked for the consistency the per-slice reviews could not see.

| | `edify-review-range.sh` | `check_line_limits.sh` |
|---|---|---|
| shebang | `#!/usr/bin/env bash` | same |
| header | purpose, contract, exit table | purpose, usage, caps, exit codes |
| `set -euo pipefail` | line 23 | line 32 |
| exit 0 | verdict with a range | clean |
| exit 1 | verdict without a range | overage |
| exit 2 | failure to run | failure to run |
| stdout | verdict line only | `oversized-file:` lines only |
| stderr | diagnostics only | diagnostics only |
| bash floor | 3.0 (`BASH_REMATCH`) | 3.2 (linear scan, no `declare -A`) |

Exit-code discipline is identical and correct in both: 2 is reserved for "the
check did not run", so a `set -e` abort can never be mistaken for a result.
Both scripts document it in the header.

- **No suppression.** `grep -n '2>/dev/null\||| true'` over both scripts returns
  three hits, all `grep -m1 … || true` on a no-match — the rule's stated
  exception. No `2>/dev/null` anywhere. The dead `agents/decisions` loop and its
  `2>/dev/null` that Item 1.11 was to delete are gone.
- **Quoting.** `shellcheck` clean on both (exit 0). Every expansion quoted;
  `dirname -- "$artifact"` and `grep -m1 --` guard a leading `-`; NUL-delimited
  `find -print0` / `read -r -d ''` throughout the walk. No whitespace splitting.
- **Comments** say what and why. The one narration flagged at slice 8
  (`walk`'s comment recounting its own history) was fixed there; re-read, it
  now states the constraint, not the story.
- **`set -e` AND-list.** `[ "$(basename "$file")" = "SKILL.md" ] && cap=200` and
  `[[ -z "$1" ]] && return 0` are both non-final commands of an AND-list, where
  `set -e` is suppressed by POSIX rule; exercised green by slices 1 and 3.

### Minor, not fixed — deliberate, each recorded with its reason

- **`wc -l` undercounts a file with no final newline** by one line, in both the
  cap check and the allowlist ceiling. Every file in scope ends in a newline and
  the formatter guarantees it; fixing it would add untested behaviour to the SUT.
- **Uppercase sha in a prior artifact's `Base:` yields a spurious `CONFLICT:`.**
  `resolved_base` comes from `git rev-parse` (lowercase, normalised);
  `prior_base` is raw artifact text, compared with `==`. Git only ever emits
  lowercase and no artifact in the tree is hand-uppercased. Recorded rather than
  changed — a `tr` fold is behaviour no slice specifies.
- **`sed -Ene 's/^([^:]+):…'` in `format` truncates a path containing a colon.**
  No markdown path in scope has one.
- **`portable.just`'s precommit now needs `rumdl` and a `.rumdl.toml` in the
  consumer**, neither of which the module ships. The module already assumes a
  consumer layout (`run-line-limits` hardcodes `./scripts/check_line_limits.sh`),
  so this extends an existing assumption rather than creating one — but it is
  worth a ruling before the next plugin release.

## 4. Tests

Both files re-read in full. **26/26 pass.**

- **Behaviour-focused, exact assertions.** Every stdout assertion in
  `test_review_range.py` is `result.stdout == "<exact line>\n"`; every one in
  `test_line_limits.py` is `result.stdout.splitlines() == [...]` or an exact
  `not in`. No substring matching on a verdict, no `.split()` anywhere in either
  file, so no whitespace splitting.
- **Genuine discrimination.** `_init_repo` commits twice so the first sha is not
  `HEAD` — a script emitting `git rev-parse HEAD` cannot pass. Slice 1's review
  proved this by mutation and it redded on two visibly different shas.
- **Real invocation.** Bare name off `PATH`, CWD outside the repo, git insulated
  by `GIT_CONFIG_GLOBAL=/dev/null` — the same way the skill will call it.
- **Slice 3–7's Major test-side finding is resolved.**
  `test_line_limits_matches_allowlist_paths_exactly` now allowlists
  `docs/notes.md` at ceiling **500** (strictly above the 401-line decoy) and
  drops the `docs/my-notes.md` claim on the exit code, so basename matching and
  exact matching now diverge on `returncode`. Verified by reading the fixture:
  the docstring states the divergence mechanism correctly.

**Split due, flagged not done.** `tests/test_review_range.py` is **396 lines**
against the 400 cap. It has four lines of headroom and is not in this group's
scope to restructure; the next slice that touches it must split it first.
`tests/test_line_limits.py` is 314 and has room.

## 5. Open-items ledger from the slice reviews

Every item any slice review flagged as not fixed, with its state now.

| # | Source | Item | State |
|---|---|---|---|
| 1 | 1.2/s1 F1 | `Derived from: none — <rationale>` covered only by a real-artifact run, no test | **Resolved** — `test_first_pass_none_with_rationale_emits_range` (slice 8), plus `test_base_with_trailing_rationale_emits_range` for the `Base:` sibling |
| 2 | 1.2/s1 F2, 1.2/s2 F4 | `Derived from:` naming **only** the motivating report emits `NO-PROVENANCE:` | **Still open, and now pinned by a test.** See below |
| 3 | 1.2/s2 F2 | Bare (unbackticked) `superseding <path>.` keeps the sentence period, so an existing prior reports `NO-PRIOR:` | **Open.** Orchestrator's call; the prescribed backticked form is immune |
| 4 | 1.2/s2 F3 | Absolute `superseding /abs/path` yields `NO-PRIOR:` with a wrong claim (the prior exists) | **Open, note only.** Outside KD-2 and outside the prescribed shape |
| 5 | 1.2/s3 | No `RANGE:` prefix convention; no multi-hop fixture | **Closed by design** — KD-2 is explicitly one hop only |
| 6 | 1.2/s4-8 | Shared-fixture extraction between the two test files deferred | **Open, judgement call.** Do not act on it before the 396-line split (§4) |
| 7 | 1.10/s1-2 | Boundary mutant not discriminated at slice 2 | **Resolved** by slice 3 |
| 8 | 1.10/s3-7 C | `test_line_limits_matches_allowlist_paths_exactly` did not discriminate basename matching (Major) | **Resolved** — ceiling 500, decoy claim dropped |
| 9 | 1.10/s3-7 §3 | `find` failure left part of the tree unchecked at exit 0 | **Resolved** by slice 8 — `walk` spools to a temp file, exit 2 on failure |
| 10 | 1.10/s3-7 | CRLF in a two-field allowlist line dies with `ceiling is not an integer: 401`, the invisible CR making the message read as a lie | **Open, Minor.** Exit 2 with file and line named, nothing silent; the repo authors this sidecar itself |
| 11 | 1.10/s3-7 | A path containing a TAB is inexpressible | **Closed** — documented in the script header; no in-repo path has one |
| 12 | 1.10/s8 | A second positional argument silently overwrites `ROOT` | **Open, Minor.** No caller passes one |

### Item 2 — the one that needs a ruling, not a patch

`test_derived_from_naming_only_a_report_reported` now **pins** the verdict:

```python
assert result.returncode == 1
assert result.stdout == "NO-PROVENANCE:\n"
```

for an artifact whose `## Provenance` section is present, well-formed, and
carries both fields. KD-1's sixth row treats this shape as real and expected;
KD-2's table has no verdict for it. The *action* is defensible — the skill asks
the user for the range, which is consistent with KD-1 writing `TODO` over such a
`Base:` — but the *label* says the section is absent, which is plainly false
about the artifact.

Flagged at slice 1, flagged again at slice 2, never ruled on, and now locked in
by a test. Not fixable as a review call: it wants a KD-2 amendment naming a
verdict for the shape (a distinct token, or `RANGE:` on the grounds that no
prior exists to conflict with), and then the script, the test, and the skill's
verdict table in `deliverable-review/SKILL.md` move together. **Recommend
amending KD-2 before this job closes**, since the skill half of Item 1.2 has
already landed against the current table.

## 6. Concurrent commit — the tree is red, for a cause outside this group

`d4e0a2b5` ("review gate — base-relative sibling pointers, finishing.md §1
citations, description shape") landed **after** `04b627a1`, i.e. after Item
1.11's reflow and allowlist, while this review was running. It is the markdown
dispatch's commit, and markdown is Scope OUT here. It leaves the gate red two
ways:

1. **`rumdl fmt --check` exits 1.** Four files it edited now carry over-80
   paragraphs: `plugin/skills/build/references/finishing.md`,
   `phase-boundary.md`, `review-dispatch-template.md`, `tdd-slice.md`. Remedy:
   `just format`.
2. **`plugin/skills/design/SKILL.md` is 286 lines against its allowlist ceiling
   of 285.** The ratchet firing on first growth — KD-7's stated design, and the
   risk the outline names explicitly. Per the maintenance rule the fix is to
   trim the file by at least one line, **not** to raise the ceiling.

Neither is a defect in this group and neither is mine to fix: reflowing another
dispatch's files while that dispatch may still be live would race it, and
raising the ceiling would violate KD-7. **Handed to the orchestrator.**

This is also, incidentally, the first live proof of the fix in §1: before it,
`precommit` would have aborted at `run-line-limits` printing nothing but the ten
`oversized-file:` lines and no `✗`.

## 7. Final checks

```
$ shellcheck plugin/bin/edify-review-range.sh scripts/check_line_limits.sh
shellcheck exit: 0

$ pytest -q tests/test_review_range.py tests/test_line_limits.py
**Summary:** 26/26 passed
```

`just precommit`, full output, after the §1 fix and after `d4e0a2b5`:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# rumdl
--- plugin/skills/build/references/finishing.md
+++ plugin/skills/build/references/finishing.md
@@ -14,8 +14,8 @@
 2. Group by artifact type (code/tests/plans, skill definitions, agent
    definitions, design documents)
 3. Look up the reviewer per group from the routing table
-4. Read `references/review-dispatch-template.md` and dispatch each group to its reviewer,
-   structuring the prompt by it
+4. Read `references/review-dispatch-template.md` and dispatch each group to its
+   reviewer, structuring the prompt by it

 **Two dispatch patterns:**

--- plugin/skills/build/references/phase-boundary.md
+++ plugin/skills/build/references/phase-boundary.md
@@ -11,12 +11,12 @@

 Run `verify-step.sh` with `dangerouslyDisableSandbox: true`.

-Read `references/dispatch-composition.md` and compose by it a checkpoint-form dispatch of
-`edify:corrector`: scope IN/OUT from the phase's items, design and recall
-artifact by path, changed-files list, report path from that reference's §Prompt
-contents rule under the dispatch name `phase-P-corrector`. IN/OUT lists must be
-non-empty and the changed-files list present — empty fields → STOP before
-delegating. UNFIXABLE → STOP and escalate. Otherwise commit and continue.
+Read `references/dispatch-composition.md` and compose by it a checkpoint-form
+dispatch of `edify:corrector`: scope IN/OUT from the phase's items, design and
+recall artifact by path, changed-files list, report path from that reference's
+§Prompt contents rule under the dispatch name `phase-P-corrector`. IN/OUT lists
+must be non-empty and the changed-files list present — empty fields → STOP
+before delegating. UNFIXABLE → STOP and escalate. Otherwise commit and continue.

 The **final checkpoint** adds a lifecycle audit: verify all stateful objects
 (MERGE_HEAD, staged content, lock files) cleared on success paths.
--- plugin/skills/build/references/review-dispatch-template.md
+++ plugin/skills/build/references/review-dispatch-template.md
@@ -1,8 +1,8 @@
 # Review Dispatch Template

-Prompt template for reviewer delegation from `finishing.md` §1. Reviewer selection
-happens upstream (`finishing.md` §1 routing) — this template structures the prompt for
-the selected reviewer.
+Prompt template for reviewer delegation from `finishing.md` §1. Reviewer
+selection happens upstream (`finishing.md` §1 routing) — this template
+structures the prompt for the selected reviewer.

 Two variants. Use §Template for a fix-capable reviewer, §Report-only variant for
 a reviewer that can neither write nor edit.
@@ -65,8 +65,8 @@

 The **calling session** then writes the returned findings to
 `plans/<job>/reports/review-<group>.md` and applies the fixes itself. The
-structural-proof Read in `finishing.md` §1 then finds a file that exists, so the gate
-stops blocking on skill-definition groups.
+structural-proof Read in `finishing.md` §1 then finds a file that exists, so the
+gate stops blocking on skill-definition groups.

 ## Field Rules

@@ -87,8 +87,9 @@
   resolves recall by path and moves writing and fixing to the caller. `Grep` and
   `Glob` are its search tools; a prompt instructing it to run `rg` fails.
 - **Report path:** one rule — `plans/<job>/reports/review-<group>.md`, `<group>`
-  being the artifact group `finishing.md` §1 routed. The structural proof reads the path
-  actually dispatched, so the prompt and the proof must name the same file.
+  being the artifact group `finishing.md` §1 routed. The structural proof reads
+  the path actually dispatched, so the prompt and the proof must name the same
+  file.
 - **Scope IN/OUT:** From design or outline, not invented. Prevents reviewer from
   flagging work explicitly deferred.
 - **Scope completeness:** Reviewer must mechanically diff every Scope IN item
--- plugin/skills/build/references/tdd-slice.md
+++ plugin/skills/build/references/tdd-slice.md
@@ -2,9 +2,9 @@

 An item carrying `Slices:` lists behaviour slices and carries nothing else to
 execute. It reaches here from a runbook, or from an outline or design routed to
-`/build`. Read `references/dispatch-composition.md` and compose by it each of the four
-dispatches that execute slice `N.M/k`, then take the after-the-slice steps. Only
-such an item reaches this file.
+`/build`. Read `references/dispatch-composition.md` and compose by it each of
+the four dispatches that execute slice `N.M/k`, then take the after-the-slice
+steps. Only such an item reaches this file.

 ## The four dispatches

# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 286 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/design.md: 1221 lines > 400
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✗ Precommit failed
precommit exit: 1
```

Both failures are `d4e0a2b5`'s, per §6. The same recipe ran **green** on the
tree as it stood at `04b627a1`, before that commit landed:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
precommit exit: 0
```

(that run predates the §1 fix, so its ten `oversized-file:` lines appear without
the `# line limits` header — which is the defect §1 fixes.)

## 8. `git diff --stat`

Group against baseline `1f54633b`, as it now stands:

```
 .rumdl.toml                      |  31 +++
 plugin/bin/edify-review-range.sh | 160 ++++++++++++++++
 plugin/portable.just             |  15 +-
 pyproject.toml                   |   1 +
 scripts/check_line_limits.allow  |  24 +++
 scripts/check_line_limits.sh     | 190 +++++++++++++++++--
 tests/test_line_limits.py        | 314 +++++++++++++++++++++++++++++++
 tests/test_review_range.py       | 396 +++++++++++++++++++++++++++++++++++++++
 uv.lock                          |  17 ++
 9 files changed, 1131 insertions(+), 17 deletions(-)
```

Uncommitted, this review's own fix — the orchestrator commits it:

```
 justfile             | 6 +++++-
 plugin/portable.just | 6 +++++-
 2 files changed, 10 insertions(+), 2 deletions(-)
```
