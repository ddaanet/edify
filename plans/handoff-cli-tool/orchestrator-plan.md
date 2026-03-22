# Orchestrator Plan: handoff-cli-tool

**Agent:** none
**Corrector Agent:** handoff-cli-tool-corrector
**Type:** tdd
**Tester Agent:** handoff-cli-tool-tester
**Implementer Agent:** handoff-cli-tool-implementer

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | handoff-cli-tool-tester | tdd |
| 2 | handoff-cli-tool-tester | tdd |
| 3 | handoff-cli-tool-tester | tdd |
| 4 | handoff-cli-tool-task | general |
| 5 | (orchestrator-direct) | inline |


## Steps

- step-1-1-test.md | Phase 1 | sonnet | 30 | TEST
- step-1-1-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT
- step-1-2-test.md | Phase 1 | sonnet | 30 | TEST
- step-1-2-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT
- step-1-3-test.md | Phase 1 | sonnet | 30 | TEST
- step-1-3-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
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
- step-4-1.md | Phase 4 | sonnet | 30 | PHASE_BOUNDARY
- INLINE | Phase 5 | — | PHASE_BOUNDARY

## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
- Phase 4: sonnet
- Phase 5: sonnet

## Phase Summaries

### Phase 1:

- IN: (not specified)
- OUT: Phase 2, Phase 3, Phase 4, Phase 5

### Phase 2:

- IN: (not specified)
- OUT: Phase 1, Phase 3, Phase 4, Phase 5

### Phase 3:

- IN: (not specified)
- OUT: Phase 1, Phase 2, Phase 4, Phase 5

### Phase 4:

- IN: (not specified)
- OUT: Phase 1, Phase 2, Phase 3, Phase 5

### Phase 5:

- IN: - Delete dead code (M#6)
- OUT: Phase 1, Phase 2, Phase 3, Phase 4
