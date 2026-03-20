# Design: Outline Proofing

Adds `/proof` gates at three pipeline stages: /design Moderate, /runbook Tier 2, and /runbook Tier 3 (post-simplification). Eliminates /runbook Tier 1 (dead code after /design Moderate handles that scope). Introduces `inline-plan.md` artifact for Moderate agentic-prose path.

## Scope

**Affected files:**
- `agent-core/skills/design/SKILL.md` — §Routing Moderate section (two paths: agentic-prose → inline-plan.md, non-prose → outline.md)
- `agent-core/skills/design/references/write-inline-plan.md` — new reference file for inline-plan format
- `agent-core/skills/runbook/SKILL.md` — Three-Tier Assessment → Two-Tier Assessment (remove Tier 1, rework Tier 2)
- `agent-core/skills/runbook/references/tier3-planning-process.md` — move /proof from Phase 0.75 step 5 to after Phase 0.86 (unconditional)
- `agent-core/skills/proof/SKILL.md` — Integration Points table (new rows + count), dispatch table (inline-plan.md → none)
- `src/claudeutils/inference.py` — add `inline-planned` status, fix `outlined` → `/design` routing

**IN:**
- /design Moderate agentic-prose: code reading → `inline-plan.md` → `/proof` (no corrector) → `/inline`
- /design Moderate non-prose: code reading → `outline.md` → `/proof` (outline-corrector dispatched by /proof) → `/runbook`
- /runbook Tier 1 removal, rename to Two-Tier Assessment
- /runbook Tier 2: replace self-check + runbook.md with runbook-outline.md → corrector → /proof
- /runbook Tier 3: unconditional /proof after Phase 0.86 (replaces conditional Phase 0.97 and Phase 0.75 step 5)
- /proof integration points table update
- inference.py: `inline-planned` status → `/inline`, `outlined` → `/design` (not `/runbook`)

**OUT:**
- outline-corrector criteria (format-agnostic PDR criteria, no change)
- runbook-corrector criteria (expansion format unchanged)
- validate-runbook.py (Tier 3 only, not affected by these changes)
- /inline SKILL.md (already finds execution document via Glob; no change needed)

## Dependencies

- `runbook-outline-corrector` agent already exists (handles runbook-outline.md review at Phase 0.75)
- `outline-corrector` agent already exists (handles outline.md review at Phase A.6)
- `/proof` already handles both `outline.md` and `runbook-outline.md` artifact types (dispatch table present); needs `inline-plan.md` → none entry added
- Phase 0.75 step 5 /proof on runbook-outline.md (added in anchor-proof-state) is REMOVED — replaced by unconditional /proof after Phase 0.86

## Design Decisions

### D1: Moderate Inline Plan Format

**Location:** New reference file `agent-core/skills/design/references/write-inline-plan.md` (parallel to `write-outline.md` for Complex).

**Artifact:** `plans/<job>/inline-plan.md` — the execution plan for direct inline implementation. Named after its structural role (parallel to `runbook.md` for orchestrated execution), not content type.

**Format:**
```markdown
## Scope
**Affected files:** [enumerated from code reading — actual paths, not brief assumptions]
**Changes:** [per-file: what changes and why]

## Boundaries
IN: [specific changes included]
OUT: [explicitly excluded]

## Dependencies
[Cross-file or external dependencies discovered during code reading]
```

**Properties:** Prose-only artifact. No research, no options analysis, no risks section. Requires code reading to populate (this is the value — brief assumptions vs actual codebase state). No automated corrector — document is small enough that /proof (human review) catches scope issues better than pattern matching. /proof dispatch: `none` (like requirements.md).

**Status:** `inline-planned` → `/inline plans/{plan}` (parallel to `planned` → `/orchestrate`).

### D2: Moderate Outline Generation Steps

New §Routing Moderate path (replaces single-line routing), split by artifact destination:

**Agentic-prose path:**
1. **Code reading:** Read affected files to ground the brief against actual codebase state
2. **Generate** `plans/<job>/inline-plan.md` using format from `references/write-inline-plan.md`
3. **Proof:** Invoke `/proof plans/<job>/inline-plan.md` (no corrector — scope completeness is domain knowledge, not structural checking)
4. **Route (after /proof approval):** follow §Continuation (prepends `/inline plans/<job> execute`)

**Non-prose path:**
1. **Code reading:** Read affected files to ground the brief against actual codebase state
2. **Generate** `plans/<job>/outline.md` using lightweight format
3. **Proof:** Invoke `/proof plans/<job>/outline.md` (outline-corrector dispatched by /proof on revise/kill)
4. **Route (after /proof approval):** follow §Continuation (prepends `/runbook plans/<job>`)

### D3: Tier 1 Elimination

Remove entire "Tier 1: Direct Implementation" section from /runbook SKILL.md. Rename "Three-Tier Assessment" header to "Two-Tier Assessment". Minimum tier is now 2.

**Rationale:** Work that was Tier 1 scope reaches /inline via /design Moderate → inline-plan.md → proof → /inline (never touches /runbook). Work reaching /runbook is always Tier 2+ minimum. Tier 1 is dead code.

**If /runbook called directly (bypassing /design):** STOP. Check plan directory for design-stage artifact (`outline.md`, `inline-plan.md`, or `design.md`). Absent → halt and route to `/design` first. /runbook without prior /design gating is an error condition, not a fallback.

### D4: Tier 2 New Flow

Replace the current Tier 2 planning sequence with:

1. Implementation recall (unchanged — D+B anchor)
2. **Generate** `plans/<job>/runbook-outline.md` using Tier 2 outline format (below)
3. **Review:** Delegate to runbook-outline-corrector (fix-all mode, same prompt pattern as Tier 3 Phase 0.75 step 4). Dispatch prompt must specify Tier 2 format expectations — no requirements mapping table. Corrector skips mapping table validation for Tier 2.
4. **Proof:** Invoke `/proof plans/<job>/runbook-outline.md`
5. **After /proof approval:** follow §Continuation (prepends `/inline plans/<job> execute`)

**Remove:** "Consolidation self-check (after planning cycles)" paragraph — no longer the self-check substitute.
**Remove:** "Output channel: Write plan directly to `plans/<job>/runbook.md`" — replaced by runbook-outline.md.

**Tier 2 outline format** (simpler than Tier 3):
```markdown
## Phase N: [title] (type: [tdd|general|inline])
- Item N.1: [target file] — [concrete action]
- Item N.2: [target file] — [concrete action]
  Depends on: Item N.1
```
No requirements mapping table (Tier 2 scope too small to need traceability table). Type tags required (same as Tier 3). Per-item: concrete action + target file. Dependencies noted where relevant.

**Execution:** /inline executes from the approved runbook-outline.md as its execution guide. No runbook.md generated.

### D5: Tier 3 — Unconditional /proof After Phase 0.86

**Change:** Remove /proof from Phase 0.75 step 5. Add unconditional /proof immediately after Phase 0.86 (simplifier).

**Placement:** Between Phase 0.86 (runbook-simplifier) and Phase 0.9 (complexity check).

**Rationale:** All execution paths that lead to expansion (or promotion, or exit) pass through this single gate:
- Path 1 (normal expansion): 0.86 → **proof** → 0.9 → 0.95 → Phase 1 ✓
- Path 2 (0.9 callback): 0.86 → **proof** → 0.9 (callback, STOP) → restructure → pipeline restarts from 0.75 → 0.86 → **proof again** ✓
- Path 3 (0.95 promote): 0.86 → **proof** → 0.9 → 0.95 (sufficient → promote) → Phase 4 ✓
- Path 4 (0.95 exit): 0.86 → **proof** → 0.9 → 0.95 (exit) → handoff ✓

One proof gate, unconditional, no conditional logic. Cleaner than two-proof approach (Phase 0.75 + conditional Phase 0.97).

**Phase text:**
```
## Phase 0.87: Pre-Expansion User Validation

1. Invoke `/proof plans/<job>/runbook-outline.md` — user validates post-simplification outline before expansion
2. On approval: proceed to Phase 0.9 complexity check
```

**Scope change from original design:** tier3-planning-process.md edit now includes REMOVING /proof from Phase 0.75 step 5 (not just adding a new phase).

### D6: /proof Integration Points Table Update

Add 3 new rows and update count from 5 to 8. Adjust for accumulated revisions (inline-plan.md, unconditional post-0.86):

| Hosting Skill | Stage | Artifact | Defect Layer |
|---------------|-------|----------|-------------|
| /design | Moderate agentic-prose (Post-code-reading) | inline-plan.md | Moderate scope validation |
| /design | Moderate non-prose (Post-code-reading) | outline.md | Moderate scope validation |
| /runbook | Tier 2 (Post-outline-corrector) | runbook-outline.md | Tier 2 scope validation |
| /runbook | Phase 0.87 (Post-simplification, unconditional) | runbook-outline.md | Pre-expansion validation |

Count line: "Invoked at 8 points across 3 hosting skills" (5 existing + 4 new - 1 removed = 8)

Dispatch table additions:
- `inline-plan.md` → none (no corrector, like requirements.md)
- `outline.md` already dispatches to outline-corrector

Note: /design Phase B (Complex, post-outline) remains separate from Moderate invocation — different path through /design SKILL.md.
