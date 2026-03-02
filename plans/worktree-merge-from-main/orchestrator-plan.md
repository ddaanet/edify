# Orchestrator Plan: worktree-merge-from-main

**Agent:** none
**Corrector Agent:** worktree-merge-from-main-corrector
**Type:** tdd
**Tester Agent:** worktree-merge-from-main-tester
**Implementer Agent:** worktree-merge-from-main-implementer

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | worktree-merge-from-main-tester | tdd |
| 2 | worktree-merge-from-main-tester | tdd |
| 3 | worktree-merge-from-main-tester | tdd |
| 4 | (orchestrator-direct) | inline |


## Steps

- step-1-1-test.md | Phase 1 | sonnet | 30 | TEST
- step-1-1-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT
- step-1-2-test.md | Phase 1 | sonnet | 30 | TEST
- step-1-2-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-2-1-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-1-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT
- step-2-2-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-2-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT
- step-2-3-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-3-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT
- step-2-4-test.md | Phase 2 | sonnet | 30 | TEST
- step-2-4-impl.md | Phase 2 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- step-3-1-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-1-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-2-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-2-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-3-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-3-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT
- step-3-4-test.md | Phase 3 | sonnet | 30 | TEST
- step-3-4-impl.md | Phase 3 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY
- INLINE | Phase 4 | —
- step-4-1.md | Phase 4 | opus | 30 | PHASE_BOUNDARY

## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
- Phase 4: opus

## Phase Summaries

### Phase 1:

- IN: (not specified)
- OUT: Phase 2, Phase 3, Phase 4

### Phase 2:

- IN: (not specified)
- OUT: Phase 1, Phase 3, Phase 4

### Phase 3:

- IN: (not specified)
- OUT: Phase 1, Phase 2, Phase 4

### Phase 4:

- IN: (not specified)
- OUT: Phase 1, Phase 2, Phase 3
