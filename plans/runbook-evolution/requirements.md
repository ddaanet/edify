# Runbook Evolution Requirements

Runbook skill generates plans with recurring quality gaps. Two independent failure classes identified with distinct fixes.

## Problem Statement

Deliverable reviews across multiple orchestrations consistently find:
- Missing wiring/integration code (components built and tested in isolation, production call paths never connected)
- Prose artifact inconsistencies when edits to the same file are split across steps

Root causes are in the runbook generation directives, not enforcement.

## FR-1: Prose Atomicity

All edits to a prose file must land in a single step. No splitting across steps or phases.

**Rationale:** Prose artifacts have no automated tests. The editor's context window is the only verification mechanism. Fragmenting context degrades the only quality lever available. A single holistic opus edit is more reliable than multiple focused edits.

**Applies to:** Skills, agents, fragments, decision docs — any prose artifact consumed by LLMs where sections are semantically coupled.

**Exception:** Migration-driven expand/contract (see FR-2).

## FR-2: Self-Modification Discipline

When orchestration modifies its own pipeline infrastructure (orchestrate skill, executor agent, review agents/skills), two sub-constraints apply:

### FR-2a: Migration Consistency

Modified artifact must work with environment state before AND after the edit. May require expand/contract pattern — first edit adds forward compatibility, second edit removes backward compatibility after environment transitions. This is the exception to FR-1 prose atomicity.

### FR-2b: Bootstrapping Ordering

Apply tool improvement completely before using that tool in subsequent steps. Phase ordering follows tool-usage dependency graph, not logical grouping. Reinforces FR-1 (holistic edit before use).

Existing decision: `agents/decisions/workflow-advanced.md` "When Bootstrapping Self-Referential Improvements". Needs codification in runbook skill generation directives.

## FR-3: Testing Diamond

Replace pyramid-shaped testing guidance with diamond (integration-first).

### FR-3a: Integration Tests as Primary Layer

All key behaviors tested through production call paths. Integration tests are the default, not supplementary.

**Rationale:** The recurring failure mode is missing wiring — components built and tested in isolation, production call path never connected. Integration tests make wiring the default thing tested. A component can't be "done" while wiring is absent because the integration test stays RED.

### FR-3b: Unit Tests as Surgical Supplement

Unit tests only for:
- Combinatorial explosion (too many paths to cover at integration level)
- Genuinely hard-to-isolate edge cases
- Key internal contract details

### FR-3c: Real Subprocesses for Subprocess Domains

When production code's primary operation is subprocess calls (e.g., git), tests use real subprocesses. Mocks only for error injection (lock files, permission errors).

**Existing alignment:** `agents/decisions/testing.md` "When Preferring E2E Over Mocked Subprocess" already established this for git. FR-3c generalizes the principle.

**IPC performance:** Real cost for cross-process tests (test containers, subprocesses). Managed at infrastructure level (parallelism, selective test running), not by retreating to mocks.

### FR-3d: Local Substitutes for External Dependencies

SQLite for database tests, local services for network tests. Preserve the production call path; accept fidelity trade-offs (SQL dialect differences) with a few IPC-heavy tests at the e2e layer verifying the real service path.

## FR-4: Integration Test Bookend Enforcement (Deferred)

Plan-reviewer enforcement for "phase includes test exercising production call path" is deferred. Observe FR-3 generation results first. Add enforcement only if integration tests are still missing after running diamond-shaped runbooks.

**Rationale:** One change at a time. Existing quality enforcement (RED behavioral, vacuous assertion detection) provides backstop. Stronger generation may succeed where weak generation failed.

## FR-5: Test Suite Migration (Separate Design)

Migrate existing test suite (1027 tests) to diamond strategy. Separate design from runbook evolution — different scope, different execution profile. Depends on FR-3 being codified first.

## Scope

**IN:**
- Runbook SKILL.md generation directives (testing section, prose handling, self-modification)

**OUT:**
- Plan-reviewer enforcement criteria (unchanged, strategy-agnostic — verified by grep)
- Vet-fix-agent criteria (unchanged)
- `agents/decisions/testing.md` (historical corrections, not revisionist)
- Test suite migration (FR-5, separate design)

## Evidence

Source: Deliverable review findings across workwoods and prior orchestrations.

- M-4: `infer_state()` gate logic works but `list_plans()` never passes `vet_status_func` — wiring absent
- M-6: TreeInfo has fields but production path doesn't populate them — display.py duplicates git queries
- `_task_summary`: function exists with 4 passing tests, never called from `format_rich_ls`
- C-1, M-1, M-2: Prose inconsistencies from split edits across phases
