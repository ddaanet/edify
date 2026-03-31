# Brief: p: Directive Triggers Brief Generation

## Problem

`p:` directive assesses model tier and defers session.md write to handoff, but doesn't create `plans/<slug>/brief.md`. Plan-backed tasks are mandatory — every task needs a plan directory with at least one artifact. Currently the brief is created ad-hoc or forgotten.

## Proposed Change

When `p:` creates a pending task:
1. Create `plans/<slug>/` directory
2. Write `brief.md` capturing the task context from conversation
3. Task command references the brief: `/design plans/<slug>/brief.md`

Same applies to `d:` mode conclusions that produce pending work — the discussion context that motivated the task should be captured in the brief, not lost to conversation history.

## Scope

Edit `plugin/fragments/execute-rule.md` — p: directive section. Agentic-prose change.
