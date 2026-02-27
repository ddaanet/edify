# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When a proximal requirement reveals lifecycle gaps
- Triage feedback (Gap 7) required a post-execution comparison point. Investigation: /commit too generic (fires all sessions), /handoff wrong scope (session state not execution assessment). Root cause: inline execution (Tier 1, /design direct execution) has no lifecycle skill. The pipeline state machine goes /requirements → /design → /runbook → /orchestrate → /deliverable-review → /commit, but work classified as execution-ready exits through an unstructured gap between /design and /handoff.
- Correct pattern: the proximal requirement points at the structural gap. Fix the gap (inline execution skill covering pre-work + execute + post-work), and the proximal requirement becomes one FR among many.
- Corollary: conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the negative path. A Read returning file-not-found is cheaper than the risk of a missed comparison.
## When implementation modifies pipeline skills
- Anti-pattern: Using the full runbook pipeline (prepare-runbook.py → orchestrator → step files) when the planned work modifies pipeline skills (/design, /runbook) or pipeline contracts. Self-modification coupling: a runbook step that edits the runbook skill creates stale-instruction risk for subsequent steps.
- Correct pattern: Structure as inline task sequence orchestrated through session pending tasks. Each task executes with fresh CLAUDE.md loads, sidestepping stale instructions. TDD discipline preserved — executing session dispatches test-driver via Task tool per cycle. Corrector dispatch per task replaces checkpoint gates.
- Also applies when: no parallelization benefit (strict dependency chain negates Tier 3's parallel step execution), overhead/value mismatch (pipeline coordination cost > error-recovery value for ~10 sequential work units).
## When delegating TDD cycles to test-driver
- Anti-pattern: Sending all N cycles in a single prompt. Agent loses focus on later cycles, context overloaded with spec it hasn't reached yet. Also: full prompt may trigger hooks on path patterns in test fixture descriptions.
- Correct pattern: Piecemeal — one cycle per invocation. Resume the same agent for subsequent cycles (preserves accumulated file reads + implementation context). Continue until agent context nears 150k. Fresh agent if context exhausted.
- Context priming: Sub-agents don't share parent context. Each NEW agent must self-prime by running `when-resolve.py` on relevant recall-artifact entries. Include instruction: "Read plans/X/recall-artifact.md, then batch-resolve relevant entries via `agent-core/bin/when-resolve.py`." Resumed agents already have this context.
## When assessing just precommit cost
- `just precommit` is fast when the test suite is green, thanks to test sentinel. Not a heavy operation in the common case — valid as both entry gate and exit gate without redundant overhead concern.
## When editing skill files
- The `description` field is dual-purpose: CLI picker display AND agent triggering (no separate field — #28934). Lead with action verb (user display), then trigger phrases (agent matching). H1 title is body content only. Fallback: first paragraph if `description` omitted.
- Extraction safety: every content block moved to references/ must leave trigger condition + Read instruction in SKILL.md body.
- Control flow verification: after restructuring conditional branches, enumerate all paths, verify user-visible output on each.
- D+B gate additions: must not change gate decision outcome on existing paths.
- Entry point naming: named entry points (`execute`) not `--flag` conventions. Skills parse prose args, not CLI flags.
- Prose quality: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
- Pending: consolidate into `/skill-dev` skill (front-loads plugin-dev:skill-development via continuation passing)
