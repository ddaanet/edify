# Skill-review verification — summary, 2026-09-21

Every finding in the eleven per-skill reviews under `plans/skill-reviews/`,
dispositioned against the **working tree** (not HEAD). Per-skill detail and the
exact edit text: `verify-<skill>.md` beside this file.

## Count reconciliation

| | Critical | Major | Minor | Total |
|---|---|---|---|---|
| README tally | 24 | 74 | 91 | 189 |
| Measured here | 24 | 74 | **90** | **188** |

The one discrepancy is `inline.md`, whose Minor section (:23-38) holds **16**
bullets where the README tallies 17. That review carries no self-tally of its
own (unlike `orchestrate.md`, which states "2 critical, 8 major, 9 minor"), so
the README figure looks like a transcription error. Every other skill reconciles
exactly.

## Status × severity, per skill

`f` fixed · `mo` moot · `mi` migrated · `OM` open-mechanical · `OD` open-design
· `D` disputed

| Skill | C: f/mo/mi/OM/OD/D | M: f/mo/mi/OM/OD/D | m: f/mo/mi/OM/OD/D | Σ |
|---|---|---|---|---|
| ground | 0/0/0/0/0/0 | 0/0/0/5/1/0 | 0/0/0/4/3/1 | 14 |
| recall | 2/0/0/0/0/0 | 2/0/0/2/1/0 | 2/0/0/2/0/1 | 12 |
| formalize | 1/0/0/0/2/0 | 0/0/0/4/1/0 | 0/0/0/4/0/1 | 13 |
| proof | 0/0/0/1/1/0 | 1/0/0/6/2/0 | 0/0/0/6/0/0 | 17 |
| design | 1/0/0/0/2/0 | 3/0/0/1/2/0 | 0/1/0/5/1/0 | 16 |
| runbook | 1/1/0/0/0/0 | 0/0/0/6/1/0 | 0/0/0/6/2/0 | 17 |
| requirements | 1/0/0/1/0/0 | 0/1/0/5/0/0 | 0/0/0/9/1/0 | 18 |
| review | 1/0/0/1/0/0 | 0/0/0/8/0/0 | 0/0/0/4/3/0 | 17 |
| deliverable-review | 0/0/0/1/2/0 | 0/0/0/7/0/0 | 0/0/0/8/1/0 | 19 |
| inline | 3/0/0/0/0/0 | 4/0/3/0/0/0 | 7/0/9/0/0/0 | 26 |
| orchestrate | 0/0/2/0/0/0 | 2/0/5/0/1/0 | 5/0/4/0/0/0 | 19 |
| **total** | **10/1/2/4/7/0** | **12/1/8/44/9/0** | **14/1/13/48/11/3** | **188** |

Across all severities: **36 fixed, 3 moot, 23 migrated, 96 open-mechanical, 27
open-design, 3 disputed.**

### What the numbers mean

- **36 fixed** concentrates in `inline` (14) and `orchestrate` (7) — the two
  skills that were rewritten into `/build` — and in `recall` (6), which was
  rewritten this week. Nothing was fixed in `ground` or `deliverable-review`.
- **23 migrated** are all in `inline` and `orchestrate`: the defect travelled
  into `plugin/skills/build/` with the code, usually into
  `references/{phase-boundary,finishing,review-dispatch-template}.md` or into a
  fragment (`delegation.md`, `escalation-acceptance.md`,
  `review-requirement.md`) the successor still reads.
- **96 open-mechanical** is the bulk, and roughly a third of it is one pattern:
  a threshold asserted without the ungrounded marker its sibling documents
  carry, or a claim about a sibling file that the sibling contradicts.
- **3 disputed** are the findings resting on ungrounded rules: ground m9 (a bare
  common word as a weak trigger, with no measurement offered), recall m3 (a
  procedure with a documented override is still one procedure), formalize 11 (a
  self-trigger clause called undetectable where it is the skill's own purpose
  statement). Two further half-findings are disputed inside otherwise-valid
  items: inline m16's `argument-hint` half (no edify skill declares that key, so
  its absence is the convention) and runbook M7's blocking claim (rests on
  `allowed-tools` restricting, which nothing in-repo establishes).

### Cross-cutting items the README raised

| README cross-cutting item | Outcome |
|---|---|
| `AskUserQuestion` mandated by four skills | **Settled by rewrite.** No skill declares it; formalize:46, review:44 and requirements:185 forbid it explicitly with inline numbered prose in its place. formalize 3, requirements C2, review C1, proof M7 all fixed. |
| `docs/` does not ship with the plugin | **Open.** deliverable-review C2 (now citing `docs/references/deliverable-review.md`) and formalize 2 both survive. |
| Bare `/proof` ambiguous across three skills | **Open at six call sites.** proof M1, runbook M9, design (2 sites), requirements, write-outline, write-design. |
| Ungrounded operational thresholds unmarked | **Open in five places.** deliverable-review M2, runbook M5 (×2 files), review m16, formalize 7, design m1 (×2 sites). |
| Progressive disclosure inverted | review M8 open-mechanical; requirements M6 open-mechanical; formalize 8 open-design. |
| Recall contract diverged in three places | proof M4 open-mechanical; requirements m3 open-mechanical; runbook's re-invocation is the same pattern. |
| Skills disagree with their fragments | orchestrate M6 **fixed**; M7 and M8 migrated; recall M5 open-mechanical. |
| Required model stated in prose | requirements m7 and review M7 both open-mechanical. |

### README decisions, as they now stand

1. `AskUserQuestion` — **decided**: rewritten, no exception needed.
2. deliverable-review terminal vs findings routing — **still open**, pending job
   (5).
3. recall's index Read — **decided**: `docs/references/quality-gates.md:37-49`
   (D-48) now makes the index Read conditional (D-85) and the artifact Read the
   anchor; `recall/SKILL.md:62-66` implements it. The design no longer
   self-contradicts. How much of `gitlore:recall` edify still duplicates is the
   surviving half (recall M1).
4. Are `inline` phases real — **decided: no.**
   `docs/references/pipeline-contracts.md:116-121` abolishes the type with the
   `/build` merge (D-34). runbook C2 moot.
5. `/design` → execution commit and baseline ownership — **decided**: `/design`
   commits the artifact and names `/build plans/<job>`; `/build` §2 takes the
   baseline after its own clean-tree gate. inline C1 fixed.

## Line-budget constraint on open-mechanical edits

Five allowlisted `SKILL.md` files sit at **exactly** their recorded ceiling in
`scripts/check_line_limits.allow`, and the allowlist policy only ratchets down —
so any additive edit to them turns the gate red:

| File | Lines = ceiling |
|---|---|
| `plugin/skills/build/SKILL.md` | 218 |
| `plugin/skills/design/SKILL.md` | 285 |
| `plugin/skills/proof/SKILL.md` | 203 |
| `plugin/skills/requirements/SKILL.md` | 357 |
| `plugin/skills/review/SKILL.md` | 231 |
| `plugin/agents/corrector.md` | 682 |
| `plugin/agents/design-corrector.md` | 460 |
| `plugin/agents/outline-corrector.md` | 450 |

Every edit proposed for those files in the per-skill reports is net-zero or
shrinking, or is explicitly paired with a deletion that funds it. Three files
supply the budget: `review/SKILL.md` M8 frees ~81 lines by moving the report
template out; `requirements/SKILL.md` m7 frees 4 and m6 frees 2;
`design/SKILL.md` M3 frees 5 and m2 frees 1. `corrector.md` has no budget at
all, which is why orchestrate M5 is `open-design` rather than mechanical.

## Open-mechanical edits, grouped by target file

Exact old → new text is in the named report. 96 edits across 24 files.

### `plugin/skills/ground/SKILL.md` — verify-ground.md
1 (×4 sites: "Task agent" → the Agent tool, :42/:46/:50/:55) · 2 (:32 "consult
for guidance" → "Read and select by it", plus a process-skill sentence in the
codebase bullet) · 4 (:91 output path gains the `-grounding` suffix) · 5 (:66
names `fragments/delegation.md` §Quiet Execution Pattern) · 7 (:7 drops the
mechanics tail) · 11 (:94-99 moves the grounding label to first position).

### `plugin/skills/ground/references/grounding-criteria.md` — verify-ground.md
6 (:100-101 drops the unsourced "highest-signal" ranking) · 12 (:115 splits the
non-runnable pipeline into three real subcommands) · 14 (adds `memory/MEMORY.md`
to the internal-source list).

### `plugin/skills/recall/SKILL.md` — verify-recall.md
M3 + m4 (:17-18 the blanket "callers do not restate any of this" gains the
sub-agent exception) · M5 (:42-43 "supplied" resolved to paths, against
`delegation.md:118`) · m1 (:74 the 5-entry ceiling labelled arbitrary).

### `plugin/skills/formalize/SKILL.md` — verify-formalize.md
4 + 5 (step 3 gains exit codes and the `budget`/`vacuity_warning` fields) · 6 +
13 (:93-95 repoints at the living design and says what it holds) · 7 (:79-80 the
cap becomes a number, labelled arbitrary) · 9 (:51 adds the icontract import) ·
10 (:21-24 second person → house imperative) · 12 (:13 drops unused `Write`).

### `plugin/skills/proof/SKILL.md` — verify-proof.md *(net-zero)*
C2 (:57, :66 the advertised action list replaced with the real one) · M2 (:4-5
description opens with what the skill does) · M3 (:86 `rg --files` gains `-g`) ·
M4 (:120 recall args gain the plan-dir half) · M5 (:153-154 the guard names its
three exceptions) · M6 (:187 revisit is post-iteration only) · m1 (:118 drops
the dangling FR-3) · m2 (:58 table row covers a recorded verdict) · m3 (:101 the
Checkpoint bullet emits the state line) · m4 (delete :162-166, frees 5 lines).

### `plugin/skills/proof/references/item-review.md` — verify-proof.md
m5 (delete the duplicated verdict list at :64-73) · m6 (single home for
Revisit).

### `plugin/skills/design/SKILL.md` — verify-design.md *(net-zero)*
M3 (delete the drifted coupling table at :261-267, keep the authoritative
pointer; −5) · m2 (delete the maintainer aside at :238; −1) · m5 (:189
"verbatim" → "filled-in").

### `plugin/skills/design/references/design-content-rules.md` — verify-design.md
m1 (:36-38 and :47-48 gain the ungrounded marker their neighbours carry).

### `plugin/skills/design/references/write-outline.md` — verify-design.md
m6 (delete the triplicated recall-diff paragraph at :149-153, point at
`research-protocol.md`) · m7 (:50 routes to a named fragment, not a glob).

### `plugin/skills/design/references/write-design.md` — verify-design.md
m6 (same deletion at :7-16).

### `plugin/skills/runbook/SKILL.md` — verify-runbook.md
M3 (:26-28 the prerequisites anchor names `rg --files plans/<job>`) · M5 (:105
gains the ungrounded marker) · M6 (a type-assignment criterion after :32) · M7
(:119-122 runs `just precommit` and routes the commit) · M8 (:18 usage line
becomes the directory form) · M9 (:141 `/proof` → `/edify:proof`) · m10 (:3 `|`
→ `>-`) · m11 (description gains synonyms and a boundary clause) · m12 (delete
`requires:`/`outputs:` at :8-12) · m14 (stage-1 substeps renumbered a.-e.) · m15
(:16 H1 no longer duplicates :75).

### `plugin/skills/runbook/references/runbook-format.md` — verify-runbook.md
m17 (:66-67 the example stops inlining `Depends on:`, or :17-18 permits it).

### `plugin/agents/runbook-corrector.md` — verify-runbook.md
M5 (:82 gains the ungrounded marker its :85-86 neighbour already has).

### `plugin/skills/requirements/SKILL.md` — verify-requirements.md *(net-zero)*
C1 (step 5 writes the draft before `/proof`; step 6 becomes Finalise) · M2
(three STOP conditions moved beside the guidance they qualify) · M3 (steps 1, 3,
4 open with a tool call — three net-zero rewordings) · M4 (:4 adds `Edit`) · M5
(:133 numbered 2.5; :229-230 recap matches the real headings) · M6 (delete the
last-line route at :357, route inline at :110-112) · m1 (:29 and :125 `rg
--files` → `test -f`) · m2 (:49 states why no plan-dir is passed) · m3 (:136-137
runs the loaded procedure inline) · m5 (:25, :198, :50-53 descriptive →
imperative) · m6 (delete the two duplicate budget statements) · m7 (delete
§Target Model at :14-17; frees 4 lines) · m8 (:264 marks the example report as
inherited) · m9 (:312, :342 "Standalone" → "stop here") · m10 (:3 → block
scalar; apply only if the re-count allows).

### `plugin/skills/review/SKILL.md` — verify-review.md *(net-zero)*
M8 first (move :84-166 to a new `references/report-template.md`; frees ~81
lines) · C2 (:182-183 permits read-only search alongside git) · M3 (:3 gains
trigger phrases and an exclusion) · M4 (:14-15 rewritten against `code-review`)
· M5 (:4 block-sequence form, `Write` added, unused `diff:*` dropped) · M6
(:170-172 output path moves to `tmp/` or the plan's reports dir) · M7 (:214-220
stages gain `/requirements` and lose the model assertions) · M9 (both reference
routes move to their point of need) · M10 (step 2 gains a design-document
branch) · m14 (delete the duplicated field summary at :224-228).

### `plugin/skills/review/references/review-axes.md` — verify-review.md
M10 (:12 states how design-doc availability is established).

### `plugin/skills/review/references/example-execution.md` — verify-review.md
m11 (:3-15 the agent infers scope instead of asking, per the new step 1) · m12
(:39 the volatile dated `scratch/` path removed).

### `plugin/skills/review/references/common-scenarios.md` — verify-review.md
m16 (:24 the 1000-line threshold marked ungrounded).

### `plugin/skills/deliverable-review/SKILL.md` — verify-deliverable-review.md
C1 (delete :96's `run_in_background=true`) · M1 (Phase 4 gains a step reading
and merging the Layer 1 reports; :120-123 reworded to scope the prohibition to
judgement) · M2 + M3 (:81 gate marked an ungrounded starting point and resolved
to churn) · M4 + m8 (:48 pathspec narrowed to `.claude/handoff-*`; type-table
rows for `.claude/rules/*.md` and `docs/`) · M5 (:113 "Fragment convention
compliance" gains a referent or is cut) · M6 (:94 routes through
`fragments/delegation.md`) · M7 (:21-24 gains an `ls` check and a STOP) · m1
(:157 says it extends D-56) · m2 (:94 defines `<type>`) · m3 (template gains a
Sub-reports section) · m4 (:151 Gap Analysis columns match the example) · m7
(:134 names `date -I`) · m9 (:72-73 the "acceptable if justified" excess rule
gains a test).

### `plugin/skills/deliverable-review/references/example-report.md`
*(verify-deliverable-review.md)*

m2 (sub-report names match the `<type>` vocabulary) · m3 (the trailing block
becomes the template's `## Sub-reports`) · m5 (:19-20 approximations → exact
counts).

### Migrated-defect targets — verify-inline.md and verify-orchestrate.md

These are not `open-mechanical` (their finding status is `migrated`), but the
fixes are written up and several overlap. Grouped for whoever actions them:

- `plugin/skills/build/SKILL.md` *(net-zero)* — orch M1+m7 (drop `TaskOutput`
  from `allowed-tools` and from :198), M4 (:131 commits review fixes first),
  M7 (:144 states the override over `escalation-acceptance.md`), m3 (define or
  replace "checkpoint form"), m5 (:53 untracked files are dirt); inline m9 (:93
  sentence fragment).
- `plugin/skills/build/references/phase-boundary.md` — orch C1 (changed-files
  against a recorded phase base), M8 (halt on every field the fragment
  requires), m4 (drop the redundant `verify-step.sh`).
- `plugin/skills/build/references/finishing.md` — inline m10 (:31 scope is the
  baseline diff, not uncommitted changes), m11 (:43 invokes the UNFIXABLE
  validation protocol and re-reviews report-only groups), m12 (commit and verify
  the correctors' fixes before §2), M3 (:54-56 handles the triage warning).
- `plugin/skills/build/references/review-dispatch-template.md` — inline M1+m15
  (one report-path rule, one return contract), M2 (Constraints block; Changed
  files scoped to the group), m6 (delete the duplicated planning-routing
  paragraph), m16 (a slot for the agent-development criteria).
- `plugin/bin/triage-feedback.sh` — inline M3 (exclude `review*.md` from
  `reports_count`).
- `plugin/fragments/delegation.md` — inline m2 (:112-114 the broken
  `git status --porcelain && just lint` compound).
- `plugin/fragments/review-requirement.md` — orch C1 (:125 the inherited bare
  `git diff --name-only`).
- `plugin/fragments/escalation-acceptance.md` — orch M7 (:49-52 scope the rule
  and drop the unconfirmed destructive default).
- `plugin/agents/tdd-auditor.md` — orch M2 (:52-53 and :192-193 the subagent
  transcript fallback).

## Open-design forks, grouped by pending job

### (1) Repo-relative `plugin/…` paths that break from an installed plugin
- **deliverable-review C2** — SKILL.md:64, :135, :173 cite
  `docs/references/deliverable-review.md`, which does not ship. :135 is inside
  the report template, so every consumer's report hardcodes a dead citation.
  Fork: duplicate the axis definitions into `references/methodology.md` against
  the design-graph convention, or have SKILL.md carry them and cite the node as
  provenance only.
- **formalize 2** — SKILL.md:59's bare `edify check` works only in the dev
  checkout. D-12 (`docs/references/cli-and-package.md:98-109`) still records an
  **open gate**: nobody has confirmed `${CLAUDE_PLUGIN_DATA}` substitutes in
  skill content. The probe settles the fix.

### (2) The sweep / review-scoping exit-condition job
No finding falls inside it. Recorded here so the absence is explicit.

### (3) `/proof`'s verdict prompt replaced by conversational verdicts
- **proof C1** — whether `/proof` dispatches a corrector at apply time or the
  three callers stop claiming it. Decides whether the T6 and T1 review gates
  fire on the Moderate non-prose and resumed-design paths. Also disposed as
  **design C2** — one fix, two reports.
- **proof C2** is deliberately *not* filed here: the state line's action list is
  wrong under any vocabulary, so its fix is mechanical and does not conflict.

### (4) Corrector-family dedup (pilfer defect 21)
- **orchestrate M5** — "the corrector never commits" is asserted only by
  `dispatch-composition.md:31-32` and `tdd-slice.md:63`;
  `plugin/agents/corrector.md` carries no prohibition and holds `Bash`. The fix
  belongs inside the agent definition, which sits at its 682-line ceiling, so
  the dedup has to free the lines first.

### (5) Deliverable-review report contract and findings routing
- **deliverable-review C3** — SKILL.md:166-168 ("the skill does not queue
  follow-up work or record lifecycle state") against D-58
  (`docs/references/deliverable-review.md:53-57`, "Every finding resolves to a
  fix or a tracked task. There is no third option") and D-60 (:65-67, "Route
  findings unconditionally to `/design`"). One side is stale; deciding which may
  change Phase 4.

### No pending job — 19 forks

- **design C1** — the Defect route names `structured-bugfix`, which does not
  exist. Build it, or fold Defect into Simple/Moderate/Complex.
- **design M5** — which file owns the A.5 output spec (`write-outline.md` vs
  `research-protocol.md`); the conditional read is currently defeated.
- **design M6** — give `triage-feedback.sh` Moderate and Defect branches (what
  evidence discriminates them is undecided), or say only Simple and Complex are
  checked.
- **design m4** — the A.0/A.2.5/C.4.5 numbering accretion; renumbering breaks
  every inbound cross-reference.
- **formalize 1** — the CLI has no no-contract signal (`vacuity_warning` flags
  any default-budget verified run). Add contract detection to the CLI, reopening
  L1's deferral at `docs/superpowers/design/invariant-guided-verify-loop.md:85`,
  or detect decorator absence in the skill.
- **formalize 8** — whether the budget discipline lands inline or in a new
  `references/` node; same call as whether finding 4 is a requirement.
- **ground M3** — precedence between `grounding-criteria.md`'s two scope
  selectors (:52 question shape vs :122 topic class).
- **ground m8** — what the description should exclude (it has no exclusion
  clause; the reference defines four cases).
- **ground m10** — "design a methodology" overlaps `/design`'s trigger surface.
- **ground m13** — `agents/learnings.md` is cited as a source while 195 lines
  over its own 80-line limit and routing consolidation to the deleted `/codify`.
- **proof M8** — `p:` semantics is cited twice and defined nowhere; establishing
  the handoff plugin's real syntax, or dropping the token.
- **proof M9** — `agents/learnings.md` as a write target from inside a plugin;
  same question as ground m13.
- **recall M1** — how much of `gitlore:recall` edify still carries, now that the
  index-Read question is settled.
- **requirements m4 / runbook m13** — expanding "D+B" at 14 sites across six
  skills, or routing once from a shared fragment.
- **review m13** — whether the report template keeps a mandatory Positive
  Observations section.
- **review m15** — splitting the two runbook-only axes out of `review-axes.md`,
  which loads on every code review.
- **review m17** — whether `/review` gets a recall checkpoint (needs `Skill` in
  `allowed-tools` and a pipeline-level decision).
- **runbook M4 / m16** — whether §3 Self-Check becomes a pointer plus the rules
  `runbook-format.md` does not carry, or the format file becomes the only
  checklist. Two names for the same rule have already drifted.
- **deliverable-review m6** — ✅/❌ in the example report's Gap Analysis; nothing
  in-repo governs table status glyphs.
