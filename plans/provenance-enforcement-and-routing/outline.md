# Outline: Provenance enforcement, and routing by need rather than by prose

Job: `plans/provenance-enforcement-and-routing/`

Third pass in the `design-routing-and-provenance` line, working the 6 major
and 5 minor findings of `provenance-reach-and-sweep`'s deliverable review.
Four parts. B and C are agentic prose; A adds one script and D a recipe, a
script and a config file — the job's two tdd items.

## Provenance

- **Derived from:**
  `plans/provenance-reach-and-sweep/reports/deliverable-review.md`,
  superseding `plans/provenance-reach-and-sweep/outline.md`
- **Base:** `926e372d02a0366202b2bb6a684551128d1f2a66` — copied verbatim from
  the superseded outline, not recomputed.

## Requirements

The review report is the requirement. Ids below are the report's own.

| # | Finding | Part | Settled as |
|---|---|---|---|
| M-1 | Corrector repair writes `TODO` over a correct `Derived from:` | A | placeholder scoped to `Base:` |
| M-2 | Corrector barred from the verbatim copy it has already verified; D-80 repeats the rationale | A | allow the copy, keep the ban on derived bases |
| M-4 | `/edify:deliverable-review` never checks the inheritance rule | A | range script, stop on conflict |
| m-1 | `research-protocol.md:41` "as shown" covers a first-pass value | A | scope to heading and labels |
| M-3 | "Edit targets named" binds the `/runbook` branch on a no-runbook rationale | B | binds `/build` branches only — falls out of KD-3 |
| M-5 | Node defers to a gate branch that does not exist | B | write the branch |
| m-2 | `design/SKILL.md:174` singular "B gate" | B | rewritten with the caller list |
| m-3 | Final `ELSE` mislabelled | B | route table rewritten |
| m-4 | `docs/changelog.md:29-31` wider than what shipped | B | new dated entry, old one untouched |
| M-6 | Five stale "per X" pointers tree-wide | C | imperative Reads |
| m-5 | Correctors under the cap only for want of a wrapper | D | formatter and guard in the gate |

**Decisions taken before this outline** (my human partner, this session):

- **`/build` from an outline is not reserved for prose.** The intent is that
  a plan simple enough not to need the runbook layer is built directly. Pure
  prose qualifies because it needs no test-driver; a simple plan with a TDD
  loop qualifies too. This replaces the M-3 fork the review posed.
- **M-6: fix the five sites here.** The sweep-mechanism question stays its own
  job.
- **m-5 rides this job**, as an example of non-prose work that does not need
  runbook ceremony.

## Key decisions

**KD-1 — The corrector's Provenance repair is a table, not a ban.** Replaces
the "Never fill in `Base:` yourself" bullet in both correctors:

| Found | Repair |
|---|---|
| Section absent | add it, `TODO` in both fields |
| `Derived from:` absent, `Base:` present | `TODO` in `Derived from:` only |
| `Derived from:` names a prior artifact that resolves and carries a full-sha `Base:`; this `Base:` differs or is missing | copy the prior `Base:` verbatim; report Critical if it differed |
| `Derived from:` resolves, prior artifact has no usable `Base:` | `TODO` in `Base:` only |
| `Derived from:` path does not resolve | `TODO` in `Base:` only; leave `Derived from:` as found |
| `Derived from:` is `none`, `Base:` not reachable from HEAD | `TODO` in `Base:` only |

Two invariants stated under it: never write a `Base:` obtained any way other
than the verbatim copy — `git log`, `git merge-base` and `HEAD` are all the
recomputation; never overwrite a `Derived from:` that is present.

The block stays duplicated in both correctors, edited identically. Neither
corrector Reads any external file today, a path under `plugin/fragments/`
resolves only inside this checkout, and the family's dedup is already queued
as pilfer defect 21. *(Reverses the extraction I first proposed.)*

**KD-2 — A script establishes the review range and stops on conflict.**
(My human partner: detect by script, stop on conflict.) New
`plugin/skills/deliverable-review/scripts/review-range.sh <artifact>`, called
repo-relative as `/build` calls `verify-step.sh`. It parses §Provenance,
resolves `<Base>^{commit}`, and where `Derived from:` names a superseded
artifact, reads that artifact's `Base:` and compares. One verdict line on
stdout:

| Exit | Line | Skill does |
|---|---|---|
| 0 | `RANGE: <base>..HEAD` | proceed with it |
| 1 | `CONFLICT: base <a> != <b> inherited from <path>` | **STOP**, report both |
| 1 | `NO-PROVENANCE:`, `UNRESOLVED: <base>`, `NO-PRIOR: <path>` | ask the user for the range |
| 2 | — | STOP: the script failed, no verdict |

Phase 1 step 2 shrinks to the call and this table; the parsing prose it
carries today is deleted. No substitution: a conflict means one of two
artifacts is wrong, and the script cannot know which. One hop only — each
artifact in a chain was compared against its predecessor at its own review.

**KD-3 — The route asks whether the work needs the runbook layer.** What
`/runbook` adds, read off the tree: phases with boundaries
(`build/references/phase-boundary.md`), and a corrector, simplifier and
`/proof` pass over the decomposition itself. New route table:

```
IF work type = Investigation or Exploration   → /build
ELSE IF a runbook discriminator holds         → /runbook
ELSE                                          → /build
```

Discriminators, either one: cross-file coordination requiring sequencing
(kept); a decomposition the author judges needs its own review before
execution (new — **ungrounded, no threshold offered**; no data exists on item
counts at which an unreviewed decomposition fails). "Implementation loops" is
deleted as a discriminator, and the prose-path rationale goes with the branch
it justified. D-39 already records the principle for one case — TDD run per
slice from the executing session, no runbook; KD-3 stops treating it as an
exception, and D-39 is reworded to cite the general rule.

Preconditions: the first (executor decisions resolved) binds every branch.
The second (edit targets named) binds the `/build` branches only, evaluated
after the route — on the `/runbook` branch, naming targets is `/runbook`'s
job. That is M-3.

**KD-4 — An outline carries a TDD change as a `tdd` item.** `/build` §4.3
fires on item type, which only a runbook carries today. An outline or design
routed to `/build` writes each behavioural change in
`runbook-format.md`'s item shape — `Item 1.M`, `Slices:`, `Interfaces:` where
consumed — by Reading that file, not by restating it. `/build` §4.3 and
`tdd-slice.md`'s "only a tdd item reaches this file" reword from "type is
`tdd`" to "the item carries `Slices:`", whichever artifact holds it. The
second precondition gains: a behavioural change has its slices written.

**KD-5 — Phase 0's Moderate non-prose route reads the node.** It stops
hard-coding `/runbook`: generate, `/proof`, then Read
`references/route-to-execution.md` and route by it. The node's callers go
from three to four; its scope sentence, `design/SKILL.md:19` and `:171-175`,
`docs/design.md:599-602`, D-35 and the caller enumeration at `:617-618` follow.
Simple and Moderate-agentic-prose still reach `/build` without reading it.

**KD-6 — A not-routable sub-problem reopens only its own entry.** New branch
in `write-outline.md`'s multi-sub-problem gate, after "If sufficient": where
the node records a sub-problem not-routable, resume A.5 for that entry alone.
Siblings with no dependency path through it stay dispatchable; its dependents
are held, and the readiness summary says which. The node's closing sentence
then points at a branch that exists.

**KD-7 — The markdown guard fails on new overage and lists the old.**
`scripts/check_line_limits.sh` gains markdown: cap picked from the path (200
for `SKILL.md`, 400 otherwise), reporting
`oversized-file: <path>: <n> lines > <cap>`. Files already over after the
reflow go in an in-script allowlist, each line naming the job that retires it;
an allowlisted file is reported but does not fail. The alternative — a hard
gate — is red on its first run (`corrector.md` is 605 lines before any
reflow), and a warn-only gate never turns red at all.

**KD-8 — rumdl, MD013 only, `reflow-mode = "normalize"`.** Per
`memory/ddaanet/markdown-formatter-choice.md`: 80 columns, `reflow = true`,
`headings`, `code-blocks` and `tables` off, `--no-cache`. Installed through
the dev dependency group. Scope: `plugin/`, `docs/`, and root `*.md`.
`plans/` is frozen work and `memory/` is a submodule with its own gate; both
stay out.

## Items

Items 1.2 and 1.10 are tdd, the rest general. Execution order is 1.1,
1.3–1.9, then 1.2, then 1.10: both tdd items depend on 1.7, and 1.10 runs
last because its reflow moves every line number the earlier items cite.

- Item 1.1: `plugin/agents/outline-corrector.md` §Provenance,
  `plugin/agents/design-corrector.md` §3.5 — replace the final bullet with
  KD-1's table and two invariants, identical text in both. Requirements: M-1,
  M-2.
- Item 1.2: `plugin/skills/deliverable-review/scripts/review-range.sh` (new),
  then `deliverable-review/SKILL.md` Phase 1 step 2 rewritten to call it per
  KD-2. Tests in `tests/test_review_range.py`, each building a throwaway git
  repo under `tmp_path` and running the script as a subprocess.
  Requirements: M-4. Depends on: Item 1.7
  Slices:
  1. External contract: `test_first_pass_emits_range` — artifact with
     `Derived from: none` and `Base:` = the repo's first commit; asserts exit
     0 and stdout exactly `RANGE: <sha>..HEAD`.
  2. Inherited match: `test_second_pass_matching_base_emits_range` — prior
     artifact carries the same `Base:`; asserts exit 0 and the `RANGE:` line.
  3. Conflict: `test_second_pass_recomputed_base_is_conflict` — this `Base:`
     is a later commit than the prior's; asserts exit 1 and a `CONFLICT:`
     line naming both shas and the prior artifact's path.
  4. No section: `test_missing_provenance_reported` — asserts exit 1 and
     `NO-PROVENANCE:`.
  5. Unresolvable base: `test_unresolvable_base_reported` — 40 hex chars
     naming no commit; asserts exit 1 and `UNRESOLVED:`.
  6. Missing prior: `test_missing_prior_artifact_reported` — `Derived from:`
     names a path that does not exist; asserts exit 1 and `NO-PRIOR:`.
  7. Wrapped field and spaced path: `test_wrapped_derived_from_with_spaced_path`
     — `Derived from:` value on continuation lines, prior artifact under
     `plans/my job/`; asserts the inherited compare still runs (exit 0).
  Interfaces:
  - `review-range.sh <artifact-path>` — stdout one verdict line per KD-2's
    table; exit 0 range, 1 verdict-without-range, 2 script failure
- Item 1.3: `docs/design.md` D-80 — consumer clause names the script and its
  stop-on-conflict; "no mechanical validator" narrows to the write side; the
  accepted-tradeoffs clause stops saying the correctors "cannot repair it" and
  states KD-1's split. Corrected in place. Requirements: M-2, M-4.
- Item 1.4: `plugin/skills/design/references/research-protocol.md:41` — "as
  shown" scoped to the heading and the two field labels; the values come from
  the rule. Requirements: m-1.
- Item 1.5: `plugin/skills/design/references/route-to-execution.md` —
  §Preconditions, §Route, §Runbook discriminators per KD-3 and KD-4; scope
  sentence per KD-5; prose-path rationale deleted. Requirements: M-3, m-3.
- Item 1.6: `plugin/skills/design/SKILL.md` — Phase 0 Moderate non-prose route
  and §Routing out per KD-5; `:19` caller list; `:174` plural. Generation step
  of both `/build`-bound routes gains KD-4's Read of `runbook-format.md` for a
  behavioural change. `docs/design.md:599-602`, D-35, D-39, `:617-618` to
  match.
  Requirements: M-3, m-2.
- Item 1.7: `plugin/skills/build/SKILL.md` §4 and §4.3,
  `plugin/skills/build/references/tdd-slice.md:3-5` — KD-4's rewording.
  `plugin/agents/outline-corrector.md` gains one criterion: an item carrying
  `Slices:` states each test's assertion, per `runbook-format.md`.
  Requirements: M-3.
- Item 1.8: `plugin/skills/design/references/write-outline.md:181-187` —
  KD-6's branch. `docs/changelog.md` — one new entry dated 2026-09-18 covering
  KD-3 to KD-6 and stating that it narrows the 2026-09-17 entry's precondition
  claim. Requirements: M-5, m-4.
- Item 1.9: the five pointers — `build/references/tdd-slice.md:4`,
  `fragments/delegation.md:33`, `runbook/SKILL.md:78`, `review/SKILL.md:207`,
  `build/references/review-dispatch-template.md:77` — each to "Read `<path>`
  and …". The last is a citation rather than a must-open node: reword to name
  D-26 without "per". Exit condition: `rg -n -i '\bper\s+`?[\w/.-]+\.md'
  plugin/ docs/` with every hit classified in the item report.
  Requirements: M-6.
- Item 1.10: `scripts/check_line_limits.sh`, `plugin/portable.just` `format`
  recipe, `.rumdl.toml`, `pyproject.toml` dev group. Requirements: m-5.
  Depends on: Item 1.7
  Slices:
  1. External contract: `test_line_limits_passes_clean_tree` — asserts exit 0
     and no `oversized-file:` line for a fixture tree holding one 10-line
     `SKILL.md` and one 10-line `notes.md`.
  2. Default cap: `test_line_limits_fails_markdown_over_400` — asserts exit 1
     and the line `oversized-file: <path>: 401 lines > 400` for a 401-line
     `notes.md`.
  3. Path-picked cap: `test_line_limits_fails_skill_hub_over_200` — asserts
     exit 1 and `> 200` for a 201-line `SKILL.md`, and exit 0 for a 201-line
     `notes.md` beside it.
  4. Allowlist: `test_line_limits_reports_allowlisted_without_failing` —
     asserts exit 0 **and** the `oversized-file:` line present for an
     allowlisted over-cap file.
  5. Spaced path: `test_line_limits_handles_spaced_path` — asserts the
     reported path is intact for `my notes.md` over the cap.
  Interfaces:
  - `scripts/check_line_limits.sh [ROOT]` — exit 0 clean, 1 on any
    non-allowlisted overage; one `oversized-file:` line per over-cap file
  After the slices, general work in the same item: delete the dead
  `agents/decisions` loop and its `2>/dev/null`; add `rumdl fmt --no-cache` to
  `format` ahead of the line guard; run the one-time reflow as **its own
  commit**, verified by rendering each touched file through `cmark-gfm` before
  and after and diffing whitespace-collapsed HTML; populate the allowlist from
  the measured post-reflow counts.

## Scope

**IN:** the eleven findings above, at the sites named.

**OUT:**
- The sweep mechanism — why a diff-scoped sweep keeps reporting clean. Own job.
- Corrector-family dedup, including the Provenance block KD-1 leaves
  duplicated — and whether the correctors' detection half should call
  `review-range.sh` too. Pilfer defect 21.
- Splitting any file the allowlist names. Each is its retiring job's work.
- `write-outline.md:116`'s "no implementation loops" downgrade criterion. It
  gates skipping the A.6 review, not the execution route; KD-3 does not reach
  it.
- `inbox/brief-review-feeds-back-into-design.md`, `/proof`'s verdict prompt,
  `plans/skill-reviews/`. Separate task-frame items.

## Author-corrector coupling

Author change: `/design`'s outline format gains tdd items (KD-4). Coupled
corrector: `outline-corrector`. **Update needed: yes** — Item 1.7's criterion.
`design-corrector` needs none: a `design.md` routed to `/build` is checked
for the same item shape by the second precondition, not by the corrector.
No mechanical validator exists.

## Risks

- **KD-3's second discriminator is judgement with no calibration.** It will
  be applied unevenly until classification.md comparisons from
  `triage-feedback.sh` give data. Stated rather than dressed as a threshold.
- **The reflow moves every line number** cited in `docs/`, the task frame and
  open review reports. Item 1.10 runs last for that reason; citations in
  frozen `plans/` reports go stale and are not chased.
- **Wrapping breaks line-grepping checkers.** Before the reflow commit, `rg`
  the test suite and `plugin/bin/` for checks that match a markdown bullet on
  one line; join continuation lines in any that do.
- **`cmark-gfm` and `rumdl` are not installed here.** `rumdl` arrives with the
  dev group; if `cmark-gfm` cannot be had, the reflow commit is held and
  reported rather than landed unverified.
- **This job routes itself by the rule it writes.** Under today's Phase 0
  text a job containing Item 1.10 is Moderate non-prose and goes to
  `/runbook`. It goes to `/build` on D-39 — work that edits pipeline skills
  leaves the runbook pipeline, the session dispatching `test-driver` per
  slice — and on my human partner's instruction. Item 1.10's dependency on
  1.7 is what makes §4.3 reachable when it runs.
