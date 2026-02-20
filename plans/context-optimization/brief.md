# Brief: Context Optimization — Fragment Demotion

**Source:** Discussion session 2026-02-20. Motivated by /context output showing 25.5k tokens (50% of 51k used) in memory files.

## Problem

Always-loaded fragments via CLAUDE.md @-references consume 25.5k tokens. This is the floor before any skill loads, conversation, or tool results. Most sessions also load worktree/design/runbook/orchestrate/deliverable-review skills, compounding the base cost.

## Analysis: What's truly incompressible

~5.5k tokens of behavioral rules shape every interaction (deslop, communication, execution-routing, session modes, token-economy, no-estimates, no-confabulation). Plus ~2k reference (session.md, CLAUDE.md hub). Everything else is either reference material, workflow-specific, or linearly growing.

## Demotable fragments (~6.6k tokens, ~26%)

| Fragment | Tokens | Mechanism |
|---|---|---|
| sandbox-exemptions (full) | 986 | Sandbox denylist + recipes handle bypass internally. Worktree skill already duplicates content. |
| claude-config-layout (full) | 984 | Inject via hook-dev/plugin-dev skills when working with hooks/config. |
| project-tooling (full) | 836 | Replace with sandbox denylist (operational) + PreToolUse hook (informative redirect). |
| bash-strict-mode (full) | 365 | Redundant — points to /token-efficient-bash skill which contains the full content including || true reconciliation. |
| vet-requirement (full) | 2,400 | Commit skill Step 1 already implements the full vet gate (proportionality, report check, UNFIXABLE escalation). Fragment is passive — agents don't vet because they read the fragment; they vet because commit skill enforces it. |
| workflows-terminology (partial) | ~588 | Keep ~100 token terminology stub. Demote pipeline description — inject via design/runbook/orchestrate skills. |
| error-handling (detail) | ~491 | Keep ~150 token core rule ("errors never pass silently"). Demote layer table and hook error protocol. |

## Fragments that stay (with reasoning)

- **pushback (455)** — Ambient behavioral shaping. Agreement momentum tracking fires in any evaluative context, not just d: directive. Core communication protocol.
- **delegation (509)** — Needed by any skill with execution access (design, runbook, deliverable-review), not just orchestrate. Cross-cutting "do directly vs delegate" boundary.
- **tool-batching (279)** — Cross-cutting, no injection point. Edit precondition cascade warning prevents wasted parallel calls.
- **code-removal (270)** — No injection point. Without it, LLM defaults to archiving. 270 tokens is small.
- **design-decisions (253)** — No injection point before the decision moment. Without it, agent asks user instead of consulting opus.
- **project-tooling (836)** — Replaced by denylist+hook (see hook-batch plan), not simply demoted.

## Blocked items (not demotable yet)

- **learnings.md (6.1k)** — Consolidation via /remember is premature. Entries need aging to confirm validity before graduating to permanent docs. 80-line soft limit is attention budget, not consolidation trigger.

## Unblocked: memory-index.md (3.7k tokens → demotable)

**Usage data now exists** (from when-recall-evaluation worktree, 2026-02-20):

- 801 sessions scanned across 71 project directories (main + worktrees)
- `/when` invoked in 8 of 193 post-merge sessions (4.1%), 22 total calls
- All clustered in one week — likely orchestration-prompted, not organic
- Direct decision file reads unchanged: 21.2% pre → 21.8% post
- Total improvement over baseline: 1.1× (noise)

**Root cause:** `/when` requires metacognitive recognition ("I might be wrong about this decision") — same bottleneck as passive index scanning. Changing the action (Read → Skill) didn't change the recognition step. Agents confident in their approach don't seek contrary guidance.

**Recommendation:** Demote memory-index.md from always-loaded. 3.7k tokens for 4.1% usage is the worst cost/benefit ratio in CLAUDE.md. The index still works as a backing store — `/when` skill loads it on demand. Removing it from context saves tokens without degrading recall (already near-zero organic usage).

**Implication for hook batch:** If hook-based topic detection + forced injection lands (Phase 1 items 8-9), the hook script can query the index mechanically. The index becomes infrastructure for hooks, not agent-visible context. This reinforces demotion — the index serves code, not the agent's attention.

## Dependencies

- **Hook batch must land first:** Sandbox denylist + PreToolUse hook replace project-tooling.md. Without them, removing the fragment loses enforcement with no replacement.
- **Skill injection points:** Each demoted fragment needs content added to the skills that consume it. Maintenance cost: each fragment now has N sites instead of 1.

## Sandbox denylist (manual, user action)

Block these commands from sandbox bypass (forces recipe usage):
- `git merge` → use `claudeutils _worktree merge`
- `git worktree` → use `claudeutils _worktree`
- `ln` → use `just sync-to-parent`

NOT blocking `git commit` — /commit skill uses it internally. Deferred until Session CLI (`_session commit`) provides the wrapper.

## Key discussion conclusions

- Vet-requirement fragment is passive — never fires as ambient awareness. Commit skill gate is the actual enforcement. Remove entirely, no stub needed.
- "Frequently useful" ≠ "always needed." Initial analysis was too conservative.
- doc-writing and release-prep skills are rarely used but full-session when active. Include them in fragment dispatch analysis as injection targets.
- ~20% savings near-term → ~34% with memory-index demotion (+3.7k tokens), ~38% after Session CLI unblocks vet-requirement and execute-rule demotion.
- Evidence: `tmp/when-recall-eval-report.md` and `tmp/when-recall-eval.py` in when-recall-evaluation worktree.
