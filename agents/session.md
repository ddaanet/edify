# Session: Worktree — Fix prepare-runbook.py step file generation bugs

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Fix prepare-runbook.py step file generation bugs** — sonnet
  - Bug 1: `extract_cycles()` line 150 — only terminates on H2, not H3 phase headers; last cycle captures next phase's preamble
  - Bug 2: `generate_cycle_file()` line 1048 / `generate_step_file()` line 1000 — writes non-existent `runbook.md` path as provenance metadata
  - Diagnostic: `plans/prepare-runbook-fixes/diagnostic.md`
