# Outline: Inline Execution Lifecycle Skill

## Naming Decision

**Decision: `/inline`**

Discoverability-first: `/inline` pairs with `/orchestrate` in the picker — user immediately grasps the tier relationship (inline execution vs orchestrated execution). Transparent about mechanism (the execution mode) rather than metaphorical.

Brainstorm-name agent evaluated 11 verb-oriented candidates; user's initial take `/inline` was superior on primary criterion. `/fulfill` was strongest on secondary criterion (edify harmony, Latinate -fy form) but metaphorical indirection hurts discoverability.

Rejected: `/execute` (collides with `x`/#execute), `/fulfill` (metaphorical, less transparent), `/implement` (no lifecycle connotation), `/deliver` (proximity to `/deliverable-review`).

**No dedicated shortcut.** `x` (#execute) already handles "do the next thing" — the skill is invoked explicitly (`/inline plans/<job>`) or by callers (/design, /runbook).

## Approach

Create a lifecycle wrapper skill (`/inline`) that sequences: pre-work → execute → post-work. Replaces ad-hoc inline execution scattered across /design Phase B/C.5 and /runbook Tier 1 with a single invocation point.

The skill does NOT prescribe how to implement (that's the caller's responsibility based on design). It provides the lifecycle envelope: context loading, corrector dispatch, evidence collection, triage feedback, deliverable-review chaining.

## Workflow Sequence

### Phase 1: Entry

- **Entry gate:** Verify `git status --porcelain` clean and `just precommit` green. Dirty tree or failing precommit → stop, surface to user. Ensures execution starts from a known-good baseline.
- Capture baseline: `BASELINE=$(git rev-parse HEAD)` — before any edits (FR-5 baseline)
- Detect entry point: `execute` in args → chained invocation (skip Phase 2); absent → cold start (full workflow)

### Phase 2: Pre-work (cold start only) [FR-2]

- Run `agent-core/bin/task-context.sh '<task-name>'` to recover origin session
- Read `plans/<job>/brief.md` if present (cross-tree context)
- Read `plans/<job>/recall-artifact.md` if present; batch-resolve via `when-resolve.py`
- If no recall artifact: lightweight recall (read memory-index, resolve domain-relevant entries)

Skipped when entry point is `execute` — caller (/design or /runbook) has already loaded all context.

### Phase 3: Execute [FR-3]

- Perform implementation (edits, TDD cycles for behavioral code, prose changes)
- Skill provides lifecycle wrapper only — execution approach comes from caller's design/plan
- Covers both Tier 1 (direct) and Tier 2 (delegated) execution — same lifecycle, different scale

**Delegation protocol** (when execution dispatches sub-agents):
- **Direct execution:** No delegation — edits performed in current session
- **Delegated execution** (artisan, test-driver):
  - Prepare sub-agent recall artifact: curated subset of plan recall-artifact entries relevant to delegation target. Separate artifact per delegation, not section-aware resolution.
  - Piecemeal dispatch for TDD: one cycle per invocation, resume same agent between cycles, fresh agent when context nears 150k
  - Context isolation: parent does cognitive work (selecting entries, curating context), child does mechanical work (resolving entries, executing). Sub-agents have no parent context.
  - test-driver commit contract: test-driver commits each cycle for audit trail. Caller does not add commit instructions. Expect clean tree on resume.
  - Post-step verification: `git status --porcelain` clean + `just lint` after each delegated step
  - Design constraints non-negotiable: when design specifies explicit classifications, include LITERALLY in delegation prompt. Agents apply design rules, not invent alternatives.
  - Artifact-type model override: opus for edits to skills/fragments/agents/design documents regardless of task complexity.

**No mid-execution checkpoints.** Deliberate omission — corrector (Phase 4a) is the sole semantic review point. Post-step lint catches mechanical issues. Triage feedback (Phase 4b) collects uninterrupted execution data for future threshold calibration. Revisit after 10+ Tier 2 executions show whether compounding drift is a real problem at this scale.

### Phase 4: Post-work

- **4a: Corrector dispatch** [FR-4] — delegate to corrector agent with standardized template (D-4). Corrector reviews implementation changes only (not planning/design artifacts per corrector agent design). Report → `plans/<job>/reports/review.md`
- **4b: Evidence + triage feedback** [FR-5, FR-6, FR-7] — run `agent-core/bin/triage-feedback.sh <job-dir> $BASELINE`. Script collects evidence, compares against classification.md, appends to log. Surface inline message on divergence only.
- **4c: Deliverable-review chain** [FR-8] — invoke `/handoff [CONTINUATION: /commit]` with `/deliverable-review plans/<job>` as pending task for next session

### Overhead budget [NFR-1]

Chained path adds vs current pattern: ~3-4 tool calls (1 Bash for triage-feedback.sh, 1 Task for corrector, 1 Read for script output, 1 skill invocation for handoff). Pre-work is zero additional calls when chaining.

## Key Decisions

### D-1: Named entry points (not --flags)

Skill workflow has named entry points matching its phases. Callers target a specific entry point via natural-language args instead of CLI-style flags.

| Entry point | Meaning | Caller |
|-------------|---------|--------|
| (default) | Full workflow: pre-work → execute → post-work | Cold start from session.md |
| `execute` | Skip pre-work, enter at execute phase | /design, /runbook (context loaded) |

/design invokes: `Skill(skill: "inline", args: "plans/<job> execute")`. Cold start: `Skill(skill: "inline", args: "plans/<job>")`. Continuation-compatible: `[CONTINUATION: /inline plans/<job> execute]`.

**Rejected:** `--chain` flag (CLI convention in prose context — unnatural per "when parsing cli flags as tokens"). File mtime detection (fragile). Conversation introspection (unavailable).

**Why named entry points:** Natural in prose-parsed args. Generalizes to any workflow phase. Continuation-compatible. Self-documenting — the entry point name IS the phase name.

### D-2: Evidence collection and triage comparison as single script

`agent-core/bin/triage-feedback.sh` — mechanical script handling both FR-5 (evidence collection) and FR-6 (comparison). Per "when choosing script vs agent judgment": all three evidence signals (git diff stat, report file count, behavioral code grep) and the comparison heuristics (pattern matching rules) are deterministic. No agent judgment needed.

Divergence heuristics in the script are initial estimates (C-3). The feedback loop itself reveals whether they need refinement — the triage-feedback-log.md provides the data for future calibration.

**Script interface:**
- Input: `triage-feedback.sh <job-dir> <baseline-commit>`
- Output: Structured text — evidence block + verdict (match / overclassified / underclassified / no-classification)
- Also appends to `plans/reports/triage-feedback-log.md` (FR-7)

**Baseline commit:** Captured via `git rev-parse HEAD` at skill entry, before any edits. Stored in local variable, passed to script.

### D-3: Classification persistence in /design Phase 0

FR-1 adds a Write step after the visible classification output block in /design Phase 0. Content = the classification block verbatim. Target = `plans/<job>/classification.md`. This is a /design change, not a /inline change — the new skill only reads this file.

### D-4: Single corrector template

One corrector dispatch pattern used everywhere (NFR-3). Template:

```
Corrector dispatch:
- Scope: uncommitted changes (git diff against baseline) — implementation changes only
- Design context: from plans/<job>/outline.md (design spec, not requirements.md — requirements are upstream abstractions)
- Recall context: review-relevant entries from plans/<job>/recall-artifact.md (if absent: lightweight recall fallback per "when recall-artifact is absent during review")
- Report: plans/<job>/reports/review.md
- Scope IN/OUT: from design or outline
- Constraint: corrector agent reviews implementation, not planning artifacts
  (planning artifacts → runbook-corrector per pipeline contracts)
```

When `/inline execute` follows /design, the baseline captured at skill entry excludes design-phase artifacts from corrector scope (only execution edits are uncommitted).

Replaces the 3+ ad-hoc corrector invocations currently in /design Phase B, /design Phase C.5, and /runbook Tier 1.

### D-5: Deliverable-review chaining via handoff continuation

FR-8: After post-work, the skill invokes `/handoff [CONTINUATION: /commit]`. The handoff writes `/deliverable-review plans/<job>` as a pending task in session.md for the next session.

**Why not chain directly to deliverable-review?** Deliverable-review benefits from a fresh session (clean context, no implementation-phase bias). The /commit + session break enforces this naturally.

### D-6: Skill structure

```
agent-core/skills/inline/
├── SKILL.md              (~1500 words — core workflow)
└── references/
    └── corrector-template.md  (full corrector dispatch template with examples)
```

Scripts live in `agent-core/bin/` (project convention — scripts are project-level, not skill-scoped):
- `agent-core/bin/triage-feedback.sh` — evidence + comparison + log append

SKILL.md is lean: workflow phases (pre-work, execute, post-work) with decision references. Corrector template detail in references/ to keep body under 2000 words.

**Continuation protocol** (per "how chain multiple skills together"):
- Frontmatter: `continuation: cooperative: true`, `default-exit: ["/handoff --commit", "/commit"]`
- `Skill` in `allowed-tools` (needed for tail-call)
- Consumption section at end of SKILL.md — peel-first-pass-remainder protocol
- Task tool prompts exclude continuation metadata

## Open Questions (Resolved)

- **Q-1 (git baseline):** `git rev-parse HEAD` at entry. Passed to evidence script. ✓
- **Q-2 (skill name):** `/inline` — no dedicated shortcut (`x` suffices). ✓
- **Q-3 (batch retrospective):** Deferred per requirements (out of scope). Can be built later using triage-feedback-log.md as input. ✓

## Scope

### IN

- New skill: `/inline` (SKILL.md + references/corrector-template.md)
- New script: `agent-core/bin/triage-feedback.sh` (evidence + comparison + log)
- /design modifications: FR-1 (classification persistence Write step in Phase 0), FR-9 (Phase B/C.5 route to /inline)
- /runbook modifications: FR-10 (Tier 1 route to /inline)
- Pipeline contracts update: add T6.5 transformation (inline lifecycle)
- Execute-rule.md: no shortcut needed (`x` is sufficient)
- Memory-index: entries for new skill decisions

### OUT

- Batch retrospective analysis (deferred)
- Tier 2/3 execution changes (handled by /orchestrate)
- /orchestrate Section 3.0 inline phases (separate concern)
- Automatic triage criteria modification
- Learning entry generation from divergence patterns
- Entry gate propagation to /orchestrate, /deliverable-review, corrector (cross-cutting — separate /design job)

## Integration Points

| Consumer | Change | Mechanism |
|----------|--------|-----------|
| /design Phase 0 | Write classification.md after visible block | New Write step in skill body |
| /design Phase B | Replace inline execution with `/inline plans/<job> execute` | Skill call replaces 3-step sequence |
| /design Phase C.5 | Replace inline execution with `/inline plans/<job> execute` | Same as Phase B |
| /runbook Tier 1 | Replace direct implementation with `/inline` invocation | Skill call replaces 4-step sequence |
| /handoff | No changes needed | Existing continuation mechanism used as-is |
| corrector agent | No changes needed | Existing agent invoked by /inline with standardized template |
| /deliverable-review | No changes needed | Chained via handoff pending task |
| execute-rule.md | No shortcut needed | `x` handles inline task pickup |
| pipeline-contracts.md | Add T6.5 row | Pipeline transformation table |
| memory-index.md | New entries | Inline skill decisions |

## Risk Assessment

- **Low risk:** Script logic is deterministic, testable. Skill is workflow prose.
- **Medium risk:** /design and /runbook edits must not break existing paths (non-inline execution still works).
- **Mitigation:** Integration edits are additive (new route), not destructive (existing behavior unchanged for Tier 2/3).
- **Rollback:** If integration edits regress existing paths, revert the /design and /runbook modifications independently. The /inline skill and triage-feedback.sh are new files — removal is clean. Classification persistence (FR-1 in /design Phase 0) is also independently revertible.

## Requirements Traceability

| Requirement | Section | Coverage |
|-------------|---------|----------|
| FR-1 | D-3 | Complete |
| FR-2 | D-1, Workflow Phase 2 | Complete |
| FR-3 | Workflow Phase 3 | Complete |
| FR-4 | D-4, Workflow Phase 4a | Complete |
| FR-5 | D-2, Workflow Phase 4b | Complete |
| FR-6 | D-2, Workflow Phase 4b | Complete |
| FR-7 | D-2 script interface | Complete |
| FR-8 | D-5, Workflow Phase 4c | Complete |
| FR-9 | Integration Points (/design Phase B, C.5) | Complete |
| FR-10 | Integration Points (/runbook Tier 1) | Complete |
| NFR-1 | Overhead budget, D-1 | Complete |
| NFR-2 | D-2 (deterministic script) | Complete |
| NFR-3 | D-4 (single template) | Complete |
| C-1 | D-3 (skill reads, /design writes) | Complete |
| C-2 | D-3 (verbatim block format) | Complete |
| C-3 | D-2 (initial estimates note) | Complete |
| C-4 | Scope OUT (Tier 2/3 excluded) | Complete |
