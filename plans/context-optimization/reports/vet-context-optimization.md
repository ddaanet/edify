# Vet Review: Context Optimization — Fragment Demotion

**Scope**: Fragment demotion from always-loaded CLAUDE.md context
**Date**: 2026-02-21
**Mode**: review + fix

## Summary

Four @-references removed from CLAUDE.md (vet-requirement, bash-strict-mode, sandbox-exemptions, claude-config-layout), two fragments trimmed (workflows-terminology, error-handling), and hook-development.md updated to receive demoted content. All injection points verified to exist. The implementation is structurally sound with one minor issue.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **workflows-terminology.md stub references non-existent skill trigger**
   - Location: `agent-core/fragments/workflows-terminology.md:11`
   - Note: The stub says "Load design/runbook/orchestrate skills for pipeline details." This is correct guidance, but the sentence before it ends with a period and then there's an abrupt horizontal rule — the transition reads naturally, no issue there. However, "Load design/runbook/orchestrate skills" uses an imperative that doesn't match the declarative tone of the rest of the stub. Minor style inconsistency.
   - **Status**: FIXED — Reworded to match declarative stub tone.

2. **error-handling.md retains `|| true` cross-reference to a skill but no longer cross-references planning-work.md**
   - Location: `agent-core/fragments/error-handling.md:11`
   - Note: The trimmed fragment still says "See `/token-efficient-bash` skill" for the `|| true` exception, which is correct. The Error Handling Framework table was demoted. The stub does NOT mention that planning-work.md provides the layer table when needed. This is fine — the rule file triggers automatically from path matching, so agents working on plans get the framework without needing a cross-reference here. Not an issue.
   - **Status**: OUT-OF-SCOPE — No cross-reference needed; planning-work.md triggers via path pattern, not via this fragment.

## Injection Point Verification

| Demoted Content | Injection Point | Verified |
|-----------------|-----------------|---------|
| sandbox-exemptions (full) | `agent-core/skills/worktree/SKILL.md` Usage Notes, Sandbox bypass section | Pass — lines 118-131 cover all bypass scenarios |
| vet-requirement (full) | `agent-core/skills/commit/SKILL.md` Step 1 Gate | Pass — lines 63-81 implement full vet gate with proportionality, routing table, and UNFIXABLE detection |
| bash-strict-mode (full) | `agent-core/skills/token-efficient-bash/SKILL.md` | Pass — full pattern, caveats, reconciliation with error-handling rules |
| claude-config-layout (full) | `.claude/rules/hook-development.md` line 17 reference | Pass — explicit reference to full fragment |
| Hook Error Protocol (D-6) | `.claude/rules/hook-development.md` lines 19-29 | Pass — protocol inlined verbatim with condensed table |
| workflows-terminology pipeline paragraph | `agent-core/skills/runbook/SKILL.md` line 974-976 workflow block | Pass — full Route captured in runbook skill |
| error-handling layer table + D-6 | `.claude/rules/planning-work.md` error-classification.md reference | Pass — planning-work.md injects framework fragments on plan files |

## Fixes Applied

- `agent-core/fragments/workflows-terminology.md:11` — Changed "Load design/runbook/orchestrate skills for pipeline details." to "Details in design, runbook, and orchestrate skills." for consistent declarative register with the stub.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Remove ~5.8k tokens of demotable fragments | Satisfied | All 4 @-refs removed from CLAUDE.md; 2 fragments trimmed to stubs |
| sandbox-exemptions demoted safely | Satisfied | Worktree skill bypass content verified at SKILL.md:118-131 |
| claude-config-layout demoted safely | Satisfied | hook-development.md references fragment + inlines D-6 |
| bash-strict-mode demoted safely | Satisfied | token-efficient-bash skill is full content superset |
| vet-requirement demoted safely | Satisfied | commit skill Step 1 gate implements full vet protocol |
| workflows-terminology partial demotion | Satisfied | Stub retains entry points + terminology table; pipeline Route in runbook skill |
| error-handling detail demotion | Satisfied | Core rule preserved; layer table demoted; D-6 in hook-development.md |
| Hook Error Protocol (D-6) remains available for hook dev | Satisfied | Inlined in hook-development.md with path-based activation |

---

## Positive Observations

- hook-development.md D-6 table is correctly condensed (Rationale column merged into Behavior) — reduces tokens without losing protocol meaning
- workflows-terminology stub preserves the "Progressive discovery" principle by pointing to the right skills rather than enumerating the pipeline
- error-handling.md stub retains the `|| true` exception cross-reference — agents writing bash still get the reconciliation note without reading the full skill
- CLAUDE.md removals are clean — no stale references remain pointing to the demoted content
- Injection points are structurally guaranteed (path-matching rules, skill frontmatter activation) rather than relying on agent compliance
