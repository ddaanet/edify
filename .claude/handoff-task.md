# Task — 2026-09-17

## Current task

`/build plans/design-routing-and-provenance` — the first exercise of the merged `/build`. Both items are **executed and committed**; the run is at §5 Finish, review gate, with three reviewer dispatches not yet sent.

Baseline for the run: `a533a842` (in `tmp/build-baseline`). Commits landed:

- `a533a842` — 📝 require unsandboxed verify-step.sh in /build (out-of-plan, user-requested mid-run)
- `20f6bdad` — ♻️ collapse /design's duplicated routing block into one node (Item A)
- `6a98c5fb` — ✨ /design artifacts record the base commit their deliverable starts from (Item B)

### What Item A did

New `plugin/skills/design/references/route-to-execution.md` states the routing decision once, asking "does this work need a runbook?". Both call sites — `write-outline.md`'s Outline Sufficiency Gate and `write-design.md` §C.5 — now point at it. Criteria split into preconditions (bind every branch, prose included; failure returns work to design) and runbook discriminators. Dropped the false single-session-capacity criterion and the Exploration branch's `AND design resolved all questions` conjunct. `write-outline.md:185`'s dangling `§Continuation` reference repointed. Inbound refs updated in `design/SKILL.md` (:19, :174-175) and `docs/design.md` (D-35, L-2).

**Exit-condition audit ran** (case-insensitive, phrase + word-level, whole tree). Every remaining hit classified **accurate**: `build/SKILL.md:110` §4.1 "Direct execution" (out of scope by design, different meaning); `build/SKILL.md:5,:35` "execution-ready" (describes what /build accepts, file not in scope); `docs/design.md:604` D-37 "Direct execution" (names the rejected alternative) and `:602` D-36 "direct implementation"; `runbook-corrector.md:112` "Execution Readiness" (runbook *item* readiness, unrelated concept); all `readiness` hits in `write-outline.md` multi-sub-problem section (per-sub-problem readiness level, distinct concept); `write-design.md:53` "Proceed to C.5" (C.5 label retained as a phase id). No dangling `§Continuation` references remain.

### What Item B did

`## Provenance` spec written once in `design-content-rules.md` §Provenance Section (`Derived from:` + `Base:`, with the copy-verbatim inheritance rule). `research-protocol.md` §A.5 content list and `design/SKILL.md:139` (Moderate non-prose route) point at it. `deliverable-review/SKILL.md` Prerequisites now take `design.md` else `outline.md`; Phase 1 step 2 builds the range as `<Base>..HEAD` from Provenance, asking the user only when absent. Both correctors gained a Provenance criterion. `docs/design.md` gained **D-80** in §6.4 and D-55 reworded off its `design.md`-only claim. `docs/changelog.md` has the dated entry.

### Next step

§5 review gate per `plugin/skills/build/references/finishing.md`. Three groups over `git diff --name-only a533a842`, dispatched sequentially (this box will not take parallel heavy work):

1. **Skill definitions** → `plugin-dev:skill-reviewer`, **§Report-only variant** of `references/review-dispatch-template.md` (Read/Grep/Glob only — it cannot write or fix; ask for parts under 4000 chars with `CONTINUED` / `END OF REPORT` markers; this session writes the report and applies fixes). Files: `plugin/skills/design/SKILL.md`, `plugin/skills/design/references/{write-outline,write-design,route-to-execution,design-content-rules,research-protocol}.md`, `plugin/skills/deliverable-review/SKILL.md`. Report → `plans/design-routing-and-provenance/reports/review-skills.md`.
2. **Agent definitions** → `edify:corrector`, criteria from `plugin-dev:agent-development` named in the prompt. Files: `plugin/agents/{outline,design}-corrector.md`. Report → `reports/review-agents.md`.
3. **Human docs** → `edify:corrector`. Files: `docs/design.md`, `docs/changelog.md`. Not `design-corrector`: that agent's criteria target a plan `design.md`, not the living design record.

Then structural-proof Read of each report, grep UNFIXABLE, `plugin/bin/triage-feedback.sh design-routing-and-provenance "$(cat tmp/build-baseline)"`, and the run summary naming `/deliverable-review plans/design-routing-and-provenance` (opus, fresh session) as the follow-up.

### Operational note for this run

`plugin/skills/build/scripts/verify-step.sh` and `just precommit` must run with `dangerouslyDisableSandbox: true`. Sandboxed, `git status` invents untracked `.claude/` phantoms (`launch.json`, `loop.md`, `output-styles/`, `routines/`, `workflows/`) and the gate returns a false `DIRTY`. This is now documented in `build/SKILL.md` §2 and `references/phase-boundary.md`.
