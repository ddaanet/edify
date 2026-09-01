# Recall Artifact: Pipeline Simplification

Read each file listed below — do not rely on inline summaries.

## Entries

memory/workflow-pipeline-revival.md — the state this replaces: revived 2026-08-04 by reference-sweep, no test coverage, never run end-to-end
memory/strategic-pivot.md — superpowers is the baseline process skillset; the revival restored tooling, not the mission
memory/cc-subagent-context-capabilities.md — a child's result never reaches its parent; no `max_turns`; `SendMessage` resumption; subagents get the index but no auto-fetch — constrains what the orchestrator can rely on
memory/ddaanet/green-is-not-evidence.md — ghmem B1 observation: one wrong-reason test per task; RED must be dispatched separately from GREEN so a reviewer can hunt it
memory/ddaanet/outside-in-tdd.md — e2e red first when architecture is settled; a plan-ordering property, independent of who writes tests
memory/ddaanet/remove-cleanly-no-vestigial.md — cut the whole machinery in one pass: tests, fixtures, docs, recipes, inbound refs
memory/distribution-published.md — no user base; compatibility is never a reason to keep anything
memory/ddaanet/plan-length-matches-work.md — plan doc length tracks executable work, not topic; informs the runbook format
memory/ddaanet/spec-enumerations-need-rederiving.md — this artifact's deletion lists are claims about the corpus; re-derive by grep at review time
memory/ddaanet/genuine-red-not-missing-sut.md — red = failed assertion via inert stub, one stub run validates a batch, second run against a wrong SUT proves wrongness detection; interface contracts one per line
memory/ddaanet/cc-subagent-approval.md — a one-shot sub-agent has no addressable parent; resumption is `SendMessage` to the agent's name, and a bare idle notification is not a report — constrains the orchestrator's dispatch/resume contract (FR-4)
memory/ddaanet/cc-async-task-notification-quirks.md — trust only the agent's own reply for its delegated task; a late notification on a reported task-id may answer something else — constrains how the orchestrator reads child completions (FR-4)
memory/feedback-stale-claims-survive-reference-sweeps.md — repointing references does not validate claims; re-derive capability assertions when rewiring `docs/design.md` (FR-7)
memory/feedback-decision-docs-are-living.md — rewire `docs/design.md` claims when components change; generalize where the mechanism dies but the principle survives (FR-7)
memory/ddaanet/design-doc-writing.md — changelog = design-significant only, dated rationale vs present-tense mechanism, superseding pointer stays on the old section (FR-7)
memory/ddaanet/directive-states-acts.md — agent-facing directives carry only the acts the reader performs; cut mechanism, rationale and prohibitions that introduce the forbidden thing (FR-4, FR-5 agent rewrites)
memory/ddaanet/skill-description-purpose-first.md — skill/agent `description:` = purpose, then "Use when", never a workflow summary; descriptions are injected every session (FR-1, FR-3, FR-4)
