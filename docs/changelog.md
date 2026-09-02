# Changelog

How edify got here. **Design-significant changes only** — decisions reversed,
subsystems built or torn down, requirements added or dropped, a rationale that
turned out false. Git history is already the full changelog and needs no
duplicate here; what belongs on this page is what explains why the project is
the way it is, never a line-by-line account of every edit. An entry earns its
place by answering a question a future reader would otherwise ask of
`docs/design.md` and find no answer to.

`docs/design.md` holds the present-tense answer to *what the system is and why*.
This file is the write-time record of how it got that way.

## 2026-09-02 — Shared ddaanet conventions load in every session; the design record sheds situational state

`CLAUDE.md` now imports `@memory/ddaanet/shared-claude.md`. That file declares
itself the always-in-context tier for every repo mounting the `ddaanet` memory
store — the scope between a repo's own conventions and `~/.claude/CLAUDE.md` —
but edify had never wired the import, so its standing defaults reached no
session here.

L-5 is retired rather than corrected. It recorded that `memory/MEMORY.md`
exceeded the loader cutoff, with a byte figure that went stale within days. A
measurement of a store that changes on every memory write is situational state,
not a design limitation, and neither the size nor the "the index is truncated"
claim belongs in a present-tense design record; the retirement pass it called
for is `/gitlore:index-audit`. Limitation IDs are referenceable, so the gap
stands rather than renumbering L-6.

## 2026-09-01 — One-stage runbook replaces the two-stage expansion pipeline

The expanded-runbook stage — outline → phase files → assembled runbook →
step files and an orchestrator manifest — existed so a weak (haiku)
orchestrator could dispatch pre-written sub-agent prompts. The user's
diagnosis from operating the pre-teardown pipeline was that a strong
orchestrator does not need them and that pre-written prompts turn harmful the
moment implementation deviates; the revived two-stage pipeline had also never
been run end to end (`plans/pipeline-simplification/requirements.md`, C-1).

`/runbook` now writes `plans/<job>/runbook.md` as the terminal planning
artifact: typed phases of prose items with requirement IDs, `Interfaces:`
blocks where one item feeds another, and behaviour slices on tdd items.
`runbook-corrector` (the renamed outline corrector) and `runbook-simplifier`
gate it, `/proof` validates it, and `/orchestrate` composes every dispatch
prompt from it live. TDD runs four dispatches per slice — RED, test review,
GREEN, code review — with `refactor` on review signal and a list-revision step
after each slice; `test-driver` owns RED and GREEN as two named modes.

Deleted in one pass: `prepare-runbook.py`, `validate-runbook.py` and its
tests, `assemble-runbook.py`, `split-execution-plan.py`, `verify-red.sh`,
`/review-plan`, the old `runbook-corrector`, `plugin/docs/`, and the tier-3
runbook references — 7,029 lines / 97,724 tokens measured before deletion
(`plans/pipeline-simplification/reports/measurements.md`). Deterministic
runbook validation does not survive (D-51). FR-19, FR-20 and L-1 closed;
D-31 superseded; D-24 to D-26, D-30, D-32 to D-35, D-39, D-49, D-69, L-2 and
L-6 rewired; §7 records the rejected two-stage model, per-test dispatch and
RED-less whole-task batching.

The planning/execution session boundary lost one of its two grounds. It was
kept on model-tier and context-budget grounds in 2026-08-13; orchestration no
longer runs a tier below planning, so D-25 now rests on context budget alone.

## 2026-08-14 — Decision records folded into one living design doc

The 23 files under `agents/decisions/` (~286KB) were folded into
`docs/design.md` and deleted. The fold triaged three ways: design rationale
moved into the design doc, live agent rules already covered by `CLAUDE.md` or
`memory/ddaanet/` were not duplicated, and content describing torn-down
subsystems was dropped rather than carried across.

Dropped subjects were verified absent from the tree first — the `analyze` and
`rules` CLI commands and `filtering.py`, the worktree CLI and its `session.md`
merge machinery, the memory-index validator and resolver, the retired autoformat
and recall-check hooks, and the CLAUDE.md fragment-ordering scheme.

The document follows the six-section format: functional requirements,
non-functional requirements, architecture, decisions, rejected alternatives,
changelog — with the resume affordances the project's living-design format adds
on top (status stamp, Now, status legend, and the split between limitations and
non-goals).

## 2026-08-13 — Per-plan generated agents retired

Execution now delegates by reference: the orchestrator dispatches a standing
agent with the path to a step file (D-24). The bespoke `<plan>-task`,
`<plan>-corrector`, `<plan>-tester` and `<plan>-implementer` definitions that
`prepare-runbook.py` used to generate into `.claude/agents/` are gone — they
fought the platform, since generated agents are not discoverable as
`subagent_type` values until session restart.

The forced planning/execution session restart stopped being a discoverability
requirement as a result. It was kept on model-tier and context-budget grounds
(D-25), and auto-chaining `/runbook` into `/orchestrate` was deliberately not
taken.

## 2026-08-10 — Sub-agent capability claims re-probed

Several long-standing claims about sub-agents were measured false. Sub-agents
have the `Skill` tool, receive `CLAUDE.md` and `memory/MEMORY.md` natively, and
can spawn sub-agents via `Agent`; there is no `Task` tool at any level (D-72).

The rule that execution agents never review their own work survived the
falsification, but as policy rather than capability limit — it holds *because*
an execution agent is now technically able to review its own work and must not
(D-28).

## 2026-08-04 — Pipeline revived

The workflow pipeline was restored from the `edify-plugin` GitHub repo, the only
place the purged history survived, and rewired off the dead subsystems it
depended on. Recall became a read of `memory/MEMORY.md` and the files it
indexes, `/commit` and `/handoff` moved to the `commit-commands` and `handoff`
plugins, and the session task frame became `.claude/handoff-task.md`.

## 2026-07-17 — Bootstrap reversed from stdlib venv to uv

The previous day's choice of a stdlib venv (`python3 -m venv` + pip) was
reversed. A stdlib venv inherits the host interpreter, so it required host
`python3` ≥3.14 and failed loudly otherwise — unshippable on hosts still at
3.13. uv fetches its own interpreter, removing the host floor. The price is a uv
runtime dependency, paid down by informative degradation when uv is absent
(NFR-5).

Publication was postponed indefinitely by user decision the same day (D-9): the
PyPI publish and the marketplace `git-subdir` entry are parked, so edify is
uninstallable meanwhile.

## 2026-07-16 — Plugin de-submoduled

`plugin/` stopped being a git submodule and became a plain tracked subdirectory
of the package repo (D-10, commit `c3c4477f`). The submodule shipped a live
defect: a parent repo cannot `git add` inside a submodule, so
`git add plugin/.claude-plugin/plugin.json` failed and `just release` could not
complete a real release. The old `ddaanet/edify-plugin` GitHub repo was
archived.

## 2026-05 — Teardown

The homegrown workflow system was removed in favour of the ecosystem
(superpowers plus auto-memory), and the project's direction narrowed to
Lean-assisted, formal-proof-backed requirements tracking. Session scraping,
token counting, markdown tooling and contract checking survived as the CLI.
(Partially reversed by the 2026-08-04 revival above.)

## 2026-02 — Pipeline contracts and execution tiers

Pipeline contracts, review gates, execution tiers and model-selection rules
accumulated from operational incidents through the month. The three-tier
execution structure was grounded in execution-environment constraints — context
window capacity, delegation overhead, prompt generation cost — rather than in an
external methodology framework (D-34).

## 2026-01 — Weak orchestrator and TDD workflow

The weak-orchestrator pattern and the TDD workflow were delivered, along with
the terminology still in use: job (the user's goal), design (architectural
spec), runbook (implementation steps), step (individual unit of work). The
pattern was claimed on a single small execution, and the token-cost and
reliability figures quoted alongside that claim were estimates rather than
measurements (L-6).

remark-cli was selected as the markdown formatter over Prettier and
markdownlint-cli2 after a corpus evaluation (D-14).
