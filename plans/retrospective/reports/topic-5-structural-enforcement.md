# Topic 5: Structural Enforcement — Evidence Bundle

## Git Timeline

### Phase 0: Pre-history — Commit Gates and Role Separation (Oct 2025–Jan 2026)

Structural enforcement didn't begin with D+B anchoring. The first enforcement mechanisms appeared five months earlier as commit gates and role separation.

| Date | Repo | Hash | Event |
|------|------|------|-------|
| 2025-10-12 | scratch/emojipack | `9cc5c62` | "`just agent` before every commit" — first commit gate. Mechanical recipe as enforcement. |
| 2025-10-25 | tuick | `7d2fa67` | Same commit gate propagated. Template-copy enforcement. |
| 2025-11-23 | scratch/box-api | `0bbdbf8` | Agent-vs-human command separation: `just agent` (AI), `just dev` (human). Structural role differentiation. |
| 2025-12-05 | scratch/box-api | `b3aa473` | "One-letter commands" — shorthand for frequent agent operations. |
| 2026-01-03 | scratch/pytest-md | `fd939eb` | `.claude/settings.json` — platform-level configuration as enforcement. Rules encoded in platform, not prose. |
| 2026-01-13 | scratch/home | `deb0d91` | Orchestrator constraints: "Allowed/Delegate" model. What orchestrator can and cannot do, structurally enforced. |
| 2026-01-13 | scratch/home | `37b08e7` | "Require protocol read before execution" — read-before-act gate. |
| 2026-01-22 | home | `83cef17` | Agent-core submodule — enforcement via shared infrastructure. Rules can't drift per-project. |

**Enforcement escalation in pre-history:**

| Level | Mechanism | First appearance |
|-------|-----------|-----------------|
| Recipe gate | `just agent` before commit | emojipack, Oct 2025 |
| Role separation | Agent vs human commands | box-api, Nov 2025 |
| Platform config | `.claude/settings.json` | pytest-md, Jan 2026 |
| Structural constraints | Allowed/Delegate model | scratch/home, Jan 2026 |
| Read-before-act | Protocol read required | scratch/home, Jan 2026 |
| Shared infrastructure | Agent-core submodule | home, Jan 2026 |

The pre-history shows enforcement escalating through the same pattern as the claudeutils era — each mechanism addresses failures of the previous one — but at a coarser granularity. `just agent` prevents bad commits; role separation prevents wrong tool usage; platform config prevents configuration drift. The claudeutils era applies the same principle at the instruction-following level.

### Phase A: Foundation (Feb 8)

| Date | Commit | Event |
|------|--------|-------|
| 2026-02-08 | `e3d26b1e` | Document defense-in-depth quality gate pattern (first D+B mention) |

Defense-in-depth document (`e3d26b1e`) establishes the four-layer model and names the D+B hybrid pattern: "merge prose gates with adjacent action steps, anchor with tool call." This is the theoretical framework.

### Phase B: Discovery + Inventory (Feb 21-24)

| Date | Commit | Event |
|------|--------|-------|
| 2026-02-21 | `5f4801cc` | Deploy first PreToolUse hooks via sync-to-parent |
| 2026-02-24 | `7ee9d0c0` | Design recall gate tool-anchoring (31 gates inventoried, 61% prose-only) |
| 2026-02-24 | `66f58df0` | Runbook for recall-tool-anchoring (promoted from outline) |

PreToolUse hooks deployed (`5f4801cc`). Recall gate audit reveals 31 gates across 13 files, 61% prose-only (`7ee9d0c0`). The problem quantified: most quality gates exist only as prose instructions that agents skip under execution momentum.

### Phase C: Structural Remediation (Feb 24-25)

| Date | Commit | Event |
|------|--------|-------|
| 2026-02-24 | `cd45d076` | Replace language strengthening with structural remediation in /reflect |
| 2026-02-24 | `e1a35cd1` | Restructure design skill triage with 4 structural fixes |
| 2026-02-25 | `59904514` | Anchor recall gates with when-resolve.py in /reflect and /runbook |
| 2026-02-25 | `8a19b983` | Add PreToolUse hook blocking index.lock removal |

Three commits in 36 hours replace prose gates with tool-call-anchored gates: /reflect (`cd45d076`), /design triage (`e1a35cd1`), recall gates (`59904514`). Language strengthening explicitly rejected in favor of structural fixes.

### Phase D: Hook Evolution (Feb 26-28)

| Date | Commit | Event |
|------|--------|-------|
| 2026-02-26 | `f2d49839` | Add python3/uv redirect hook; shorten all hook commands |
| 2026-02-26 | `97569f3e` | Migrate hooks to permissionDecision:deny; improve UPS systemMessage |
| 2026-02-28 | `8b9f0185` | Plan recall-null: D+B gate anchoring + post-explore gates |
| 2026-02-28 | `654f7ec7` | Fix hook cwd-drift bypass via absolute paths |
| 2026-02-28 | `df886503` | Add null mode to when-resolve.py and propagate D+B gate anchoring |
| 2026-02-28 | `2293da87` | Runbook outline for UPS topic injection |

PreToolUse hooks gain recipe-redirect (`f2d49839`), permissionDecision:deny (`97569f3e`), cwd-drift fix (`654f7ec7`). D+B null mode (`df886503`) propagated across pipeline skills.

### Phase E: Topic Injection Attempt + Removal (Feb 28–Mar 6)

| Date | Commit | Event |
|------|--------|-------|
| 2026-03-01 | `b213939c` | Restructure UPS topic injection from orchestrate to inline |
| 2026-03-01 | `e253c43f` | UPS topic deliverable review (0C/0Ma/3Mi) |
| 2026-03-06 | `108a444d` | Remove UPS topic injection (Tier 2.75) — "noisy, low relevance" |

UPS topic injection built as ambient recall via keyword matching from user prompts. Delivered with clean review (`e253c43f`). Removed 5 days later (`108a444d`) — "noisy, low relevance." 896 lines deleted. The structural enforcement via hooks (PreToolUse) proved more effective than semantic matching (topic injection).

---

## Session Excerpts

### Excerpt 1: The Discovery — Prose Gates Get Skipped

**Session:** `21fea8cf` | **Project:** recall-tool-anchoring
**Context:** Agent ran /reflect after skipping a recall step during /runbook execution

> **Phase 3: Root Cause Analysis**
>
> **Proximal cause:** The design skill content was in context (it ran the triage), and the runbook skill was injected as a command. When Tier 1 assessment completed, the agent scanned for what to do next and landed on "file discovery" (Phase 0.5) rather than the recall step that precedes it. The recall step is prose-only with no anchoring tool call at the start — it says "Read memory-index.md (skip if already in context)." The skip condition ("if already in context") was evaluated incorrectly: memory-index.md was NOT in context, but the agent pattern-matched the *class* of thing ("I've done recall-ish work in loading the skill") rather than the specific check.
>
> **Contributing factors:**
> - Tier 1's recall instruction sits at the top of the Tier 1 section as prose — no gate tool call anchors it. The first concrete tool calls are in the file discovery block. The agent skipped to the tool call.
> - The "skip if already in context" language is a weak gate: it invites the agent to claim the skip condition without verifying it.

This is the inflection point: a prose-only instruction was skipped not because the agent couldn't understand it, but because execution momentum pulled toward the next tool call. The prose gate had no structural anchor.

### Excerpt 2: D+B Pattern Named and Classified

**Session:** `21fea8cf` | **Project:** recall-tool-anchoring

> **Rule gap analysis:**
> - The rule is clear but skippable — it's prose without a D+B anchor. Same pattern class as "When Preventing Skill Steps From Being Skipped" (implementation-notes.md: "Every skill step must open with a concrete tool call (Read/Bash/Glob)"). The recall step doesn't open with a concrete Read — it opens with a conditional skip.
>
> **Phase 4: Classify Fix Scope**
>
> | Layer | Classification | Fix |
> |---|---|---|
> | Rule text | **Rule fix** — no anchor tool call | Add Bash/Read anchor to Tier 1 recall step |
> | Agent behavior | **Behavioral** — substituted related work | Strengthen skip condition language |
> | Pattern | **Systemic** — D+B anchor class | Apply established fix pattern |

The diagnosis identifies the systemic pattern: prose gates need tool-call anchoring. This connects to the defense-in-depth document's Layer 1 pattern and names it as a class of fix applicable across the codebase.

### Excerpt 3: Gate Inventory — Quantifying the Problem

**Commit:** `7ee9d0c0` (2026-02-24)
**Commit message:** "Design recall gate tool-anchoring (31 gates, 61% prose-only)"

From the session handoff:
> - Gate inventory: 31 gates across 13 files, 61% prose-only (report: `plans/recall-tool-anchoring/reports/recall-gate-inventory.md`)
> - Outline through 3 discussion rounds: D+B hybrid application, reference manifest format, throwaway prototype
> - Key decisions: reference manifest forces tool-anchoring structurally (format requires resolution call)

The audit quantified the vulnerability: 19 of 31 recall gates existed only as prose instructions. The design insight was that changing the recall-artifact *format* from content dumps to thin trigger lists would force a tool call (resolution) — the format itself becomes the structural enforcement.

### Excerpt 4: Structural Enforcement Named Explicitly

**Session:** `4d31c984` | **Project:** fix-ups-topic-findings
**Context:** Agent misclassified a behavioral code change as Simple during triage, skipping TDD

> **This is the second recurrence** of this pattern (first was codified to `agents/decisions/workflow-planning.md`). The learning and decision entry exist but didn't prevent the deviation. Language strengthening won't help — this needs structural enforcement.

The phrase "language strengthening won't help — this needs structural enforcement" marks the explicit rejection of prose-based fixes. Two prior attempts to fix via better wording had failed. The pattern: a codified decision existed, the agent had it in context (via topic injection), and still violated it. Prose rules are necessary but insufficient.

### Excerpt 5: D+B Anchor Firing But With Wrong Arguments

**Session:** `4d31c984` | **Project:** fix-ups-topic-findings

> The D+B anchor fired (tool call happened) but with wrong arguments. [...] conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the signal.

This reveals a subtlety: even after adding tool-call anchoring, conditional gates reintroduce the prose-gate failure mode. The fix is unconditional execution — the tool call always runs, and the *absence* of the expected file is the signal, not a prose-level decision about whether to call the tool.

### Excerpt 6: PreToolUse Hook Evolution

**Session:** `eaeb3710` | **Project:** userpromptsubmit-topic

From defense-in-depth document read during session:
> 1. **Layer 1 — Outer defense (Execution Flow):** D+B hybrid (merge prose gates with adjacent action steps, anchored by tool call)

And from hooks configuration:
> ```json
> "PreToolUse": [
>   {
>     "matcher": "Bash",
>     "hooks": [{ "type": "command", "command": "p..." }]
>   }
> ]
> ```

PreToolUse hooks represent the next escalation: from in-skill D+B anchoring (agent-mediated) to platform-level enforcement (hook-mediated). The `matcher` field enables targeted enforcement per tool type — Bash commands get recipe-redirect checking, preventing `python3` prefix that breaks permissions.allow matching. This is enforcement the agent cannot bypass.

### Excerpt 7: Topic Injection — The Keyword Matching Attempt

**Session:** `cc1c5f34` | **Project:** rm-ups-topic

> That last recall entry is particularly telling — it documents the *motivation* for building the UPS topic injection in the first place: agents self-retrieve at ~4% rate, so forced injection via hooks was designed to bypass the recognition gap. The task now is to remove it because in practice it's "noisy, low relevance" — the cure was worse than the disease.

**Commit:** `108a444d` (2026-03-06) — 896 lines deleted (307-line module, 584 lines of tests)

The topic injection attempted structural enforcement of recall by injecting relevant decisions into every prompt via keyword matching. It was architecturally sound (delivered clean: 0C/0Ma/3Mi in review, commit `e253c43f`), but the keyword matching produced low-relevance hits. The structural mechanism (hook injection) was correct; the semantic layer (keyword matching for relevance) was not precise enough.

### Excerpt 8: The Recall Gate Anchoring Implementation

**Session:** `20545bb6` | **Project:** recall-tool-anchoring

From the session handoff (commit `3bf1e59a`):
> **RCA: skipped recall in /design -> /runbook Moderate path:**
> - /design triaged Moderate correctly, routed to /runbook Tier 1
> - No recall pass executed — "skip if already in context" escape hatch allowed full skip
> - On-disk skills already had triage recall D+B anchor (commit `e1a35cd1`) but injected versions were stale

Key implementation commits on this branch:
- `cd45d076` — Replace language strengthening with structural remediation in /reflect
- `e1a35cd1` — Restructure design skill triage with 4 structural fixes
- `59904514` — Anchor recall gates with when-resolve.py in /reflect and /runbook

The implementation replaced prose gates with `when-resolve.py` calls — a script that reads the recall artifact and resolves entries. The tool call is the gate: if recall-artifact.md exists, entries get resolved; if not, the null result is the signal. No prose-level skip conditions.

---

## Key Inflection Points

### Inflection 0: The First Commit Gate (Oct 2025)

**When:** Oct 12, 2025
**Evidence:** scratch/emojipack `9cc5c62`, tuick `7d2fa67`, scratch/box-api `0bbdbf8`
**What:** "`just agent` before every commit" — the first structural enforcement of quality. A recipe that must run before committing. Not prose advice ("run tests before committing") but a named gate in the workflow.
**Significance:** This is structural enforcement at the workflow level, five months before D+B anchoring. The same principle (mechanical check, not advisory instruction) applied to a different problem (commit quality, not instruction following). The evolution: recipe gates → platform config → orchestrator constraints → D+B tool-call anchoring → PreToolUse hooks.

### Inflection 0.5: Platform-Level Configuration (Jan 2026)

**When:** Jan 3, 2026
**Evidence:** scratch/pytest-md `fd939eb`, scratch/home `deb0d91`
**What:** `.claude/settings.json` moves enforcement from per-session instructions to platform configuration. Orchestrator constraints (Allowed/Delegate model) structurally limit what the orchestrator can do — not via prose rules but via role definitions.
**Significance:** The enforcement moves from "instructions the agent should follow" to "configuration the platform enforces." This is the same conceptual step that PreToolUse hooks later take: enforcement at a layer the agent cannot bypass through rationalization.

### Inflection 1: Prose-to-Structure Threshold (Feb 24)

The recall gate skip (session `21fea8cf`) proved that clearly-written prose instructions with conditional skip clauses are systematically unreliable under execution momentum. The agent substituted "related activity" for "specific required action" — a pattern that repeated across multiple contexts. This drove the gate inventory (`7ee9d0c0`) and the systematic D+B remediation.

### Inflection 2: Language Strengthening Rejected (Feb 24–Mar 2)

Three commits explicitly chose structural fixes over language fixes:
- `cd45d076`: "Replace language strengthening with structural remediation in /reflect"
- `e1a35cd1`: "Restructure design skill triage with 4 structural fixes"
- Session `4d31c984`: "Language strengthening won't help — this needs structural enforcement"

The evidence was recurrence: the same pattern violated twice despite codified decisions, learnings, and recall entries. Each prose-level mitigation added words; the agent still skipped.

### Inflection 3: Conditional-to-Unconditional Gate (Mar 2)

Session `4d31c984` revealed that even tool-call-anchored gates fail when conditional: "D+B anchor fired but with wrong arguments." The fix: unconditional execution. The tool always runs. File absence is the signal, not a prose-level decision about whether to run the tool. This is the D+B principle's mature form.

### Inflection 4: Hook-Level Enforcement (Feb 21–Feb 28)

PreToolUse hooks represent enforcement the agent cannot bypass:
- `5f4801cc` (Feb 21): First hook deployment
- `8a19b983` (Feb 25): Block index.lock removal
- `f2d49839` (Feb 26): Recipe-redirect (python3 prefix → direct invocation)
- `97569f3e` (Feb 26): permissionDecision:deny migration
- `654f7ec7` (Feb 28): Fix cwd-drift bypass

These hooks enforce at the platform level. The agent cannot "momentum-skip" a PreToolUse hook the way it can skip a prose instruction in a skill file.

### Inflection 5: Semantic Matching Failure (Feb 28–Mar 6)

Topic injection (UPS Tier 2.75) was the attempt to use keyword matching for ambient recall — inject relevant decisions into context without the agent needing to request them. Built, reviewed clean, then removed 5 days later as "noisy, low relevance." The structural hook mechanism worked (injection happened reliably); the semantic layer (keyword matching for relevance determination) produced too many false matches. Structural enforcement works best with deterministic triggers (file existence, tool name matching) rather than semantic matching (keyword overlap).

---

## The Full Enforcement Ladder

```
`just agent` commit gate (emojipack, Oct 2025)
  → Agent-vs-human command separation (box-api, Nov 2025)
    → Platform config: .claude/settings.json (pytest-md, Jan 2026)
      → Orchestrator constraints: Allowed/Delegate (scratch/home, Jan 2026)
        → Shared infrastructure: agent-core submodule (home, Jan 2026)
          → Defense-in-depth document: D+B named (Feb 8)
            → Prose gates skipped under momentum (Feb 24)
              → Gate inventory: 31 gates, 61% prose-only (Feb 24)
                → Language strengthening rejected (Feb 24)
                  → Tool-call-anchored gates (Feb 25)
                    → Conditional gates still fail (Mar 2)
                      → Unconditional gates: file absence = signal (Mar 2)
                        → PreToolUse hooks: platform enforcement (Feb 21-28)
                          → Topic injection: semantic matching fails (Mar 1-6)
```

Each rung exists because the previous one failed under a specific condition. The pre-claudeutils rungs (Oct 2025–Jan 2026) operated at the workflow level (commit gates, role separation, platform config). The claudeutils rungs (Feb–Mar 2026) operate at the instruction-following level (D+B anchoring, hooks). The principle is the same: replace advisory instructions with structural mechanisms.

---

## Meta-Pattern: Connecting the Other Four Topics

Structural enforcement is the meta-pattern that connects the other four retrospective topics:

- **Memory system** (Topic 1): Recall gates were the first domain where prose-only instructions were systematically catalogued (31 gates, 61% prose-only). The D+B remediation originated from recall skip failures.

- **Pushback** (Topic 2): Pushback rules are prose instructions that compete with sycophantic momentum. The same pattern: prose rules get overridden by behavioral momentum. D+B anchoring applies (force a specific verification tool call before agreeing). Pre-history parallel: tuick's cognitive protocols (overengineered metacognition) were the same failure class as verbose prose gates — more words doesn't mean more compliance.

- **Deliverable review** (Topic 3): The review process itself was a structural gate — requiring a specific review skill invocation before marking work as delivered. The `review-pending` planstate enforces this structurally. External validation: devddaanet ran the full review→fix→re-review cycle (commits `265c8c7`, `cae9155`, `4ffb1ea`), confirming the structural gate works outside claudeutils.

- **Ground skill** (Topic 4): Grounding decisions via tool calls (Read the evidence, resolve recall entries) rather than prose reasoning. Same D+B principle: anchor the verification in a tool call, not in prose instructions to "check carefully."

The progression: prose instructions (easily skipped) → D+B tool-call anchoring (agent-mediated, mostly reliable) → recall gates with unconditional execution (format-enforced) → PreToolUse hooks (platform-enforced, agent cannot bypass) → topic injection (semantic matching, partially failed). Each step addresses a failure mode of the previous step, except the last, which overreached by applying structural enforcement to a semantic problem.
