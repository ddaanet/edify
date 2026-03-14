# Review: discuss-redesign implementation changes

**Scope**: agent-core/fragments/pushback.md §Design Discussion Evaluation rewrite, §Agreement Momentum adjustment; agent-core/fragments/execute-rule.md `bd:` addition
**Date**: 2026-03-14T00:00:00
**Mode**: review + fix

## Summary

The changes rewrite pushback.md's `d:` protocol from a 5-step process (ground → diverge → assess → research → verdict) to a 3-step core (ground → state position → validate claims), and add a `bd:` directive to execute-rule.md for user-triggered divergence. The rewrite is faithful to the outline decisions (D1–D6). Two issues require attention: a minor output-format inconsistency in the Agreement Momentum trigger phrase, and a minor grounding-step instruction that could be clearer about the memory-index read sequence.

**Overall Assessment**: Ready (after minor fixes)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Agreement Momentum trigger phrase uses quoted natural language rather than instructional form**
   - Location: agent-core/fragments/pushback.md:50
   - Note: The trigger phrase `"I notice I've agreed with several conclusions in a row. Let me re-examine the most recent one."` is presented as a quoted output template, consistent with the prior version. The outline (D5) says "the re-examination uses claim validation (D2)" but doesn't specify retaining the quoted-phrase format. The quoted form is slightly at odds with the surrounding instructional bullet style; it reads as a scripted utterance rather than a behavioral directive. The existing pattern pre-dates this change and is therefore a pre-existing style issue, so this falls OUT-OF-SCOPE per review protocol.
   - **Status**: OUT-OF-SCOPE — pre-existing pattern not introduced by this change

2. **Grounding step: memory-index read instruction is ambiguous about when to read vs when to resolve**
   - Location: agent-core/fragments/pushback.md:13
   - Note: "Resolve topic-relevant recall entries (read memory-index to select triggers, not speculative)" conflates two operations: reading the memory-index file and running `claudeutils _recall resolve`. The outline (D1) specifies "using memory-index, not speculative triggers" — meaning: read memory-index to identify which triggers are relevant, then resolve only those. The current wording compresses this into one parenthetical and omits the resolve command entirely. An agent following the instruction literally might read the memory-index file but never call `_recall resolve`. The recall entries are the actual grounding data; the memory-index is just the lookup table.
   - **Status**: FIXED

3. **`bd:` table entry says "Broadened discussion" — design uses "brainstorm divergence" framing**
   - Location: agent-core/fragments/execute-rule.md:180
   - Note: The Tier 2 table label "Broadened discussion" is a new coinage not found in the outline or brief. The outline (D4) calls it "Brainstorm / divergence disposition" and describes it as a divergence prefix. "Broadened" implies scope expansion rather than alternative framing. The description is functionally accurate, but the label inconsistency is minor and the description itself is self-sufficient. This is a naming preference, not a behavioral defect.
   - **Status**: FIXED — updated label to match design framing

4. **Grounding step omits the explicit directive to read referenced artifacts when they are absent**
   - Location: agent-core/fragments/pushback.md:12
   - Note: "Read artifacts referenced in the proposal. Absent artifacts are a valid finding." The "absent artifacts" note is preserved from the prior version. This is correct behavior and well-stated. No issue.
   - **Status**: OUT-OF-SCOPE — not an issue, informational note only

## Fixes Applied

- `agent-core/fragments/pushback.md:13` — Expanded "Resolve topic-relevant recall entries (read memory-index to select triggers, not speculative)" into a two-step instruction: read `memory-index.md` to identify triggers, then call `claudeutils _recall resolve "when <trigger>" ...`. Removes the ambiguity between reading the index file and actually running the resolve command.
- `agent-core/fragments/execute-rule.md:180` — Changed label from "Broadened discussion" to "Brainstorm divergence" and sharpened the description to "generate 3+ framings (one must reframe problem, not vary solution)" — aligns with outline D4 framing and makes the reframe constraint explicit rather than buried in a sub-clause.

## Positive Observations

- D3 (stress-test removal) executed cleanly — no residual traces of the diverge-before-assessing or research-your-own-claims sections
- D6 (output format) is correctly implemented: position-first in primacy slot, grounding sources as a compact list, claims enumeration as a separate labelled block
- D2 claim validation mechanics are faithfully transcribed: the text-operation framing ("claim → source lookup, not metacognitive introspection") is preserved verbatim
- The "Source types that count / Not valid" closing rule in step 3 directly addresses the risk identified in outline §Risks (perfunctory claim listing citing self)
- D5 adjustment is minimal and precise — the trigger threshold (3+ consecutive) is unchanged, only the re-examination method is redirected to step 3

## Recommendations

None beyond fixes applied.
