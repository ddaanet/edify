# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)
## RED pass blast radius assessment
- Anti-pattern: Handling unexpected RED pass as isolated cycle issue (skip or retry)
- Correct pattern: Run blast radius across all remaining phase cycles — test each RED assertion against current state
- Classification: over-implementation (commit test, skip GREEN), test flaw (rewrite assertions), correct (proceed)
- Critical finding: Test flaws are deliverable defects — feature silently skipped when test passes for wrong reason
- Protocol: `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`
## Common context signal competition
- Anti-pattern: Phase-specific file paths and function names in global common context section of agent definition
- Correct pattern: Common context must be phase-neutral (project conventions, package structure). Phase-specific paths belong in cycle step files only
- Rationale: Persistent common context is stronger signal than one-time step file input. At haiku capability, persistent signal wins when step file task is semantically ambiguous
- Evidence: 1/42 cycles derailed (3.5), caused by fuzzy.py paths in common context competing with resolver.py in step file
## Vacuous assertion from skipped RED
- Anti-pattern: Committing a test that never went RED without evaluating assertion strength
- Correct pattern: When RED passes unexpectedly, verify assertions would catch the defect class — not just "doesn't crash" but "produces correct results"
- Example: `assert isinstance(relevant, list)` passes on empty list — pipeline silently returns no matches but test passes
- Detection: Check if key assertions distinguish "correct output" from "empty/default output"
## Index exact keys not fuzzy
- Anti-pattern: Using fuzzy matching in validator to bridge compressed triggers to verbose headings
- Correct pattern: Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery
- Rationale: Exact keys are deterministic and debuggable; fuzzy in validation creates invisible mismatches when scores drift below threshold
## DP zero-ambiguity in subsequence matching
- Anti-pattern: Initializing DP matrix with 0.0 for all cells — impossible states (i>0, j=0) indistinguishable from base case (i=0)
- Correct pattern: Initialize score[i>0][j] with -inf, only score[0][j] = 0.0. Impossible subsequences propagate -inf
- Rationale: When score[i-1][j-1] = 0 (no valid match for i-1 chars), transition score[i-1][j-1] + MATCH_SCORE produces positive score from nothing
- Evidence: "when mock tests" scored 128.0 against candidate with no 'o' or 'k' — matched only 5 of 15 chars
## Agent composition via skills frontmatter
- `skills:` YAML frontmatter in agent definitions injects skill content as prompt
- Pattern: wrap fragments as lightweight skills, reference via `skills:` in agent definitions
- No build step needed — native mechanism, stays current automatically
- 6 agents now use skills: (vet-fix-agent, design-vet-agent, outline-review-agent, plan-reviewer, refactor, runbook-outline-review-agent)
## Sub-agent memory recall transport
- Sub-agents lack Skill tool, cannot invoke `/when` or `/how` skills
- Pattern: inject memory index via `skills:` (discovery), recall via Bash (transport)
- Agent runs `when-resolve.py when "<trigger>"` instead of `/when` skill
- Index syntax unchanged — `/when` triggers work for both main agent and sub-agents, different transport
## Reflexive bootstrapping for self-referential improvements
- When improving tools/agents, apply each improvement before using that tool in subsequent steps
- Phase ordering follows tool-usage dependency graph, not logical grouping
- Collapses design→plan→execute into design→apply for prose-edit work
- Avoids the bootstrapping problem: unimproved agents reviewing their own improvements
- Generalizes: any self-referential improvement task should order by downstream usage, not by topic cluster
## CC sub-agent prompt is minimal
- Sub-agents (Task tool) receive only: identity, "do what was asked; nothing more, nothing less", file search guidance, absolute paths, no emojis
- No prose quality rules, no token economy, no error handling philosophy, no project conventions
- CC main agent gets "avoid over-engineering" and "delete unused" but these may not reach sub-agents
- Gap analysis: deslop prose rules (0% coverage), token-economy (0%), tmp-directory (0%), code-removal (~50% — CC covers deletion)
- Implication: `skills:` injection of project-conventions is high value for sub-agents
## agent-creator can review+fix agents
- plugin-dev agent-creator has Write+Read tools — can be prompted to review and fix agent definitions, not just create
- No dedicated agent-reviewer exists in plugin-dev (only skill-reviewer, plugin-validator, agent-creator)
- Pattern: "Review and fix this agent definition at [path]" works for validation + autofix
## Diagnostic review needs interactivity
- Anti-pattern: delegating opus diagnostic review to sub-agent (loses full conversation context)
- Correct pattern: stop session primed with methodology + prompts, user switches to opus for interactive RCA
- Rationale: opus needs conversation state for effective RCA; sub-agent gets only task prompt
- Two-model separation avoids MAR's "degeneration of thought" from single-model self-reflection
## Design references need disk verification
- Anti-pattern: reviewing design document content without checking that referenced agent/file names exist on disk
- Correct pattern: Glob agent directories to verify all agent references resolve to actual files
- Rationale: design-vet-agent opus review missed outline-review-agent vs runbook-outline-review-agent — two distinct agents, design targeted the wrong one
- Extends to: any design reference to files, skills, or scripts should be verified against codebase state
## Late-addition requirements bypass outline review
- Anti-pattern: adding FRs after outline review without re-validating completeness
- Correct pattern: requirements added after outline review must trigger re-check for traceability and mechanism specification
- Rationale: FR-18 added during design session bypassed outline-level validation, resulting in mechanism-free specification that a planner couldn't implement
## Two-tier context for agent augmentation
- Always-inject (skills prolog): universal conventions, cached in system prompt, ~400 tokens
- Index-and-recall (on-demand): domain-specific knowledge, triggers only in prompt, recalled via bash transport
- Haiku paradox resolved: discovery burden stays with capable agents (design/planning), haiku gets pre-assembled context in runbook steps and agent system prompts
- Prototype before infrastructure: test whether agents actually recall when needed before building context-resolve.py
## Commit before review agent delegation
- Anti-pattern: delegating to review agent while work is uncommitted (dirty tree)
- Correct pattern: commit artifacts before delegating to review agents (outline-review, plan-reviewer, vet-fix-agent)
- Rationale: review agents operate on filesystem state; uncommitted work may be stale or inconsistent
- Applied to runbook skill: Phase 0.75 (commit outline before review) and Phase 1 (commit phase file before review)
## Indexing is not loading
- Anti-pattern: claiming a file requires restart because it appears in an @-referenced index (memory-index.md)
- Correct pattern: only files whose content is injected at startup (@-referenced or agent definitions) require restart. Indexed files accessed via /when recall load on-demand.
- Rationale: memory-index.md is @-referenced (metadata loaded at startup); indexed decision documents are not (content loaded on-demand via /when). Conflating the two produces false restart requirements.
## Reference upstream in bootstrapping
- Anti-pattern: referencing a downstream consumer of criteria (e.g., "same criteria as outline-review-agent") when the consumer hasn't been updated yet in the bootstrapping sequence
- Correct pattern: reference the upstream source where criteria are defined (e.g., runbook-review.md), not agents/skills that consume them
- Rationale: in reflexive bootstrapping, each tool is improved before downstream use. References must follow the dependency chain direction.
## Deliverable review catches cross-cutting drift
- Anti-pattern: relying solely on per-step vet reviews for quality assurance
- Correct pattern: post-orchestration deliverable review catches inter-file consistency gaps (stale copies, broken references, missing cross-references) that per-step vet misses
- Evidence: memory-index skill drifted during execution (3 entries missing); workflows-terminology.md referenced non-existent agent; runbook skill missing general-patterns.md reference
- These were invisible to per-step vet because each step's artifacts were internally consistent
## Orchestrator handles validation delegation
- Anti-pattern: Step validation sections say "Delegate to skill-reviewer" expecting execution agent to spawn plugin-dev agents
- Correct pattern: Orchestrator delegates reviews from main session after execution agents commit
- Rationale: Sub-agents can't spawn plugin-dev agents (skill-reviewer, agent-creator). Orchestrator has plugin-dev access, execution agents don't. Validation delegation is orchestrator responsibility, not execution agent responsibility.
