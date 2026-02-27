# Design Session Empirical Data

**Source:** Session scraper (`plans/prototypes/session-scraper.py`) applied to 8 design sessions
**Date:** 2026-02-26
**Purpose:** Ground /design skill grounding refresh with empirical behavioral evidence from actual sessions

---

## Sessions Analyzed

| Session | Worktree | Entries | Agents | Commits | Outcome |
|---------|----------|---------|--------|---------|---------|
| 383be939 | error-handling-design | 194 | 1 | 2 | Complete — shortcircuited to execution |
| f36b9829 | design-workwoods | 77 | 2 | 2 | Partial — outline committed, review interrupted |
| 4452d81a | design-quality-gates | 12 | 0 | 0 | Aborted — user interrupted twice at Phase 0 |
| 065996f4 | main | 75 | 1 | 0 | Failed — triage misalignment, user corrected |
| 4ec020d3 | main | 10 | 0 | 0 | Aborted — Read errors, immediate interruption |
| 2e376b75 | pushback | 196 | 3 | 2 | Complete — full A→B→C pipeline |
| b89c8ef6 | requirements-skill | 236 | 5 | 3 | Complete — full pipeline, heaviest delegation |
| ebe6cbf8 | worktree-merge-data-loss | 299 | 4 | 5 | Mixed — design secondary to other work |

---

## Empirical Patterns

### Pattern 1: Pipeline Completion Rate

3 of 8 sessions completed full design pipeline. 5 of 8 interrupted or aborted.

**Complete sessions:**
- error-handling-design: shortcircuited at artifact check (design.md already existed)
- pushback: full A→B→C with user discussion
- requirements-skill: full A→B→C with parallel exploration

**Aborted sessions:**
- design-quality-gates: user interrupted twice at Phase 0 (12 entries total)
- main/4ec020d3: Read errors at Phase 0 (10 entries)
- main/065996f4: triage misalignment — agent guessed task meaning

**Partial sessions:**
- design-workwoods: outline committed but review agent interrupted
- worktree-merge-data-loss: design was secondary work in mixed session

### Pattern 2: Research Phase Skipping

**Session:** pushback (2e376b75)
**Evidence:** Designer classified "Complex" within ~1 minute, dispatched scout and started reading decision files. Skipped A.3-A.4 (external research) entirely. User noticed 47 minutes later:
> "Wow, that took a lot of thinking. I love grounding in research, best p..."
Designer admitted: "Fair point. I skipped external research (A.3-4) reasoning the framework was obvious."
3 WebSearch calls followed to partially correct.

**Significance:** Research phase (A.3-A.4) is a prose gate — "follow external research protocol." Agent rationalized skipping it. This matches the D+B principle (Principle 6 in grounding report): prose-only gates get rationalized away. The research step itself lacks a structural anchor.

### Pattern 3: Triage Misalignment

**Session:** main/065996f4
**Evidence:** Agent selected task from pending list, invoked /design, classified and routed to /runbook, then invoked /runbook and dispatched an agent — all before understanding the task. User interrupted: "you are guessing what the task means. Even I do not remember what it me[ans]."

**Significance:** Validates requirements-clarity gate (Gap 1). Agent proceeded through classification without validating task comprehension. The requirements-clarity gate is prose-only and failed silently.

### Pattern 4: Design Artifact Shortcircuit

**Session:** error-handling-design (383be939)
**Evidence:** Phase 0 detected existing design.md → routed directly to inline execution. Agent created 7 TaskCreate entries and executed changes across 5 files. 194 entries, 2 commits.

**Significance:** Artifact check short-circuit works correctly. When design.md exists, pipeline appropriately skips to execution. This is the happy path for resumed/continuation work.

### Pattern 5: Parallel Exploration Effectiveness

**Session:** requirements-skill (b89c8ef6)
**Evidence:** 3 scout agents dispatched simultaneously for different exploration facets:
- Agent a3dc94f: runbook skill handling of requirements
- Agent aab3d33: requirements.md usage patterns across project
- Agent a617dff: workflow entry points and skill chain

Total: 5 agents (3 scouts + outline-corrector + design-corrector), 236 entries, 3 commits.

**Significance:** Heaviest delegation pattern observed. Parallel exploration is effective for Complex tasks with multiple discovery facets. However, this is the most resource-intensive design session in the sample.

### Pattern 6: Design-Corrector Effectiveness

**Session:** pushback (2e376b75)
- Corrector found: 0 critical, 2 major, 3 minor issues
- All fixes applied autonomously (18 tool calls by corrector)
- Key fixes: wrong file path reference, overly prescriptive implementation detail

**Session:** requirements-skill (b89c8ef6)
- Corrector found: 3 major, 2 minor issues
- All fixes applied autonomously (22 tool calls)
- Key fixes: traceability table added, clarity improvements

**Significance:** Design-corrector catches real issues (wrong paths, missing traceability). The CDR-style review (Principle 7) adds measurable value. Both sessions show the corrector as the most tool-intensive agent in the pipeline.

### Pattern 7: User Intervention Points

| Session | Intervention | Phase | Nature |
|---------|-------------|-------|--------|
| design-quality-gates | 2 interrupts | Phase 0 | Early abort — unclear motivation |
| main/065996f4 | "you are guessing" | Phase 0 | Triage misalignment |
| main/4ec020d3 | interrupt after errors | Phase 0 | Read failures |
| design-workwoods | interrupted corrector | Phase A.6 | Unclear — user said "confusing prompt" |
| pushback | "I love grounding in research" | Post-A.5 | Research skip called out |
| requirements-skill | "are you sure about sonnet?" | Post-commit | Model selection correction |

**Significance:** 4 of 6 interventions occurred at Phase 0 (triage/entry). This is the highest-friction zone. The remaining 2 occurred after outline production (research quality, model selection). No interventions during Phase C (design generation/review) — suggesting that phase works smoothly.

### Pattern 8: Classification Timing

| Session | Time to classification | Method |
|---------|-----------------------|--------|
| pushback | ~2 min | Read requirements → classify (no when-resolve.py visible) |
| requirements-skill | ~30 sec | Classify → load skill dependency |
| design-workwoods | <30 sec | Immediate "Complex" classification |
| error-handling-design | ~15 sec | Artifact check shortcircuit |

**Significance:** Classification is fast but accuracy varies. The fastest classifications correlate with the sessions that had issues (workwoods: confusing prompt; 065996f4: guessing task meaning). Sessions with more deliberate classification (pushback: 2 min) had better outcomes. This supports the D+B anchor — forcing a tool call before classification adds deliberation time.

---

## Aggregate Metrics

### Deep sample (n=8, manually parsed with session scraper tree)

- **Average entries per complete session:** 209
- **Average agents per complete session:** 3
- **Average commits per complete session:** 2.3
- **Design-corrector fix rate:** 100% of issues self-resolved (no UNFIXABLE in either complete session)

### Full population (n=38, batch extraction script — v2 with fixes)

- **Classification distribution:** Complex 17, Moderate 10, Simple 3, Shortcircuit 1, Unknown 7
- **Sessions with interrupts:** 24/38 (63%)
- **Completion rate (commit proxy):** 33/38 (87%)
- **Sessions with review gates (outline+design corrector):** 8/38 (21%) — all from ≥2026-02-23; infrastructure absent in earlier sessions
- **Agent count range:** 0–10 (median ~2)
- **Entry count range:** 25–2376 (median ~400)

### Extraction fixes applied (v2)

- **Interrupt detection:** v1 checked string-format content only; missed list-format `[{"type":"text","text":"[Request interrupted by user]"}]` entries. v2 checks text blocks within list content. Result: 0/38 → 24/38 (63%) sessions with interrupts.
- **Classification detection:** v1 regexes broken by markdown bold markers (`**Complexity:** Moderate` → `[:\s]*` couldn't cross `**`). v2 strips `**` before matching and adds "This is (a) complex/moderate/simple" patterns. Result: Unknown 15 → 7 (8 sessions resolved).
- **Remaining Unknown (7/38):** Genuinely unclassifiable — aborted before classification (4452d81a, 4ec020d3), mixed sessions where /design wasn't primary activity, or sessions with no formal classification statement.

---

## Grounding-Relevant Findings

### Finding 1: Research step needs D+B anchor (supports Gap extension)

The pushback session shows A.3-A.4 research being rationalized away despite explicit prose instructions. This is the same failure class as Principle 6 (observable evidence). The research step should have a structural anchor — a tool call that proves external research was attempted before proceeding to outline.

### Finding 2: Requirements-clarity gate failure confirmed empirically

The 065996f4 session shows an agent proceeding through full triage and routing without understanding the task. Requirements-clarity gate (Gap 1) is confirmed as a real failure mode, not just a theoretical gap.

### Finding 3: Phase 0 is the primary friction zone

4 of 6 deep-sample interventions occurred at Phase 0 (triage/entry). Full population shows 24/38 (63%) sessions with at least one interrupt. Phase 0 is where the most value is lost: either the agent makes wrong assumptions (triage misalignment) or the process takes too long to show value (multiple interruptions). Improvements to Phase 0 gates have the highest expected impact.

### Finding 4: Design-corrector (CDR) works well; outline-corrector data insufficient

Both complete sessions show design-corrector catching and fixing real issues. Outline-corrector was interrupted in the workwoods session; only the pushback session shows a complete outline-corrector run (3 fixes applied). More data needed on outline-corrector effectiveness.

### Finding 5: Parallel exploration scales delegation load

The requirements-skill session used 5 agents (most in sample). 3 parallel scouts is the observed maximum. This is the empirical upper bound for Phase A delegation. The session completed successfully, suggesting the delegation overhead is justified for Complex tasks.

### Finding 6: No evidence of post-outline complexity re-check in traces

None of the observed sessions show evidence of the post-outline complexity downgrade gate firing. This may mean: (a) all observed tasks were genuinely complex, (b) the gate was added after most of these sessions, or (c) the gate is prose-only and gets skipped. More targeted data collection needed.
