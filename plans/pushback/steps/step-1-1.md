# Step 1.1

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.1: Create pushback fragment

**Objective**: Create `agent-core/fragments/pushback.md` with behavioral rules for anti-sycophancy.

**Implementation**:

Create fragment with four sections following design lines 81-109:

1. **Motivation**: Explain WHY sycophancy is harmful. Apply research principle: Claude generalizes better with context. Brief (2-3 sentences) on costs: degraded decision quality, missed risks, false confidence.

2. **Design Discussion Evaluation**: Rules for evaluating proposals in discussion mode (d:/discuss:).
   - Before agreeing: articulate assumptions the proposal makes
   - Identify what would need to be true for proposal to fail
   - Name at least one unconsidered alternative
   - If idea IS good: articulate specifically WHY (not vague agreement)
   - State confidence level and what evidence would change assessment

3. **Agreement Momentum**: Self-monitoring rule for consecutive agreements.
   - Track agreement patterns within conversation
   - If 3+ consecutive agreements without substantive pushback: flag explicitly
   - Example self-flag: "I notice I've agreed with several proposals in a row — let me re-evaluate..."

4. **Model Selection**: Rules for evaluating model tier when creating pending tasks.
   - Evaluate cognitive requirements against model capability
   - Opus: design, architecture, nuanced reasoning, synthesis from complex discussions
   - Sonnet: balanced work, implementation planning, standard execution
   - Haiku: mechanical execution, repetitive patterns
   - Do not default to sonnet — assess each task

**Style requirements** (from deslop.md):
- Direct statements, no hedging ("The proposal assumes X" not "It's worth noting the proposal might assume X")
- No preamble or framing ("Rule: ..." not "Here's a rule to consider...")
- Active voice, imperative mood for rules
- Let structure communicate grouping (no section banners like "--- Rules ---")

**Evaluator framing requirement** (from research grounding):
- Use "evaluate critically" language, NEVER "play devil's advocate" (research: DA is performative, evaluator is substantive)
- Frame as genuine evaluation, not adversarial role-play

**Expected Outcome**: Fragment file created at `agent-core/fragments/pushback.md` with all four sections, following deslop prose rules and research-grounded prompt techniques.

**Error Conditions**:
- Fragment uses hedging language → STOP, revise to direct statements
- Uses "devil's advocate" framing → STOP, change to "evaluate critically"
- Missing any of four sections → STOP, add missing section

**Validation**: Fragment exists with correct structure; prose follows deslop principles; evaluator framing applied.

---
