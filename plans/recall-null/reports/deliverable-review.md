# Deliverable Review: recall-null

**Date:** 2026-02-28
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | `src/claudeutils/when/cli.py` | 8 | 1 |
| Test | `tests/test_when_null.py` | 50 | 0 |
| Agentic prose | `skills/design/SKILL.md` (submodule) | 2 | 0 |
| Agentic prose | `skills/inline/SKILL.md` (submodule) | 12 | 12 |
| Agentic prose | `skills/requirements/SKILL.md` (submodule) | 12 | 0 |
| Agentic prose | `skills/runbook/SKILL.md` (submodule) | 8 | 4 |
| Agentic prose | `skills/runbook/references/tier3-planning-process.md` (submodule) | 9 | 2 |

**Total:** 7 files, +101/-19 (net +82)

**Design conformance:** All 7 deliverables map to outline items. No missing deliverables. No unspecified deliverables.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**Style/consistency:**

1. **"proves gate was reached" wording varies across skills** — **FIXED**
   - Normalized to "proves gate was reached" in inline/SKILL.md, runbook/SKILL.md (×2), tier3-planning-process.md

2. **Null artifact consumer enumeration differs between /requirements and /design** — **FIXED**
   - Added "(/runbook Phase 0.5)" consumer enumeration to design/SKILL.md:209

3. **CLI help text doesn't document "null" as reserved** — **FIXED**
   - Added `"null" is reserved as a D+B gate anchor` to cli.py docstring

## Gap Analysis

| Design Requirement | Status | Reference |
|--------------------|--------|-----------|
| Phase 1 Cycle 1.1: null query exits silently (exit 0, empty) | Covered | `cli.py:79-81`, `test_when_null.py:10-15` |
| Phase 1 Cycle 1.2: null mixed with real queries | Covered | `cli.py:79`, `test_when_null.py:18-42` |
| Phase 1: operator-prefixed null ("when null") | Covered | `_strip_operator` logic, `test_when_null.py:45-50` |
| Phase 2 item 2.1(a): /requirements recall pass gate anchor | Covered | `requirements/SKILL.md:40` |
| Phase 2 item 2.1(a): /requirements null artifact format | Covered | `requirements/SKILL.md:63` |
| Phase 2 item 2.1(b): /requirements post-explore gate | Covered | `requirements/SKILL.md:102-108` |
| Phase 2 item 2.2: /design null artifact + A.2.5 verify | Covered | `design/SKILL.md:209`, A.2.5 already canonical |
| Phase 2 item 2.3: /runbook Tier 1 D+B three-path | Covered | `runbook/SKILL.md:116-120` |
| Phase 2 item 2.3: /runbook Tier 2 D+B three-path | Covered | `runbook/SKILL.md:134-138` |
| Phase 2 item 2.4(a): tier3 Phase 0.5 step 1 D+B framing | Covered | `tier3-planning-process.md:22-25` |
| Phase 2 item 2.4(b): tier3 post-explore gate | Covered | `tier3-planning-process.md:44-49` |
| Phase 2 item 2.5: /inline 2.3 D+B three-path | Covered | `inline/SKILL.md:68-78` |

## Cross-Cutting Verification

- **Path consistency:** All 7 skill files reference `agent-core/bin/when-resolve.py` — uniform ✓
- **API contract alignment:** cli.py null filter (`_strip_operator(q) != "null"`) matches skill instructions (`when-resolve.py null`) ✓
- **Null artifact format:** Exact string `null — no relevant entries found` consistent between /requirements and /design ✓
- **Corrector fixes verified:** Tier 2 parenthetical "(moderate path skipped design)" present; test assertion at line 41-42 uses standalone-line check (not fragile substring) ✓
- **Pipeline skill coverage:** All skills with agent-facing recall decision points updated (requirements, design, runbook T1/T2/T3, inline). /orchestrate and /deliverable-review excluded correctly — they dispatch to these skills rather than making independent recall decisions ✓
- **Test suite:** 3/3 null mode tests passing ✓

## Summary

- **Critical:** 0
- **Major:** 0
- **Minor:** 3 (style/consistency, non-functional)
