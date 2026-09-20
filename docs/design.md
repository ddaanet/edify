# Edify — Living Design

**Status:** Partial. The CLI is implemented and pinned by tests. The skills
pipeline is prose, revived 2026-08, simplified to one runbook stage 2026-09, and
not yet exercised end to end.

Edify is two artifacts in one git tree: the `edify-cli` PyPI package (source in
`src/edify/`) and the `edify` Claude Code plugin (`plugin/`). Direction:
Lean-assisted, formal-proof-backed requirements tracking.

This document is the hub: what the system is, and why, in the sections below.
`docs/decisions.md` indexes every decision as one conclusion line, and
`docs/references/` holds one node per decision group, carrying the argument.
Read the node before making a claim about, or changing, the mechanism it argues.

## 1. Now

**Focus** — dogfood the one-stage pipeline end to end (`/design` → `/runbook` →
`/build`). The one-stage runbook landed 2026-09-01 and `/build` replaced the
`/inline` + `/orchestrate` split on 2026-09-17; the composed-prompt dispatch and
slice-batched TDD have not yet run against a real plan (L-6).

**Next** — a `/gitlore:index-audit` pass over the memory store.

**Do not re-litigate** — the planning-to-execution session boundary (D-25 keeps
it on context-budget grounds, not discoverability); the publication postponement
(D-9); the one-stage runbook — it is the terminal planning artifact (§5.3, FR-9)
and a strong orchestrator composes every dispatch prompt from it live (D-24),
which retired the three-tier structure (D-34). Pre-written step files were the
weak-orchestrator premise, rejected in `docs/references/pipeline-contracts.md`.

## 2. Status legend

| Status | Meaning |
|---|---|
| **Done** | Implemented and pinned by a test |
| **Done (prose)** | Skill or agent instructions; no code, no test |
| **Partial** | Implemented, with a stated gap |
| **Planned** | Decided, not built |

## 3. Functional requirements

### 3.1 CLI

| # | Requirement | Status | Where · pinned by |
|---|---|---|---|
| FR-1 | List top-level sessions for a project | Done | `cli.py:list_sessions`, `discovery.py` · `test_cli_list.py`, `test_discovery.py` |
| FR-2 | Extract feedback from one session, recursing through its agent tree | Done | `cli.py:extract`, `extraction.py` · `test_cli_extract_basic.py`, `test_cli_extract_output.py`, `test_extraction.py`, `test_agent_files.py` |
| FR-3 | Batch-collect feedback across all sessions | Done | `cli.py:collect` · `test_cli_collect.py` |
| FR-4 | Count tokens per file via the Anthropic API, resolving model aliases | Done | `tokens.py`, `tokens_cli.py`, `token_cache.py` · `test_cli_tokens*.py`, `test_tokens_*.py`, `test_token_cache*.py` |
| FR-5 | Postprocess Claude-authored markdown into valid CommonMark | Done | `markdown*.py` · `test_cli_markdown.py`, `test_markdown_*.py` |
| FR-6 | Verify a Python target against its icontract contract (CrossHair) | Done | `check.py`, `check_cli.py` · `test_cli_check.py`, `test_check_e2e.py`, `test_check_parse.py`, `test_check_argv.py` |

`extract` and `collect` read paths from the project history dir; `markdown`
reads paths from stdin. `tokens` takes the model as an option and files as
positional arguments.

### 3.2 Plugin

| # | Requirement | Status | Where · pinned by |
|---|---|---|---|
| FR-7 | Capture requirements from conversation into `requirements.md` | Done (prose) | `skills/requirements/` |
| FR-8 | Triage complexity, produce design artifacts, route to `/build` or `/runbook` | Done (prose) | `skills/design/` |
| FR-9 | Decompose a design into a one-stage runbook: typed phases of prose items, interface blocks, behaviour slices | Done (prose) | `skills/runbook/`, `references/runbook-format.md` |
| FR-10 | Execute a runbook by composing each dispatch prompt from its items, four dispatches per TDD slice | Done (prose) | `skills/build/`, `references/dispatch-composition.md` |
| FR-11 | Wrap runbook-less work in a lifecycle: pre-work → execute → corrector → triage → deliverable-review | Done (prose) | `skills/build/` |
| FR-12 | Review every pipeline transformation at a typed gate | Done (prose) | `agents/*corrector*.md`, `agents/runbook-simplifier.md` |
| FR-13 | Review production artifacts against ISO 25010 / IEEE 1012 axes | Done (prose) | `skills/deliverable-review/` |
| FR-14 | Select and read relevant memory entries at pipeline recall checkpoints | Done (prose) | `skills/recall/` |
| FR-15 | Ground methodology claims in external research before asserting them | Done (prose) | `skills/ground/` |
| FR-16 | Validate an artifact item-by-item with forced verdicts | Done (prose) | `skills/proof/` |
| FR-17 | Write an icontract contract for a function and repair it against CrossHair | Done (prose) | `skills/formalize/` |
| FR-18 | Provide the version-matched CLI to the plugin at session start | Done | `bin/bootstrap-venv.sh`, `hooks/hooks.json` · `tests/bootstrap-venv.bats` via `test_bootstrap_hook.py` |

FR-19 (step artifacts from a runbook) and FR-20 (deterministic runbook structure
checks) were dropped 2026-09-01 with the two-stage runbook
(`docs/references/pipeline-contracts.md`); the IDs are not reused.

## 4. Non-functional requirements

| # | Requirement | Status | Where · pinned by |
|---|---|---|---|
| NFR-1 | No source or prose file exceeds the cap its path picks — 400 lines, 200 for a `SKILL.md` hub | Done | `scripts/check_line_limits.sh` and its allowlist sidecar, run by `just precommit` behind `rumdl fmt --check` · `tests/test_line_limits.py` |
| NFR-2 | Errors never pass silently — no `\|\| true`, no `2>/dev/null`, no ignored exit codes | Done (prose) | `CLAUDE.md` "Error Handling" |
| NFR-3 | Agent-consumed commands emit structured markdown on stdout and signal via exit code | Done | D-1 |
| NFR-4 | Plugin and package versions move in lockstep | Done | `bin/check-version-consistency.py` |
| NFR-5 | A missing `uv` degrades to an informative message, never a blocked session | Done | `bin/bootstrap-venv.sh` · `tests/bootstrap-venv.bats` |
| NFR-6 | The markdown pipeline is idempotent: `(preprocessor → remark)²` is a fixed point | Done | `test_markdown_fixtures.py` |
| NFR-7 | Full type annotations under strict mypy | Done | `just lint` |

## 5. Architecture

### 5.1 One tree, two products

The repo root *is* the `edify-cli` package: `pyproject.toml` at root, source in
`src/edify/`, hatchling build, uv for dependency management, Python ≥3.14. The
Claude Code plugin is a plain tracked subdirectory `plugin/`, holding
`.claude-plugin/plugin.json`, `skills/`, `agents/`, `bin/`, `fragments/` and
`hooks/`. `plugin/` is the plugin root, so a subdir-sourced install copies
exactly `plugin/` and never the sibling `src/` tree.

The plugin does not ship the CLI's code. It obtains the CLI at runtime through a
`SessionStart` hook that builds a venv with uv (§5.4). The two are locked to one
version by `plugin/bin/check-version-consistency.py`, which requires
`plugin.json` version == `pyproject.toml` version — currently `0.1.1`.

`memory/` is a separate submodule, gated by gitlore. It is unaffected by the
plugin de-submodule and stays a submodule.

### 5.2 CLI structure

`src/edify/` is flat — no subpackages. Modules split by functional
responsibility under a 400-line hard limit (NFR-1): `discovery` (session and
agent-file enumeration), `parsing` (content extraction and filtering),
`extraction` (recursive feedback collection), `paths` (project-path encoding),
`models` (Pydantic types), `markdown*` (the postprocessor, split across
`markdown`, `markdown_parsing`, `markdown_block_fixes`, `markdown_inline_fixes`,
`markdown_list_fixes`), `tokens` + `tokens_cli` + `token_cache` + `user_config`,
`check` + `check_cli`, `exceptions`, and `cli` as the Click entry point
(`edify = "edify.cli:main"`).

`__init__.py` stays empty: callers import from the specific module rather than
package-level re-exports.

Private helpers live beside their callers — `_extract_feedback_from_file()` in
`parsing.py`, `_process_agent_file()` in `discovery.py` — and get extracted only
when complexity limits force it.

**Session storage.** Claude Code stores transcripts under
`~/.claude/projects/<encoded-path>/`, where the encoding replaces `/` with `-`
(root `"/"` → `"-"`). `paths.py:encode_project_path()` reproduces that.
Top-level session files are validated by UUID regex, which is what excludes
`agent-*.jsonl`. Agent IDs *are* session IDs for child agents, so recursive
collection is plain tree recursion with no special tracking.

### 5.3 Pipeline structure

The plugin is a skills bundle plus standing agents plus two verification
scripts.

Pipeline skills: `requirements` → `design` → `runbook` → `build`, or `design` →
`build` for work that needs no runbook, with `review` as the in-progress quality
gate. Standalone skills: `proof`, `ground`, `deliverable-review`, `formalize`,
`recall`.

The runbook is one artifact, `plans/<job>/runbook.md`: typed phases (`tdd` /
`general`) of prose items against named targets, each carrying requirement IDs,
an `Interfaces:` block where another item consumes its output, and — for tdd
items — behaviour slices with per-slice test lists
(`plugin/skills/runbook/references/runbook-format.md`). Nothing expands it:
`runbook-corrector` and `runbook-simplifier` gate it, `/proof` validates it, and
`/build` reads it and composes every dispatch prompt live
(`plugin/skills/build/references/dispatch-composition.md`).

Standing agents in `plugin/agents/`: the correctors (`corrector`,
`design-corrector`, `outline-corrector`, `runbook-corrector`,
`runbook-simplifier`), the executors (`artisan`, `test-driver`, `refactor`), and
the investigators (`scout`, `tdd-auditor`, `brainstorm-name`).

Scripts: `plugin/skills/build/scripts/verify-step.sh` (clean tree + precommit
after every committing dispatch — GREEN, code review and general items, never
after a RED or a test review whose tests are uncommitted by design) and
`plugin/bin/triage-feedback.sh` (the post-execution gate `/build` runs when the
work is done, D-26 T5).

The orchestrator owns every commit a review produces. A corrector applies
fix-all and never commits; after the per-slice code review the orchestrator
commits the corrector's fixes, the same step it takes at a phase boundary, and
`verify-step.sh` runs after that commit. A slice's own commit is the
implementer's, made in GREEN mode.

**Slice commits carry `Item N.M/k` in the subject.** The convention is
`<type>: Item N.M/k — <title>`, and the type is the executor's choice — `feat`,
`fix`, `docs`, `perf`, `test`, `build` and `chore` are all legitimate, since a
slice that pins an error path is not a feature. Nothing keys on it: the
installed gitmoji `commit-msg` hook rewrites the prefix to an emoji before the
commit is written, so the `Item N.M/k` marker, which the hook preserves, is the
only thing `tdd-auditor` may match in a subject. A reviewed slice carries two
commits with that marker — the implementer's GREEN commit and the orchestrator's
review-fix commit — so subject matching alone cannot pick the slice out. The
auditor keys on the hash the GREEN report names; the report also records the
tests run and the one-at-a-time sequence, and the session's `subagents/`
transcripts are the fallback where a report is missing. Git serves only to
confirm the named commit exists and to diff it.

**Delegation is by reference.** The orchestrator's prompt carries the item text
and the paths of the design and recall artifacts, never their content (D-24).

### 5.4 Runtime bootstrap

`plugin/hooks/hooks.json` registers one `SessionStart` command hook running
`${CLAUDE_PLUGIN_ROOT}/bin/bootstrap-venv.sh` with a 300 s timeout. The script
is POSIX sh and shellcheck-clean. It parses the pinned version from
`plugin.json`, fast-path exits when `venv-<version>/bin/edify` already exists,
otherwise prunes stale `venv-*` siblings, runs `uv venv --python '>=3.14'` plus
`uv pip install edify-cli==<version>`, and links `current`.

Any bootstrap failure — uv missing, venv build, install — emits SessionStart
JSON (`systemMessage` for the user, `hookSpecificOutput.additionalContext` for
Claude) and exits 0, so the session is never blocked. A missing version in
`plugin.json` is a packaging defect and exits 2.

Skills reach the binary as `${CLAUDE_PLUGIN_DATA}/current/bin/edify`, relying on
placeholder substitution in skill content rather than a live environment
variable (D-12).

## 6. Decisions

Conclusions are indexed in `docs/decisions.md` — one line per decision, grouped
by the node that argues it. The arguments live in `docs/references/`:

- `cli-and-package.md` — the `edify-cli` package, the plugin/package split, the
  runtime bootstrap, the markdown postprocessor and the token counter.
- `testing.md` — what a RED assertion proves, real-git e2e, `CliRunner`,
  self-diagnosing setup.
- `pipeline-contracts.md` — dispatch by reference, the planning/execution
  session boundary, the typed review gates, phase types, artifact provenance.
- `execution-routing.md` — the planning artifacts, the runbook discriminators,
  classification, escalation tiers.
- `agent-instructions.md` — model assignment per dispatch, instruction ordering,
  format and density.
- `quality-gates.md` — gate layering, chokepoint placement, tool-call anchors.
- `deliverable-review.md` — what counts as a deliverable, the review axes,
  finding resolution.
- `project-configuration.md` — rules files, sub-agent capabilities, line caps,
  naming, agent frontmatter.

## 7. Rejected alternatives

Named in `docs/decisions.md`, one *Rejected* line per decision group; each
group's node argues them under its own `## Rejected alternatives` heading.

## 8. Limitations

L-1 (`prepare-runbook.py` test coverage) closed 2026-09-01 by deletion of the
script; the ID is not reused.

**L-2 — The routing thresholds are ungrounded operational parameters.** The
file-count and component-count figures `/design` uses to triage complexity have
no empirical calibration, and the runbook decision carries no numbers at all —
its second discriminator is judgement with no item count behind it (D-82). The
route *structure* is justified (D-34, D-82); the parameters inside it are not.
`plans/reports/triage-feedback-log.md` collects per-execution evidence — files
changed, agent count, behavioral code, classification verdict — for eventual
calibration.

**L-3 — Several prompt-structure figures are heuristics, not measurements.** The
20/60/20 distribution comes from organizational change management, and the
~200-rule adherence ceiling is an empirical observation without a calibrated
method behind it.

**L-4 — Turn and duration bounds do not exist.** The `Agent` tool has no
`max_turns` parameter and no duration bound, so the spinning/hanging taxonomy
has no enforcement. See `plugin/fragments/escalation-acceptance.md`.

**L-6 — The pipeline is unvalidated.** The one-stage runbook and slice-batched
TDD landed 2026-09-01 and have not been exercised end to end. Slice-batching
cost and the test review's catch rate are unvalidated until the dogfood run
supplies counts (dispatches per item, wrong-reason tests caught, slices whose
GREEN revised the list); the implementation-shortcut risk from an executor
seeing a whole slice's tests is detected by `tdd-auditor` and likewise
unmeasured. The earlier weak-orchestrator claim rested on a single small
execution in 2026-01 with estimated, not measured, figures.


## 9. Non-goals

**Publishing to PyPI and the marketplace** — parked indefinitely by user
decision (D-9), not blocked.

**Cross-version compatibility** — there is no user base, so nothing is kept for
migration's sake.

**Model-specific instruction variants** — deferred until haiku execution quality
becomes a demonstrated problem.

**Glob expansion inside `edify tokens`** — shell expansion covers it.

**A dprint plugin replacing the markdown preprocessor** — single-pass processing
and cleaner toolchain integration would be better, but the preprocessor works
and the migration is not scheduled.

## 10. Changelog

`docs/changelog.md` — design-significant changes only: decisions reversed,
subsystems built or torn down, requirements added or dropped. Git history is the
full record; the changelog carries what explains why the project is the way it
is.
