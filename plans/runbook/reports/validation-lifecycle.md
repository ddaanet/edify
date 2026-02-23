# Validation Report: lifecycle

**Runbook:** plans/phase-scoped-agents/runbook.md

**Date:** 2026-02-23T15:19:21Z

**Result:** FAIL

## Summary

Failed: 5

## Violations

- Cycle 1.1: `agent-core/bin/prepare-runbook.py` — no prior creation found
- Cycle 2.3: `tests/test_prepare_runbook_mixed.py` — no prior creation found
- Cycle 2.3: `tests/test_prepare_runbook_orchestrator.py` — no prior creation found
- Cycle 2.3: `tests/test_prepare_runbook_inline.py` — no prior creation found
- Cycle 2.3: `tests/test_prepare_runbook_phase_context.py` — no prior creation found
