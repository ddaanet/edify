# Brief: Runbook Warnings

## 2026-03-13: Warning fatigue in prepare-runbook.py file validation

`prepare-runbook.py` emits ~95 "references non-existent file" warnings for greenfield plans where steps create new files. Legitimate path typos (e.g., `validation/task_parsing.py` when the design says `src/edify/session/validate.py`) are buried in noise from files that prior steps will create.

**Root cause:** Validator checks paths against current filesystem. No awareness of step ordering — a file created by step 2.1 is "non-existent" when validating step 3.1's references.

**Desired behavior:** Distinguish files created by prior steps (suppress or downgrade) from files genuinely absent from the plan (error or prominent warning). Could track declared outputs per step, or scan all step files for file-creation references before validating.

**Evidence:** handoff-cli-tool plan regeneration produced 95 file warnings + 25 missing-dependencies warnings. Real issues invisible without manual review.
