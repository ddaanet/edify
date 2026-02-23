# Edit: Orchestrate Skill - Review Recall Field

## What was added

A `**Review recall:**` field in the checkpoint delegation template (Section 3.3, lines 173-174 of the template block).

## Location

`agent-core/skills/orchestrate/SKILL.md`, Section 3.3 "Post-step verification and phase boundary", within the checkpoint delegation template code block. Inserted between `**Design reference:**` and `**Changed files:**`.

## Content added

```
**Review recall:** Read `plans/<name>/recall-artifact.md` if it exists. Incorporate review-relevant entries: common review failures, quality anti-patterns, over-escalation patterns from project history. If file missing, proceed without it.
```

## Design decisions embedded

- **D-2 (orchestrator doesn't filter):** The orchestrator mechanically references the artifact path. No filtering logic added. Content was pre-selected at planning time and baked into the recall artifact.
- **FR-4 (review-stage recall):** Injected into the corrector prompt via the checkpoint template -- the corrector reads the artifact and incorporates relevant entries.
- **FR-10 (content delivery guarantee):** The corrector reads the artifact directly into its own context, ensuring content availability.
- **Graceful degradation:** "If file missing, proceed without it" -- plans without recall artifacts are unaffected.

## What was NOT changed

- Section 3.0 (inline execution) -- unchanged
- Section 3.1 (agent delegation) -- unchanged
- No filtering logic added to the orchestrator
- Template enforcement rules unchanged (new field is optional by design -- recall artifact may not exist)
