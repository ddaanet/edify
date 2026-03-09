# Brief: Bootstrap Tag Support — Post-Execution Context

## Status

Execution complete. Corrector review done (`plans/bootstrap-tag-support/reports/review.md`). Two minor fixes applied (silent degradation warning, malformed-bootstrap test coverage).

## Follow-up: Fix TDD Context Scoping

`DEFAULT_TDD_COMMON_CONTEXT` is injected at runbook level (into assembled body) when it should be scoped to TDD phases only. In mixed runbooks (general + TDD phases), the injected Common Context text sits in the assembled body as inert noise for general phases. Functionally correct (general steps don't consume Common Context), but conceptually wrong.

**Fix:** Change injection from runbook-level (`assembled_body = DEFAULT_TDD_COMMON_CONTEXT + assembled_body`) to phase-level — inject into phase preambles for TDD-typed phases only. Affects `assemble_phase_files` and possibly `validate_and_create` common_context building.

**Scope:** `agent-core/bin/prepare-runbook.py` — behavioral code change. Sonnet, no restart.

## Post-Execution Review Findings

Session review identified 6 process issues, routed to 3 new plans:
- Runbook quality directives (`plans/runbook-quality-directives/`) — over-specific Verify GREEN, vacuous Bootstrap absence, redundant integration cycles, missing output-channel guidance
- Inline lifecycle gate (`plans/inline-lifecycle-gate/`) — corrector gate D+B anchor, triage-feedback.sh review.md check
- Markdown AST parser (`plans/markdown-ast-parser/`) — cross-cutting infrastructure, prepare-runbook.py's `---`-based parsing is a consumer

## Architectural Note

The `split_cycle_content` 3-tuple and `---` splitting added by this task will be superseded if the markdown-ast-parser plan ships. Current implementation is functional — the AST rewrite is an improvement, not a fix.
