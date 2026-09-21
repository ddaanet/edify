# Verification of `plans/skill-reviews/deliverable-review.md` — 2026-09-21

Checked against the working tree: `plugin/skills/deliverable-review/SKILL.md`
(175 lines, unmodified today) and `references/example-report.md` (231).
`docs/design.md` §6.8 is now the split-out node
`docs/references/deliverable-review.md` (67 lines), which carries D-55 to D-60.
Neither deliverable-review file is on `scripts/check_line_limits.allow`;
SKILL.md is 175 against a 200 cap, so small additions are affordable.

Review tally: 3 critical, 7 major, 9 minor = 19 findings. My table carries 19.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | open-mechanical | SKILL.md:96 still "Use `run_in_background=true` for parallel agents." Refuted twice in-repo: `plugin/fragments/escalation-acceptance.md:61-65` ("the spawn tool is `Agent`, and its parameters are `description`, `prompt`… There is no `max_turns`, no `run_in_background`, and no `resume`") and `docs/references/project-configuration.md:88-90` (D-72, same list). The string still appears in `plugin/` exactly twice: this line and the fragment refuting it. |
| C2 | Critical | open-design | The citation moved but not into the plugin: SKILL.md:64, :135 (inside the report template) and :173 now point at `docs/references/deliverable-review.md`. That file exists and holds the operative content — axis definitions at :24-34, the severity rubric at :36-38, the ISO/IEEE sources at :40-46 — but `docs/` still does not ship: the plugin releases from `plugin/`. :135 still writes a citation into every consumer's report that resolves to nothing, which the skill's own broken-references rule would flag as Major. Fork: duplicate the axis definitions into `references/methodology.md` (against the design-graph convention that `docs/references/` owns decisions), or have SKILL.md carry the definitions itself and cite the node only as provenance. |
| C3 | Critical | open-design | Unchanged on both sides. SKILL.md:166-168 still "Report severity counts only. No merge-readiness language … The report is the deliverable; the skill does not queue follow-up work or record lifecycle state." `docs/references/deliverable-review.md:53-57` (D-58) still "Every finding resolves to a fix or a tracked task. There is no third option… "Noted in report" is not a resolution", and :65-67 (D-60) still "Route findings unconditionally to `/design`." Only D-59 (:59-63) survives in the skill. **Pending job (5)** — deliverable-review report contract changes and findings routing. |
| M1 | Major | open-mechanical | Phase 4 (:125-127) is still "Write consolidated report to …" with nothing reading the Layer 1 outputs at `plans/<plan>/reports/deliverable-review-<type>.md` (:94), while :120-123 still says "Layer 2 reads deliverables directly against the design spec, not delegation reports. The two layers are independent." The example still demonstrates the missing merge: findings carry "**Source:** Prose review #12" (example-report.md:~34) and :228-231 lists three sub-reports. |
| M2 | Major | open-mechanical | :81-87 still gates on total lines with three round numbers (<500 skip, 500–2000 two opus agents, >2000 three). `docs/references/deliverable-review.md` (D-55 to D-60) names no threshold, agent count or partitioning rule. The house marking style exists at `docs/references/agent-instructions.md:88` and `docs/design.md:299` (the 20/60/20 split, attributed and qualified). |
| M3 | Major | open-mechanical | Still ambiguous. :48-50 measures churn (`git diff --numstat <range>`); :81 gates on "total deliverable lines from Phase 1 inventory"; `example-report.md:12-19` reads as file length (`cli.py` 370, `merge.py` 290, `__init__.py` 1). `--numstat` is the prescribed instrument, so churn is the reading to fix to. |
| M4 | Major | open-mechanical | :48 still `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude'`. `.claude/rules/*.md` is tracked production content — `design-work.md`, `planning-work.md`, `workflow-work.md` are injected as project instructions in this very session — and `docs/references/project-configuration.md` makes `.claude/rules/` a discovery layer. A plan shipping a new rule file is silently dropped from the inventory. |
| M5 | Major | open-mechanical | :113 still lists "Fragment convention compliance" among the mandatory cross-cutting checks. `plugin/fragments/` holds nine files with no README, index or schema statement, and the phrase appears nowhere else in the repo. Unactionable by the skill's own constraint-precision axis (`docs/references/deliverable-review.md:31-32`). |
| M6 | Major | open-mechanical | :89-94 still specifies what each Layer 1 agent receives and never routes through `plugin/fragments/delegation.md`, unlike `build/SKILL.md:218` and `design/references/design-content-rules.md:187`. Omitted: the quiet-execution return contract (`delegation.md:39-46`), search capability (:79-87 — the skill never says which tools the sub-agents get), and the recall-artifact hand-off (:89-103). |
| M7 | Major | open-mechanical | Half fixed. §Prerequisites (:21-28) now names the fallback — "Take the first that exists: `plans/<plan>/design.md`, else `plans/<plan>/outline.md`" — which closes the agentic-prose gap the reviewer noted. Still missing: any check tool call and any failure behaviour, so with neither artifact present Phase 1 reads a Scope section that does not exist and the conformance baseline is silently empty. `plugin/fragments/prerequisite-validation.md` exists and `.claude/rules/planning-work.md:9` still routes to it; `runbook/SKILL.md:26-28` implements the pattern. |
| m1 | Minor | open-mechanical | :157-162 still adds "unimplemented design requirement" to Critical, "test gap for specified scenario" to Major and "robustness edge case" to Minor, without saying it extends `docs/references/deliverable-review.md:36-38`. The example still exceeds even SKILL.md's rubric: `example-report.md:48` "C4. No precommit failure test" and :55 "C5. No merge idempotency test" are test gaps filed as Critical. Three rubrics across two documents. |
| m2 | Minor | open-mechanical | :94 still writes `deliverable-review-<type>.md` with `<type>` undefined; :86-87 implies `code-test`/`prose-config` at one tier and `code`/`test`/`prose-config` at the other; `example-report.md:229-231` uses `-code`, `-tests`, `-prose`. Three namings. |
| m3 | Minor | open-mechanical | The template (:131-155) still defines six sections; `example-report.md:227-231` still adds a seventh, `**Sub-reports:**`. Rides with M1. |
| m4 | Minor | open-mechanical | :151 still specifies "[Table: design requirement, status (covered/missing), reference]" — three columns; `example-report.md`'s Gap Analysis table has two (`Design Requirement`, `Status`). |
| m5 | Minor | open-mechanical | `example-report.md:19-20` still "`justfile` (wt-* recipes) | ~200" and "`plugin/justfile` | ~20", where `--numstat` returns exact integers. The example is what agents imitate, so the No Estimates rule applies. |
| m6 | Minor | open-design | `example-report.md`'s Gap Analysis still uses ✅/❌. The reviewer classes this as a style call; the house form is `**Anti-pattern:**`/`**Correct pattern:**` for guidance, and nothing in-repo governs table status glyphs. |
| m7 | Minor | open-mechanical | :134 still `**Date:** <date>` with no instruction for obtaining it. |
| m8 | Minor | open-mechanical | Partly covered now: the type table row at :58 reads "Human docs | Fragments, references", which reaches `docs/references/*.md`. Still unnamed: `docs/design.md`, `docs/decisions.md` and `docs/changelog.md`, which the pathspec at :48 does not exclude and a run will surface. |
| m9 | Minor | open-mechanical | All three qualifiers survive: :72-73 "**Excess** in unspecified is acceptable if justified (edge case coverage, defensive tests)", :76 "Layer 1 is optional", :107 "issues delegation cannot catch". Only the first lacks a test — the other two have concrete material immediately following, as the reviewer allowed. |

## Cross-file links

- C1 is the same class as ground finding 1 and orchestrate M1: a skill naming a
  tool or parameter that does not exist, with the correction already written
  down in a fragment the skill does not read.
- C2 is the same class as formalize 2 (a path that works only in the dev
  checkout) and the pending job (1) on repo-relative `plugin/…` references.
- C3 is the same class as formalize 1's living-design half: skill and design
  node disagreeing, with the node the more authoritative side.
- M6 = ground finding 5 = recall M3 in class (the delegation fragment boundary).
- m1 is the same class as design m1 / runbook M5 (ungrounded or drifted criteria
  asserted where a sibling document is authoritative).

## Exact edits for `open-mechanical`

### `plugin/skills/deliverable-review/SKILL.md`

**C1** — delete :96 (`Use `run_in_background=true` for parallel agents.`) and its
preceding blank line. Parallelism comes from issuing the Agent calls in one
message, which :89-90 already implies; state it if the deletion reads as a loss:

- :89 old: `When Layer 1 applies, partition deliverables by type and launch parallel review`
  new: `When Layer 1 applies, partition deliverables by type and launch the review`
  `agents in a single message — that is what makes them parallel.`

**M1** — insert as the first step of Phase 4, before :127:

- new: `1. Where Layer 1 ran, Read each `plans/<plan>/reports/deliverable-review-<type>.md``
  `   it produced and merge its findings into the consolidated set, deduplicating`
  `   against Layer 2's own. Attribute each merged finding to its sub-report.`
  and reword :120-123:
- old: `Layer 2 reads deliverables directly against the design spec, not delegation`
  `reports. The two layers are independent.`
- new: `Layer 2 forms its own judgement by reading deliverables directly against the`
  `design spec, never by reading a delegation report first. The judgements are`
  `independent; Phase 4 merges the findings.`

**M2** — :81:

- old: `Gate on total deliverable lines from Phase 1 inventory:`
- new: `Gate on total changed lines from Phase 1 inventory. The three thresholds below`
  `are an **ungrounded starting point** — no measurement supports them:`

**M3** — :81 (same edit as M2, "changed lines" resolves the ambiguity to churn)
plus `example-report.md` per m5 below, so the inventory column is churn not file
length.

**M4** — :48:

- old: `   `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude'` for per-file`
- new: `   `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude/handoff-*'` for`
  `   per-file`
  and add two rows to the type table after :58:
- new: `| Human docs | Fragments, references, `docs/` | Universal + accuracy, consistency, completeness, usability |`
  `| Configuration | Justfile, pyproject, `.claude/settings.json`, `.claude/rules/*.md` | Universal only |`
  (replacing the existing Human docs and Configuration rows — net zero; this
  also closes m8)

**M5** — :113:

- old: `- Fragment convention compliance`
- new: `- Fragment convention compliance — each `plugin/fragments/` file opens with an`
  `  `## ` heading naming its rule, states the rule before its rationale, and is`
  `  referenced by path from at least one skill`
  (If those are not the actual conventions, cut the bullet instead — asserting
  invented ones would be confabulation.)

**M6** — insert after :94 (the output-report-path bullet):

- new: `Each agent follows `plugin/fragments/delegation.md`: quiet execution (report to`
  `the named file, return the filepath or an error), `Bash` in its tool list for`
  `search, and the recall artifact resolved by path rather than inlined.`

**M7** — :21-24:

- old: `## Prerequisites`
  ``
  `Before starting, gather:`
  `- **Design artifact** — the conformance baseline. Take the first that exists:`
- new: `## Prerequisites`
  ``
  `` `ls plans/<plan>` — branch on what it lists. Neither `design.md` nor ``
  `` `outline.md` present → STOP: there is no conformance baseline, and a review ``
  `without one reports an empty gap analysis as a clean one.`
  ``
  `- **Design artifact** — the conformance baseline. Take the first that exists:`

**m1** — :157:

- old: `**Severity classification:**`
- new: `**Severity classification** — `docs/references/deliverable-review.md:36-38``
  `(D-56) defines the three levels; the parenthetical extensions below are this`
  `skill's, not the node's:`

**m2** — :94:

- old: `- Output report path: `plans/<plan>/reports/deliverable-review-<type>.md``
- new: `` - Output report path: `plans/<plan>/reports/deliverable-review-<type>.md`, ``
  `` `<type>` being `code`, `tests`, `prose` or `config` — one per partition, ``
  `  joined with `-` where a partition covers two`

**m3** — add a seventh section to the template, after :153:

- new: `## Sub-reports`
  `[Paths of every Layer 1 report merged in Phase 4; omit when Layer 1 skipped]`

**m4** — :151:

- old: `[Table: design requirement, status (covered/missing), reference]`
- new: `[Table: design requirement, status (covered/missing) with the finding id]`

**m7** — :134:

- old: `**Date:** <date>`
- new: `` **Date:** <date — from `date -I`> ``

**m9** — :72-73:

- old: `- **Excess** in unspecified is acceptable if justified (edge case coverage,`
  `  defensive tests)`
- new: `- **Excess** in unspecified is acceptable only where the deliverable itself`
  `  states why it exists — an edge case named in a test docstring, a defensive`
  `  branch with a comment. Unexplained excess is a finding.`

### `plugin/skills/deliverable-review/references/example-report.md`

**m5** — :19-20, replace the approximations with exact counts, or drop the two
`justfile` rows if exact numbers are not recoverable; do not leave `~200`.

**m2** — :229-231, rename the three sub-report paths to match SKILL.md's
`<type>` vocabulary once m2's edit lands.

**m3** — the `**Sub-reports:**` block at :227-231 becomes the `## Sub-reports`
section the template now defines.
