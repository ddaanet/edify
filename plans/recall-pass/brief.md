# Recall Pass — Brief

## Problem

Project memory (learnings, decision files) has 2.9% baseline recall rate. Agents don't invoke `/when` proactively. The UserPromptSubmit topic detection hook (recommended by frozen-domain analysis in remember-skill-update) is necessary but insufficient — it fires on raw user input before semantic context is established.

Memory recall should be part of the discovery process, not a prompt-time keyword match.

## Core Concept: Recall Pass

A **recall pass** is an explicit step in the agent pipeline where project memory is read, relevant entries are selected by name, and results are forwarded to downstream stages.

## 4-Pass Model with Reference Forwarding

Each pass produces a **recall artifact** — named references + decision file content — that forwards to all downstream stages. Later passes augment rather than restart.

### Pass 1 — Design recall (deepest, broadest)

- Read `memory-index.md` → select relevant decision files → read whole files
- Enumerate each relevant entry by name (explicit list, not ambient context)
- Output: recall artifact (named references + decision file content)
- Forwards to all downstream stages

### Pass 2 — Runbook recall (implementation-focused)

- Inherit Pass 1 artifact
- Add implementation learnings (`decisions/implementation-notes.md`)
- Add testing learnings (`decisions/testing.md`)
- Domain-specific: TDD cycle pitfalls, step file quality, precommit gotchas
- Output: augmented artifact (Pass 1 + implementation + testing)

### Pass 3 — Task agent injection (filtered)

- Inherit accumulated artifact
- Orchestrator filters to phase-relevant subset
- Injected in task prompt — agent receives, doesn't discover

### Pass 4 — Review recall (failure-mode focused)

- Inherit accumulated artifact
- Add review-specific patterns (common failure modes, quality anti-patterns)
- Used by correction agents and deliverable-review

## Key Design Decisions

**Reference forwarding over re-discovery:** Breadth comes from forwarding accumulated context, not repeating recall loops. Dissolves the convergence problem — no need to iterate until no new entries surface.

**Named enumeration:** Each relevant entry is listed by name. Downstream stages can reference "the learning about merge commit --amend failures" explicitly. Makes the artifact traceable.

**Decision files as primary source:** Pass 1 reads whole decision files, not individual learnings. Decision files are the permanent knowledge store; learnings.md is the transient buffer.

**Domain-specific augmentation:** Each pass adds its domain lens. Design adds architectural context, runbook adds implementation + testing, review adds failure modes.

**Weighted injection, not uniform:** Deep recall at design + runbook + review. Filtered injection at orchestration. No recall at mechanical dispatch.

## Pipeline View

```
Design ──[recall artifact]──→ Runbook ──[augmented]──→ Orchestrate ──[filtered]──→ Review
  ↑ deep pass                   ↑ +impl +testing        ↑ per-phase subset         ↑ +failure modes
  reads whole decision files    reads whole files        injected in prompts         reads whole files
```

## Integration Points

Recall passes trigger at key points in: `/design`, `/runbook`, `/orchestrate` (inline ops), `/deliverable-review`. Results injected in prompts of task agents and correction agents.

UserPromptSubmit topic detection remains as cheap first layer (keyword matching, zero agent cooperation). Recall passes are the deep layer.

## Open Questions

- Recall artifact format (markdown section? separate file? structured data?)
- How the orchestrator filters the accumulated artifact per phase
- Whether mid-design recall (second pass after exploration, before synthesis) adds value
- Grounding needed: RAG pipeline patterns, multi-stage retrieval literature
