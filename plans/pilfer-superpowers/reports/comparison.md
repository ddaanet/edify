# Comparison: edify workflow pipeline vs superpowers 6.3.0

Date: 2026-08-13. Sources: full read of `plugin/skills/`, `plugin/agents/`,
`plugin/docs/`, `plugin/bin/prepare-runbook.py`, `plugin/bin/validate-runbook.py`,
`plugin/scripts/create-plan-agent.sh` (edify side) and
`~/.claude/plugins/cache/superpowers-marketplace/superpowers/6.3.0/` — all 14
skills, subagent prompt templates, scripts, hooks, README/CLAUDE.md (superpowers
side). Analysis is exploration-only; no changes were made to either side.

## Architectural contrast

The two systems solve the same problem — making LLM-executed development work
reliable — with opposite center-of-gravity:

- **edify** is an *artifact-gated pipeline*: numbered requirements → triaged
  design → typed runbook → orchestrated execution, with a persisted artifact and
  a review gate at every transformation (`agents/decisions/pipeline-contracts.md`
  T1–T6.5), deterministic Python/shell validators at the structural boundaries,
  model tiers pinned in agent frontmatter, and `/proof` human-validation loops on
  planning artifacts. Quality lives in **structure and mechanical verification**.
- **superpowers** is a *behavioral skill library*: 14 mostly-small skills
  (350–1,400 words core) injected via a SessionStart hook, engineered with
  documented persuasion research (Meincke et al. 2025, Cialdini) — Iron Laws,
  rationalization tables, red-flag lists — and empirically tuned by behavioral
  testing (pressure scenarios, no-guidance controls, 5-rep micro-tests). Its
  execution engine (subagent-driven-development, SDD) is one large skill plus
  three prompt templates and three tiny scripts. Quality lives in **compliance
  engineering and reviewer discipline**.

## What edify does better

1. **Requirements as a first-class artifact.** FR/NFR/C/Q numbering, acceptance
   criteria, traceability matrices in three corrector agents. Superpowers has
   *no* requirements artifact: requirements exist as chat turns until the
   architectural brainstorming path writes a spec, and the only
   requirement→work link is an eyeball pass in writing-plans' self-review.
2. **Complexity triage with a closed feedback loop.** Two-axis Stacey
   classification, persisted `classification.md`, post-hoc verdicts via
   `triage-feedback.sh`. Superpowers' equivalent (spike/bounded/architectural)
   is self-assigned by the agent, ratchets only upward by honor, and two of its
   three paths produce no durable artifact at all.
3. **Deterministic validation.** `prepare-runbook.py` (2,078 lines: parsing,
   splitting, agent composition, recall resolution, file-existence checks),
   `validate-runbook.py` (model-tag policy, create-before-modify lifecycle,
   test-count arithmetic, RED-plausibility), `verify-red.sh`/`verify-step.sh` at
   execution time. Superpowers mechanically validates **nothing** — its three
   scripts are plumbing; every quality judgment is an LLM reading prose. Its
   `task-brief` awk extraction is even a silent-corruption risk on any
   unconventional plan layout.
4. **Model tier as configuration, not advice.** Agent frontmatter models,
   per-phase model resolution, artifact-type opus overrides. SDD's model-selection
   section is well-reasoned prose the controller must re-obey per dispatch, with
   its own warning that an omitted field silently inherits the most expensive
   model. No enforcement, no config surface.
5. **Independent test execution inside the loop.** edify's RED gate
   (`verify-red.sh`) and GREEN gate (`just test` + `verify-step.sh`) run
   mechanically between agent hand-offs. In superpowers, the implementer runs
   tests and writes its own transcript; every reviewer is told *not* to re-run
   the suite; the first independent execution is finishing-a-development-branch
   Step 1 — after every gate has passed. TDD itself is optional inside SDD
   ("following TDD if task says to").
6. **Review of planning artifacts.** outline-corrector, design-corrector,
   runbook-outline-corrector (opus) with coverage matrices, orphan detection,
   growth projection, interface-compatibility checks. Superpowers gives its spec
   and plan — the documents every downstream error inherits from — author
   self-review only ("not a subagent dispatch"), while its reviewer prompt files
   for both sit orphaned in the tree.
7. **Human validation loops on planning artifacts.** `/proof` item-by-item
   review at outline, design, and runbook stages. SDD deliberately designs the
   human out of execution *and* of plan-defect adjudication (controller
   "Rulings"), surfacing decisions only in a closing list.
8. **Memory/recall integration.** Curated recall artifacts flow planning-stage
   context to execution agents (with deterministic per-phase resolution in
   prepare-runbook.py). Superpowers has no memory story at all.

## What superpowers does better

1. **Token economy.** Core skills are 350–1,400 words with explicit targets
   (<200 frequently-loaded, <500 others). edify's pipeline text is ~470KB with
   heavy duplication: the recall protocol restated in ~8 places, the
   continuation block ×4, the runbook report template ×3 verbatim, and four
   corrector agents totaling ~10,100 words that share ~80% of their skeleton.
2. **Empirical behavioral testing of skill wording.** writing-skills treats
   skills as code with TDD: pressure scenarios as failing tests, baseline
   rationalizations collected verbatim, wording micro-tested against a
   no-guidance control (5+ reps, every flagged match read manually, variance as
   a metric), documented regressions (removing one prose section dropped
   test-first behavior 8/10 → 5/10). This is a working answer to edify's
   pervasive "(ungrounded — needs calibration)" annotations and its
   No Confabulation rule — a *method* for grounding behavioral rules where no
   corpus exists.
3. **Match-the-form-to-the-failure design table.** Rule-skipping under pressure
   → prohibition + rationalization table + red flags; wrong-shaped output →
   positive recipe (prohibitions measurably backfired); omitted element →
   structural REQUIRED slot; conditional behavior → observable predicate. Plus
   two measured hard rules: nuance clauses degrade winning recipes; exemption
   clauses don't scope. edify has no equivalent guidance for its own skill/agent
   authoring.
4. **Compliance engineering on discipline gates.** Iron Laws, "violating the
   letter is violating the spirit", rationalization tables built from real
   transcripts, red-flag self-check lists. edify states rules once, plainly —
   e.g. `/inline`'s review-skip gate has justification requirements but no
   counter-rationalization armor, and its known bypass risk is patched
   downstream by a `triage-feedback.sh` warning instead.
5. **Verification-before-completion as a speech-act gate.** Claim→evidence
   mapping (tests pass ⇒ fresh output with 0 failures *in this message*; agent
   completed ⇒ VCS diff, not the agent's report; regression test ⇒ red-green
   verified by reverting the fix). edify gates artifacts mechanically but has no
   rule gating orchestrator/inline *claims* — the "Green is not evidence" memory
   covers adjacent ground but nothing enforces it at completion time.
6. **Bounded fix loops with scoped re-review.** Max 5 rounds per task; rounds
   1–3 resume the implementer, rounds 4–5 escalate to a more capable model with
   honest framing ("a prior implementer attempted this task N times; you own it
   now"); re-review verdicts each finding ADDRESSED/NOT ADDRESSED and flags new
   breakage *in the fix diff only*; at the cap, per-finding adjudication with
   parked/deferred rulings, never silent discard. edify's correctors are
   single-pass fix-all with a binary UNFIXABLE escape — no protocol for the fix
   that fails, no round caps, no re-review contract.
7. **Reviewer independence discipline.** "Do Not Trust the Report" (implementer
   rationales never downgrade severity); no-pre-judging rule for dispatch
   prompts ("if your prompt contains 'do not flag' — stop"); evidence rule
   (file:line for every affirmative answer); calibrated severity definitions
   (Important = "this task cannot be trusted until it is fixed"); read-the-diff-
   once economy. edify's correctors have suppression layers and status
   taxonomies but none of this adversarial framing.
8. **Context-hygiene mechanics.** Review packages (commits + stat + `-U10` diff
   written to a file that never enters the controller's context); per-task BASE
   SHA recorded before dispatch ("never `HEAD~1`, which silently drops all but
   the last commit"); dispatch prompts limited to five enumerated things;
   documented failure anecdotes with costs (a 42k-char dispatch that was 99%
   pasted history). edify has the quiet-execution contract but correctors gather
   their own diffs with no scope-precise base.
9. **Rulings ledger.** Every autonomous decision logged as
   `Ruling: <what> — <why> — <what it costs if wrong>` and surfaced verbatim to
   the human at completion ("a ruling that dies with the workspace was a
   decision made in secret"). edify's orchestrator writes RCA pending tasks but
   has no concept for surfacing judgment calls.
10. **Compaction-resilient progress ledger.** `progress.md` with defined resume
    semantics ("trust the ledger and git log over your own recollection");
    motivated by the observed most-expensive-failure (re-dispatching completed
    task sequences). edify's `session.md` died in the teardown;
    `.claude/handoff-task.md` is coarser.
11. **Plan-format details.** `Interfaces: Consumes/Produces` block (how a
    context-isolated executor learns neighbor tasks' exact names and types — the
    authoring-side complement to edify's semantic-propagation *check*); Global
    Constraints block implicitly included in every task; `Spec:` path traveling
    with the plan; the No-Placeholders "plan failures" list (bans "add
    appropriate error handling", "similar to Task N", types defined in no task).
12. **Lifecycle skills edify simply lacks:** systematic-debugging (4-phase root
    cause discipline, ≥3-failed-fixes architectural circuit breaker),
    receiving-code-review (verify-before-implement, forbidden performative
    agreement), finishing-a-development-branch (integration menu, typed
    `discard` confirmation, merged-result re-test, worktree provenance rules),
    using-git-worktrees (native-tool-first detection, ignore-verification).
    These are installed and already partially wired in (the revival mapped
    `/worktree` → `superpowers:using-git-worktrees`).

## Direct conflicts to reconcile

- **Skill descriptions.** Superpowers SDO: triggers only, *never* summarize the
  workflow (documented failure: a description saying "code review between
  tasks" caused one review where the flowchart specified two). edify user rule
  (`memory/ddaanet/skill-description-purpose-first.md`): purpose first, then
  triggers. These compose: purpose clause ≠ process summary. Resolution: purpose
  + "Use when" triggers, no step/workflow enumeration.
- **Fix-all correctors vs read-only reviewers.** edify merges reviewer and
  fixer (fix-all policy, pipeline-contracts.md); superpowers strictly separates
  them (reviewer is read-only on the checkout; controller never fixes;
  implementer fixes and a re-reviewer verifies). Both are internally coherent;
  which yields better outcomes is unmeasured on both sides.
- **Human-in-the-loop placement.** edify gates planning artifacts through the
  user (`/proof`) and runs execution autonomously; superpowers gates *nothing*
  through the user during SDD except four stop conditions, but gates integration
  (finishing menu) hard. edify should keep its planning gates and can still
  adopt SDD's execution-side mechanisms (ledger, rulings, caps).
- **Instruction philosophy.** Superpowers' own CLAUDE.md states it deliberately
  diverges from Anthropic's published skill guidance and rejects compliance-
  style rewrites without eval evidence — which coincidentally matches edify's
  no-speculative-rules and No Confabulation stances. Any imported rationalization
  table must be built from observed transcripts, not invented.

## Superpowers weaknesses (do not import)

- No requirements artifact, no traceability, no deterministic validation, no
  independent test execution inside the review loop, TDD optional in SDD.
- Compliance rests on a single SessionStart hook (fails silently on Windows
  without bash) and on persuasion pressure that degrades unpredictably against
  competing instructions.
- The no-subagent fallback (executing-plans, 344 words) has no review, no
  ledger, no verification gate — a stub that self-deprecates.
- Model control, budgets, and all cost claims are anecdotal; eval harness lives
  in a separate repo, not runnable by users, not in CI.
- The human is designed out of execution *and* adjudication; "Rulings I made"
  is self-reported by the agent that made them after deleting its workspace.

## edify weaknesses surfaced during this read (independent of pilfering)

Full 33-item list: `plans/pilfer-superpowers/reports/edify-defects.md`. The
load-bearing ones:

- **Dead references:** `scripts/create-plan-agent.sh` resolves a baseline agent
  (`agents/task-execute.md`) that no longer exists — guaranteed failure; the
  `skill-reviewer` and `agent-creator` agents named by `/inline` Phase 4a and
  `fragments/review-requirement.md` exist only in the plugin-dev marketplace
  plugin, not in edify; agent frontmatter declares `skills:
  ["project-conventions"]`/`["error-handling"]` which don't exist as skills;
  `Bash: recall diff` is prescribed at four points but no such command exists;
  `/plan`, `/plan-adhoc`, `/plan-tdd`, `/review-analysis` survive as callers in
  review-plan, runbook-outline-corrector, and tdd-workflow docs.
- **Contradictions:** orchestrator model tier (Sonnet in `/orchestrate`, Haiku
  in both pattern docs, no `model:` frontmatter to settle it);
  `runbook/references/examples.md` demonstrates the exact ImportError-as-RED
  anti-pattern four other components exist to prohibit, and a corrupted
  find-and-replace string ("Use Read/Write/Edit/`rg` (Bash)s") is baked into
  `prepare-runbook.py`'s DEFAULT_TDD_COMMON_CONTEXT and injected into every TDD
  agent lacking a Common Context; `/orchestrate` preflight doesn't check for the
  two TDD corrector agents its own §3.2 dispatches.
- **Verification gaps:** `validate-runbook.py verify-green-paths` exists but is
  absent from the Phase 3.5 invocation list; all validators operate on TDD
  cycles only, so general/inline runbooks pass vacuously while Phase 3.5 is
  called "mandatory for all Tier 3 runbooks"; `triage-feedback.sh`'s behavioral-
  code grep is Python/JS-only.
- **Evidence hygiene:** both pattern docs declare all hypotheses validated from
  a single 3-step execution; the "94% token reduction" figure is derived from
  invented per-step numbers with the author's mid-calculation correction still
  in the file.
