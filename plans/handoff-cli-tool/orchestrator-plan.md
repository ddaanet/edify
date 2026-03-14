# Orchestrator Plan: handoff-cli-tool

**Agent:** none
**Corrector Agent:** handoff-cli-tool-corrector
**Type:** tdd
**Tester Agent:** handoff-cli-tool-tester
**Implementer Agent:** handoff-cli-tool-implementer

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | handoff-cli-tool-task | general |
| 2 | handoff-cli-tool-tester | tdd |
| 3 | handoff-cli-tool-tester | tdd |
| 4 | handoff-cli-tool-task | general |
| 5 | handoff-cli-tool-tester | tdd |
| 6 | handoff-cli-tool-tester | tdd |
| 7 | handoff-cli-tool-tester | tdd |


## Steps

- step-1-1.md | Phase 1 | sonnet | 30
- step-1-2.md | Phase 1 | sonnet | 30
- step-1-3.md | Phase 1 | sonnet | 30 | PHASE_BOUNDARY
- step-2-1-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-1-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT
- step-2-2-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-2-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-3-1-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-1-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-2-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-2-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-3-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-3-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-4-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-4-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-4-1-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-1-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-2-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-2-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-3-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-3-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-4-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-4-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-6-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-6-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-7-test.md | Phase 4 | sonnet | 30 | TEST
- step-4-7-impl.md | Phase 4 | sonnet | 30 | IMPLEMENT
- step-4-8.md | Phase 4 | sonnet | 30 | PHASE_BOUNDARY
- step-5-1-test.md | Phase 5 | sonnet | 30 | TEST
- step-5-1-impl.md | Phase 5 | sonnet | 30 | IMPLEMENT
- step-5-2-test.md | Phase 5 | sonnet | 30 | TEST
- step-5-2-impl.md | Phase 5 | sonnet | 30 | IMPLEMENT
- step-5-3-test.md | Phase 5 | sonnet | 30 | TEST
- step-5-3-impl.md | Phase 5 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-6-1-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-1-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT
- step-6-2-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-2-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT
- step-6-3-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-3-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT
- step-6-4-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-4-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT
- step-6-5-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-5-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT
- step-6-6-test.md | Phase 6 | sonnet | 30 | TEST
- step-6-6-impl.md | Phase 6 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-7-1-test.md | Phase 7 | sonnet | 30 | TEST
- step-7-1-impl.md | Phase 7 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY

## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
- Phase 4: sonnet
- Phase 5: sonnet
- Phase 6: sonnet
- Phase 7: sonnet

## Phase Summaries

### Phase 1:

- IN: Extract git utilities and establish package structure. Foundation for all subcommands.
- OUT: Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7

### Phase 2:

- IN: Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.
- OUT: Phase 1, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7

### Phase 3:

- IN: Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.
- OUT: Phase 1, Phase 2, Phase 4, Phase 5, Phase 6, Phase 7

### Phase 4:

- IN: Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.
- OUT: Phase 1, Phase 2, Phase 3, Phase 5, Phase 6, Phase 7

### Phase 5:

- IN: Markdown stdin parser (commit-specific format) and scripted vet check.
- OUT: Phase 1, Phase 2, Phase 3, Phase 4, Phase 6, Phase 7

### Phase 6:

- IN: Staging, submodule coordination, amend semantics, structured output.
- OUT: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 7

### Phase 7:

- IN: Cross-subcommand contract test. Verifies parser consistency between handoff writes and status reads.
- OUT: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6
