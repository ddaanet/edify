# Topic Cross-Reference — New Evidence Mapped to Existing 5 Topics

Maps evidence from expanded repos to the 5 existing retrospective topics.

## Topic 1: Memory System Evolution

**Pre-edify origins of agent memory:**

| Date | Repo | Hash | Evidence |
|------|------|------|----------|
| 2025-09-30 | rules | `7b0a4b4` | Initial `rules.md` — proto-memory. Rules written by human, consumed by agent. No agent self-modification. |
| 2025-10-02 | rules | `eacf188` | Rename to AGENTS.md — file naming as memory convention. |
| 2025-11-28 | oklch-theme | `b0c0d64` | AGENTS.md titled "Agent Memory" with retrospective self-update protocol: "At the end of each session, perform a retrospective and update this file." First explicit agent→file write loop. |
| 2025-11-23 | box-api | `0bbdbf8` | AGENTS.md with session-specific rules. "Include any feedback that is general enough in scope" — filtering criterion for what to remember. |
| 2026-01-12 | home | `e31a4c0` | File organization table with session.md, design-decisions.md. Memory distributed across file types by content. |
| 2026-01-12 | pytest-md | `69bf88b` | Session log design — structured conversation state persistence. |
| 2026-01-15 | pytest-md/plugin | `5783aef` | Agent-core initialized — memory patterns extracted into shared infrastructure. |
| 2026-02-27 | home | `ebcabc1` | Memory infrastructure setup — decision files consolidated. |

**Arc:** Human-written rules (rules) → agent retrospective self-update (oklch-theme) → structured file taxonomy (home) → shared infrastructure (plugin) → memory-index + recall system (edify).

## Topic 2: Pushback Protocol

**Pre-pushback state in early agent instructions:**

| Date | Repo | Hash | Evidence |
|------|------|------|----------|
| 2025-09-30 | rules | `7b0a4b4` | "Proceed autonomously without asking" — anti-pushback directive. Agent directed to work without stopping. |
| 2025-10-12 | emojipack | `9cc5c62` | "#auto Proceed autonomously without asking until all tasks complete" — same pattern. No evaluation before action. |
| 2025-10-25 | tuick | `7d2fa67` | Same emojipack template, no pushback mechanisms. |
| 2025-12-01 | oklch-theme | `64cbf8f` | "LLM Limitation Awareness" — metacognitive rules asking agent to flag uncertainty. Same class of wishful thinking as tuick's cognitive protocols — assumes confidence-monitoring capability that doesn't exist. |
| 2025-12-12 | tuick | `a3e15a1` | "Cognitive protocols and rule improvements" — explicit metacognition rules (later removed). Overengineered attempt at structured self-awareness. |
| 2025-12-15 | tuick | `26c3b5d` | "Remove epistemic standards" — pullback from cognitive protocol experiment. Too heavy-handed. |
| 2026-01-13 | home | `37b08e7` | "Require protocol read before execution" — structural enforcement replacing trust-based compliance. |

**Arc:** "Proceed autonomously" (no pushback) → metacognitive wishful thinking (oklch-theme "flag uncertainty", tuick cognitive protocols — both dead ends) → structural enforcement (home) → formalized pushback protocol (edify).

## Topic 3: Deliverable-Review Origins

| Date | Repo | Hash | Evidence |
|------|------|------|----------|
| 2025-10-18 | emojipack | `996158f` | "Red-Green does not apply when removing code" — first quality gate exception. Review of process, not output. |
| 2025-12-08 | tuick | `5bd7536` | "Require explanatory comments for all suppressions" — quality enforcement at commit level. |
| 2026-01-30 | pytest-md | `de59b20` | "Phase 5-6 TDD runbook with design and agent tooling" — structured review within execution phases. |
| 2026-03-10 | devddaanet | `265c8c7` | "Deliverable review worktree-sync: 1 critical, 3 minor" — deliverable-review in production use. |
| 2026-03-10 | devddaanet | `cae9155` | "Fix worktree-sync deliverable-review findings" — review→fix cycle working as designed. |
| 2026-03-10 | devddaanet | `4ffb1ea` | "Re-review: all findings resolved, delivered" — review loop completed, but 3 of next 5 commits are bug fixes the review missed. |

**Arc:** Ad-hoc quality rules → structured process review → deliverable-review skill in production. devddaanet shows the pipeline runs outside edify but also its limits — post-delivery bug fixes show the review gate ensures a review happens, not that it catches everything.

## Topic 4: Ground Skill Origins

| Date | Repo | Hash | Evidence |
|------|------|------|----------|
| 2025-09-30 | rules | `824ed21` | "Incorporate zed rules into rules.md, adjusted by hand" — human-mediated knowledge import. External source → manual integration. |
| 2025-11-23 | box-api | `791a962` | "Flesh out AGENTS.md (incorporate relevant rules for tuick)" — cross-project rule import. Pattern: take rules from one project, adapt for another. |
| 2025-12-15 | tuick | `7a97ef3` | "Restructure agent rules into multi-agent system" — methodology-level restructuring. |
| 2026-01-08 | ddaanet | `bacd587` | "Document template-based design refactoring in design decisions" — methodology documentation. |

**Notes:** Ground skill origins are mostly internal to edify (confabulated scoring → diverge-converge research). External repos show the precursor pattern: manual knowledge curation from external sources, but no grounding-as-methodology.

## Topic 5: Structural Enforcement / Gating

| Date | Repo | Hash | Evidence |
|------|------|------|----------|
| 2025-10-12 | emojipack | `9cc5c62` | "`just agent` before every commit" — first commit gate. Mechanical enforcement via recipe. |
| 2025-10-25 | tuick | `7d2fa67` | Same commit gate pattern propagated. |
| 2025-11-23 | box-api | `0bbdbf8` | Agent-specific `just` recipes: `just agent`, `just agent-check`, `just agent-test`. Separation of agent and human commands — structural role differentiation. |
| 2025-12-05 | box-api | `b3aa473` | "One-letter commands" — shorthand for frequent agent operations. |
| 2026-01-03 | pytest-md | `fd939eb` | `.claude/settings.json` — platform-level configuration as enforcement. |
| 2026-01-13 | home | `deb0d91` | Orchestrator constraints: "Allowed/Delegate" model. Structural separation of what orchestrator can and cannot do. Proto-gating. |
| 2026-01-13 | home | `37b08e7` | "Require protocol read before execution" — read-before-act gate. |
| 2026-01-22 | home | `83cef17` | Agent-core submodule — enforcement via shared infrastructure. Rules can't drift per-project. |

**Arc:** `just agent` gate (emojipack) → agent-specific recipes (box-api) → platform config (pytest-md) → orchestrator constraints (home) → shared infrastructure (plugin) → D+B tool-call anchoring → PreToolUse hooks (edify).
