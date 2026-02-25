# Skills Quality Pass — Design

## Problem

30 skills and 13 agent files have accumulated prose quality issues and structural anti-patterns. Two workstreams:

1. **Prose deslop:** Hedging, preamble, second-person, narrative examples, redundant framing
2. **D+B gate anchoring:** 12 prose-only judgment gates lacking tool-call anchors

## Requirements

**Functional:**
- FR-1: Fix description frontmatter anti-pattern across 18 skills (replace "This skill should be used when..." with factual noun phrases + trigger list)
- FR-2: Remove/fold "When to Use" preamble sections (~15 skills)
- FR-3: Extract narrative content to references/ for C-grade skills (review, orchestrate, token-efficient-bash)
- FR-4: Trim/extract for B- skills (reflect, shelve, plugin-dev-validation)
- FR-5: Anchor 12 prose-only gates with tool calls per D+B pattern
- FR-6: Fix correctness issues (worktree `list_plans()` → CLI, orchestrate absolute paths, requirements stale note)
- FR-7: Add "When Refactoring Procedural Prose" decision entry to implementation-notes.md + memory-index

**Non-functional:**
- NFR-1: Control flow correctness — every routing/branching path must produce correct behavior after restructuring
- NFR-2: User reporting correctness — user-visible output (classification blocks, status messages, routing decisions) must emit correctly on every path
- NFR-3: Opus model for all prose edits to skills/agents/fragments (per pipeline-contracts.md)
- NFR-4: Bootstrapping order — fix tools used in the fix process first (corrector agents → skills that delegate to them)

**Out of scope:**
- Creating an optimize-skill skill (discussed, decided against — low recurrence frequency)
- Runbook/design skill progressive disclosure optimization (next session topic)
- Full recall-gate inventory D+B fixes beyond the 12 identified (recall-specific gates already have tool-required enforcement)

## Architecture

### Workstream 1: Deslop

**Phase structure by effort level:**

**Mechanical (description + preamble):**
All 18 description anti-patterns are the same fix: replace "This skill should be used when the user asks to 'X', 'Y', 'Z'" with "Purpose statement. Triggers: 'X', 'Y', 'Z'." Preamble removal: delete "When to Use" section, keep counter-conditions folded into description.

**Skills needing description fix:**
error-handling, gitmoji, token-efficient-bash, next, when, how, recall, ground, codify, handoff, prioritize, worktree, doc-writing, deliverable-review, memory-index, reflect, runbook, design

**Skills needing "When to Use" removal:**
gitmoji, release-prep, shelve, worktree, orchestrate, review, codify, reflect, runbook, design, deliverable-review, next, doc-writing, handoff-haiku, handoff

**Body surgery (C-grade — extract to references/):**
- `review` (~1100 words → ~400): Extract "Common Scenarios" (60 lines), "Example Execution" (60 lines), trim "When to Use", remove "Be constructive" hedging, fix second-person
- `orchestrate` (~1500 words → ~600): Extract "Weak Orchestrator Pattern" (50 lines), "Example Execution" (80 lines), "Handling Common Scenarios" (60 lines) to references/; fix hardcoded absolute paths in References section
- `token-efficient-bash` (~900 words → ~150): Extract "How It Works", "Token Economy Benefits", worked examples with "Benefits" annotations, "Summary" to references/; keep pattern + caveats only

**Body surgery (B- — trim/extract):**
- `reflect` (~1100 → ~800): Extract "Key Design Decisions" section to references/; remove "When to Use"; fix second-person "User switches"
- `shelve` (~340 → ~200): Replace "Example Interaction" with terse note (it models conversational register "I'll help you..."); remove "When to Use"
- `plugin-dev-validation` (~1400 → ~600): Extract Rationale sub-bullets, Verification/Fix Procedures, Good/Bad Examples to references/; remove "Usage Notes" second-person framing

**Correctness fixes:**
- `worktree` Mode B step 1: Replace `list_plans(Path('plans'))` with `claudeutils _worktree ls`
- `orchestrate` References section: Replace absolute paths with relative
- `requirements`: Remove stale "Integration Notes" section

### Workstream 2: D+B Gate Anchoring

**12 gates, 7 files. Fix pattern:** Add a tool call (Read, Bash, Grep, Glob) that opens the judgment step, producing output the decision logic operates on.

**High priority (3 — all in design skill):**

| # | Gate | Fix |
|---|------|-----|
| 1 | Post-Outline Complexity Re-check | Add `Read plans/<job>/outline.md` before downgrade criteria |
| 2 | Outline Sufficiency Gate (Phase B exit) | Add `Read plans/<job>/outline.md` before sufficiency criteria |
| 3 | Direct Execution Criteria C.5 | Add `Read plans/<job>/design.md` before execution-readiness criteria |

**Medium priority (4):**

| # | File | Gate | Fix |
|---|------|------|-----|
| 4 | commit | Production artifact classification | Add Grep for artifact paths after git diff |
| 5 | handoff | Command derivation from plan status | Add `Bash: claudeutils _worktree ls` before derivation |
| 6 | requirements | Extract vs Elicit mode detection | Add Glob/Read of `plans/<job>/requirements.md` as primary signal |
| 7 | codify | Target file routing | Add Grep of candidate domain files before routing |

**Low priority (5):**

| # | File | Gate | Fix |
|---|------|------|-----|
| 8 | handoff | Prior handoff detection | Simplify to structural date check |
| 9 | runbook-outline-corrector | Growth projection | Add `wc -l` for target files |
| 10 | corrector | Task type validation | Add Read of input file at Step 1 |
| 11 | design-corrector | Document type validation | Add Grep for runbook markers |
| 12 | design | Classification gate (borderline) | Recall Bash partially anchors — add Glob for behavioral code check |

### Workstream 3: Doc Update

Add to `agents/decisions/implementation-notes.md`:

**"When Refactoring Procedural Prose"**
- Anti-pattern: Deslop/restructuring that merges adjacent branches or rewords conditionals without verifying each path's user-visible output
- Correct pattern: Enumerate control flow paths before editing, verify each path's output after
- Evidence: Design skill deslop combined two fast paths, regressed user-facing classification message

Add to `agents/memory-index.md`:
```
/when refactoring procedural prose | deslop restructure control flow regression user-visible output
```

## Key Design Decisions

- D-1: **No optimize-skill skill.** Low recurrence frequency; the runbook IS the procedure for batch passes. Decision entry fills the regression-prevention gap at lower cost.
- D-2: **Bootstrapping order.** Fix corrector agents (gates 9-11) before skills that delegate to them (design, commit, handoff). This ensures improved agents review improved skills.
- D-3: **Description format.** Replace verbose "This skill should be used when..." with factual noun phrase + trigger list. Format: `"Purpose. Triggers: 'X', 'Y', 'Z'."` Per plugin-dev:skill-development guidance, third-person trigger phrases required.
- D-4: **Progressive disclosure target.** C-grade skills should reach ~400-600 words body with detail in references/. Current A+ skills (brief: 120w, commit: 390w, how/when: 130w) are the density benchmark.
- D-5: **Control flow verification.** After restructuring any skill with conditional branches (design, commit, handoff, requirements, codify, orchestrate), enumerate all paths and verify user-visible output on each. This is a review criterion, not a separate step — the corrector receives it as context.
- D-6: **Gate fix pattern.** Add tool call that produces output → prose judgment operates on output → if/then with explicit branch targets. The tool call IS the anchor; the judgment following it is acceptable because it operates on loaded data.

## Implementation Notes

**Affected files (all workstreams combined):**

Skills (19 files):
- `agent-core/skills/commit/SKILL.md` — FR-5 (gate), FR-2 possible
- `agent-core/skills/codify/SKILL.md` — FR-1, FR-2, FR-5
- `agent-core/skills/deliverable-review/SKILL.md` — FR-1, FR-2
- `agent-core/skills/design/SKILL.md` — FR-1, FR-2, FR-5 (×3 gates)
- `agent-core/skills/doc-writing/SKILL.md` — FR-1, FR-2
- `agent-core/skills/error-handling/SKILL.md` — FR-1
- `agent-core/skills/gitmoji/SKILL.md` — FR-1, FR-2
- `agent-core/skills/ground/SKILL.md` — FR-1
- `agent-core/skills/handoff/SKILL.md` — FR-1, FR-5 (×2 gates)
- `agent-core/skills/handoff-haiku/SKILL.md` — FR-2
- `agent-core/skills/how/SKILL.md` — FR-1
- `agent-core/skills/memory-index/SKILL.md` — FR-1
- `agent-core/skills/next/SKILL.md` — FR-1, FR-2
- `agent-core/skills/orchestrate/SKILL.md` — FR-2, FR-3, FR-6
- `agent-core/skills/plugin-dev-validation/SKILL.md` — FR-4
- `agent-core/skills/prioritize/SKILL.md` — FR-1
- `agent-core/skills/recall/SKILL.md` — FR-1
- `agent-core/skills/reflect/SKILL.md` — FR-1, FR-2, FR-4
- `agent-core/skills/release-prep/SKILL.md` — FR-2
- `agent-core/skills/requirements/SKILL.md` — FR-5, FR-6
- `agent-core/skills/review/SKILL.md` — FR-3
- `agent-core/skills/runbook/SKILL.md` — FR-1, FR-2
- `agent-core/skills/shelve/SKILL.md` — FR-2, FR-4
- `agent-core/skills/token-efficient-bash/SKILL.md` — FR-1, FR-3
- `agent-core/skills/when/SKILL.md` — FR-1
- `agent-core/skills/worktree/SKILL.md` — FR-1, FR-6

Agents (3 files):
- `agent-core/agents/corrector.md` — FR-5
- `agent-core/agents/design-corrector.md` — FR-5
- `agent-core/agents/runbook-outline-corrector.md` — FR-5

Decision files (2 files):
- `agents/decisions/implementation-notes.md` — FR-7
- `agents/memory-index.md` — FR-7

**Testing strategy:** `just precommit` after each phase. No behavioral code → no unit tests. Control flow verification via manual path enumeration for skills with conditional branches.

**Phase typing guidance:**
- FR-1 + FR-2 (description + preamble): general — mechanical edits, high file count
- FR-3 + FR-4 (body surgery): general — progressive disclosure restructuring
- FR-5 (D+B anchoring): general — structural edits to procedural steps
- FR-6 (correctness): general — targeted fixes
- FR-7 (doc update): inline — two-file additive edit

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `plans/skills-quality-pass/reports/skill-inventory.md` — per-skill grades, specific issues, quoted examples
- `plans/skills-quality-pass/reports/full-gate-audit.md` — 12 gates with fix directions
- `agents/decisions/implementation-notes.md` — D+B pattern definition, skill placement rules
- `agents/decisions/pipeline-contracts.md` — prose artifact model selection (opus)
- `agent-core/skills/project-conventions/SKILL.md` — deslop rules (bundled)

**Skill to load:** `plugin-dev:skill-development` — description format, progressive disclosure, writing style requirements

**Context7:** Not needed.

## References

- `plans/skills-quality-pass/reports/skill-inventory.md` — sonnet scout: 30-skill audit with grades
- `plans/skills-quality-pass/reports/full-gate-audit.md` — sonnet scout: 12 prose-only gates
- `plans/recall-tool-anchoring/reports/recall-gate-inventory.md` — prior recall-specific gate audit (31 gates, 13 files)
- `plans/recall-tool-anchoring/recall-artifact.md` — D+B pattern entry "How to Prevent Skill Steps From Being Skipped"
- `agents/decisions/implementation-notes.md` — D+B hybrid fix codified decision

## Next Steps

Route to `/runbook plans/skills-quality-pass/design.md` — general phases, opus execution model.
