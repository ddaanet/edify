# Brief: Remove Fuzzy Matching from Recall Resolve

## Context

`claudeutils _recall resolve` uses fuzzy matching (`when/resolver.py`) to suggest alternatives on no-match. This masks two distinct diagnostic signals:

1. **Stale recall artifact** — entry was renamed/removed during codification. Artifact needs upstream fix (unrecoverable at resolve time).
2. **Unanchored recall** — agent guessed at trigger phrases without reading memory-index. Recoverable by reading index.

Session evidence: 11 speculative trigger phrases fired, 6 returned "No match" with "Did you mean:" suggestions. Fuzzy matching enabled continued guessing instead of forcing index read.

## Target Repository

`claudeutils` (the tool repo, not this project). Code change in `src/claudeutils/when/resolver.py`.

## Proposed Change

**Keyword-form failure** (`_recall resolve "when <trigger>"`):
- Remove fuzzy suggestions from error output
- Print: "No memory entry for '<trigger>'. Read agents/memory-index.md to find valid entries."
- This guides the agent to the recoverable action (read index)

**Artifact-form failure** (`_recall resolve plans/<job>/recall-artifact.md`):
- Fail with error indicating stale/incorrect artifact key
- No guidance to read index — this is an upstream artifact problem, not an index-reading problem

**Implementation:**
- Remove or disable `_get_suggestions()` and `_handle_no_match()` fuzzy paths in `when/resolver.py`
- Replace with hard failure + guidance message
- Update tests expecting "Did you mean:" output

## Evidence

- `when/resolver.py` lines 125-165: fuzzy suggestion implementation (sequential character matching)
- `agents/decisions/operational-practices.md`: "when index keys must be exact — fuzzy only for runtime recovery"
- Learning: "when writing memory-index trigger phrases" — exact matching is design intent
- `plans/when-resolve-fix` (referenced in learnings) — never created, planned fuzzy improvement never implemented. Direction now reversed.

## Open Questions

None — failure modes and error messages specified.
