# Discuss Divergent Thinking

## Requirements

### Functional Requirements

**FR-1: Add divergent step to discuss protocol**
Insert a divergent thinking step between grounding and assessment in the `d:` directive. The step generates 3+ alternative framings of the problem/proposal before narrowing to a verdict. At least one framing must reframe the problem (different conceptual frame), not just vary the solution within the current frame.

Acceptance: `d: <proposal>` produces 3+ framings before assessment. At least one framing differs conceptually from the proposal's implicit frame.

**FR-2: Update hook expansion**
Modify `_DISCUSS_EXPANSION` in `agent-core/hooks/userpromptsubmit-shortcuts.py` (lines 75-88) to include the divergent step between "Ground first" and "Form your assessment."

Acceptance: Hook output includes divergent step instruction in correct position.

**FR-3: Update pushback fragment**
Modify "Design Discussion Evaluation" section in `agent-core/fragments/pushback.md` (lines 5-33) to add a divergent thinking subsection between "Ground your evaluation" and "Form your assessment."

Acceptance: Fragment contains divergent thinking subsection with reframing instruction.

### Constraints

**C-1: Unconditional step**
The divergent step is unconditional — every `d:` invocation is a design space that benefits from alternatives. No conditional trigger or opt-out mechanism.

Rationale: `d:` is never used for factual assessment (those don't need `d:`). The discussion directive self-selects for design questions.

**C-2: Relationship to existing `b:` directive**
The `b:` (brainstorm) directive already exists for pure divergence without judgment. The divergent step in `d:` is scoped differently: it generates framings as input to the subsequent assessment, not as a standalone brainstorm. The `b:` directive remains independent — `d:` embeds a mini-divergence within a convergent protocol.

**C-3: Two-artifact edit scope**
Only two files change: the hook expansion string and the pushback fragment. No new files, no new directives, no skill promotion (deferred — see `directive-skill-promotion` plan).

### Out of Scope

- Skill promotion of `d:` directive — tracked separately in `plans/directive-skill-promotion/`
- Changes to `b:` (brainstorm) directive — independent, not affected
- Conditional triggering logic — explicitly rejected (C-1)
- Agreement momentum counter interaction — the divergent step runs before assessment, so it doesn't interact with the agreement counter

### References

- `plans/discuss-divergent-thinking/brief.md` — origin problem and observed failure (droplet naming)
