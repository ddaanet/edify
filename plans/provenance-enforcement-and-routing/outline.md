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

The review report is the requirement. Major ids are the report's own; `m-N`
is the report's minor finding N.

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
| M-6 | Stale "per X" pointers tree-wide | C | imperative Reads |
| m-5 | Correctors under the cap only for want of a wrapper | D | formatter and guard in the gate |

**Decisions taken before this outline** (my human partner, 2026-09-18):

- **`/build` from an outline is not reserved for prose.** The intent is that
  a plan simple enough not to need the runbook layer is built directly. Pure
  prose qualifies because it needs no test-driver; a simple plan with a TDD
  loop qualifies too. This replaces the M-3 fork the review posed.
- **M-6: fix the sites here.** The sweep-mechanism question stays its own
  job.
- **m-5 rides this job**, as an example of non-prose work that does not need
  runbook ceremony.

**Cross-cutting rule** (my human partner, 2026-09-18, at `/proof`): every
path this job writes into a skill body resolves from an installed plugin, not
from this checkout. `CLAUDE_PLUGIN_ROOT` is unset in the agent's Bash; what
does resolve is the skill's announced base directory (`references/x.md`,
`../runbook/references/runbook-format.md`) and, for scripts, the plugin's
`bin/`, which Claude Code puts on PATH for every enabled plugin
(`plugin-craft:skill-authoring` §Bundled scripts). A repo-relative
`plugin/…` path is a defect. The 34 such references already in the tree are
out of scope (§Scope).

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
| `Derived from:` names only the report | `TODO` in `Base:` only; leave `Derived from:` as found |
| `Derived from:` is `none`; `Base:` missing, not a full sha, or not reachable from HEAD | `TODO` in `Base:` only |

Three invariants stated under it: never write a `Base:` obtained any way
other than the verbatim copy — `git log`, `git merge-base` and `HEAD` are all
the recomputation; never overwrite a `Derived from:` that is present; every
value a `TODO` replaces is quoted in the report.

The block stays duplicated in both correctors, edited identically. Neither
corrector Reads any external file today, an agent gets no announced base
directory, and the family's dedup is already queued as pilfer defect 21.

**KD-2 — A script establishes the review range and stops on conflict.**
(My human partner: detect by script, stop on conflict.) New
`plugin/bin/edify-review-range.sh <artifact>`, invoked by bare name — one
simple script, directly in `bin/`, no shim and no `scripts/` directory. It
locates the repository from the artifact's directory and resolves every path
it reads against `git rev-parse --show-toplevel`, since `Derived from:` values
are repo-relative. It parses §Provenance; the prior artifact is the path
following `superseding`. It resolves `<Base>^{commit}`, and where a prior
artifact is named, reads that artifact's `Base:` and compares. One verdict
line on stdout:

| Exit | Line | Skill does |
|---|---|---|
| 0 | `RANGE: <base>..HEAD` | proceed with it |
| 1 | `CONFLICT: base <a> != <b> inherited from <path>` | **STOP**, report both |
| 1 | `NO-PROVENANCE:`, `UNRESOLVED: <base>`, `NO-PRIOR: <path>` | ask the user for the range |
| any other | — | STOP: the script failed, no verdict |

`NO-PRIOR:` covers a prior artifact that is missing or carries no full-sha
`Base:`. `NO-PROVENANCE:` also covers a `Derived from:` that is neither
`none` nor names a `superseding` artifact — the report-only shape KD-1
repairs — since no range can be established from it (ruled at the review
gate; pinned by `tests/test_review_range.py`, since split into five
`tests/test_review_range_*.py` modules plus `tests/review_range_helpers.py`
to stay under the line cap). Phase 1 step 2 shrinks to the call and this
table; the parsing prose it carries today is deleted. No substitution: a
conflict means one of two artifacts is wrong, and the script cannot know
which. One hop only — each artifact in a chain was compared against its
predecessor at its own review.

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
deleted as a discriminator, and the prose-path branch goes. Its rationale's
definition survives, moved under the first discriminator: prose edits are
commutative, multi-file prose is not cross-file coordination, and
coordination arises from runtime ordering dependencies such as build↔verify —
the `test↔implementation` example is dropped, since under this rule a TDD
loop alone is not coordination. D-39 keeps its own ground — stale-instruction
risk when a runbook step edits the runbook skill — and only its closing
generalisation is reworded to cite this rule.

Preconditions: the first (executor decisions resolved) binds every branch.
The second (edit targets named) binds the `/build` branches only, evaluated
after the route — on the `/runbook` branch, naming targets is `/runbook`'s
job. That is M-3.

**KD-4 — An outline carries a TDD change as a `tdd` item.** `/build` §4.3
fires on item type, which only a runbook carries today, and there as a phase
attribute. An outline or design routed to `/build` writes each behavioural
change in `runbook-format.md`'s item shape — `Item 1.M`, `Slices:`,
`Interfaces:` where consumed — by Reading
`../runbook/references/runbook-format.md`, not by restating it. `/build` §4.3
and `tdd-slice.md`'s "only a tdd item reaches this file" reword from "type is
`tdd`" to "the item carries `Slices:`", whichever artifact holds it. An item
carrying `Slices:` carries nothing else to execute; general work goes in its
own item. The second precondition gains: a behavioural change has its slices
written.

**KD-5 — Phase 0's Moderate non-prose route reads the node.** It stops
hard-coding `/runbook`: generate, `/proof`, then Read
`references/route-to-execution.md` and route by it. The node's callers go
from three to four; its scope sentence, the skill's `description:`
(`design/SKILL.md:6-7`, "routes moderate to /runbook"), `:19` and `:171-175`,
`docs/design.md:599-602`, D-35 and the caller enumeration at `:617-618`
follow. The node's precondition-failed branch gains the fourth caller's return
point: the Moderate route's own generate step, since that caller ran neither
A.5 nor C.1. Simple and Moderate-agentic-prose still reach `/build` without
reading it.

**KD-6 — A not-routable sub-problem reopens only its own entry.** New branch
in `write-outline.md`'s multi-sub-problem gate, after "If sufficient": where
the node records a sub-problem not-routable, resume A.5 for that entry alone.
Siblings with no dependency path through it stay dispatchable; its dependents
are held, and the readiness summary says which. The revised entry alone goes
back through the node; the user confirms that entry, not the whole outline,
and its held dependents release once it routes. The node's closing sentence
then points at a branch that exists.

**KD-7 — The markdown guard fails on new overage and lists the old.**
`scripts/check_line_limits.sh` gains markdown over KD-8's scope: cap picked
from the path (200 for `SKILL.md`, 400 otherwise), reporting
`oversized-file: <path>: <n> lines > <cap>`; the Python loop adopts the same
line. Files already over after the reflow go in an allowlist — a sidecar file
beside the script, overridable by argument so a test can supply its own. Each
entry records the file's measured line count as a ceiling and names the job
that retires it, or "no job yet". An allowlisted file is reported but does
not fail unless it exceeds its ceiling; the ceiling only ratchets down. The
alternative — a hard gate — is red on its first run (`corrector.md` is 605
lines before any reflow; six files are over today), and a warn-only gate
never turns red at all.

**KD-8 — rumdl, MD013 only, `reflow-mode = "normalize"`.** Per
`memory/ddaanet/markdown-formatter-choice.md`: 80 columns, `reflow = true`,
`headings`, `code-blocks` and `tables` off, `--no-cache`. Installed through
the dev dependency group. Scope: `plugin/`, `docs/`, and root `*.md`,
excluding `docs/superpowers/plans/` and `docs/superpowers/specs/`. `plans/`
and those two are frozen work and `memory/` is a submodule with its own gate;
all stay out. `precommit` runs `run-line-limits` but never `format`, so the
gate gains a non-fixing formatter check ahead of the line guard: it fails
when `rumdl fmt` would change a file. The exact invocation is **unverified**
— the memory records `fmt` exiting 0 with unwrappable lines left and
`check --fix` exiting 1, and nothing has measured plain `check` on a line it
cannot wrap; Item 1.11 probes it.

## Items

Items 1.2 and 1.10 are tdd, the rest general. Execution order is 1.1,
1.3–1.9, then 1.2, then 1.10, then 1.11: both tdd items depend on 1.7, and
1.11 runs last because its reflow moves every line number the earlier items
cite. Every pointer an item writes into a skill body is skill-relative
(§Requirements, cross-cutting rule).

- Item 1.1: `plugin/agents/outline-corrector.md` §Provenance,
  `plugin/agents/design-corrector.md` §3.5 — replace the final bullet with
  KD-1's table and three invariants, identical text in both.
  `outline-corrector.md` also gains one criterion: an item carrying `Slices:`
  states each test's assertion, per `runbook-format.md`. Requirements: M-1,
  M-2 — the `Slices:` criterion serves KD-4 rather than a review finding.
  M-3 is a Part B routing finding and belongs to Items 1.3 and 1.5–1.7.
- Item 1.2: `plugin/bin/edify-review-range.sh` (new), then
  `deliverable-review/SKILL.md` Phase 1 step 2 rewritten to call it by bare
  name per KD-2. Tests in `tests/test_review_range.py`, since split into
  five `tests/test_review_range_*.py` modules plus
  `tests/review_range_helpers.py` to stay under the line cap, each building a
  throwaway git repo under `tmp_path` and running the script as a subprocess
  by bare name, with `plugin/bin` on PATH and CWD outside the repo.
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
  7. Prior without a base: `test_prior_without_base_reported` — the prior
     artifact exists but its `Base:` is absent or not a full sha; asserts
     exit 1 and `NO-PRIOR:`.
  8. Wrapped field, spaced path, foreign CWD:
     `test_wrapped_derived_from_with_spaced_path` — `Derived from:` value on
     continuation lines, prior artifact under `plans/my job/`, script run
     from a directory outside the repo with the artifact given as an absolute
     path; asserts the inherited compare still runs (exit 0). Also a
     first-pass artifact whose `Derived from:` reads `none — <rationale>`,
     the idiom the tree's real artifacts use; asserts `RANGE:` (added after
     slice 1's code review, which found the bare-`none` match rejecting it).
  List revision after slice 2: its GREEN implemented the compare, and the
  code review probed slices 3, 6 and 7's verdicts already matching KD-2's
  table verbatim. For those three, RED writes the test, the test review
  proves it by mutation (mutate the SUT, the test reds, restore), the test is
  committed as `test: Item 1.2/k — …`, and no GREEN or code-review dispatch
  runs since the implementation does not change. After slice 3: slices 4
  and 5 were implemented by slice 1's GREEN and slice 8's cases were probed
  by the reviews, so 4–8 take the same form, batched into one RED dispatch
  and one test review.
  Interfaces:
  - `edify-review-range.sh <artifact-path>` — repo located from the
    artifact's directory, `Derived from:` paths resolved against the repo
    root; stdout one verdict line per KD-2's table; exit 0 range, 1
    verdict-without-range, any other exit script failure
- Item 1.3: `docs/design.md` — D-80: consumer clause names
  `edify-review-range.sh` and its stop-on-conflict; "no mechanical validator"
  narrows to the write side; the accepted-tradeoffs clause stops saying the
  correctors "cannot repair it" and states KD-1's split. `:599-602`, D-35,
  D-39 and `:617-618` per KD-3 and KD-5. All corrected in place.
  Requirements: M-2, M-4, M-3.
- Item 1.4: `plugin/skills/design/references/research-protocol.md:41` — "as
  shown" scoped to the heading and the two field labels; the values come from
  the rule. Requirements: m-1.
- Item 1.5: `plugin/skills/design/references/route-to-execution.md` —
  §Preconditions, §Route, §Runbook discriminators per KD-3 and KD-4; scope
  sentence and the precondition-failed return point per KD-5; prose-path
  branch deleted, its commutativity definition relocated. Requirements: M-3,
  m-3.
- Item 1.6: `plugin/skills/design/SKILL.md` — `description:`, Phase 0
  Moderate non-prose route and §Routing out per KD-5; `:19` caller list;
  `:174` plural. Generation step of both `/build`-bound routes gains KD-4's
  Read of `../runbook/references/runbook-format.md` for a behavioural change.
  Requirements: M-3, m-2.
- Item 1.7: `plugin/skills/build/SKILL.md` §4 and §4.3,
  `plugin/skills/build/references/tdd-slice.md:3-5` — KD-4's rewording, and
  `tdd-slice.md:4`'s "per `dispatch-composition.md`" made an imperative Read
  while the file is open. Requirements: M-3, M-6.
- Item 1.8: `plugin/skills/design/references/write-outline.md:181-187` —
  KD-6's branch. `docs/changelog.md` — one new entry, dated the day it lands,
  covering KD-3 to KD-6 and stating that it narrows the 2026-09-17 entry's
  precondition claim. Requirements: M-5, m-4.
- Item 1.9: the remaining "per X" pointers — `fragments/delegation.md:33`,
  `runbook/SKILL.md:36-37` and `:78`, `review/SKILL.md:207`,
  `build/references/phase-boundary.md:14-15`,
  `build/references/finishing.md:10-11` and `:17-18` — each to "Read
  `<path>` and …", the path skill-relative (`review/SKILL.md:207` →
  `../../fragments/review-requirement.md`). `delegation.md:33` is a fragment
  with no base directory: its wording is fixed here, its path form belongs to
  the repo-relative job (§Scope). `review-dispatch-template.md:77` and
  `finishing.md:35-36` are citations rather than must-open nodes: reword to
  name D-26 without "per". The review counted five sites because its search
  was single-line; five more had "per" at a line end. Exit condition:
  `rg -n -U -i '\bper\s+`?[\w/.-]+\.md' plugin/ docs/` with every hit
  classified in the item report. Requirements: M-6.
- Item 1.10: `scripts/check_line_limits.sh` and its allowlist file, with
  `tests/test_line_limits.py`, `tests/line_limits_helpers.py` and
  `tests/test_line_limits_exit_codes.py` (split off to keep the first module
  under its cap).
  Requirements: m-5. Depends on: Item 1.7
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
     test writes an allowlist naming an over-cap file at its current count;
     asserts exit 0 **and** the `oversized-file:` line present.
  5. Ceiling: `test_line_limits_fails_allowlisted_file_over_ceiling` —
     allowlist records 450 for a file now at 451 lines; asserts exit 1.
  6. Exclusion: `test_line_limits_skips_frozen_docs` — a 401-line file under
     `docs/superpowers/plans/`; asserts exit 0 and no `oversized-file:` line.
  7. Spaced path: `test_line_limits_handles_spaced_path` — asserts the
     reported path is intact for `my notes.md` over the cap.
  8. Partial walk is a failure: `test_line_limits_fails_when_find_cannot_walk`
     — an unreadable directory under `docs/`; asserts exit 2 and no
     `oversized-file:` line (added after slices 3–7's code review found
     `find` failing inside process substitution left the gate green).
  Final list revision (TDD audit): the landed suites carry seven tests the
  reviews added beyond the slice lists — in the `test_review_range_*` modules
  the `Base:`-only and report-only Provenance shapes and a `Base:` with a
  trailing rationale; in `test_line_limits.py` a comment-and-blank allowlist
  fixture, `docs/superpowers/specs/` excluded and `docs/superpowers/design/`
  in scope, and an exact-path allowlist match. Slice 1.10/8's "no
  `oversized-file:` line" assertion was dropped as vacuous (nothing in its
  fixture is printable); the contract is exit 2.
  Six more tests were unaccounted for by that enumeration and are added to it
  here (`reports/deliverable-review.md`, Test-suite bookkeeping) — all six do
  real work, so the defect was the stale list rather than the tests:
  `test_one_hop_only_ignores_grandprior_mismatch`
  (`tests/test_review_range_range.py`), the only thing pinning KD-2's "One
  hop only" clause; in `tests/test_line_limits.py`,
  `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent`,
  `test_line_limits_rejects_crlf_on_full_entry_line` and
  `test_line_limits_rejects_crlf_on_two_field_entry_line`; and both functions of
  `tests/test_line_limits_exit_codes.py`,
  `test_unreadable_file_outranks_a_later_overage` and
  `test_walk_failure_outranks_a_later_overage`, which pin KD-7's "exit 2
  outranks exit 1".
  List revision before slice 1: today's script ignores a `ROOT` argument and
  exits 0 on any tree, so slice 1 alone cannot red. Slices 1 and 2 run as
  one RED dispatch — 2 supplies the genuine red, the review proves 1 by
  mutation — and one GREEN.
  Interfaces:
  - `scripts/check_line_limits.sh [--allowlist FILE] [ROOT]` — exit 0 clean,
    1 on any non-allowlisted overage or allowlisted file over its ceiling;
    one `oversized-file:` line per over-cap file
- Item 1.11: `plugin/portable.just` `format` and `precommit` recipes,
  `.rumdl.toml`, `pyproject.toml` dev group. Delete the dead
  `agents/decisions` loop and its `2>/dev/null` from
  `scripts/check_line_limits.sh`; add `rumdl fmt --no-cache` to `format`;
  probe and add the non-fixing check to `precommit` ahead of `run-line-limits`
  (KD-8); run the one-time reflow as **its own commit**, verified by rendering
  each touched file before and after and diffing whitespace-collapsed HTML —
  `cmark-gfm` if it can be installed, else `markdown-it-py` in the venv, the
  method being the render diff and not the tool; populate the allowlist from
  the measured post-reflow counts. Requirements: m-5. Depends on: Item 1.10

## Scope

**IN:** the eleven findings above, at the sites named; the cross-cutting
skill-relative path rule for every path this job writes; the precommit
formatter check.

**OUT:**
- The sweep mechanism — why a diff-scoped sweep keeps reporting clean. Own job.
- Resolving the existing repo-relative `plugin/…` references from an
  installed plugin — 34 sites across 16 files in `plugin/skills`,
  `plugin/agents` and `plugin/fragments`, including the five script call
  sites (`verify-step.sh` ×3, `triage-feedback.sh` ×2). Own job.
- Corrector-family dedup, including the Provenance block KD-1 leaves
  duplicated — and whether the correctors' detection half should call
  `edify-review-range.sh` too. Pilfer defect 21.
- Splitting any file the allowlist names. Each is its retiring job's work.
- `write-outline.md:116`'s "no implementation loops" downgrade criterion. It
  gates skipping the A.6 review, not the execution route; KD-3 does not reach
  it.
- `inbox/brief-review-feeds-back-into-design.md`, `/proof`'s verdict prompt,
  `plans/skill-reviews/`. Separate task-frame items.

## Author-corrector coupling

Author change: `/design`'s outline format gains tdd items (KD-4). Coupled
corrector: `outline-corrector`. **Update needed: yes** — Item 1.1's criterion.
`design-corrector` needs none: a `design.md` routed to `/build` is checked
for the same item shape by the second precondition, not by the corrector.
No mechanical validator exists.

## Risks

- **KD-3's second discriminator is judgement with no calibration.** It will
  be applied unevenly until classification.md comparisons from
  `triage-feedback.sh` give data. Stated rather than dressed as a threshold.
- **The reflow moves every line number** cited in `docs/`, the task frame and
  open review reports. Item 1.11 runs last for that reason; citations in
  frozen `plans/` reports go stale and are not chased.
- **Wrapping breaks line-grepping checkers.** Surveyed at `/proof`: no test
  in the suite and no script in `plugin/bin/`, `build/scripts/` or
  `plugin/hooks/` greps markdown in the reflow's scope line by line; the one
  line-oriented markdown grep, `triage-feedback.sh` on `classification.md`,
  reads `plans/`. Item 1.9's exit condition is multiline for this reason.
  Re-run the survey before the reflow commit; join continuation lines in
  anything it finds.
- **`cmark-gfm` and `rumdl` are not installed here.** `rumdl` arrives with the
  dev group. The render diff needs `cmark-gfm` or `markdown-it-py`; if
  neither can be had, the reflow commit is held and reported rather than
  landed unverified.
- **The allowlist ceiling turns the gate red on first growth of a listed
  file** — `docs/design.md` and `corrector.md` among them — until the file is
  trimmed or split; a ceiling is never raised. By design; the first red is
  not a regression.
- **This job routes itself by the rule it writes.** Under today's Phase 0
  text a job containing Items 1.10 and 1.11 is Moderate non-prose and goes to
  `/runbook`. It goes to `/build` on both of D-39's grounds — it edits
  `build/SKILL.md` and `tdd-slice.md`, the files a runbook step would execute
  by, and it needs no phase or decomposition review — and on my human
  partner's instruction. The dependency of 1.2 and 1.10 on 1.7 is what makes
  §4.3 reachable when they run.
