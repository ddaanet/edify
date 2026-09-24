# Digest — what `plans/remaining-sweep/reports/` left open

2026-09-23. Checked against the tree at `0b4c46f8`. Report paths below are
relative to `plans/remaining-sweep/reports/`. Item IDs (M-n, F-n, C-n) are the
source report's own.

Frame bullets, from `.claude/handoff-todo.md` §Remaining in order:

- **R1** read the 2026-09-21/22 reports before acting
- **R2** `/edify:design` job for repo-relative `plugin/…` references
- **R3** `../claude-plugins/README.md` edify section; marketplace description
- **R4** `plans/skill-reviews/` open-design and disputed findings
- **R5** sweep-exit-condition job
- **R6** pilfer defect 21 (corrector-skeleton dedup)
- **R7** brief-triage jobs: tdd-slice, git-hygiene hooks, context-triggered
  handoff
- **R8** `just test` once on macOS
- **R9** FR-12 remainder
- **R10** `/design plans/pilfer-superpowers/`
- **R11** README dprint pairing, `.dprint.json`
- **R12** five untracked `.claude/` paths
- **R13** `memory/MEMORY.md` over loader budget

Not counted below: items `brief-triage-decisions.md` §Dropped closes (F-2, F-7,
F-8, F-9, F-10, F-11) and C-2.2 (`brief-triage.md` "Not carried forward").

## STILL-OPEN, in frame

**tdd-slice job — M4, M5, M9 (D2), F-12.** Skip artifacts for dispatches (b)
and (d); a superseded review fix still commits its report; a test-only slice
still gets its report; a named form for a red taken under a stated mutation.
Sources: `brief-triage.md` M4/M5/M9, F-12, D1/D2/D-o3, C-2.4/C-2.5;
`brief-triage-decisions.md` §Routed; `green-report-commit.md` §Open bullet 2
(two of six audited slices had no GREEN report, so D-86 needed a RED-report
fallback). Evidence: `grep -i "skip\|superseded\|test-only"` over
`plugin/skills/build/references/tdd-slice.md` finds none of the three. D-84's
`Mutation proof` fallback exists at `tdd-slice.md:19-31`; the decisions record,
dated after D-84, still routes F-12 to this job. Frame: **R7**.

**M11, executor half — git hygiene.** Forbid `git stash`, `git reset` and
blanket `git add` in the executing agents, now as agent-scoped `PreToolUse`
deny hooks plus one prose line, after confirming the frontmatter `hooks:` field.
Sources: `brief-triage.md` M11/D-o4; `brief-triage-decisions.md` §Routed.
Evidence: no `hooks:` in any `plugin/agents/*.md`; prose covers it only in
`test-driver.md:48` (`git stash`) and `:101` (`git add -A`); `artisan.md` and
`refactor.md` have neither. Frame: **R7**.

**F-3 — context-triggered handoff** (bundles C-A, D-o2, D-o5). A harness script
reads the transcript's last `usage` at each dispatch return and routes to
clear-and-resume past 150k soft / 200k hard. The brief's 35–55% saving stays
ungrounded for edify. Sources: `brief-triage.md` F-3; `brief-triage-decisions.md`
§Routed. Evidence: no match for `150k`, `clear-and-resume` or `last usage` under
`plugin/` or `scripts/`. Frame: **R7**.

**M2 — U-ARCH names the design record, not the runbook.** Sources:
`brief-triage.md` M2/B1; `brief-triage-decisions.md` §Routed (defect 21).
Evidence: `plugin/agents/corrector.md:47-48` still read as the triage quoted
them. Frame: **R6**.

**M7 — guards on the corrector's mutated-SUT run.** Refuse a dirty target,
verify the restore, add the `tmp/`-not-`/tmp/` rule. Sources: `brief-triage.md`
M7/C-x; `brief-triage-decisions.md` §Routed (defect 21). Evidence:
`corrector.md:418-422` still says "save the SUT, mutate it in place … restore",
with no guard. `sweep-review.md` C3 replaced exactly that save-and-restore method
in `test-driver.md` and `tdd-slice.md` with an exact-string mutation and a grep
check on the restore (`tdd-slice.md:21-28`), and its Minor on `test-driver.md`
records `git diff --quiet` misreporting when RED wrote the stub itself. M7 as
worded in `brief-triage.md` prescribes `git diff --quiet`. Frame: **R6**.

**F-4 — machine-shaped corrector report head, with the feeds-back brief.**
Sources: `brief-triage.md` F-4/C-D and §Overlaps (d);
`brief-triage-decisions.md` §Routed. Evidence: `corrector.md:450` still opens
with the prose `**Overall Assessment**` line;
`inbox/brief-review-feeds-back-into-design.md` still present. Frame: **R6**.

**M11, corrector half — "corrector never commits" prohibition.** Sources:
`brief-triage-decisions.md` §Routed. Evidence: `grep -i "never commit\|commits
nothing"` over `corrector.md` finds nothing. Frame: **R6**.

**F-5 — citation convention in `/design`, and whether it binds a review
report's `Location` field.** Sources: `brief-triage.md` F-5/A1;
`brief-triage-decisions.md` §Routed (sweep-exit job); `sweep-review.md` Minor
not fixed (`token-economy.md` against 11 `file:line` sites, "owner's call").
Evidence: no citation-convention text under `plugin/skills/design/`.
`token-economy.md` was deleted in `5594a753`, so the face-conflict it carried is
gone. `corrector.md` still holds 6 `file:line`/`path:line` hits; `review/SKILL.md`
and `deliverable-review/SKILL.md` now hold 0. Frame: **R5**, **R7**.

**recall M1 — how much of `gitlore:recall` edify duplicates.** Source:
`skill-doc-pass.md` §What I deliberately left. Evidence: listed open-design at
`plans/skill-reviews/reports/verify-summary.md:341`. Frame: **R4**.

**O-5 — shipped skills cite `docs/` nodes an installed plugin lacks.** Source:
`skill-doc-pass.md` §What I deliberately left (design-doc-split
`independent-review.md` call 5). Frame: **R2**, which states it.

**Five untracked `.claude/` paths.** Source: `skill-doc-pass.md` §Observable
state note. Evidence: `git status --porcelain -- .claude` lists `launch.json`,
`loop.md`, `output-styles`, `routines`, `workflows`. Frame: **R12**.

## STILL-OPEN, missing from frame

**The `just` recipes have no automated coverage.** No test exercises the
`format` recipe or any other recipe. Source: `format-fix.md` §Test coverage
(1g). Evidence: no test under `tests/` runs `just`;
`tests/test_line_limits_default_invocation.py:3` mentions the justfiles only in
its docstring. The frame carried this and dropped it in `a3697f15` ("drop the
just-recipe harness item from the task frame").

**Nothing mechanically checks D-86.** No check that a commit adding a report
also carries the work it reports; `verify-step.sh` catches only the symptom, one
dispatch late. Source: `green-report-commit.md` §Open bullet 3. Evidence: no
`diff-filter` under `scripts/`, `plugin/bin/`, `plugin/skills/build/scripts/` or
`tests/`.

**D-52/D-53/D-54 placement.** Whether the skill-authoring rules move from
`quality-gates.md` to `agent-instructions.md`. Source: `skill-doc-pass.md` §What
I deliberately left (design-doc-split `independent-review.md` call 4).
Evidence: all three still defined in `docs/references/quality-gates.md`. The
frame carried the design-doc-split leftovers until `0b4c46f8`. That commit's
message lists the memory pointer, the H2 and §6 as applied, and says nothing of
this one.

**Root `justfile` still duplicates `bash_prolog`, and consumers inherit a new
obligation.** Sources: `sweep-review.md` Major (UNFIXABLE, "~100-line
`bash_prolog` duplication … predates this change"); `small-defects.md` item 4,
which judged the duplication intentional. Evidence: `justfile:79` redeclares
`bash_prolog`, with its own `run-checks` (`:144`) and `run-lint-checks`
(`:151`). The `run-project-checks` no-op sits inside portable's prolog
(`plugin/portable.just:90`, prolog closes at `:98`). A consumer that overrides
`bash_prolog` without defining it gets the "command not found" risk the review
named.

**`check_design_links.sh` leaks one temp file** when the first `mktemp`
succeeds and the second fails. Source: `sweep-review.md` Minor not fixed.
Evidence: `scripts/check_design_links.sh:76-80`, where the `EXIT` trap is
installed only after both `mktemp` calls.

**Violation-line order in `check_design_links.sh` depends on the filesystem.**
Content is unaffected, and no test depends on the order. Source:
`sweep-review.md` Minor not fixed. Evidence: `find "$@" -print0` at `:112` with
no `sort` in the script.

**`design/SKILL.md` gained `Edit` in `allowed-tools` with no recorded
rationale.** Source: `sweep-review.md` Minor not fixed. Evidence:
`plugin/skills/design/SKILL.md:8` carries `Edit`; no hit in `docs/`.

**Mutate-and-run script (brief C's C-x "script" half).** The brief proposes a
script that refuses a dirty target and verifies an empty diff afterwards.
Sources: `brief-triage.md` table row C-x ("script needs-design"). The row has no
F-number, and `brief-triage-decisions.md` records no disposition for it; only
the M7 guard half is routed. Evidence: no such script under `scripts/` or
`plugin/`.

**The deliverable-review "multiple rounds" claim is unverified outside one
chain.** Source: `deliverable-review-rounds.md` §Verdict. Evidence: the
multi-round deliverable-review reports on disk are still only the three
provenance-chain jobs (`ls plans/*/reports/deliverable-review*.md`). This is an
evidence-scope limit, not a work item: `0b4c46f8`'s message records the decision
it fed, "the review range stays Base..HEAD".

## RESOLVED-SINCE

**M6 / C-2.6 — `verify-step.sh` bare `CLEAN`.** Sources: `brief-triage.md` M6.
Evidence: `plugin/skills/build/scripts/verify-step.sh:33` `echo "CLEAN:
$checks"` (applied in `format-fix.md` Task 2).

**F-1 — where a GREEN report is committed.** Sources: `brief-triage.md`
F-1/C-3a; `skill-doc-pass.md` §What I deliberately left. Evidence: D-86 in
`docs/decisions.md` and `docs/references/pipeline-contracts.md`
(`green-report-commit.md`).

**`docs/changelog.md` at its 400-line cap, per-date split owed.** Sources:
`green-report-commit.md` §Open bullet 1; `skill-doc-pass.md` Open question 1;
`sweep-review.md` Major. Evidence: `docs/changelog.md` is 60 lines, with 24
entry files under `docs/changelog/`.

**`tests/test_design_links.py` E501/D205 blocker.** Source:
`crosslink-green.md` §Blocker. Evidence: no line in the file is over 88
characters (`:279` counts 89 bytes, of which 3 are one em-dash);
`plans/open-items-sweep/reports/preflight.md:30` records `just precommit` pass.

**Design-links docs coupling (D-46 enumeration, changelog entry).** Source:
`crosslink-green.md` §Docs updates needed. Evidence:
`docs/references/quality-gates.md:28`;
`docs/changelog/2026-09-21-design-graph-crosslinks-checked-mechanically.md`.

**`check_design_links.sh` `ROOT` default (repo root against `.`).** Source:
`crosslink-red.md` §`ROOT` default. Evidence: `scripts/check_design_links.sh:10`
"ROOT defaults to `.`", matching `check_line_limits.sh`.

**`docformatter` line in `format` a no-op, then a reverse-apply.** Sources:
`format-fix.md` (flagged, not fixed); `sweep-review.md` C1 (fixed). Evidence:
`plugin/portable.just:171-186` reads names off the diff, with no `|| true`.

**`run-lint-checks` / `just check` lacked `ruff format --check`.** Sources:
`format-fix.md`; `skill-doc-pass.md` §What I deliberately left;
`sweep-review.md` Major. Evidence: `plugin/portable.just:50`, `justfile:157`.

**`format` recipe applied nothing (missing `-p0`, filename regex); no `ruff
format --check` gate; docs note.** Sources: `small-defects.md` item 5 and
§docs/ updates; `format-fix.md` Task 1. Evidence: `plugin/portable.just:148`;
`run-checks` at `justfile:146` and `plugin/portable.just:40`; D-46
(`skill-doc-pass.md` E).

**`fail()` drift between the two prologs.** Source: `small-defects.md` item 4.
Evidence: `justfile:93` and `plugin/portable.just:18` are identical;
`0b4c46f8` "fail() unified on the portable definition".

**Root `justfile` copied portable's `precommit` body.** Source:
`sweep-review.md` Major. Evidence: `run-project-checks` hook,
`plugin/portable.just:90,126` and `justfile:205`; `10b509e2` "… precommit hook
…". The residual consumer obligation is listed under missing-from-frame.

**`design/SKILL.md` allowlist ceiling ratchet (285 → 277).** Source:
`sweep-review.md` §Concurrent modification. Evidence: the file is 174 lines and
off `scripts/check_line_limits.allow` (`5f860e07` "… skill hub splits …").

**Retiring `plugin/fragments/token-economy.md`.** Source: `skill-doc-pass.md`
Open question 2. Evidence: deleted in `5594a753`; `plugin/fragments/` holds five
files, and this is not one of them.

**`cli-and-package.md` duplicate H2.** Sources: `skill-doc-pass.md` §D ("Not
3") and §What I deliberately left (`independent-review.md` fix 3 / call 2).
Evidence: the only H2s are `:158` and `:192`; `0b4c46f8`.

**Stale `§7` pointer in a memory file.** Source: `skill-doc-pass.md` §What I
deliberately left (`independent-review.md` finding 3 / call 1). Evidence:
`memory/feedback-decision-docs-are-living.md` no longer exists; memory-repo
commit `3a2cfd0` "… design-record memory retired".

**Three routing surfaces (`docs/design.md` §6 against `CLAUDE.md`).** Sources:
`skill-doc-pass.md` Open question 3 (`independent-review.md` finding 6 / call 3).
Evidence: `docs/design.md:270-275` is now a pointer ("this hub does not repeat
it"), added in `0b4c46f8`.

**recall M3, M5 and the m-items.** Source: `skill-doc-pass.md` §What I
deliberately left. Evidence: `plans/skill-reviews/reports/apply-review.md:156-167`;
`plugin/skills/recall/SKILL.md:77` ("an arbitrary ceiling").

**`dispatch-composition.md` "Every dispatch" did not cover `tdd-audit`.**
Source: `sweep-review.md` Minor not fixed. Evidence:
`plugin/skills/build/references/dispatch-composition.md:19` names the
`tdd-audit` exception (`5594a753`).

**`tdd-auditor.md` Scope compliance named only later items.** Source:
`sweep-review.md` Minor not fixed. Evidence: `plugin/agents/tdd-auditor.md:137-138`
applies the check per slice within one item (`5594a753`).

**Final gate was a snapshot; `just format && just precommit` owed as one step.**
Source: `sweep-review.md` §Final gate. Evidence:
`plans/open-items-sweep/reports/preflight.md:30` (`just precommit` pass) and
`:214` (`✓ Precommit OK`).

**Marketplace `description` still "framework-agnostic".** Sources:
`split-and-reword.md` §Occurrences deliberately left (fifth site); frame R3's
second sentence. Evidence: `../claude-plugins/.claude-plugin/marketplace.json`
edify entry now reads "A lean bundle of Claude Code skills and agents built
around a requirements → design → runbook → build planning pipeline". The frame
still describes it as pending the next release. R3's README half is unaffected:
`../claude-plugins/README.md:214` still names `/orchestrate`.

**A report amended after its commit lands resolves to the original commit.**
Source: `green-report-commit.md` §Open bullet 4. Evidence: recorded as an
accepted tradeoff in D-86, `docs/references/pipeline-contracts.md:277`.

## UNCLEAR

**Brief A's `claude-plugin-dev` evidence.** `toolkit/release.sh:254` citing
`:780-785`, plus two `version-guard-test.sh` citations. Source:
`brief-triage.md` Brief A §Verification ("could not confirm"). Check made:
`../claude-plugin-dev/toolkit/release.sh:250-256` holds no line citation, and a
grep for `:NNN-NNN` or `780` in that file finds nothing. That does not show
whether the citations were fixed or had moved; `version-guard-test.sh` was not
checked.

**Review coverage of the concurrently edited `formalize`/`ground` files.**
`plugin/skills/formalize/SKILL.md`, `plugin/skills/ground/SKILL.md` and
`ground/references/grounding-criteria.md` were edited outside the sweep
review's scope and left unreviewed. Source: `sweep-review.md` §Concurrent
modification. Check made: the round-3 deliverable review's range ran
`926e372d..HEAD` through `5594a753`, and it cites `ground/SKILL.md:70` at that
commit (`plans/provenance-enforcement-and-routing/reports/deliverable-review.md:8-12,150-153`).
Nothing shows it examined `formalize/SKILL.md` or `grounding-criteria.md`.
`5f860e07` edited them again since.

## Counts

- STILL-OPEN, in frame: 11
- STILL-OPEN, missing from frame: 9
- RESOLVED-SINCE: 22
- UNCLEAR: 2
