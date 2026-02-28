# Outline: Runbook Recall Expansion

## Approach

Add recall artifact resolution to `prepare-runbook.py` so step agents in full orchestration (Tier 3) receive pre-resolved decision content. Three integration points:

1. **prepare-runbook.py** — read recall artifact, resolve keys via CLI, inject resolved content into agent definition's Common Context
2. **runbook SKILL.md** — document two orchestration patterns (lightweight vs full) and where recall resolution happens in each
3. **corrector.md** — add self-contained recall loading (same pattern as design-corrector.md Step 1.5)

## Open Questions Resolved

**Q1: Shared vs per-step injection?**
Shared entries → agent definition (Common Context section). Phase-specific entries → step file Phase Context section. This matches the existing architecture: `generate_phase_agent()` receives `plan_context` (Common Context) and `phase_context` (phase preamble). Both already flow to the right places — recall content piggybacks on these existing channels.

**Q2: Format marker in runbook source?**
No new marker needed. The runbook template already has a `**Recall (from artifact):**` section in Common Context. The planner writes curated recall entries there as prose. `prepare-runbook.py` reads `plans/<job>/recall-artifact.md` independently — it resolves the artifact keys and appends a `## Resolved Recall` section to Common Context before generating agents. The planner's curated prose and the mechanically-resolved content are complementary: planner provides constraint framing, resolver provides full decision text.

## Key Decisions

**Injection point in agent definition:** Append `## Resolved Recall` section after existing Common Context content. Not interleaved — keeps planner-curated content separate from mechanically-resolved content.

**Resolution mechanism:** `prepare-runbook.py` calls `claudeutils _recall resolve <artifact-path>` via subprocess, captures stdout. Same CLI used by all other recall consumers.

**Phase-scoped recall:** Recall artifact entries support phase tags (e.g., `when editing skill files — phase 2 only`). `prepare-runbook.py` resolves ALL entries, then partitions: untagged entries → `plan_context` (Common Context, all phase agents), phase-tagged entries → corresponding `phase_context` (phase preamble → step files + phase agent). Uses existing `phase_context` channel — no new injection point needed.

**Phase tag validation:** `prepare-runbook.py` errors (not warns) if a phase-tagged entry references a nonexistent phase or an inline phase (no agent/step files generated for inline). Errors at preparation time force the planner to fix the artifact. Agents ignore soft failures — warnings during preparation are seen only by the orchestrator, which has no protocol for surfacing them.

**Conflicting signals constraint:** Per "When agent context has conflicting signals" — persistent Common Context is stronger signal than step file input at haiku capability. Planners must not place the same entry in both shared and phase-tagged locations with different framing. This is a curation constraint documented in the runbook SKILL.md template, not enforced in code.

**Backward compatibility (NFR-3):** `prepare-runbook.py` checks for `plans/<job>/recall-artifact.md`. If absent, no recall section appended — existing behavior unchanged.

**Token budget (NFR-1):** `prepare-runbook.py` does not filter or truncate resolved content. The planner curates the artifact at planning time (existing constraint in runbook SKILL.md). The resolver is a mechanical pass-through.

**Corrector recall loading (FR-7):** Corrector needs the job name to locate `plans/<job>/recall-artifact.md`. The task prompt already contains plan directory paths (e.g., "Review plans/foo/reports/review.md"). Extract job name from first `plans/<name>/` path in task prompt. Fallback: lightweight recall via memory-index (same pattern as design-corrector.md).

## Scope

**IN:**
- `prepare-runbook.py`: recall artifact reading + resolution + injection into `plan_context`
- `agent-core/skills/runbook/SKILL.md`: two-pattern documentation section
- `agent-core/agents/corrector.md`: self-contained recall loading step
- Tests for prepare-runbook.py recall functionality
- Recall artifact format: phase tag syntax addition
- Phase tag validation (error on nonexistent/inline phases)

**OUT:**
- Lightweight orchestration changes (already works)
- Recall artifact generation (/design and /runbook Phase 0.5 handle this)
- `when-resolve.py` / `claudeutils _recall resolve` changes
- Step file format changes (phase context already supports recall content)

## Affected Files

- `agent-core/bin/prepare-runbook.py` — add `resolve_recall_artifact()`, modify `generate_phase_agent()` call site
- `agent-core/skills/runbook/SKILL.md` — add two-pattern documentation section
- `agent-core/agents/corrector.md` — add Step 1.5 recall loading
- `tests/test_prepare_runbook.py` — tests for recall resolution and injection

## Task Decomposition

Pipeline self-modification constraint applies (learning: "When implementation modifies pipeline skills"). Inline task sequence, not full runbook pipeline.

Strict dependency chain — no parallelization benefit:

1. **prepare-runbook.py recall resolution** — FR-1, FR-2, FR-3, FR-4, NFR-2, NFR-3. Add `resolve_recall_artifact()` function that reads artifact, resolves keys, partitions by phase tag, validates phase tags against runbook phases (error on nonexistent/inline). Wire into `main()` to inject shared entries into `plan_context` and phase-tagged entries into `preambles`. TDD: test with/without artifact, test phase partitioning, test phase validation errors, test resolution failure handling.

2. **Corrector recall loading** — FR-7. Add Step 1.5 to corrector.md matching design-corrector.md pattern. Prose edit, no behavioral code.

3. **Runbook skill two-pattern docs** — FR-5, FR-6. Add section documenting lightweight vs full orchestration recall patterns. Prose edit.

4. **Integration verification** — Verify prepare-runbook.py + runbook template + corrector changes work together. Run `just precommit`.
