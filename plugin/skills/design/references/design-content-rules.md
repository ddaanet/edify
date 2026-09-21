# Design Content Rules

Content principles and structure guidance for Phase C.1 design document
generation, plus the Provenance section every `/design` artifact carries.

## Content Principles

- Dense, not verbose -- downstream agents are intelligent
- Decisions with rationale, not just conclusions
- Concrete file paths and integration points
- Explicit scope boundaries (in/out)

## Decision Tradeoff Documentation

Each major architectural decision in design.md must include accepted tradeoffs —
what the choice makes harder or more expensive, not just what it achieves.
Follows ADR consequences pattern (Nygard 2011, Y-statement format).

Embed within each decision's rationale:
- **Decision:** [the choice]
- **Rationale:** [why this approach]
- **Accepted tradeoffs:** [what becomes harder, more expensive, or constrained]

Required for decisions affecting module boundaries, API contracts, execution
model, or downstream workflow. Not required for routine implementation choices
(variable names, standard patterns).

## Density Checkpoint

Before generating design, validate outline item granularity:
- **Too granular:** >8 items per phase, or adjacent items with <20 LOC delta
  each -- collapse into parent item or merge adjacents
  *(both thresholds ungrounded — need calibration)*
- **Too coarse:** Single item handling >3 unrelated concerns or spanning
  multiple module boundaries -- split by concern
- **Heuristic:** items-per-phase x avg-LOC-per-item should fall in the 100-300
  range. Below 100 suggests items are trivially small; above 300 suggests items
  are overloaded. *(ungrounded — needs calibration)*
- Flag and fix before proceeding to design generation.

## Repetition Helper Prescription

When design specifies 5+ operations following the same pattern (e.g., "update
field X in files A, B, C, D, E, F"), recommend extracting a helper function or
script. Rationale: repeated manual operations multiply both token cost (each
repetition consumes planning + execution budget) and error rate (drift between
repetitions increases with count). Five is an arbitrary trigger point, not
calibrated against measured extraction or repetition cost.

## Agent-Name Validation

Before finalizing design, verify all referenced agent names exist on disk:
- `rg --files` (Bash) over `plugin/agents/*.md`, `.claude/agents/*.md`, and
  `.claude/plugins/*/agents/*.md`
- Every agent name in the design must resolve to an actual file
- If an agent name doesn't exist: flag as design error, not an implementation
  detail to defer
- Prevention: catches naming mismatches (e.g., `outline-corrector` vs
  `runbook-corrector`) before they propagate to planning and execution

## Late-Addition Completeness Check

Requirements added after outline review (Phase B) must be re-validated before
design generation:
- **Traceability:** Does the new requirement map to a specific outline item or
  design section?
- **Mechanism:** Does the new requirement specify a concrete implementation
  approach, not just a goal?
- If a late-added requirement lacks either: flag for completion before
  proceeding.
- Grounding: FR-18 added during a design session bypassed outline-level
  validation, resulting in a mechanism-free specification that downstream
  planners could not implement.

## Classification Tables Are Binding

When design includes classification tables (e.g., "X is type A, Y is type B"),
these are LITERAL constraints for downstream planners/agents, not interpretable
guidelines. Planners must pass classifications through verbatim to delegated
agents.

Format classification tables with explicit scope:
- Default behavior (what happens without markers)
- Opt-out mechanism (how to deviate from default)
- Complete enumeration (all cases covered)

## Structure Guidance (adapt as needed)

- Provenance (see below)
- Problem statement
- Requirements (functional, non-functional, out of scope)
- Architecture/approach
- Key design decisions with rationale
- Implementation notes (affected files, testing strategy)
- References (see below)
- Documentation Perimeter (see below)
- Next steps

## Requirements Section Format

When requirements.md exists in job directory, include traceability mapping:

```markdown
## Requirements

**Source:** `plans/<job-name>/requirements.md` (or inline if documented during design)

**Functional:**
- FR-1: [requirement] -- addressed by [design decision/section]
- FR-2: [requirement] -- addressed by [design decision/section]

**Non-functional:**
- NFR-1: [requirement] -- addressed by [design decision/section]

**Out of scope:**
- [item] -- rationale
```

Each requirement should map to a design element for downstream validation.

## TDD Mode Additions

For designs with behavioral phases, include spike test strategy, confirmation
markers for uncertain decisions, "what might already work" analysis. Reference
the integration-first ordering (defined in
`plugin/skills/runbook/references/runbook-format.md`) -- note when
integration-first ordering applies (external boundaries -> internal logic, not
bottom-up by module).

## Provenance Section

Every `/design` artifact carries one -- `outline.md` and `design.md` alike,
since the agentic-prose route produces only an outline.
`/edify:deliverable-review` reads it to build its review range.

```markdown
## Provenance

- **Derived from:** `plans/<prior-job>/reports/deliverable-review.md`, superseding `plans/<prior-job>/outline.md`
- **Base:** `<full sha>` -- the commit the deliverable started from
```

- **Derived from:** the review report that motivated this design *and* the
  artifact it supersedes, or `none`. Naming both is what makes the base
  copyable -- a second pass in a new job directory has no other route to it.
- **Base:** on a first pass, run `git rev-parse HEAD` and record the full sha.
  On a second pass, open the artifact named in `Derived from:` and
  **copy its `Base:` verbatim**; never recompute it. Recomputing makes the range
  start after the first pass's work, so the review sees the fixes instead of the
  deliverable -- and a too-narrow diff reads as a clean review, so nothing
  surfaces the error.

Taking `HEAD` at generation time is correct: `plans/` is excluded from the
review diff, so the artifact's own commit cannot pollute the range it defines.

Distinct from §References, which is a reading list. Provenance carries a git ref
a later command substitutes into `git diff`.

## References Section

Track research artifacts and external references that informed the design --
what shaped it, distinct from Documentation Perimeter (forward-looking -- what
the planner should read).

```markdown
## References

- `plans/<job-name>/reports/explore-<topic>.md` -- codebase exploration findings
- `plans/reports/<topic>-grounding.md` -- grounding research (if `/ground`
  invoked)
- [External Paper Title](url) -- informed decision D-3
- Context7: `/org/project` -- queried for hook configuration patterns
```

**Include when:** Any Phase A research produced reports, external sources were
consulted, or `/ground` was invoked. Omit if design was based entirely on loaded
internal documentation.

## Documentation Perimeter Section

Include this section specifying what the planner should read before starting:

```markdown
## Documentation Perimeter

**Required reading (planner must load before starting):**
- `docs/design.md` §5 "Architecture" -- module patterns, path handling
- `plugin/fragments/delegation.md` -- quiet execution pattern
- `plans/{job-name}/reports/explore-{topic}.md` -- exploration results

**Context7 references:**
- `/anthropics/claude-code` -- hook configuration patterns (query: "PostToolUse hooks")

**Pipeline contracts:** `docs/references/pipeline-contracts.md` (for tasks producing runbooks)

**Additional research allowed:** Planner may do additional Context7 queries or exploration for technical implementation details not covered above.
```

**Rationale:** Designer has deepest understanding of what knowledge the task
requires. Encoding this explicitly prevents planner from either under-reading
(missing critical context) or over-reading (wasting tokens on irrelevant docs).

## Skill-Loading Directives

**Plugin-related topics (hooks, agents, skills, plugins):** When the design
involves Claude Code plugin components, include a skill-loading directive in
"Next steps":
- Hooks -> `Load plugin-dev:hook-development before planning`
- Agents -> `Load plugin-dev:agent-development before planning`
- Skills -> `Load plugin-dev:skill-development before planning`
- Plugin structure -> `Load plugin-dev:plugin-structure before planning`
- MCP integration -> `Load plugin-dev:mcp-integration before planning`

This ensures the planner has domain-specific guidance loaded before creating the
runbook.

## Execution Model Directives

When the design involves modifying the living design (`docs/design.md`,
`docs/decisions.md`, `docs/references/`), skill files (`plugin/skills/`), or
agent procedures (`plugin/agents/`), include an execution directive in "Next
steps":
- Workflow/skill/agent edits: opus required

Ensures architectural artifacts get appropriate scrutiny during execution, not
just planning.
