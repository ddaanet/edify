# Review — skill definitions (pipeline-simplification)

Reviewer: `plugin-dev:skill-reviewer` (report-only; Read/Grep/Glob). Fixes
applied in the calling session with Edit, 2026-09-01. Baseline `a4aad0c8`.

## Summary

Critical 0 · Major 3 · Minor 16. Verdict: **accept with fixes** — all 19
applied (status FIXED below). The ten files implement D1, D4–D9, D13 and D15
as written: one runbook stage, live prompt composition from
`dispatch-composition.md`, the four-dispatch slice with the list-revision
step, prose-plus-interfaces beside the item format, pinned model tiers, the
`/proof` gate. No removed name (`prepare-runbook.py`, `validate-runbook.py`,
`assemble-runbook.py`, `split-execution-plan.py`, `verify-red.sh`,
`review-plan`, `runbook-outline`, `tier3-*`, `progress-tracking.md`,
orchestrate's `common-scenarios.md`, `plugin/docs/`) appears in any of them,
and no "Tier 1/2/3", "step file", "cycle", "manifest" or "3-5" survives
(`rg` over the ten files). Every referenced path resolves. The three majors
were one dangling internal section pointer in `/orchestrate`, a `/runbook`
self-check that did not cover the format's own binding rules, and a
`/requirements` exit route that `/runbook`'s prerequisite check would refuse.

## Findings

### 1. plugin/skills/orchestrate/SKILL.md:44 — major — dangling "Section 2.4" pointer
Problem: §2.1 routed non-trivial inline-item review to "Section 2.4 checkpoint form"; there is no §2.4, the checkpoint form is §4 "Phase Boundary".
Fix: `(Section 2.4 checkpoint form)` → `(Section 4 checkpoint form)`.
Status: FIXED

### 2. plugin/skills/runbook/SKILL.md:90-91 — major — self-check omits the format's binding rules
Problem: §3 Self-Check checked `Depends on:` but not the D7/FR-6 rules `runbook-format.md` makes binding (`Requirements:` on every item, `Interfaces:` on cross-item dependencies, `Slices:` on tdd items, no code blocks).
Fix: four bullets added after the inter-item dependencies bullet.
Status: FIXED

### 3. plugin/skills/requirements/SKILL.md:260 — major — exit route `/runbook` refuses
Problem: "Workflow positioning" still offered `/requirements <job> → /runbook plans/<job>/requirements.md`; `/runbook` STOPs without a design-stage artifact and D1 decides runbook-or-not at `/design`.
Fix: line deleted.
Status: FIXED

### 4. plugin/skills/requirements/SKILL.md:64 — minor — stale phase name
Fix: `/runbook Phase 0.5` → `/runbook §1 Recall and Discovery`.
Status: FIXED

### 5. plugin/skills/orchestrate/references/dispatch-composition.md:22-23 — minor — test-driver mode not in the single source
Problem: D2 makes the `RED`/`GREEN` mode line a required element the test-driver refuses without; only `/orchestrate` §2.3 stated it.
Fix: item 6 **Mode** added to §Prompt contents.
Status: FIXED

### 6. dispatch-composition.md:22 — minor — report path has no naming convention
Fix: report path is `plans/<job>/reports/<dispatch name>.md` (the `name` from §Naming).
Status: FIXED

### 7. dispatch-composition.md:43-46 — minor — mechanism and prohibition where an act belongs
Fix: `Agent`-tool `resume`/`max_turns` mechanism sentences replaced by "an unnamed agent cannot be resumed".
Status: FIXED

### 8. plugin/skills/orchestrate/SKILL.md:3 — minor — description is a process summary with no "Use when"
Fix: description rewritten purpose-first with a trigger clause.
Status: FIXED

### 9. plugin/skills/orchestrate/SKILL.md:13 — minor — standing-agent list omits tdd-auditor
Fix: `edify:tdd-auditor` added.
Status: FIXED

### 10. plugin/skills/runbook/SKILL.md:7 — minor — allowed-tools does not cover the body's Bash use
Fix: `Bash(mkdir:*, rg:*, git:*, echo:*|pbcopy)`.
Status: FIXED

### 11. plugin/skills/runbook/SKILL.md:19 — minor — title keeps "steps" vocabulary
Fix: `# Plan Implementation Steps` → `# Write the Runbook`.
Status: FIXED

### 12. plugin/skills/runbook/SKILL.md:30 — minor — `inline-plan.md` accepted as a runbook prerequisite
Problem: `/design` routes `inline-plan.md` to `/inline`, never to `/runbook`.
Fix: prerequisites accept `outline.md` or `design.md` only.
Status: FIXED

### 13. plugin/skills/runbook/references/runbook-format.md:34 — minor — slice identifier undefined
Fix: "Slice k of Item N.M is `N.M/k` — the id `/orchestrate` uses in dispatch names and slice commit subjects."
Status: FIXED

### 14. plugin/skills/design/SKILL.md:17 — minor — Haiku executor premise
Fix: `(Sonnet/Haiku)` → `(sonnet executors, opus reviewers)`.
Status: FIXED

### 15. plugin/skills/design/SKILL.md:21 — minor — two phase types named, format has three
Fix: planning consumer line names tdd / general / inline.
Status: FIXED

### 16. plugin/skills/design/references/design-content-rules.md:33 — minor — "expansion" vocabulary
Fix: `expansion + execution budget` → `planning + execution budget`.
Status: FIXED

### 17. plugin/skills/inline/SKILL.md:88,94,96 — minor — "step" for a dispatch
Fix: "Post-step" → "Post-dispatch" (×2), "After each delegated step" → "After each dispatch".
Status: FIXED

### 18. plugin/skills/inline/SKILL.md:4-7 — minor — description carries a process summary
Fix: description rewritten purpose-first, process tail removed.
Status: FIXED

### 19. plugin/skills/review/references/review-axes.md:40-43 — minor — "step"/"steps" left after line 33 rewire
Fix: "step"/"steps" → "item"/"items" (×3).
Status: FIXED

## Reference resolution

| Path named (in) | Exists |
|---|---|
| `plugin/skills/runbook/references/runbook-format.md` (runbook, design-content-rules, design coupling table) | yes |
| `plugin/skills/orchestrate/references/dispatch-composition.md` (orchestrate, inline) | yes |
| `plugin/skills/orchestrate/scripts/verify-step.sh` (orchestrate §3, §References) | yes |
| `plugin/fragments/review-requirement.md` (orchestrate §2.1, inline 4a) — `### Proportionality` present | yes |
| `plugin/fragments/delegation.md` (orchestrate, dispatch-composition, design-content-rules) — report-to-file, resume-once, recall-by-path present | yes |
| `plugin/fragments/continuation-passing.md` (runbook, orchestrate, inline, design) — `## Consumption Protocol`, `## Error Propagation`, step 2 present | yes |
| `plugin/fragments/escalation-acceptance.md` (orchestrate §5) | yes |
| `plugin/skills/design/references/write-outline.md`, `write-inline-plan.md` (design) | yes |
| `plugin/skills/inline/references/review-dispatch-template.md` (inline 4a) | yes |
| `plugin/bin/triage-feedback.sh` (inline 4b, design, example-execution) | yes |
| `plugin/skills/requirements/references/empirical-grounding.md` (requirements) | yes |
| `agents/learnings.md` (item-review) | yes |
| `docs/design.md` §6.4 "Pipeline contracts" (line 370), T1–T5 table (T5 at 425, before §6.5 at 498); D-32 (479), D-39 (540), D-42 (568) | yes |
| `plugin/agents/{runbook-corrector,runbook-simplifier,outline-corrector,artisan,test-driver,corrector,refactor,tdd-auditor}.md` | yes (all) |
| `runbook-corrector` writes `plans/<job>/reports/runbook-review.md`; `test-driver` refuses a mode-less prompt | confirmed |
| Removed: `plugin/skills/review-plan/`, `plugin/docs/`, `orchestrate/references/progress-tracking.md`, `orchestrate/references/common-scenarios.md`, `plugin/agents/runbook-outline-corrector.md` | absent (as required) |
| `plugin/skills/review/references/common-scenarios.md` (live, different file) | yes, untouched |

## Scope completeness

| Scope IN item | Deliverable found |
|---|---|
| FR-1 one runbook stage, `plans/<job>/runbook.md`, no Tier 2/3 split | `runbook/SKILL.md` frontmatter `outputs`, §2, one-path §Process; `runbook-format.md:3-6` |
| FR-4 compose per item from item + design path + recall path; no preflight, step files, mapping table | `orchestrate/SKILL.md:12-27` ("no preflight"); `dispatch-composition.md` §Prompt contents |
| FR-5 RED → test review → GREEN → code review per slice; list-revision named; no "3-5 cycles" | `orchestrate/SKILL.md` §2.3 (a)–(d), "After the slice" item 2; no checkpoint-interval text |
| FR-6 prose-plus-interfaces, never code, beside item format; one line per contract with signature + return type | `runbook-format.md` §Interfaces blocks (38-42), §Prose plus interfaces (65-70) |
| NFR-1 `/proof` gate on `runbook.md`; pinned tiers (sonnet/opus, artifact-type override, `Model:`) | `runbook/SKILL.md` §7; `dispatch-composition.md` §Model assignment; `runbook-format.md:25-26` |
| C-4 no vestigial names in these files | `rg` over the ten files: none |
| D1 `/inline` never consumes a runbook; delegated path per `dispatch-composition.md` | `inline/SKILL.md:19, 86` |
| D8 process (recall + discovery, write, self-check with ≤8 as signal, commit, corrector, consolidate + simplifier, proof, no-prepend continuation; ≤2,000 words) | `runbook/SKILL.md` §1–§7, §Continuation; 821 words |
| D13 inline items by the orchestrator with the fragment's proportionality; general items one dispatch | `orchestrate/SKILL.md` §2.1, §2.2 |
| D5 gate placement (`verify-step.sh` after (c), (d), general; not (a)/(b)); resume-once → fresh artisan → escalate | `orchestrate/SKILL.md` §3 |
| D4 run summary in context, carried by `/handoff:handoff` | `orchestrate/SKILL.md` §6.3 |
| `/design` T1–T5 pointer; coupling row `runbook-format.md → runbook-corrector` | `design/SKILL.md:163, 173` |
| `design-content-rules.md` live naming pair, integration-first pointer, §6.4 pointer | lines 41, 95, 127 |
| `item-review.md` `## Phase` / `Item N.M:` markers | line 14 |
| `requirements/SKILL.md:252` → `/design plans/<job>/` | line 252 (sibling at 260 was stale — finding 3, fixed) |
| review references stale script name rewired | `example-execution.md:21,42`; `review-axes.md:33` |
| Continuation sections end at `plugin/fragments/continuation-passing.md` | runbook, orchestrate, inline, design — all four |
| §2.3 ↔ `dispatch-composition.md` naming (`item-N-M-s<k>-red` / `-test-review` / `-green` / `-code-review`, `phase-P-corrector`) | consistent; §6 reuses the same ids |
