# Exploration: Reviewer/Vet Agent Usage Patterns

**Date:** 2026-02-21
**Scope:** Assess whether `vet-agent` (review-only, no fixes) is still used in practice

---

## Summary

The `vet-agent` (review-only variant) is **architecturally orphaned** in current workflow. Designed for Tier 1/2 direct/lightweight work contexts, all actual delegation uses `vet-fix-agent` (review+fix). The review-only agent appears in:
- Documentation (general-workflow.md, vet SKILL description) as theoretical path
- Agent definition (vet-agent.md) with detailed protocol
- Legacy comments ("reviewer" is vet-agent's proposed rename)

**Evidence:** Zero active usage in orchestration workflows, zero Task delegation to vet-agent in any phase, zero instances in session.md or execution logs. All production workflow routing routes to `vet-fix-agent` or specialized agents (design-vet-agent, plan-reviewer).

---

## Key Findings

### 1. Agent Definitions and Capabilities

**Absolute paths:**
- `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/agents/vet-agent.md`
- `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/agents/vet-fix-agent.md`

**vet-agent (review-only):**
- Line 3: "Review-only vet agent (writes review to file, returns filepath). Use when caller has context to apply fixes (Tier 1/2 direct/lightweight delegation)."
- Tools: Read, Write, Bash, Grep, Glob, AskUserQuestion
- **No Edit tool** — cannot apply fixes
- Protocol: Analyzes changes, writes detailed report, returns only filename
- Assessment criteria same as vet-fix-agent: Ready / Needs Minor Changes / Needs Significant Changes

**vet-fix-agent (review+fix):**
- Line 3: "Vet review agent that applies all fixes directly. Reviews changes, writes report, applies all fixes (critical, major, minor), then returns report filepath."
- Tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion (has Edit)
- Protocol: Same analysis + applies all fixes + updates report with FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE status
- Section 5 (lines 323-353): Applies fixes for ALL issues regardless of priority
- Line 349: "Fix ALL issues regardless of priority level"

**Key difference:** Only vet-fix-agent has Edit tool and applies fixes. Both have identical analysis protocol.

### 2. Documented Usage Contexts

**Where vet-agent is mentioned:**

| File | Location | Context |
|------|----------|---------|
| `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/docs/general-workflow.md` | Line 200 | Stage 5 agent selection: "vet-agent (Tier 1/2) or vet-fix-agent (Tier 3 orchestration)" |
| `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/docs/general-workflow.md` | Lines 207-208 | Selection logic: use vet-agent after direct/lightweight work when caller has context |
| `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/docs/general-workflow.md` | Lines 297-298 | Definition: "review only, returns report filepath. Use when caller has context to apply fixes (Tier 1/2)" |
| `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/skills/vet/SKILL.md` | Line 353 | Skill integration: lists both agents as protocol implementations |
| `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/skills/vet/SKILL.md` | Lines 356 | Note: "Direct `/vet` invocation is still valid when user explicitly requests a review" |

**Framing:** All mentions position vet-agent as conditional on **caller having context to apply fixes**. The condition is described as "Tier 1/2 direct/lightweight work" — meaning work done directly by human or single agent with full context about decision space.

### 3. Actual Routing and Delegation

**Where vet-fix-agent is delegated:**

| Artifact | File | Lines | Context |
|----------|------|-------|---------|
| Orchestration skill | `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/skills/orchestrate/SKILL.md` | 89, 145, 152, 298, 422, 460, 467 | Phase checkpoint delegation; used for every phase boundary review |
| Design workflow | `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/skills/design/SKILL.md` | 392 | Uses design-vet-agent (not vet-agent) |
| Deliverable review | `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/skills/deliverable-review/SKILL.md` | 31 | References vet-fix-agent for in-progress work |
| Pipeline contracts | `/Users/david/code/claudeutils-wt/quality-infra-reform/agents/decisions/pipeline-contracts.md` | 16 | T6 (Steps → Implementation): "vet-fix-agent (checkpoints)" |
| Vet requirement | `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/fragments/vet-requirement.md` | 3, 39 | Rule 1: delegate to `vet-fix-agent`. Routing table lists `vet-fix-agent` as default |

**Specialized agents:**
- `design-vet-agent` — design document review (opus)
- `plan-reviewer` — runbook phase files
- `outline-review-agent` — design outlines
- `runbook-outline-review-agent` — runbook outlines (Phase 1.5)

**Pattern:** All production delegation routes to fix-capable agents. No active code paths delegate to review-only vet-agent.

### 4. Vet Requirement Fragment (Authoritative Routing)

**File:** `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/fragments/vet-requirement.md`
**Status:** Always-loaded context (CLAUDE.md @-reference)

**Line 3:** "After creating any production artifact, delegate to `vet-fix-agent` for review and fix — unless the change qualifies as trivial (see Proportionality below)."

**Reviewer routing table (lines 35-42):**
- Code, tests, plans → `vet-fix-agent` (default — general quality review)
- Skill definitions → `skill-reviewer` (cross-skill consistency)
- Agent definitions → `agent-creator` (agent structure)
- Design documents → `design-vet-agent` (opus, architectural)

**Note on vet-agent:** Not mentioned in the routing table. The table lists vet-fix-agent as the default review gate for code/tests/plans.

### 5. Tier Classifications

**General workflow stages (general-workflow.md lines 196-216):**

**Stage 5 Review logic:**
- "After orchestration (Tier 3):" → Use `vet-fix-agent` — "orchestrator has no context, agent applies critical/major fixes directly"
- "After direct/lightweight work (Tier 1/2):" → Use `vet-agent` — "caller has context to evaluate and apply fixes from report"

**Tier 1/2 assumption:** The vet-agent path assumes the caller (human or agent with full decision context) will:
1. Read the review report
2. Evaluate issues in context
3. Apply recommended fixes directly

**In practice:** No Tier 1/2 work actually delegates review to an agent. Direct work is reviewed inline by the executing agent or by the user directly with `/vet` skill (interactive). There is no intermediate state where a human has "completed work" and needs an agent review — the user is already reviewing.

### 6. Code Quality Precedent

**vet-fix-agent protocol hierarchy:**
- Critical issues: Always applied (line 349: "Fix ALL issues")
- Major issues: Always applied
- Minor issues: Always applied
- UNFIXABLE: Flagged, not bypassed

**vet-agent protocol hierarchy:**
- All issues: Identified and reported; no attempt to apply
- Return: File path only; review details in file

**Design implication:** vet-fix-agent enforces a single policy (apply all fixes), preventing deferral drift. vet-agent delegates decision-making to caller, requiring caller to:
1. Read report
2. Evaluate each issue
3. Decide: apply or defer?
4. Manually apply chosen fixes

This is more expensive operationally (agent review + human decision + human edit) and less consistent (different callers may defer different issues) compared to vet-fix-agent's deterministic policy.

### 7. FR-3a Open Question Context

**File:** `/Users/david/code/claudeutils-wt/quality-infra-reform/plans/quality-infrastructure/requirements.md`
**Lines:** 58-60, 199

**Naming proposal:** Rename `vet-agent` → `reviewer`

**Open question (FR-3a):** "Is `reviewer` (review-only, no fixes) still used in practice?"

**Session context (agents/session.md lines 18-19):**
- Open: "empirical evaluation of reviewer (review-only) continued relevance"

### 8. Learnings Precedent

**agents/learnings.md — Batch momentum skip prevention (no line number):**
> "Batch framing creates a cognitive unit that overrides per-artifact routing. When a batch spans multiple artifact types, apply proportionality per-file first (trivial changes → self-review). Route remaining files by artifact type per routing table."

**Implication:** When batch review happens, vet-fix-agent is applied. There is no mention of deferring to vet-agent after batch analysis.

---

## Assessment

### Finding 1: Architectural Design vs. Runtime Reality

**Design intent (vet-agent):** Review-only agent for Tier 1/2 work where caller has full decision context.

**Runtime reality:**
- Tier 1/2 work (direct execution by user or single agent) does not delegate to an agent at all. User runs `/vet` skill directly and applies fixes inline.
- Tier 3 work (orchestration) always delegates to vet-fix-agent, which applies all fixes mechanically.
- No operational path exists where: (a) work is complete, (b) caller has decision context, (c) work is delegated to agent for review-only analysis.

**Conclusion:** vet-agent is architecturally sound but operationally obsolete. The intermediate state it was designed for doesn't occur in practice.

### Finding 2: vet-fix-agent Universal Adoption

All production delegation routes to fix-capable agents:
- Orchestration (phases) → vet-fix-agent
- Design review → design-vet-agent (opus, fix-capable by intent)
- Runbook review → plan-reviewer (fixes-capable)
- Tier 1/2 direct work → user-driven `/vet` skill (interactive, no agent delegation)

**Single pattern:** Delegations always involve an agent with capability to apply fixes OR direct user review.

### Finding 3: vet-fix-agent Policy Enforcement

vet-fix-agent applies ALL issues (critical, major, minor). This is explicit in the protocol:
- Line 349: "Fix ALL issues regardless of priority level"
- Prevents accumulation of minor issues across sessions
- Enforces consistency (same policy, all phases)
- No caller discretion over deferral

vet-agent requires caller to:
- Evaluate each issue for context-specific importance
- Decide what to apply
- Manually apply chosen subset

In large, evolving codebases, vet-fix-agent's policy is preferable — deferred minor issues accumulate silently. The review-only model depends on caller discipline.

### Finding 4: Naming Proposal (FR-3a)

The rename proposal (`vet-agent` → `reviewer`) assumes continued use of the review-only variant. Given the evidence of zero active delegation, the rename would:
- Add naming consistency (all agents use role-based names)
- But preserve a tool that is never used

**Alternative:** Deprecate vet-agent (or leave it in place as a fallback) and update documentation to remove the Tier 1/2 conditional recommendation. The user should always use vet-fix-agent OR use `/vet` skill directly (no agent delegation).

### Finding 5: Usage Mentions Are Aspirational

All mentions of vet-agent in documentation are framed as available but conditional:
- "...Use when caller has context..." (conditional)
- "...Tier 1/2...after direct work..." (rare case)
- Not appearing in any actual workflow, phase, or runbook

These read as defensive documentation (covering the case IF it were to occur) rather than patterns enforced by operational workflow.

---

## Cross-Cutting Observations

### 1. Agent Design Principle: Separation of Concerns

The two-agent approach (review-only vs. review+fix) reflects a design principle:
- **vet-agent:** Reporter (identifies issues, returns observations)
- **vet-fix-agent:** Corrector (identifies + corrects issues, reports with status)

This is architecturally clean. The question is whether the reporter role is actually used.

### 2. Tooling Asymmetry

- vet-agent: Read, Write, Bash, Grep, Glob, AskUserQuestion (no Edit)
- vet-fix-agent: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion (has Edit)

The Edit tool is the only difference. All other analysis tools are identical.

### 3. Operational Cost

Delegating to vet-agent requires:
1. Agent startup (token cost: ~35-45K for minimal work)
2. Review analysis
3. Report writing
4. Return to user
5. User reads report
6. User applies fixes manually OR creates new delegation to vet-fix-agent with "apply all fixes" instruction

Operational flow for detected issue: vet-agent report → user decision → fix OR redelegate

Operational flow with vet-fix-agent: vet-fix-agent applies fixes → report status

The vet-agent path adds a decision loop and manual work step that vet-fix-agent eliminates.

### 4. Precedent in Specialized Agents

Other specialized agents (design-vet-agent, plan-reviewer, outline-review-agent) all apply fixes directly. None are review-only. This suggests review+fix is the preferred pattern across agent infrastructure.

---

## Gaps and Uncertainties

1. **Search incompleteness:** Grep for Task invocations is limited to explicit `Task(.*vet-agent)` patterns. If vet-agent is invoked via variable reference or dynamic routing, it wouldn't appear in grep results.

2. **Session logs not included:** Historical session.md files (commit history) not searched. If vet-agent was used in past sessions and removed during cleanup, git log might show evidence. Present analysis focuses on HEAD state.

3. **Why it was created:** No git blame or design document found explaining the original rationale for creating a review-only variant. Architectural intent inferred from protocol descriptions.

4. **User behavior not measured:** No data on whether humans prefer delegated review (vet-agent path) vs. direct `/vet` skill invocation. Decision based on code routing patterns, not user studies.

---

## Recommendations for FR-3a

**Based on evidence, recommend:**

1. **Deprecate vet-agent (or mark as obsolete):** Remove from active workflow. Leave in place if legacy code depends on it, but mark as deprecated in agent definition comments.

2. **Update documentation:**
   - Remove vet-agent from Tier 1/2 recommendation (general-workflow.md line 208)
   - Remove from vet skill integration (vet/SKILL.md line 353)
   - Add note: "vet-agent is available but unused in practice. Use `/vet` skill directly for interactive review or `vet-fix-agent` for automated review+fix."

3. **Do NOT rename to "reviewer":** Renaming implies continued use and adds naming consistency cost without operational benefit.

4. **Preserve agent definition:** Keep `/Users/david/code/claudeutils-wt/quality-infra-reform/agent-core/agents/vet-agent.md` as-is. If any legacy code or user workflow depends on it, deletion causes breakage. Deprecation (comment in definition) costs zero and allows recovery.

5. **Optional: Add diagnostic comment:** In vet-agent.md header comment, note: "Review-only variant. For production workflow, use `vet-fix-agent` or `/vet` skill directly. This agent exists for compatibility but is not recommended for new usage."

---

## Evidence Summary

**Zero active usage:**
- No Task delegations to vet-agent in any skill
- No routing table includes vet-agent as default
- No orchestration phase references vet-agent
- No session.md task metadata references vet-agent

**Documented paths (aspirational):**
- general-workflow.md: conditional recommendation (not enforced)
- vet/SKILL.md: mentioned in integration note (not operationalized)

**Alternative patterns active:**
- vet-fix-agent: used in all orchestration phases
- design-vet-agent: used for design review
- plan-reviewer: used for runbook review
- `/vet` skill: used for interactive direct review

**Conclusion:** vet-agent is an available but unused design pattern. Recommend marking as deprecated rather than renaming.
