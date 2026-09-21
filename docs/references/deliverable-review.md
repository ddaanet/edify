# Deliverable review

Decisions governing the post-execution review of production artifacts: what
counts as a deliverable, which axes each artifact type is judged on, and what a
review may and may not conclude. Read this before running or changing
`/edify:deliverable-review`.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

**D-55 — A deliverable is a production artifact that persists after execution
and affects system behavior.** Identify by comparing the in-scope section of the
job's design artifact — `design.md`, else `outline.md` — against the repository
diff over the range D-80's Provenance defines: every created or modified file
that is not a planning or execution artifact is a deliverable. The artifact
specifies what should exist; the diff shows what was produced; the gap between
them is findings — missing deliverables (incompleteness) or unspecified ones
(excess).

**D-56 — Each deliverable is classified into exactly one type, and the type
selects the axes.** Types: code, test, agentic prose, human documentation,
configuration.

*Universal axes:* conformance (satisfies the design spec's conditions — IEEE
1012), functional correctness and functional completeness (ISO 25010), vacuity
(does real work rather than ceremony), excess (anything unspecified).

*Code:* robustness, modularity, testability, idempotency, error signaling.
*Test:* specificity (fails for the right reason and only that), coverage,
independence (verifies behavior, not implementation). *Agentic prose:*
actionability (every step maps to a tool call or state change), constraint
precision (measurable criteria, not "relevant"/"appropriate"), determinism,
scope boundaries. *Human documentation:* accuracy, consistency, completeness,
usability.

Findings are Critical (incorrect behavior, data loss, security), Major (missing
functionality, broken references, vacuous artifact) or Minor (style, clarity,
naming).

*Sources:*
[ISO/IEC 25010:2023](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010),
[IEEE 1012](https://standards.ieee.org/ieee/1012/5609/),
[ISO/IEC 26514](https://www.iso.org/standard/43073.html),
[AGENTIF benchmark](https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf),
[arXiv 2601.03359](https://arxiv.org/abs/2601.03359),
[Anthropic: Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

**D-57 — Holistic review catches what per-step review structurally cannot.**
Per-step review validates each step's artifacts against that step's scope; it
cannot catch gaps between files that were never both in scope at once — stale
copies, broken references, missing cross-references, naming drift.

**D-58 — Every finding resolves to a fix or a tracked task.** There is no third
option. "Minor findings deferred, no task created" is abandonment: the finding
disappears from every active surface. Severity exists so report readers can
assess risk, not as skip permission for executors. "Noted in report" is not a
resolution, because reports are not read proactively.

**D-59 — Reviews report severity counts and make no merge-readiness judgment.**
A review that classifies findings as Major and then adds "doesn't block merge,
follow-up work" is sycophancy in artifact form — the reviewer softening its own
classification to avoid blocking the pipeline. The user reads the counts and
decides.

**D-60 — Route findings unconditionally to `/design`.** Conditional dispatch on
fix size or an "architectural?" judgment reintroduces judgment at a stage that
should be mechanical. `/design` triage already handles proportionality.
