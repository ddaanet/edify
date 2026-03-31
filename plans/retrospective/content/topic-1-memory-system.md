# Topic 1: Memory System Evolution — Evidence Bundle

## 1. Git Timeline

### Phase 0: Pre-history — Agent Instructions as Proto-Memory (Sep 2025–Jan 2026)

Before memory-index.md existed, agent instructions *were* the memory system. The evolution from flat rules to structured memory predates claudeutils by five months.

| Date | Repo | Hash | Event |
|------|------|------|-------|
| 2025-09-30 | rules | `7b0a4b4` | Initial `rules.md` — 14 rules, human-curated, agent-consumed. No agent self-modification. |
| 2025-10-02 | rules | `eacf188` | Rename to AGENTS.md — naming convention born. |
| 2025-11-28 | oklch-theme | `b0c0d64` | AGENTS.md titled "Agent Memory" with retrospective self-update: "At the end of each session, perform a retrospective and update this file." First agent→file write loop. |
| 2025-11-23 | box-api | `0bbdbf8` | Session-specific rules with filtering: "Include any feedback that is general enough in scope." First curation criterion for what to remember. |
| 2026-01-12 | home | `e31a4c0` | File organization table: AGENTS.md (behavioral), session.md (transient), design-decisions.md (rationale), plans/ (artifacts). Memory distributed by content type. |
| 2026-01-12 | pytest-md | `69bf88b` | Session log design — structured conversation state persistence. 100-line max, archive strategy. |
| 2026-01-15 | pytest-md/plugin | `5783aef` | Agent-core initialized — memory patterns extracted into shared infrastructure. |

**Arc:** Human-written flat rules → agent retrospective self-update → filtering criterion for persistence → structured file taxonomy → shared infrastructure. Each step adds a capability: authorship (human→agent), selectivity (what to keep), organization (where to put it), sharing (across projects).

oklch-theme (`b0c0d64`) started with Gemini (AGENTS.md references "Gemini agent"), later iterated in Claude Desktop. The agent→file write loop idea is a natural pattern for any stateless agent system.

### Phase A: Foundation — Memory Index & Always-Loaded Context (Feb 1)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-01 | `9a5f9f71` | Implement ambient awareness with memory index and path-scoped rules |
| 2026-02-01 | `6e88a294` | Move memory index to project-level, seed with 46 entries |

Commit `9a5f9f71` body: "Import memory-index.md in CLAUDE.md for always-loaded discovery. Add 2 path-scoped rules. Document memory index pruning design problem."

Commit `6e88a294` body: "Create agents/memory-index.md with seeded entries (4 sections). Entry format: keyword-rich summaries with arrow separator. Seeding: behavioral rules (5), workflows (7), decisions (9), tools (7)."

The memory-index was the first attempt to bridge the gap between the pre-history (rules scattered across files) and the goal (agents that recall relevant decisions). It aggregated the structured taxonomy from Phase 0 into a single lookup index.

### Phase B: /when and /how Skills — Active Lookup (Feb 8–13)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-08 | `00b8ec35` | Add memory index recall analysis tool |
| 2026-02-13 | `1a9b2c4b` | Cycle 11.1: Update recall index parser for /when format |
| 2026-02-13 | `fc0f293f` | Cycle 11.3: Verify recall analysis with new /when format |
| 2026-02-13 | `8df92e27` | Fix recall path matching and rerun baseline analysis |
| 2026-02-13 | `fb16d94e` | Refactor complex parsing functions to reduce complexity |
| 2026-02-13 | `f2715734` | Merge when-recall worktree |

The when-recall worktree implemented fuzzy matching for `/when` and `/how` skill invocations — TDD cycles 0.1 through 1.x covering word-overlap tiebreaker, minimum score threshold, section navigation, and file navigation.

### Phase C: Recall Infrastructure — Measurement & Tooling (Feb 13–23)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-13 | `8df92e27` | Fix recall path matching and rerun baseline analysis |
| 2026-02-23 | `c7a55dd5` | Finalize remember-skill-update outline with 6 phases and 13 FRs |
| 2026-02-23 | `ebbc7936` | Rename /remember skill to /codify (step 6.1) |
| 2026-02-23 | `ed951bc1` | Ground recall pass: 4-pass pipeline memory model |

### Phase D: The Measurement Inflection (Feb 20)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-20 | `c4b1e043` | Evaluate /when recall: 4.1% usage, unblock memory-index demotion |
| 2026-02-20 | `917122ba` | Context optimization analysis and hook batch scoping |

Commit `c4b1e043` body: "801 sessions scanned across 71 project dirs: 22 /when calls in 8/193 post-merge sessions. Direct decision file reads unchanged (21.2% to 21.8%), 1.1x improvement (noise). Root cause: metacognitive recognition bottleneck, not tool awareness. Unblock memory-index.md (3.7k tokens) demotion in context-optimization brief."

**Note on the 4.1% statistic:** This figure measured `/when`/`/how` skill invocations — a mix of user-initiated testing and procedural usage. It did not measure spontaneous agent recall. A later direct measurement (Phase G) found the spontaneous rate to be 0%.

### Phase E: Recall Gate Anchoring — Tool-Based Enforcement (Feb 24–Mar 1)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-24 | `7ee9d0c0` | Design recall gate tool-anchoring (31 gates, 61% prose-only) |
| 2026-02-24 | `66f58df0` | Runbook for recall-tool-anchoring (promoted from outline) |
| 2026-02-24 | `b982c69f` | Phase 2: Convert recall-artifact to reference manifest format |
| 2026-02-25 | `4ecd09b7` | Wire memory-index validation into precommit, fix orphans and duplicates |
| 2026-02-28 | `fc7d94e1` | Cycle 2.1: Check succeeds on valid artifact (recall CLI) |
| 2026-02-28 | `ff71a254` | Cycle 3.1: Resolve artifact mode — happy path |
| 2026-02-28 | `0ad15370` | Phase 5: Integration, cleanup, prototype deletion |
| 2026-03-01 | `0d867a23` | Cycle 1.1: Build inverted index from parsed entries |
| 2026-03-01 | `f4de036b` | Cycle 3.1: Topic detector block in hook |

### Phase F: Active Recall System — Architectural Redesign (Mar 2–6)

| Date | Hash | Message |
|------|------|---------|
| 2026-03-02 | `fc0d9b8a` | Create active recall system plan from architectural discussion |
| 2026-03-02 | `60de1237` | Capture requirements for active recall system |
| 2026-03-03 | `cff6fd79` | (session) Design inputs: metacognitive analysis, forced injection, Context7 |
| 2026-03-06 | `43abd7fe` | Design active recall system: outline + 7 architectural decisions |
| 2026-03-06 | `de5ddfdd` | Redraft outline with decomposition methodology (8 sub-problems, DAG) |

### Phase G: Spontaneous Recall Measurement — 0% (Mar 2026)

Direct measurement across 129 recall tool invocations in 69 sessions:

| Category | Count | % |
|----------|-------|---|
| Skill-procedural | 113 | 87.6% |
| User-triggered | 16 | 12.4% |
| Hook-injected | 0 | 0% |
| Spontaneous | 0 | 0% |

Method: Scanned 265 session files, found 129 actual recall tool invocations. All 37 initially-classified "spontaneous" hits were reclassified on manual review: discussion-grounding (11), test-execution (7), orchestration-phase (6), user-triggered (5), non-recall (5), skill-procedural (3). Report: `plans/measure-agent-recall/report.md`.

The 0% spontaneous rate is a stronger finding than the 4.1% statistic from Phase D. The 4.1% measured `/when`/`/how` skill invocations (users testing the tool). The 0% measures agent behavior directly: agents never independently decided to consult the recall system. The "actionable index" concept — entries loaded in context that would self-trigger agent recognition — did not produce spontaneous recall.

---

## 2. Session Excerpts

### Excerpt 1: The 4.1% Discovery — Recognition Bottleneck Diagnosed

**Session:** `f9e199ea` | **Project:** when-recall-evaluation | **Date:** 2026-02-20

The pivotal moment where measurement data revealed the fundamental failure of agent-initiated recall.

> **Agent:** `/when` is barely used and hasn't moved the needle.
>
> - 801 sessions scanned across 71 project directories
> - 22 total `/when`/`/how` invocations in 8 of 193 post-merge sessions (4.1%)
> - Direct decision file reads unchanged: 21.2% to 21.8%
> - Total recall improvement: 1.1x (essentially noise)
>
> **Root cause:** `/when` changed the action mechanism (Read -> Skill -> Bash) but not the recognition step. Agents still need to recognize they're in a decision-relevant situation to invoke it — the same cognitive step the passive index relied on.

> **User:** so we are back to relying on explicit exploration steps and grep?

> **Agent:** For decisions that matter during execution, yes. The data confirms the recognition problem: giving agents a lookup tool doesn't help if they don't recognize when to use it — same failure mode as the passive index, different mechanism.
>
> What actually works, by the evidence:
> - **Always-loaded fragments** — 100% "recall" by definition, but token-expensive.
> - **Explicit paths in prompts** — orchestrator/vet delegation templates that name specific files.
> - **Grep during exploration** — design and planning phases where agents actively search.
>
> `/when` occupies a dead zone: cheaper than always-loaded, but requires the same recognition step that fails at 0.2%.
>
> Two paths forward that the data supports:
>
> **Hook-based injection** (already in hook batch Phase 1). UserPromptSubmit detects topic keywords and injects relevant decision content — same as forced-eval hook pattern from learnings (84% activation vs 20% baseline). Moves recognition from agent to script.
>
> **Structural embedding** — put decisions where agents already look.

### Excerpt 2: Metacognitive vs Procedural Recognition

**Session:** `f9e199ea` (continued) | **Date:** 2026-02-20

User challenges the agent to evaluate its own diagnosis.

> **User:** d: agents do not recognize "/when" as actionable

> **Agent:** Partially agree, but the diagnosis is imprecise in a way that matters for choosing the fix.
>
> **Reason 2: `/when`'s trigger is metacognitive, not procedural.** Compare with skills that work:
> - `/commit` — trigger is a clear action boundary ("commit this")
> - `/handoff` — trigger is a clear action boundary ("end session")
> - `/when` — trigger is "you might be wrong about how to handle this situation"
>
> The first two require recognizing an *action*. `/when` requires recognizing *uncertainty about a decision you're currently making confidently*. LLMs don't introspect on their own confidence well. An agent that's about to handle errors incorrectly doesn't think "I should check the error handling decision" — it just handles errors the way it would by default.
>
> **Verdict:** The mechanism that fails is not "recognition of /when as a tool" but "recognition of uncertainty as a state requiring action." No amount of skill description tuning fixes that because the bottleneck is metacognition, not tool awareness.

### Excerpt 3: From Agent-Invoked to Script-Invoked Resolution

**Session:** `f9e199ea` (continued) | **Date:** 2026-02-20

The conceptual pivot from agent recall to forced injection.

> **Agent:** The memory index and `/when` could still serve as the *backing store* for hook-based injection — the hook script matches topics against index entries and injects content. The agent never needs to recognize the situation; the hook does it mechanically.

> **Agent:** Brief updated. memory-index.md (3.7k tokens) moved from "blocked — waiting for usage data" to demotable, with the evaluation data as evidence. Key addition: the index's future role is as hook infrastructure (queried by scripts), not agent-visible context.

### Excerpt 4: Recall Gate Inventory — 61% Prose-Only Gates

**Session:** `3a299440` | **Project:** recall-tool-anchoring | **Date:** 2026-02-24

Design session that grounded the enforcement problem.

> **Agent:** All three plan files loaded:
> - **outline.md** — Design document: reference manifest format, 3 prototype scripts, D+B restructure of 8 skills/agents, PreToolUse hook. 9 prototype steps.
> - **recall-artifact.md** — 11 entries in current content-dump format (will be converted to reference manifest)
> - **reports/recall-gate-inventory.md** — 31 gates across 13 files; 61% prose-only, 26% tool-required, 13% implicit

From the outline itself (commit `7ee9d0c0`): "31 recall gates across 13 files. 61% (19/31) prose-only. Documented bypasses: deliverable-review ran without recall; recall-artifact summary treated as full recall pass. Root cause codified: 'Execution-mode cognition optimizes for next tool call. Steps without tool calls register as contextual commentary.'"

### Excerpt 5: TDD Execution of /when Fuzzy Matching

**Session:** `d2a626b7` | **Project:** when-recall | **Date:** 2026-02-12–13

Orchestrated TDD execution building the recall matching engine.

> **Agent:** Resuming when-recall execution. Current state: 4/47 cycles complete (0.1, 0.2, 0.3 skip, 0.4).
>
> **Blocker identified:** Cycle 0.5 has a known test flaw. The assertions pass due to boundary bonuses (212 vs 202) even though the word-overlap tiebreaker feature is absent. The test needs rewriting with inputs that produce genuinely tied fzz scores.
>
> **Blast radius protocol:** "Fix test flaws before continuing. Test flaws are deliverable defects."

> **Agent:** Cycle 0.5 complete — Word-overlap tiebreaker implemented
> **Agent:** Cycle 0.6 complete — Minimum score threshold implemented

### Excerpt 6: Recall Fix — Path Normalization Bug

**Session:** `7304d4b5` | **Project:** recall-fix | **Date:** 2026-02-13

Post-deliverable-review fix that revealed systematic zero recall from path mismatches.

> **Agent:** Now I can see the issue. The fixture has 1 Grep + 2 Reads = 3 tool calls.
>
> **M-2: Path normalization** - The issue is that `Path.__eq__` requires exact match. Real sessions use absolute paths while index entries use relative paths. Need to normalize by comparing path suffixes.
>
> **M-1: e2e test** - The assertion expects 4 tool calls but the fixture has 3.

This bug (commit `8df92e27`) caused the recall analysis to show 0% recall for entries where agents actually did read the relevant files — absolute vs relative path comparison failure masked real usage.

### Excerpt 7: Active Recall Architecture — Forced Injection as Core Design

**Session:** `ae5d319e` | **Project:** active-recall-system | **Date:** 2026-03-06

Requirements capture session that defined the active recall system vision.

> From the brief (loaded in session): "Replace training-data reliance for operational methodology with grounded recall. Training provides reasoning capability; recall provides authoritative inputs to reason over. Interaction structure (skills, tool gates, PreToolUse hooks) enforces application at the right moments."

The requirements document (commit `60de1237`) formalized:
- FR-1: Hierarchical index structure (split flat 449-line index into domain tree)
- FR-2: Broaden trigger classes beyond project decisions
- FR-3: External environment facts with version-keyed invalidation
- FR-4: Bulk conversion from documentation sources

### Excerpt 8: Context7 as Query-Keyed Cache, Not Bulk Import

**Session:** `cff6fd79` | **Project:** active-recall-system | **Date:** 2026-03-03

Design discussion that refined how external knowledge enters the system.

> **User:** d: no bulk import, evaluate context7 as query-keyed memory class

> **Agent:** Bulk import (FR-4 style) produces entries that may never be queried. The recall system already has a recognition problem [...]. Cached queries, by contrast, are self-selecting: they were needed once, and the cache serves as replay for the next occurrence.

> **User:** Stop repeating the "4.1%" number, it pertained agent-initiated passive recall, and included user-initiated recall. Not very accurate, and not relevant to active recall.

> **Agent:** Fair point. The 4.1% figure measured `/when` skill invocations across all sessions — it conflates agent-initiated and user-initiated usage, and it measured the passive lookup tool, not the recognition problem itself. Citing it as evidence for the demand-driven argument was sloppy.

---

## 3. Key Inflection Points

### Inflection 0: Agent Instructions as Memory (Sep–Nov 2025)

**When:** Sep 30, 2025 (rules.md) → Nov 28, 2025 (oklch-theme "Agent Memory")
**What changed:** Agent instructions evolved from human-curated static rules (rules.md, `7b0a4b4`) to an agent→file write loop (oklch-theme, `b0c0d64`). The oklch-theme AGENTS.md was titled "Agent Memory" and instructed: "At the end of each session, perform a retrospective and update this file with reusable feedback."
**Evidence:** rules `7b0a4b4`, oklch-theme `b0c0d64`.
**Significance:** The memory problem was identified before claudeutils existed. Each agent session started blank; the file was the persistence mechanism. The oklch-theme approach — agent writes to the same file it reads — is the simplest memory architecture. Its limitation: unbounded growth, no structure, no cross-project sharing.

### Inflection 0.5: Structured File Taxonomy (Jan 2026)

**When:** Jan 12, 2026
**What changed:** home introduced a file organization table separating behavioral direction (AGENTS.md), session context (session.md), design rationale (design-decisions.md), and artifacts (plans/). Memory was distributed across files by content type rather than dumped into a single file.
**Evidence:** home `e31a4c0`.
**Significance:** This is the architectural predecessor of the memory-index. The problem it solved: a single AGENTS.md containing rules, session state, decisions, and plans grows unwieldy. The solution: separate files with defined roles. This taxonomy transferred directly to claudeutils.

### Inflection 1: Always-Loaded to Active Lookup

**When:** Feb 1 → Feb 8-13
**What changed:** memory-index.md started as an always-loaded `@`-reference in CLAUDE.md (3.7k tokens consumed every session). The `/when` and `/how` skills were built to make recall on-demand, reducing token cost.
**Evidence:** Commits `9a5f9f71`, `6e88a294` (creation), then `00b8ec35` through `f2715734` (when-recall implementation).
**Trigger:** Token cost concern — 3.7k tokens for an index that grew with every codified learning.

### Inflection 2: The Measurement Inflection

**When:** Feb 20
**What changed:** Quantitative evaluation revealed `/when` was invoked in only 4.1% of post-merge sessions. The tool changed the retrieval mechanism but not the recognition step. Decision file reads were unchanged (21.2% → 21.8%).
**Evidence:** Commit `c4b1e043`, session `f9e199ea`.
**Trigger:** Context optimization work needed usage data to justify demoting memory-index from always-loaded.
**Consequence:** Unblocked memory-index.md demotion. Shifted design direction from "better tools for agents" to "forced injection by infrastructure."
**Caveat:** The 4.1% figure included user-initiated testing. The actual spontaneous agent recall rate, measured later (Phase G), was 0%.

### Inflection 3: Metacognitive Recognition Bottleneck Named

**When:** Feb 20
**What changed:** The failure was diagnosed not as tool-awareness (agent doesn't know `/when` exists) but as metacognition (agent doesn't recognize it's in a situation where it should doubt its defaults). This distinction matters because it rules out an entire class of fixes (better descriptions, more prominent placement).
**Evidence:** Session `f9e199ea` — "The mechanism that fails is not 'recognition of /when as a tool' but 'recognition of uncertainty as a state requiring action.'"
**Consequence:** Procedural triggers (action boundaries) work; metacognitive triggers (uncertainty recognition) don't. This explains why `/commit` and `/handoff` succeed but `/when` fails.

### Inflection 4: Prose-Only Gates to Tool-Anchored Gates

**When:** Feb 24
**What changed:** Inventory revealed 61% of recall gates were prose-only — no tool call to enforce execution. Root cause: "Execution-mode cognition optimizes for next tool call. Steps without tool calls register as contextual commentary."
**Evidence:** Commit `7ee9d0c0`, session `3a299440`, `recall-gate-inventory.md`.
**Trigger:** Documented bypasses where deliverable-review ran without recall.

### Inflection 5: Forced Injection Architecture

**When:** Feb 20 (conceptualized) → Mar 1 (implemented) → Mar 6 (redesigned as active recall)
**What changed:** Recognition shifted from agent to deterministic code. UserPromptSubmit hooks detect topic keywords and inject relevant decision content. The memory-index becomes a backing store queried by scripts, not by agents.
**Evidence:** Commit `f4de036b` (topic detector hook), `43abd7fe` (active recall design with 7 architectural decisions).
**Trigger:** The measurement data plus the 84% activation rate for forced-eval hooks (from prior learnings) made the design choice obvious — forced injection at 84% beats voluntary recall at 0%.

### Inflection 6: From Flat Index to Hierarchical Domain Tree

**When:** Mar 2-6
**What changed:** The flat memory-index.md (449 lines, 366 entries) was recognized as unsustainable. Active recall system design introduced hierarchical index: `agents/memory/index.md` → `agents/memory/<domain>.md` → sub-domains. Prefix-free key structure with colon-delimited domains.
**Evidence:** Commit `60de1237` (FR-1), session `cff6fd79` (domain discussion), commit `de5ddfdd` (8 sub-problems DAG).
**Trigger:** Index growth from codify cycles (24-50 learnings consolidated per session) made flat file unwieldy for both token cost and navigation.

### Inflection 7: 0% Spontaneous Recall Confirmed

**When:** Mar 2026
**What changed:** Direct measurement across 129 recall tool invocations found zero spontaneous agent-initiated lookups. Every invocation was skill-procedural (87.6%) or user-triggered (12.4%). The "actionable index" concept — always-loaded entries triggering agent recognition — never worked.
**Evidence:** `plans/measure-agent-recall/report.md`.
**Significance:** This closes the loop on the memory system narrative. The full arc: rules-as-memory (Sep 2025) → structured files (Jan 2026) → always-loaded index (Feb 1) → active lookup tools (Feb 13) → measured failure (Feb 20) → forced injection (Mar 1) → 0% confirmed (Mar 2026). Every approach that relied on agent recognition failed. The only approaches that achieved recall were procedural (mandated by skill steps) or infrastructural (forced by hooks).

---

## 4. The Full Arc

```
Human-written flat rules (rules, Sep 2025)
  → Agent retrospective self-update (oklch-theme, Nov 2025)
    → Filtering criterion for persistence (box-api, Nov 2025)
      → Structured file taxonomy (home, Jan 2026)
        → Shared infrastructure extraction (plugin, Jan 2026)
          → Always-loaded memory index (Feb 2026)
            → Active lookup tools /when, /how (Feb 2026)
              → 4.1% usage measured, recognition bottleneck named (Feb 20)
                → Recall gate inventory, 61% prose-only (Feb 24)
                  → Tool-call-anchored gates (Feb 25)
                    → Forced injection via hooks (Mar 1)
                      → Active recall system design (Mar 6)
                        → 0% spontaneous recall confirmed (Mar 2026)
```

The pre-claudeutils history (Sep 2025–Jan 2026) adds five months of evidence showing the memory problem was identified and iterated on before the formal memory-index existed. The post-measurement history (Feb 20 onward) shows the shift from "give agents better tools" to "make infrastructure do the recalling."
