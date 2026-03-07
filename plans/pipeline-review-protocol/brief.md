# Pipeline Review Protocol — Brief

## Routing Decision

Outline passes sufficiency gate. Route to `/inline plans/pipeline-review-protocol execute`, NOT /runbook.

- All prose edits (skill content, hosting skill integration)
- No implementation loops (no tests, no build feedback)
- All decisions pre-resolved (D-1 through D-7)
- Outline's own execution constraint: "inline task sequence, not Tier 3 orchestration"
- Sequencing is trivial: create /proof skill first, then integrate into 3 hosting skills

## Recurrent Failure Mode

Agent routes prose-only work to /runbook when cross-file scope feels large, despite the sufficiency gate's explicit criterion: "all prose edits, no implementation loops → direct execution." The "spans N files" heuristic overrides the routing rule.

This is the same class as the "design ceremony continues after uncertainty resolves" decision — process inertia beyond what the work requires. Needs a design fix: either strengthen the routing rule or add a structural gate that catches the mismatch.

## Key Decisions (from Phase B)

- D-1: `/proof` is a skill, not reference file — enforcement requires tool-call gates
- D-2: Inline execution (no `context: fork`) — needs hosting skill's context
- D-4: No continuation push/pop — existing prepend + design-context-gate suffice
- D-5: Post-expansion (after T3 corrector) = review integration point for systemic defects
- D-6: /requirements = prevention layer, post-expansion = detection layer
- D-7: Name "proof" — transparent validation semantics, edify-thematic

## Scope

4 components: C1 (/proof skill), C2 (5 integration points across 3 hosting skills), C3 (author-corrector coupling), C4 (automatic corrector after proof). Full outline: `plans/pipeline-review-protocol/outline.md`.
