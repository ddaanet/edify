# Deliverable Review (Layer 1, docs + config): pipeline-simplification

**Date:** 2026-09-02
**Range:** `f3f1015b..HEAD` (`993b23b7`). Whole current files reviewed, not
only the diff. Baseline: `requirements.md` (FR-1..7, NFR-1..2, C-1..5),
`outline.md` (D1–D11, D13–D15).

## Inventory

| File | Lines | Type |
|---|---|---|
| `docs/design.md` | 1028 | human documentation |
| `docs/changelog.md` | 147 | human documentation |
| `CLAUDE.md` | 213 | configuration / agentic prose |
| `README.md` | 73 | human documentation |
| `plugin/README.md` | 80 | human documentation |
| `.claude/rules/workflow-work.md` | 8 | configuration |
| `agents/learnings.md` | 195 | human documentation |
| `plugin/fragments/delegation.md` | 87 | agentic prose |
| `plugin/fragments/continuation-passing.md` | 164 | agentic prose |
| `plugin/fragments/escalation-acceptance.md` | 57 | agentic prose |
| `plugin/fragments/execution-routing.md` | 41 | agentic prose |
| `plugin/fragments/review-requirement.md` | 176 | agentic prose |
| `plugin/fragments/workflows-terminology.md` | 27 | agentic prose |
| `plans/pilfer-superpowers/requirements.md` | 229 | human documentation |
| `memory/workflow-pipeline-revival.md` | 31 | human documentation |
| `memory/MEMORY.md` (one line) | — | human documentation |

## Critical Findings

**C1. `plugin/fragments/continuation-passing.md:7-13, 79, 89` — the
continuation hook does not exist.** The fragment opens with "a hook-based
system": "Hook parses multi-skill input, injects continuation via
`additionalContext`", and Transport Format states "**First invocation** (hook →
skill): JSON `additionalContext` with `[CONTINUATION-PASSING]` marker".
`plugin/hooks/hooks.json` registers exactly one hook, `SessionStart` →
`bootstrap-venv.sh` (design.md §5.4 says the same). `.claude/settings.json`
registers no hooks. `rg` for `CONTINUATION-PASSING` across the repo hits only
this fragment. A skill following the documented first-invocation path waits for
context that is never injected; only the skill-args transport is real.
*Pre-existing and outside D10/D11's contract* — no requirement in this plan
touched it, and it was equally false at `f3f1015b`. Flagged because the brief
scopes the whole file and the axis is accuracy.

## Major Findings

**M1. `docs/design.md:992` (L-5) — the stated size of `memory/MEMORY.md` is
stale.** "At ~28.9 KB against a 24.4 KB limit". Measured now: 32,420 bytes
(31.7 KiB, 32.4 kB). The figure dates from `52cb1c78`. §1 "Next" pins the
consolidation task to this limitation, so the number is load-bearing for
prioritisation, and NFR-2 requires measured data.

**M2. `plugin/README.md:72-73` — wrong gate condition for `verify-step.sh`.**
"the clean-tree and precommit gate `/orchestrate` runs after each dispatch."
Design D5 and `docs/design.md:157-160` both say it runs after every
*committing* dispatch and "never after a RED whose tests are uncommitted by
design"; `plugin/skills/orchestrate/SKILL.md:96-97` says "After GREEN (c), code
review (d), and any general item — not after (a)/(b)". Three-way inconsistency;
a reader of the README would gate after RED and fail on the uncommitted tests
that are the designed state.

**M3. `plugin/fragments/execution-routing.md:5` — `Session.md` is a retired
artifact.** "Check loaded context — Session.md, @-referenced files, and prior
conversation are already available." `docs/design.md:414-417` records the
`session.md` era as retired (2026-08-27) and
`plugin/fragments/workflows-terminology.md:7` names `.claude/handoff-task.md`
as the task frame. Pre-existing, not introduced by this plan.

**M4. `plugin/fragments/execution-routing.md:17` and
`continuation-passing.md:89` — the `Task` tool does not exist.** "Parallel
independent tasks (multiple Task calls)" and "Skills construct Task prompts
explicitly". `docs/design.md:825-826` (D-72) states flatly "there is no `Task`
tool at any level", and D-28 (`:446`) repeats it while recording both halves of
the old capability claim as measured false on 2026-08-10. The spawn tool is
`Agent`. Pre-existing.

**M5. Broken decision cross-references in two fragments.**
`escalation-acceptance.md:24` reads "**Rollback protocol (D-5):**" — D-5 in
`docs/design.md:221` is "One responsibility per error-handling layer".
`continuation-passing.md:111` reads "When a skill fails during a CPS chain
(D-1)" — D-1 at `docs/design.md:187` is "Two output conventions, split by
consumer". Both look like surviving `agents/decisions/`-era numbering; since
the 2026-08-14 fold, a bare `D-N` reads as a `docs/design.md` decision.
Pre-existing.

## Minor Findings

**Accuracy**

- `docs/design.md:7` — "**Verified against:** `06a431ec`" is stale: the file
  was edited afterwards in `6facc2ea` (task 9). The stamp claims verification
  at a commit that predates the doc's own latest content.
- `plugin/README.md:63` — "Utility scripts in `bin/` (Python 3)" heads a table
  whose first and last rows (`bootstrap-venv.sh`, `triage-feedback.sh`) are
  POSIX shell. Pre-existing.
- `plugin/fragments/continuation-passing.md:107` — "Six cooperative skills
  chain via tail-calls". Four skills declare `cooperative: true` (`design`,
  `runbook`, `inline`, `orchestrate`); the table below lists seven rows, three
  of them terminal external skills. Already wrong at `f3f1015b`, so not a
  regression from deleting `/review-plan`.
- `memory/workflow-pipeline-revival.md:28-31` — points at `docs/design.md` §7
  for the 2026-09 retirements of `runbook-outline.md` and
  `runbook-outline-corrector`. §7 names the two-stage model, step files and
  `validate-runbook.py`, not those two names; `docs/changelog.md` (the other
  pointer given) does carry them. The pointer is not wrong enough to mislead,
  but §7 alone does not answer it.

**Completeness / consistency**

- `docs/design.md:135-136` — "a skills bundle plus standing agents plus one
  verification script" names only `verify-step.sh`, while D-26 T5
  (`docs/design.md:429`) makes `triage-feedback.sh` half of the inline gate.
  §5.3 undercounts the pipeline's scripts by one.
- `docs/design.md:421-430` (D-26) — the table claims "Every transformation has
  a typed review gate" but has no row for design → design outline, gated by
  `outline-corrector`, which §5.3 lists as a standing agent. Pre-existing (the
  old T1–T6.5 table had no such row either); the renumbering did not introduce
  it.
- `plugin/fragments/escalation-acceptance.md:3, 8, 20, 26, 28, 31, 35, 37` —
  uses "step" as the unit of work throughout, after
  `workflows-terminology.md:24-25` dropped **Step** from the terminology table
  and defined **Item** and **Slice**. D10 does not list bare "step" in the
  removed vocabulary, and `verify-step.sh` keeps the word in its name, so this
  is a consistency nit rather than a sweep miss.
- `plugin/fragments/review-requirement.md:41` — routes agent-definition review
  to `plugin-dev:agent-creator`, a creator rather than a reviewer (the sibling
  row correctly uses `plugin-dev:skill-reviewer`). Pre-existing, untouched by
  this plan.

**Excess / housekeeping**

- `plugin/scripts/` survives on disk as an otherwise-empty directory holding
  `__pycache__/split-execution-plan.cpython-314.pyc`, the compiled form of a
  file D10 deleted. Untracked, so `git status` is clean and C-4's
  no-vestigial rule is formally satisfied; worth deleting anyway.
- `agents/learnings.md` — the change set is three lines, not the two D10
  scoped: line 41 and line 126 were reworded as specified, and the
  `triage-feedback.sh plans/<job>` correction note at old line 66 was deleted.
  The deletion is justified — `plugin/skills/inline/SKILL.md:150` now invokes
  `triage-feedback.sh <job>`, so the note it corrected no longer applies — but
  it is outside the stated scope.

**Vacuity, excess (universal axes):** nothing further. No file in this set
carries ceremony or unspecified content beyond the housekeeping items above.

**Usability:** no findings. The rewritten §5.3, D-26 and the changelog entry
each read standalone.

## Vocabulary sweep

`rg` over the repo excluding `.git`, `plans/`, `tmp/`, `.claude/handoff-*`,
`docs/changelog.md`, `docs/superpowers/`, and `memory/` except
`workflow-pipeline-revival.md`. Patterns with zero hits are grouped at the end.

| Pattern | Surviving hits | Disposition |
|---|---|---|
| `step file` | `docs/design.md:26, 389, 909`; `CLAUDE.md:192` | Legitimate — all past tense or explicit rejection (§1 "were the weak-orchestrator premise", D-24 "from 2026-08-13 to 2026-09-01", §7 title, CLAUDE.md "were dropped in 2026-09") |
| `steps/` | `agents/learnings.md:102-103` | Legitimate — undated incident log describing a past worktree failure; D10 scopes learnings.md to two reworded lines |
| `step artifacts` | `docs/design.md:71` | Legitimate — names the dropped FR-19 so the retired ID is not reused |
| `prepare-runbook` | `docs/design.md:394, 972` | Legitimate — D-24's history sentence and L-1's closure note |
| `validate-runbook` | `docs/design.md:933` | Legitimate — §7 rejected alternative |
| `common-scenarios` | `plugin/skills/review/SKILL.md:178` | Legitimate — `plugin/skills/review/references/common-scenarios.md` exists; D10 deletes only `orchestrate/references/common-scenarios.md`, which is gone |
| `cycle` (TDD sense) | `agents/learnings.md:109, 114` ("cycles 4.2, 4.3, 4.7", "Cycle 4.3"); `plugin/agents/tdd-auditor.md:33` | Legitimate — learnings.md is a dated evidence log; tdd-auditor's mention is the negative ("not a planned-vs-executed cycle count") |
| `cycle` (other senses) | `plugin/fragments/prerequisite-validation.md:18, 227`; `plugin/skills/ground/references/grounding-criteria.md:88`; `plugin/skills/design/references/write-design.md:21`; `CLAUDE.md:164`; `docs/design.md:485, 564, 917` | Legitimate — escalation cycles, correction cycles, review cycle, dependency cycles, and the §7/D-31 grounding incident |
| `manifest` | `docs/design.md:246`; `plugin/README.md:68` | Legitimate — plugin/marketplace sense, exactly the exclusion D10 states |
| `Tier 1/2/3`, `three-tier` | `docs/design.md:25, 518` | Legitimate — both past tense ("retired the three-tier structure", "*Supersedes* (2026-09-01) the three-tier structure") |
| `assemble-runbook`, `split-execution-plan`, `verify-red`, `review-plan`, `runbook-outline`, `runbook-phase`, `orchestrator-plan`, `common-context`, `tier3`, `3-5 cycles`, `progress-tracking`, `tdd-workflow.md`, `general-workflow.md`, `plugin/docs`, `hooks-tester`, `orchestrator manifest` | none | Clean |

Only `workflow-pipeline-revival.md:28-29` matches inside `memory/`, and there
the names appear as the stale-name → live-name map the file exists to provide.
`.claude/loop.md`, `.claude/routines`, `.claude/workflows`, `.claude/launch.json`
and `.claude/output-styles` are unreadable in this sandbox and untracked by git,
so they are outside the corpus.

Live stale references found outside the sweep patterns are M3 (`Session.md`)
and M4 (`Task` tool).

## Design conformance

| D11 / D10 item | Status | Reference |
|---|---|---|
| §1 Now, status layer + do-not-re-litigate | covered | `docs/design.md:13-26` |
| §3.2 FR-9/10/11/12 reworded; no "Tier 1/2" | covered | `:60-67` |
| FR-19 / FR-20 dropped, IDs not reused | covered | `:70-72` |
| §5.3 rewritten | covered (see Minor: script count) | `:133-163` |
| D-24 mechanism → composed prompts, principle survives | covered | `:376-405` |
| D-25 tier clause dropped, context-budget ground only | covered | `:406-419` |
| D-26 renumbered T1–T5, `runbook-corrector` at T2 | covered | `:421-430` |
| D-30 type determines format / criteria / dispatch | covered | `:468-478` |
| D-31 superseding pointer, incident moved to §7 | covered | `:482-487` |
| D-32 keeps 2×2 + opus, paired fix now prose+interfaces | covered | `:489-499` |
| D-33 consolidation before `/proof`, economics gone | covered | `:501-508` |
| D-34 two routes, boundary at `/design` C.5 | covered | `:510-525` |
| D-35 "tier" → "route" | covered | `:527-532` |
| D-39 "per cycle" → "per slice" | covered | `:554` |
| D-42 no stale claim | covered | `:578-584` |
| D-49 example → `verify-step.sh` vs `corrector` | covered | `:649-653` |
| D-51 intact | covered | `:663` |
| D-69 "react per slice" | covered | `:810` |
| §6.3 "instead of a slice of their own" | covered | `:365` |
| L-1 deleted, ID not reused | covered | `:972-973` |
| L-2 tier numbers and "3-5 cycles" gone | covered | `:975-981` |
| L-5 present | partial — figure stale (M1) | `:992` |
| L-6 reworded, unvalidated claims labelled | covered | `:996-1004` |
| §7 four additions (two-stage, per-test, RED-less batching, validator) | covered | `:909-940` |
| `docs/changelog.md` entry dated at landing | covered | `docs/changelog.md:14-45`; the 7,029-line / 97,724-token figure matches `reports/measurements.md` |
| FR-7 acceptance: no present-tense step files / manifest / expansion / per-cycle / `validate-runbook.py` | covered | every surviving mention is past tense or a §7 rejection |
| D10 `CLAUDE.md` four regions (`:57`, `:178`, `:183-184`, `:187-190`) | covered | `CLAUDE.md:57, 178-192` |
| D10 `README.md` rows | covered | `README.md:41-43` |
| D10 `plugin/README.md` rows; live skills/agents match `ls` | covered (see M2 for the script note) | 11 skills, 11 agents, both match the tree |
| D10 `.claude/rules/workflow-work.md` repointed | covered | §6.4 "Pipeline contracts" and §6.5 "Execution routing" both exist by title |
| D10 `agents/learnings.md` two lines reworded | covered, plus one extra deletion | `agents/learnings.md:41, 125` |
| D1 `delegation.md` keeps report-to-file, resume-once, recall-by-reference; loses step-file dispatch | covered | `plugin/fragments/delegation.md:22-24` (Prompt Composition, cites `dispatch-composition.md`), `:26-38` (quiet execution), `:40-50` (resume once), `:83-87` (recall by path) |
| `workflows-terminology.md`, `execution-routing.md`, `escalation-acceptance.md`, `continuation-passing.md` reworded | covered | see the diff regions; residual issues are M3–M5 and the Minor consistency item |
| Pilfer FR-9 satisfied here, FR-10 reworded, FR-12 defect 21 shrinks, NFR-1/2 inherited, dependency updated | covered | `plans/pilfer-superpowers/requirements.md:82-89` (FR-9), `:92-100` (FR-10), `:112-113` (FR-12), `:138-146` (NFR-1), `:193-195` (Dependencies) |
| `memory/workflow-pipeline-revival.md`: present tense, stale→live map, no commit ids, no "never run end-to-end" caveat | covered | file rewritten; validation status delegated to `docs/design.md` L-6 |
| `memory/MEMORY.md` index line rewritten as a trigger line | covered | index line now lists the stale names it routes |

No D11 or D10 item is missing.

## Summary

| Severity | Count |
|---|---|
| Critical | 1 |
| Major | 5 |
| Minor | 9 |

Of these, 1 Critical, 3 Major (M3, M4, M5) and 5 Minor are pre-existing
conditions that predate `f3f1015b` and fall outside D10/D11's stated contract.
