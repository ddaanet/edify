# Brief: Codebase Sweep — Expanded Scope

## Context from bootstrap-tag-support session (2026-03-08)

Post-execution review of prepare-runbook.py identified a class of code quality issue not covered by the current requirements: **conceptual design quality** distinct from code density.

### Current Requirements

Targets subprocess/exit patterns: `_git_ok`, `_fail`, exception-as-control-flow. These are density anti-patterns (redundant patterns replaceable with helpers).

### Proposed Addition: Structural Design Quality Axis

prepare-runbook.py has accreted patterns that are functionally correct but conceptually poor:

- **Global injection for phase-local concerns:** `DEFAULT_TDD_COMMON_CONTEXT` injected at runbook level when it's a TDD-phase concern. Fixed partially (bootstrap-tag-support), but the architecture remains: a runbook-level constant for a phase-level need.
- **String-marker splitting:** `split_cycle_content` uses `---` and `**Bootstrap:**` string searches. `extract_cycles` uses regex + `_fence_tracker`. Multiple consumers reimplementing structure detection.
- **Duplicate fence-boundary handling:** `strip_fenced_blocks` and `_fence_tracker` coexist, doing related but different fence processing.

These aren't density issues (no redundant helper pattern to extract). They're design issues — the code's conceptual model doesn't match the domain.

### Recommendation

1. **Ground first:** The existing grounding report (`plans/reports/code-density-grounding.md`) covers density. Structural design quality needs its own grounding — what constitutes "conceptually poor" in a markdown code generator? Research parser architecture patterns.
2. **Feed grounding back:** Update /runbook skill directives and corrector criteria so future generated code doesn't repeat these patterns.
3. **Relationship to markdown-ast-parser plan:** The prepare-runbook.py parsing issues are a consumer of the markdown-ast-parser plan (`plans/markdown-ast-parser/brief.md`). The sweep should include prepare-runbook.py but may defer parser rewriting to that plan.

### Scope Decision Needed

Is prepare-runbook.py in scope for the codebase sweep? The current requirements target `cli.py`, `merge.py`, `utils.py` — all in `src/claudeutils/worktree/`. prepare-runbook.py is in `agent-core/bin/`. The structural design quality axis adds a different kind of work (architectural revision vs mechanical pattern replacement).

Options:
- **Expand sweep:** Add prepare-runbook.py + design quality axis. Larger scope, mixed work types.
- **Keep sweep narrow:** Density patterns only per current requirements. Design quality routes to markdown-ast-parser plan.
- **Two-pass:** Sweep handles density patterns (current scope). Separate pass for design quality (after grounding).
