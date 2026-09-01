# Measurements — pipeline simplification (NFR-2, D15)

Measured with `wc -l` and `edify tokens` (claude-sonnet-5 tokenizer via
Anthropic API). Before = commit `a4aad0c8` (task 0, 2026-09-01).

## Before

### Deletion set (D10, including files migrated then deleted by tasks 3–4)

| File | Lines | Tokens |
|------|-------|--------|
| plugin/bin/prepare-runbook.py | 1949 | 25370 |
| plugin/bin/validate-runbook.py | 470 | 6769 |
| plugin/bin/assemble-runbook.py | 206 | 2559 |
| plugin/scripts/split-execution-plan.py | 222 | 2587 |
| plugin/skills/orchestrate/scripts/verify-red.sh | 29 | 382 |
| tests/test_validate_runbook_reporting.py | 137 | 1765 |
| tests/fixtures/validate_runbook_fixtures.py | 400 | 2868 |
| plugin/skills/review-plan/SKILL.md | 428 | 7757 |
| plugin/skills/review-plan/references/report-template.md | 68 | 586 |
| plugin/skills/review-plan/references/review-examples.md | 114 | 1330 |
| plugin/agents/runbook-corrector.md (old) | 149 | 2923 |
| plugin/docs/general-workflow.md | 521 | 6344 |
| plugin/docs/tdd-workflow.md | 556 | 6637 |
| plugin/skills/orchestrate/references/progress-tracking.md | 40 | 447 |
| plugin/skills/orchestrate/references/common-scenarios.md | 29 | 496 |
| plugin/skills/runbook/references/anti-patterns.md | 39 | 1975 |
| plugin/skills/runbook/references/conformance-validation.md | 12 | 202 |
| plugin/skills/runbook/references/error-handling.md | 124 | 2372 |
| plugin/skills/runbook/references/examples.md | 352 | 4107 |
| plugin/skills/runbook/references/general-patterns.md | 128 | 1556 |
| plugin/skills/runbook/references/patterns.md | 151 | 2029 |
| plugin/skills/runbook/references/tdd-cycle-planning.md | 108 | 1909 |
| plugin/skills/runbook/references/tier3-expansion-process.md | 260 | 4194 |
| plugin/skills/runbook/references/tier3-outline-process.md | 25 | 755 |
| plugin/skills/runbook/references/tier3-planning-process.md | 512 | 9805 |
| **Total** | **7029** | **97724** |

### Rewrite set

| File | Lines | Tokens |
|------|-------|--------|
| plugin/skills/runbook/SKILL.md | 193 | 3739 |
| plugin/skills/orchestrate/SKILL.md | 299 | 5546 |
| plugin/skills/inline/SKILL.md | 178 | 3275 |
| plugin/skills/orchestrate/scripts/verify-step.sh | 28 | 272 |
| plugin/agents/test-driver.md | 323 | 4086 |
| plugin/agents/artisan.md | 124 | 1563 |
| plugin/agents/refactor.md | 217 | 2608 |
| plugin/agents/tdd-auditor.md | 443 | 5098 |
| plugin/agents/corrector.md | 539 | 7981 |
| plugin/agents/runbook-outline-corrector.md | 526 | 7468 |
| plugin/agents/runbook-simplifier.md | 163 | 2084 |
| plugin/fragments/delegation.md | 89 | 1737 |
| plugin/fragments/workflows-terminology.md | 27 | 506 |
| plugin/fragments/execution-routing.md | 41 | 787 |
| plugin/fragments/escalation-acceptance.md | 57 | 1331 |
| **Total** | **3247** | **48081** |

## After

Measured by task 8 (2026-09-01) on the working tree after task 8's sweep,
same tools. The deletion set is gone entirely (0 lines, 0 tokens). The
rewrite set below is the surviving files plus the two references the
rewrite created (`runbook-format.md`, `dispatch-composition.md`);
`runbook-corrector.md` is the renamed `runbook-outline-corrector.md`.

### Rewrite set

| File | Lines | Tokens |
|------|-------|--------|
| plugin/skills/runbook/SKILL.md | 141 | 2301 |
| plugin/skills/runbook/references/runbook-format.md (new) | 120 | 1867 |
| plugin/skills/orchestrate/SKILL.md | 180 | 3041 |
| plugin/skills/orchestrate/references/dispatch-composition.md (new) | 57 | 1024 |
| plugin/skills/inline/SKILL.md | 164 | 2779 |
| plugin/skills/orchestrate/scripts/verify-step.sh | 19 | 194 |
| plugin/agents/test-driver.md | 101 | 1626 |
| plugin/agents/artisan.md | 122 | 1519 |
| plugin/agents/refactor.md | 192 | 2333 |
| plugin/agents/tdd-auditor.md | 155 | 2029 |
| plugin/agents/corrector.md | 595 | 9049 |
| plugin/agents/runbook-corrector.md | 214 | 3391 |
| plugin/agents/runbook-simplifier.md | 163 | 2043 |
| plugin/fragments/delegation.md | 87 | 1707 |
| plugin/fragments/workflows-terminology.md | 27 | 531 |
| plugin/fragments/execution-routing.md | 41 | 790 |
| plugin/fragments/escalation-acceptance.md | 57 | 1338 |
| **Total** | **2435** | **37562** |

### Net

| Set | Before lines | After lines | Before tokens | After tokens |
|-----|-------------:|-----------:|--------------:|-------------:|
| Deletion set | 7029 | 0 | 97724 | 0 |
| Rewrite set | 3247 | 2435 | 48081 | 37562 |
| **Both** | **10276** | **2435** | **145805** | **37562** |

`corrector.md` grew (539 → 595 lines, 7981 → 9049 tokens): D12 added the
TDD slice-review protocols and the vacuous-green catalogue to it.
