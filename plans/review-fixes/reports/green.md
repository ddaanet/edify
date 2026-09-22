# GREEN fixes: F-1, F-4, F-5

Job: `plans/review-fixes/`. Source finding:
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md`.

## F-1 — `wc -l` unguarded against BSD left-padding

**Edit:** `scripts/check_line_limits.sh:124` (in `check_cap`).

- old: `if ! line_count=$(wc -l <"$file"); then`
- new: `if ! line_count=$(wc -l <"$file" | tr -d ' '); then`

Added an in-situ comment above the line stating (a) the pipeline form is
what lets `wc -l`'s own failure reach the `if` at all — `pipefail` (already
set by `set -euo pipefail`, untouched) makes the pipeline's exit status the
rightmost non-zero stage's, so an unreadable `$file` still trips the branch
even though `tr` itself always succeeds — and (b) `tr -d ' '` strips BSD
`wc`'s left-padded field width, unverified on macOS (this box is Linux) but
guarded the same way as `plugin/bin/triage-feedback.sh:14`.

**`plugin/bin/triage-feedback.sh:77`** — left unguarded, per instruction.
Its value feeds `[ … -eq 1 ]` only (never printed), which tolerates BSD
padding; no change made.

### Red

```
$ just test tests/test_line_limits_wc_padding.py
```
1 failed: `test_line_limits_reports_unpadded_count_under_bsd_style_wc` —
`AssertionError: oversized-file: docs/notes.md:      401 lines > 400` vs
expected `oversized-file: docs/notes.md: 401 lines > 400` (stdout mismatch,
not a shim/import/fixture error, as the test module's docstring specifies).

### Green

```
$ shellcheck -S style scripts/check_line_limits.sh
```
clean, no output.

```
$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py \
    tests/test_line_limits_wc_padding.py tests/test_line_limits_default_invocation.py
```
`23/23 passed` — Tests OK.

## F-4 — reintroduced "per X.md" must-open pointers

Read `plans/provenance-enforcement-and-routing/reports/item-1-9.md` for the
established form: replace "per `X.md`" with an imperative "Read `X`[, …]"
naming the condition, keeping the rest of the sentence. Both target files
sit in `references/` themselves; the sibling pointers already inside them
(`references/design-content-rules.md`, `references/research-protocol.md`
elsewhere in the same files) use the **skill-base-relative** bare form
(`references/…`, not `../…`), because `Read` resolves from the skill's
announced base directory (`plugin/skills/design/`), not from the file's own
location — matched here, i.e. the path itself was left unchanged, only the
"per" wording was rewritten.

**Edit 1:** `plugin/skills/design/references/write-design.md:7`

- old: `**Recall diff:** per \`references/research-protocol.md\` §A.5 — re-invoke recall\non what just changed and reconcile the artifact.`
- new: `**Recall diff:** Read \`references/research-protocol.md\` §A.5, re-invoke\nrecall on what just changed, and reconcile the artifact.`

**Edit 2:** `plugin/skills/design/references/write-outline.md:149`

- old: same sentence as above
- new: same rewrite as above

(`just format` reflowed both afterward — cosmetic line-wrap only, content
unchanged.)

### Exit condition

```
$ rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/
```
0 hits. No remaining must-open (or any other) "per X.md" pointer to
classify — the fix reduced the count from 2 to 0, matching Item 1.9's
original zero-hit state.

## F-5 — repo-relative `plugin/…` paths reintroduced in skill bodies

Confirmed the target skill-relative form by reading both cited sites:
`plugin/skills/build/references/finishing.md:10` (`../../fragments/review-requirement.md`)
and `plugin/skills/build/references/escalation.md:35`
(`../../fragments/escalation-acceptance.md`). All four F-5 skill-body sites
are `plugin/skills/<skill>/SKILL.md`, one level shallower than a
`references/` file, so the fragment resolves the same way:
`../../fragments/delegation.md`.

**Edit 1:** `plugin/skills/ground/SKILL.md:70`
- old: `` at `plugin/fragments/delegation.md` §Quiet Execution Pattern. ``
- new: `` at `../../fragments/delegation.md` §Quiet Execution Pattern. ``

**Edit 2:** `plugin/skills/recall/SKILL.md:20`
- old: `` (`plugin/fragments/delegation.md` §Recall Artifacts For Sub-Agents). ``
- new: `` (`../../fragments/delegation.md` §Recall Artifacts For Sub-Agents). ``

**Edit 3:** `plugin/skills/recall/SKILL.md:45`
- old: `` (`plugin/fragments/delegation.md` §Recall Content In Delegation Prompts): Read ``
- new: `` (`../../fragments/delegation.md` §Recall Content In Delegation Prompts): Read ``

**Edit 4:** `plugin/skills/deliverable-review/SKILL.md:104`
- old: `` Each agent follows `plugin/fragments/delegation.md`: quiet execution (report to ``
- new: `` Each agent follows `../../fragments/delegation.md`: quiet execution (report to ``

Left alone, as instructed: `plugin/agents/tdd-auditor.md` (agent definition,
no announced base directory — owned by the deferred repo-relative job) and
every pre-existing repo-relative site.

### Before/after counts

Backticked `` `plugin/(skills|agents|fragments|bin|hooks)/…` `` paths inside
`plugin/skills`, `plugin/agents`, `plugin/fragments`
(`grep -rEo '`plugin/(skills|agents|fragments|bin|hooks)/[^`]*`' plugin/skills plugin/agents plugin/fragments`):

- **Before this fix: 31 sites in 16 files.**
- **After this fix: 27 sites in 14 files.**

`ground/SKILL.md` and `recall/SKILL.md` dropped out of the file list
entirely (each carried only the one `delegation.md` reference);
`deliverable-review/SKILL.md` remains in the list — it has other
`plugin/…` paths besides the one fixed here, out of this job's scope.

## `just format` / `just precommit`

`just format` reformatted the two F-4 files (line-wrap only, from the
inserted comma-joined sentence exceeding the wrap column) — no other files
touched.

```
$ just precommit
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 355/356 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

**PASS.** The three `oversized-file:` lines are pre-existing allowlisted
entries (`scripts/check_line_limits.allow`), reported per KD-7's design but
not gating — none of this job's edits touched those three files, and the
gate's own exit code is 0.

## Anything unsure

- None of the fixes touched files under `tests/`, as instructed.
- The F-4/F-5 rewrites left one visible inconsistency already flagged by
  Item 1.9 itself and not reopened here: sibling bare-form pointers within
  the same `references/` files (e.g. `references/design-content-rules.md`
  cited from `write-design.md`) use the skill-base-relative form without a
  "Read" imperative already — out of scope for this job, unchanged.
- `plugin/skills/deliverable-review/SKILL.md` still has other
  `plugin/(skills|agents|fragments|bin|hooks)/…` references beyond the one
  fixed (F-5 named only the `delegation.md` site there) — left alone,
  consistent with the deferred repo-relative job owning the rest.
