# Brief: TDD Context Scoping

## Problem

`DEFAULT_TDD_COMMON_CONTEXT` is injected at runbook level (`assembled_body = DEFAULT_TDD_COMMON_CONTEXT + assembled_body`) when it should be scoped to TDD phases only. In mixed runbooks (general + TDD phases), the injected Common Context text sits in the assembled body as inert noise for general phases. Functionally correct (general steps don't consume Common Context), but conceptually wrong.

## Fix

Change injection from runbook-level to phase-level: inject into phase preambles for TDD-typed phases only. Affects `assemble_phase_files` and possibly `validate_and_create` common_context building.

## Scope

`plugin/bin/prepare-runbook.py` — behavioral code change.

## Origin

Follow-up from bootstrap-tag-support post-execution review. See `plans/bootstrap-tag-support/brief.md` for full context.

## Architectural Note

If the markdown-ast-parser plan ships, `prepare-runbook.py` parsing will be rewritten. This fix is still worth doing — AST parser timeline is uncertain, and the scoping is independently correct.
