# Brief: Centralize Recall Instructions

## Context

Recall instructions are scattered across 6+ skills and 4+ agent definitions, each with independently authored procedures of varying quality. This session demonstrated the failure mode: /design's A.1 says "Execute `/recall all` protocol" (vague prose, not Skill invocation), agent filled gap with speculative `_recall resolve` calls, 6/11 missed.

Current state by consumer:

| Consumer | Recall approach | Quality |
|----------|----------------|---------|
| /requirements | `Invoke /recall all` — explicit Skill reference | Good (template) |
| /design A.1 | "Execute `/recall all` protocol" — vague prose | Bad (looks like skill ref, isn't) |
| /design triage | Direct `_recall resolve` with speculative triggers | Bad (no index read) |
| /runbook Phase 0.5 | Inline "Read memory-index.md, identify, batch-resolve" | Medium (correct but duplicated) |
| /inline | Same inline procedure | Medium (duplicated) |
| /orchestrate | Same inline procedure | Medium (duplicated) |
| corrector.md | Loads memory-index skill via frontmatter | Bad (wrong mechanism) |
| other correctors | "Read memory-index.md... batch-resolve" | Medium (duplicated) |

## Proposed Change

### 1. Refactor /recall to segmented pattern

**Core SKILL.md (gate-only, target <1ktok):**
- Description + frontmatter
- Purpose: one paragraph
- Mode table: compact, names only
- Vague reference to references/ for process details ("consult references/ when executing a recall pass")
- No dispatch table, no process details in core

**Reference files (loaded as needed):**
- `references/standard.md` — default single-pass recall
- `references/deep.md` — aggressive tail-recursion
- `references/broad.md` — whole-file loading
- `references/all.md` — deep + broad combined
- `references/everything.md` — full corpus dump

Intentionally vague reference language in core: "process details in references/" rather than "Read references/standard.md." Agent checks whether content is already in context before reading — pattern matching on context, not metacognitive confidence.

### 2. Replace inline recall in consuming skills

Each skill's recall section becomes a `/recall` Skill invocation (or Read for sub-agents):

- **Main-session skills** (/design, /runbook, /inline, /orchestrate): `Invoke /recall` with appropriate mode
- **Sub-agents** (correctors, agents): `Read plugin/skills/recall/SKILL.md` for minimal core, then Read appropriate reference if needed
- **/requirements already follows this pattern** — use as template

### 3. Differentiate error paths in consumers

- **Recall artifact form** (batch from artifact): failure = stale artifact, unrecoverable at consumer, note in escalation
- **Keyword form** (contextual recall): failure = read memory-index, recoverable

## Evidence

- Skill re-injection test: Skill tool does NOT deduplicate. Three invocations → three complete copies in context. Repeated full /recall invocations are expensive.
- /requirements already uses the correct pattern (explicit Skill invocation with note: "This is a skill invocation — /recall handles memory-index scanning")
- Skill-development guide: SKILL.md target 1,500-2,000 words, detailed content in references/, progressive disclosure
- Session deviation: vague A.1 instruction + no index read → speculative recall → 55% miss rate

## Open Questions

- Exact token count for minimal core — need to draft to measure against <1ktok target
- Whether `/recall <context>` (indicating lens: designing, testing, implementing) is the right invocation pattern vs bare `/recall` with context inferred — discussed but not resolved
- Sub-agent path validation: does "Read plugin/skills/recall/SKILL.md" work reliably from agent definitions?

## Dependencies

- Task 1 (remove fuzzy matching) changes the error behavior consumers will see
- Task 2 (remove memory-index skill) removes one consumer pattern
