# pilfer-superpowers

Adopt selected superpowers 6.3.0 techniques into the edify workflow pipeline.
Captured from the 2026-08-13 comparison analysis
(`plans/pilfer-superpowers/reports/comparison.md`); this document is the pilfer
inventory, not an implementation commitment — each FR is independently
adoptable and separately triageable by `/design`.

## Requirements

### Functional Requirements

**FR-1: Behavioral-testing methodology for skill wording**
Adopt writing-skills' TDD-for-skills method: pressure scenarios as failing
tests, baseline rationalizations collected verbatim before writing the rule,
wording micro-tested against a no-guidance control (5+ reps, flagged matches
read manually, variance as a metric). This is the missing *method* behind
edify's "(ungrounded — needs calibration)" annotations and the No Confabulation
rule. Acceptance: a documented edify procedure (fragment or skill) exists, and
at least one existing gate's wording has been validated or corrected by it.

**FR-2: Form-matched-to-failure authoring guidance**
Import the design table: rule-skipping under pressure → prohibition +
rationalization table + red flags; wrong-shaped output → positive recipe (never
prohibition — measured to backfire); omitted element → structural REQUIRED slot;
conditional behavior → observable predicate. Include the two measured hard
rules (nuance clauses degrade winning recipes; exemption clauses don't scope).
Acceptance: guidance lands where edify skill/agent authors will hit it
(fragment referenced by skill-authoring work), with provenance noted.

**FR-3: Rationalization armor on discipline-critical gates**
Add rationalization tables and red-flag lists to the gates most exposed to
pressure-driven skipping — candidates: `/inline` Phase 4a review-skip,
test-driver TDD discipline, `/design` tier classification. Constraint: rows
must come from observed violation transcripts (FR-1's method), not invention
(`memory/ddaanet/no-speculative-rules.md`). Acceptance: each armored gate cites
the transcript evidence its rows came from.

**FR-4: Claim→evidence completion gate**
Adopt verification-before-completion's speech-act gating for orchestrator and
inline completion: no success claim without fresh verification output in the
same message; "agent completed" requires the VCS diff, not the agent's report;
regression tests require a verified red-green (revert) cycle. Acceptance: a
fragment loaded by `/orchestrate` and `/inline` completion phases states the
claim→evidence mapping; completion sections reference it.

**FR-5: Bounded fix loop with scoped re-review**
Define what happens when a corrector's fixes fail verification or exceed its
authority, replacing the current single-pass fix-all → UNFIXABLE binary: round
caps, model escalation on late rounds, a re-review contract (per-finding
ADDRESSED/NOT ADDRESSED; new breakage assessed in the fix diff only), and
at-cap adjudication with explicitly parked findings — never silent discard.
Must be reconciled with the fix-all policy in `docs/design.md` §6.4 "Pipeline
contracts" (see Q-3). Acceptance: §6.4 documents the loop; orchestrate/
inline escalation paths reference it.

**FR-6: Rulings ledger**
Log every autonomous judgment call made during orchestration/inline execution
as `Ruling: <what> — <why> — <cost if wrong>`, and surface the collected list
to the user verbatim at completion. Complements (not replaces) RCA pending
tasks in `.claude/handoff-task.md`. Acceptance: `/orchestrate` and `/inline`
completion output includes a "Rulings" section when any were made.

**FR-7: Review-package mechanism**
Add a deterministic script (edify's script culture, superpowers' pattern) that
writes a review package — commit list + `git diff --stat` + `git diff -U10`
over an explicit BASE..HEAD — to a report file handed to reviewers by path.
Record BASE before each dispatch; never derive it as `HEAD~1`. Acceptance:
corrector dispatches in `/orchestrate`/`/inline` pass a package path instead of
having the reviewer gather its own diff.

**FR-8: Reviewer-independence hardening**
Fold into the corrector prompts / `fragments/review-requirement.md`: treat the
executor's report as unverified claims (stated rationales never downgrade
severity); prohibit pre-judging language in dispatch prompts ("do not flag",
"at most Minor"); require file:line evidence for every affirmative check;
adopt the calibrated severity definition (Important = cannot be trusted until
fixed). Acceptance: shared reviewer fragment carries these clauses once;
corrector agents reference rather than restate them.

**FR-9: Interfaces block in runbook format**
**Satisfied 2026-09-01 by `plans/pipeline-simplification/` FR-6.** Runbook
items carry an `Interfaces:` block (one line per method/dataclass/exception/file
contract, full signature and return type) wherever another item consumes their
output — the authoring-side complement to runbook-corrector's
semantic-propagation check, and the only way a context-isolated executor learns
neighbor items' names. Format in
`plugin/skills/runbook/references/runbook-format.md`; `/orchestrate` carries
the block into each dispatch prompt.

**FR-10: No-placeholders authoring rules**
Import the "plan failures" list into the runbook format rules
(`runbook-format.md`): no TBD/TODO, no "add appropriate error
handling"-class vagueness, no "similar to item N" (repeat the content), no
references to names defined in no item. Complements runbook-corrector's
detection-side vacuity criteria with authoring-side prohibition. Acceptance:
the format rules list the prohibitions; runbook-corrector cross-refs them.

**FR-11: Description policy reconciliation and sweep**
Reconcile superpowers SDO with the purpose-first user rule: every edify skill
description = purpose clause, then "Use when" triggers, and **never** a
process/workflow summary (documented superpowers failure: a workflow-summarizing
description caused the workflow to be half-executed). Sweep all edify skill and
agent descriptions for compliance and for stale trigger references (`/plan`,
`plan-adhoc`, `plan-tdd`). Acceptance: all descriptions match the composed
pattern; no dead caller names remain.

**FR-12: Deduplication and token-economy pass**
Single-source the repeated blocks: recall protocol (~8 restatements),
continuation block (×4, `fragments/continuation-passing.md` already exists),
runbook report template (×3), and the ~80%-shared corrector skeleton
(~10,100 words across four agents when measured; the corrector count dropped
by one with `pipeline-simplification` FR-3 on 2026-09-01). These are defects 18–21 in
`reports/edify-defects.md`, parked there for this FR rather than fixed in the
2026-08-13 backlog clearance — the measured-reduction requirement below is why. Set per-class length targets for skill
bodies (superpowers: <200 words frequently-loaded, <500 others — treat as
starting points to calibrate, not established thresholds). Acceptance: each
protocol has exactly one authoritative statement; measured token reduction
reported, not estimated. For the corrector-skeleton dedup specifically
(defect 21, a cross-agent target): each corrector runs in a fresh, isolated
context, so single-sourcing only saves tokens if the shared fragment's Read
is folded into the agent's already-planned initial read batch at dispatch —
an unbundled extra Read call is a net cost, not a reduction. Same-context
dedup targets (recall protocol, continuation block, report template, where
loaded together within one context) aren't affected by this caveat.

**FR-13: Delegate lifecycle gaps to installed superpowers skills**
Wire the pipeline's missing lifecycle stages to the already-installed
superpowers skills instead of rebuilding: branch integration →
`superpowers:finishing-a-development-branch`; root-cause discipline in the
`/orchestrate` remediation ladder → `superpowers:systematic-debugging`;
worktree setup → `superpowers:using-git-worktrees` (already mapped in the
revival). Acceptance: pipeline exit/remediation text names these skills;
subject to Q-1 (dependency direction).

### Non-Functional Requirements

**NFR-1: Preserve edify's structural advantages**
No adoption may weaken artifact traceability, pinned model tiers, independent
test execution between agent hand-offs (RED and GREEN as separate dispatches),
or `/proof` human gates on planning artifacts. Superpowers mechanisms are
additive to structure, not replacements for it. The deterministic-validation
layer is no longer on this list: `plans/pipeline-simplification/` NFR-1
retired it 2026-09-01 (`validate-runbook.py` had nothing downstream to fail
for).

**NFR-2: Provenance on imported heuristics**
Every imported rule carries its evidence class: measured (superpowers
micro-tests, e.g. recipe-vs-prohibition), anecdotal (session cost stories,
e.g. turn-count-beats-token-price), or unvalidated. Anecdotal and unvalidated
imports are marked as such per the No Confabulation rule.

### Constraints

**C-1: No wholesale SDD adoption**
SDD's human-out-of-the-loop stance (no check-ins, controller rulings on plan
defects, single closing surface) conflicts with edify's /proof-gated planning
philosophy. Pilfer its mechanisms (ledger, rulings, caps, re-review), keep
edify's gate placement.

**C-2: No hook-injected compliance kernel**
Superpowers' `<EXTREMELY_IMPORTANT>` SessionStart injection is a salience-
competition device of the kind project CLAUDE.md already rules against, and a
documented silent single point of failure. Compliance content belongs in skill
bodies and fragments.

**C-3: Evidence before compliance prose**
Superpowers' own contributor policy rejects compliance-style rewrites without
eval evidence; edify's no-speculative-rules memory says the same. FR-2/FR-3
imports are gated on FR-1's method existing first.

### Out of Scope

- Implementing any of the above — this document is capture only (the
  originating task was explicitly analysis-only).
- Replacing `/requirements`–`/design` with superpowers' brainstorming/spec flow
  — edify is stronger everywhere the two overlap (artifacts, triage, review).
- Importing superpowers' weaknesses catalogued in the comparison report (no
  requirements artifact, LLM-only validation, TDD-optional execution,
  self-reported rulings audit).
- Cost/token telemetry — absent from both systems; a separate concern.
- Fixing the edify defects surfaced by this read (dead references,
  contradictions, validator gaps — comparison report, final section). Real and
  actionable, but repair work, not pilfering. **Done 2026-08-13** — see
  `reports/edify-defects.md`, except defects 18–21, which are FR-12's.

### Dependencies

- `plans/pilfer-superpowers/reports/comparison.md` — the analysis this document
  argues from; keep with the plan (grounding reports are reusable).
- Superpowers 6.3.0 installed from `superpowers-marketplace` — FR-13 and any
  direct skill chaining depend on it remaining installed (Q-1).
- The simplified pipeline (`plans/pipeline-simplification/`, landed
  2026-09-01) is untested end-to-end; the planned dogfood run will
  re-prioritize this list with observed failure data.

### Open Questions

- Q-1: Dependency direction — invoke installed superpowers skills by name
  (FR-13) vs vendor copies into the edify plugin? edify-cli ships to PyPI with
  no user base; a hard plugin dependency may be acceptable, but distribution
  implications are undecided.
- Q-2: Minimal viable behavioral-test harness for FR-1 — superpowers' evals
  live in a separate repo, take 3–30+ min per scenario, and need an API key.
  What is edify's cheapest faithful version (`claude -p` micro-tests? drill-style
  scenarios in CI?) — needs design-phase research.
- Q-3: Fix-all correctors vs read-only-reviewer + fix-loop split — the two
  systems' models are both coherent and neither is measured. Does FR-5 bolt a
  loop onto fix-all, or trial the split on one gate first?
- Q-4: Which gates earn FR-3 armor — requires violation transcripts to exist;
  which gates have observed (not hypothesized) bypasses?

### References

- `plans/pilfer-superpowers/reports/comparison.md` — full comparison, conflict
  analysis, both weakness lists
- `~/.claude/plugins/cache/superpowers-marketplace/superpowers/6.3.0/` — source
  tree read for this analysis (version-pinned)
- superpowers `skills/writing-skills/persuasion-principles.md` — Meincke et al.
  (2025) N=28,000 compliance study; Cialdini (2021) — evidence base behind FR-2
- `docs/design.md` §6.9 "Prompt and instruction structure" — edify's existing grounded
  prompt research; FR-2 guidance must merge with it, not duplicate it

### Skill Dependencies (for /design)

- Load `plugin-dev:skill-development` before design (skill authoring changes in
  FR-1, FR-2, FR-11, FR-12)
- Load `plugin-dev:agent-development` before design (corrector prompt changes
  in FR-5, FR-8)
