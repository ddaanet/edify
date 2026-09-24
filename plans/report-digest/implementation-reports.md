# Open items from four implementation reports — digest, 2026-09-23

Sources: `plans/review-fixes/reports/` (`code-review.md`, `green.md`, `red.md`,
`test-review.md`), `plans/allowlist-ownership/reports/implementation.md`,
`plans/proof-verdict-prompt/reports/implementation.md`,
`plans/release-decision-record/reports/implementation.md`.

Frame numbering: the bullets of `.claude/handoff-todo.md` §Remaining, in order —
R1 read the passes' reports; R2 repo-relative `plugin/…` references job; R3
`../claude-plugins` README and marketplace description; R4 `plans/skill-reviews/`
open-design findings; R5 sweep exit-condition job; R6 pilfer defect 21; R7 brief
triage jobs; R8 `just test` on macOS; R9 FR-12 remainder; R10
`plans/pilfer-superpowers/`; R11 README dprint; R12 untracked `.claude/` paths;
R13 `memory/MEMORY.md` over budget.

Status was checked against the working tree at `0b4c46f8`, not taken from the
reports.

## STILL-OPEN, in frame

### review-fixes and allowlist-ownership

- **Repo-relative `plugin/…` paths (F-5 remainder).** Skill bodies, agents and
  fragments still cite `plugin/…` paths that break from an installed plugin.
  Sources: `green.md` §F-5 ("Left alone … `plugin/agents/tdd-auditor.md`") and
  §Anything unsure (`deliverable-review/SKILL.md` other paths);
  `code-review.md` §3 (tdd-auditor "left to the deferred job");
  `allowlist-ownership/…/implementation.md` §Deliverable-review findings
  ("Not fixed, listed: `dispatch-composition.md:102` … `tdd-auditor.md:209`").
  Evidence: `grep -rEo` over `plugin/skills plugin/agents plugin/fragments`
  still gives 27 sites in 14 files, including
  `plugin/skills/build/references/dispatch-composition.md:102`,
  `plugin/agents/tdd-auditor.md:209`,
  `plugin/skills/deliverable-review/SKILL.md:123`. Carried by **R2**.
- **Sibling-pointer path form inside a `references/` node.**
  `references/research-protocol.md` cited from inside
  `design/references/` resolves only from the skill base, not the citing
  file's directory. Sources: `code-review.md` §Observation; `green.md` §F-4 and
  §Anything unsure. Evidence: `write-design.md:7,12,84` and
  `write-outline.md:139,149,157,261,299` still use the bare
  `references/…` form. Carried by **R2** ("bare versus `references/…` form").

### review-fixes

- **BSD `wc` padding unverified on macOS.** F-1's premise and the guard rest
  on a padding claim never executed on macOS. Sources: `green.md` §F-1;
  `test-review.md` §Minor (docstring now carries the status; the claim itself
  stays unverified); `code-review.md` §Major (hedge noted as accurate).
  Evidence: `scripts/check_line_limits.sh:134` and
  `tests/line_limits_helpers.py:144` both still say "unverified on macOS".
  Carried by **R8**.

### allowlist-ownership

- **Three corrector allowlist entries.** Left on the allowlist as owned by
  pilfer defect 21. Source: §Inbound references, Updated. Evidence:
  `scripts/check_line_limits.allow` holds exactly `corrector.md` 682,
  `design-corrector.md` 460, `outline-corrector.md` 450, each noted "pilfer
  defect 21". Carried by **R6**.
- **design C1** — Defect route names a `structured-bugfix` workflow that does
  not exist. Source: §Left untouched. Evidence:
  `plugin/skills/design/SKILL.md:135`, `design/references/triage.md:33` still
  name it. Carried by **R4** (`verify-summary.md:315`, "No pending job").
- **design M6** — `triage-feedback.sh` has no Moderate/Defect branch. Source:
  §Left untouched. Evidence: `grep -iE 'moderate|defect'
  plugin/bin/triage-feedback.sh` returns nothing. Carried by **R4**
  (`verify-summary.md:319`).
- **design M5** — which file owns the A.5 output spec. Source: §Left
  untouched. Evidence: listed open-design at `verify-summary.md:317`; not
  re-checked individually in the tree. Carried by **R4**.
- **design m4** — A.0/A.2.5/C.4.5 numbering accretion. Source: §Left
  untouched. Evidence: listed open-design in `verify-summary.md` "No pending
  job"; not re-checked individually. Carried by **R4**.
- **formalize 8** — the "progressive disclosure inverted" instance in
  `formalize`. Source: §Skill-review findings, Folded in ("`review M8` and
  `formalize 8` … untouched"). Evidence: `verify-summary.md:328` lists it
  open-design. Carried by **R4**.

### allowlist-ownership and proof-verdict-prompt

- **proof C1 / design C2** — terminal "apply" dispatches no corrector while
  callers assert one. Sources: `proof-verdict-prompt/…` §`verify-proof.md`
  findings, Left untouched (C1); `allowlist-ownership/…` §Left untouched (C2,
  "`/proof` dispatches no corrector"). Evidence: `proof/SKILL.md:8` still
  lists `Agent` in `allowed-tools`; `design/references/write-design.md:70`
  still says "/proof dispatches design-corrector automatically";
  `design/SKILL.md:111,129` still pair `/edify:proof` with a corrector.
  Carried by **R4** (named as `proof` C1).

### proof-verdict-prompt

- **proof M8** — `p:` semantics defined nowhere. Source: §Left untouched.
  Evidence: `proof/SKILL.md:162`, `proof/references/item-review.md:115`.
  Carried by **R4**.
- **proof M9** — `agents/learnings.md` write target with no absence handling.
  Source: §Left untouched. Evidence: `proof/SKILL.md:161`,
  `item-review.md:114`. Carried by **R4**.

### release-decision-record

- **Marketplace `description` says "framework-agnostic".** The `edify` entry
  in `../claude-plugins` carries a stale description. Source: §D-9 rewiring,
  "New finding from the lead". Evidence: the recipe half is fixed (below);
  the entry's text itself clears at the next `just release`, which is what R3
  records. Carried by **R3**.

## STILL-OPEN, missing from frame

### review-fixes

- **`red.md` line count.** `red.md` says the new module is 39 lines; it is 38.
  Source: `test-review.md` §Nit ("No consequence"); `code-review.md` §1 calls
  it "the test review's standing nit, unchanged". Evidence:
  `plans/review-fixes/reports/red.md:193` still says "39 lines";
  `wc -l tests/test_line_limits_wc_padding.py` → 38.

### proof-verdict-prompt

- **Outline never run through `/proof`.** The Simple route calls for `/proof`
  between outline and `/build`; skipped for lack of an interactive user.
  Source: §Questions, item 2. Evidence: `plans/proof-verdict-prompt/` holds
  only `classification.md`, `outline.md`, `reports/implementation.md` — no
  proof record; the change itself shipped in `5f860e07` ("🐛 deliverable
  review fixes, skill hub splits, /proof verdicts, D-87 and D-9 rewired").

### release-decision-record

- **Reason for the 2026-08-04 publication reversal is unrecorded.** Source:
  §Top finding ("The reason for the reversal is unrecorded"). Evidence:
  `docs/changelog/2026-08-04-publication-postponement-reversed.md:9` and
  `docs/references/cli-and-package.md:73-75` still state that no source
  records why. The report states the gap; it does not name an action.

## UNCLEAR

### allowlist-ownership

- **Q1–Q3, defaults taken without a recorded ruling.** (1) deleting `/build`'s
  `## References` recap and `/requirements`' `## Key Principles`; (2) one
  extra Read on `/requirements` and fresh `/design`; (3) `requirements` m10
  folded in. Source: §Questions for my human partner. Check: the defaults
  shipped in `5f860e07`, and
  `docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md:27`
  records the recap deletion; no record of my human partner ratifying or
  reversing them was found in `plans/open-items-sweep/` or
  `plans/remaining-sweep/`.

### release-decision-record

- **Q1–Q5, defaults taken without a recorded ruling** (2026-07-17 changelog
  entry left unrewritten; publishing non-goal deleted; D-87 replacing D-9 in
  "Do not re-litigate"; three hub edits; D-87 numbering). Source: §Questions
  and defaults taken. Check: all shipped in `5f860e07`; no ratification record
  found in the same two sweep directories.
- **Toolkit `release.just` and `MARKETPLACE_DIR`.** Whether the toolkit's
  `release.just` requires it. Source: §Claims verified ("Not asserted
  anywhere because it is unresolvable…"). Check, read-only in
  `/Users/david/code/claude-plugin-dev`: `toolkit/release.just:53` says it
  "skips non-fatally when MARKETPLACE_DIR is unset" while
  `toolkit/release.sh:217-218` dies on it; which one governs a `release.just`
  run was not determined. Another repo; the report states D-87 does not need
  the answer.

## RESOLVED-SINCE

### review-fixes

- **`pipefail` comment inverted the mechanism** (`code-review.md` §Major).
  Evidence: `scripts/check_line_limits.sh:131-137` now says the pipeline
  depends on `pipefail` and "Do not drop `pipefail`"; introduced by
  `5f860e07`.
- **F-4 rewrite dropped the "by it" relation** (`code-review.md` §Nit).
  Evidence: `write-design.md:7` and `write-outline.md:149` read "Read
  `references/research-protocol.md` §A.5 and, by it, …"; `5f860e07`.
- **Sibling pointers lacking a Read imperative** (`green.md` §Anything unsure,
  second bullet). Evidence: `write-design.md:12` ("**Content rules:** Read
  `references/design-content-rules.md`") and `write-outline.md:137-139` now
  carry "Read". The path-form half stays open under R2 (above).

### allowlist-ownership

- **F-4 "per `X.md`" pointers not fixed** (§Deliverable-review findings).
  Fixed by review-fixes (`green.md` §F-4) and reworded again in `5f860e07`;
  see the two `write-*.md` lines above.
- **F-5's four named skill-body sites** (`recall/SKILL.md:20,45`,
  `ground/SKILL.md:70`, `deliverable-review/SKILL.md:104`). Fixed by
  review-fixes (`green.md` §F-5); the current `grep` finds no `plugin/…` path
  in `recall/` or `ground/SKILL.md`. The rest of F-5 is the in-frame R2 entry.
- **Stale frame line `.claude/handoff-todo.md:20`** ("Still unowned on the
  line-limit allowlist…"; §Left deliberately and Question 5). Evidence:
  `grep 'Still unowned' .claude/handoff-todo.md` → no match.
- **Eval §2 as the only home of an unrecorded release decision** (Question 4).
  Recorded as **D-87** by release-decision-record (`docs/decisions.md`
  D-87 line; `docs/references/cli-and-package.md`).
- **`memory/line-caps.md` "hard gate over `src` and `tests`" predating
  prose coverage** (§Stale memory references). Evidence:
  `memory/line-caps.md:11` now reads "over `src`, `tests` and the prose
  trees".
- **design open-mechanical M3, m1, m2, m5, m6, m7** — listed "all still open"
  under §Left untouched. Evidence: `design/SKILL.md:146-160` (§Author-Corrector
  Coupling) points at D-26 with no inline table (M3); no "maintainer" or
  "verbatim" hit in `design/SKILL.md` or `references/triage.md` (m2, m5);
  `design-content-rules.md:33,38` carry the ungrounded markers (m1);
  `write-outline.md:149-150` and `write-design.md:7-8` are two-line pointers
  (m6); `write-outline.md:50` names a fragment, not a glob (m7).
- **review M8** (progressive disclosure inverted in `review`; §Skill-review
  findings). Evidence: `plugin/skills/review/references/review-template.md`
  added in `5594a753` ("🐛 sweep the non-design remaining items — gates, TDD
  rules, skill-review edits"), routed from `review/SKILL.md:106`; the hub is
  161 lines.

### allowlist-ownership and release-decision-record

- **`memory/plugin-transition-eval.md` stale** — pointer over-promising
  (allowlist §Stale memory references); "blocked" description, "just release
  … BROKEN", stale citations, "marketplace entry is still missing"
  (release-decision-record §Stale memory sentences). Evidence: the file is
  gone; memory commit `7ab21b1` "Retire the plugin-transition evaluation
  memory".
- **PyPI-publish contradiction between memory and D-9** (allowlist §Stale
  memory references, second bullet). Evidence: D-9 now carries the
  2026-08-04 reversal (`docs/decisions.md:23-25`) and the contradicting memory
  is retired (`7ab21b1`).
- **Three live staleness items in `plugin-transition-evaluation.md`** —
  `bump-plugin-version.py`'s dead `sessionstart-health.sh` block;
  `plansDirectory` disagreement; `agents/learnings.md:5` routing through
  `/codify` (allowlist §`plugin-transition-evaluation.md`, Kept;
  release-decision-record §Does the eval doc still justify a page?).
  Evidence: `grep -rn sessionstart-health plugin/bin scripts` → no match;
  `plugin/.claude/settings.json:17` and `.claude/settings.json:24` both
  `"plans/claude/"`; `agents/learnings.md:5` routes to
  `/claude-md-management:revise-claude-md` and `craft:design-doc-writing`.
  All three and the page's deletion land in `10b509e2` ("🔧 sweep the
  non-design open items — correctors, drift, staleness page, precommit hook,
  release sync").

### release-decision-record

- **`memory/MEMORY.md` index lines 74-75 stale** (§Stale memory sentences).
  Evidence: the `distribution-published.md` line (`memory/MEMORY.md:79`) now
  says "PyPI + marketplace are published"; the `plugin-transition-eval.md`
  line is gone with the file.
- **`scripts/release.sh` never refreshed an existing entry's
  `description`** (§D-9 rewiring, "a real gap in the recipe"). Evidence:
  `scripts/release.sh:194` sets `.description` on the matching existing
  entry; `10b509e2`.

### proof-verdict-prompt

- **Whether D-78 widens beyond `AskUserQuestion`** (§Questions, item 1; the
  node recorded it as open). Evidence: `docs/references/agent-instructions.md`
  now records "user ruling, 2026-09-21": plain-text interaction is the default
  for every skill, and the conclusion stays worded against `AskUserQuestion`;
  `5f860e07`.

## Counts

| Classification | Entries |
|---|---|
| STILL-OPEN, in frame | 13 |
| STILL-OPEN, missing from frame | 3 |
| UNCLEAR | 3 |
| RESOLVED-SINCE | 16 |
