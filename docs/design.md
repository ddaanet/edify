# Edify — Living Design

**Status:** Partial. The CLI is implemented and pinned by tests. The skills
pipeline is prose, revived 2026-08 and not yet exercised end to end.

**Verified against:** `0eb3cdc2` (2026-08-14).

Edify is two artifacts in one git tree: the `edify-cli` PyPI package (source in
`src/edify/`) and the `edify` Claude Code plugin (`plugin/`). Direction:
Lean-assisted, formal-proof-backed requirements tracking.

## 1. Now

**Focus** — exercise the revived pipeline end to end (`/design` → `/runbook` →
`/orchestrate`). It is the first real exercise of the rewired step-file and
manifest shapes.

**Next** — test coverage for `plugin/bin/prepare-runbook.py`; the suite reaches
it only indirectly through `validate-runbook.py`'s imports.

**Do not re-litigate** — the planning-to-execution session boundary (D-24 keeps
it on model-tier and context-budget grounds, not discoverability); the
publication postponement (D-9); the three-tier execution structure (D-15, whose
*thresholds* are separately open as L-2).

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
| FR-8 | Triage complexity, produce design artifacts, route by tier | Done (prose) | `skills/design/` |
| FR-9 | Decompose a design into a typed runbook | Done (prose) | `skills/runbook/` |
| FR-10 | Execute a prepared runbook by dispatching standing agents at step files | Done (prose) | `skills/orchestrate/` |
| FR-11 | Wrap Tier 1/2 work in a lifecycle: pre-work → execute → corrector → triage → deliverable-review | Done (prose) | `skills/inline/` |
| FR-12 | Review every pipeline transformation at a typed gate | Done (prose) | `skills/review-plan/`, `agents/*corrector*.md` |
| FR-13 | Review production artifacts against ISO 25010 / IEEE 1012 axes | Done (prose) | `skills/deliverable-review/` |
| FR-14 | Select and read relevant memory entries at pipeline recall checkpoints | Done (prose) | `skills/recall/` |
| FR-15 | Ground methodology claims in external research before asserting them | Done (prose) | `skills/ground/` |
| FR-16 | Validate an artifact item-by-item with forced verdicts | Done (prose) | `skills/proof/` |
| FR-17 | Write an icontract contract for a function and repair it against CrossHair | Done (prose) | `skills/formalize/` |
| FR-18 | Provide the version-matched CLI to the plugin at session start | Done | `bin/bootstrap-venv.sh`, `hooks/hooks.json` · `tests/bootstrap-venv.bats` via `test_bootstrap_hook.py` |
| FR-19 | Generate step artifacts and an orchestrator manifest from a runbook | Partial | `bin/prepare-runbook.py` · **no test coverage** (L-1) |
| FR-20 | Check runbook structure deterministically | Done | `bin/validate-runbook.py` · `test_validate_runbook_reporting.py` |

## 4. Non-functional requirements

| # | Requirement | Status | Where · pinned by |
|---|---|---|---|
| NFR-1 | No source module exceeds 400 lines | Done | `scripts/check_line_limits.sh` (`MAX_LINES=400`), run by `just precommit` |
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
`.claude-plugin/plugin.json`, `skills/`, `agents/`, `bin/`, `fragments/`,
`hooks/` and `docs/`. `plugin/` is the plugin root, so a subdir-sourced install
copies exactly `plugin/` and never the sibling `src/` tree.

The plugin does not ship the CLI's code. It obtains the CLI at runtime through a
`SessionStart` hook that builds a venv with uv (§5.4). The two are locked to one
version by `plugin/bin/check-version-consistency.py`, which requires
`plugin.json` version == `pyproject.toml` version — currently `0.0.3`.

`memory/` is a separate submodule, gated by gitlore. It is unaffected by the
plugin de-submodule and stays a submodule.

### 5.2 CLI structure

`src/edify/` is flat — no subpackages. Modules split by functional
responsibility under a 400-line hard limit (NFR-1): `discovery` (session and
agent-file enumeration), `parsing` (content extraction and filtering),
`extraction` (recursive feedback collection), `paths` (project-path encoding),
`models` (Pydantic types), `markdown*` (the postprocessor, split across
`markdown`, `markdown_parsing`, `markdown_block_fixes`, `markdown_inline_fixes`,
`markdown_list_fixes`), `tokens` + `token_cache` + `user_config`, `check` +
`check_cli`, `exceptions`, and `cli` as the Click entry point
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

The plugin is a skills bundle plus standing agents plus two backing scripts.

Pipeline skills: `requirements` → `design` → `runbook` → `orchestrate` (Tier 3)
or `inline` (Tier 1/2), with `review-plan` and `review` as quality gates.
Standalone skills: `proof`, `ground`, `deliverable-review`, `formalize`,
`recall`.

Standing agents in `plugin/agents/`: the correctors (`corrector`,
`design-corrector`, `outline-corrector`, `runbook-corrector`,
`runbook-outline-corrector`, `runbook-simplifier`), the executors (`artisan`,
`test-driver`, `refactor`), and the investigators (`scout`, `tdd-auditor`,
`hooks-tester`, `brainstorm-name`).

Scripts: `plugin/bin/prepare-runbook.py` (runbook → step artifacts) and
`validate-runbook.py` (deterministic structural checks).

**Delegation is by reference.** The orchestrator dispatches a standing agent
with the path to a step file; the step file names the design, outline and recall
artifacts it needs. The orchestrator's prompt carries paths, never content
(D-24).

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

### 6.1 CLI and package

**D-1 — Two output conventions, split by consumer.** User-facing commands
follow Unix convention: errors to stderr via `print(..., file=sys.stderr)`
before `sys.exit(1)`, with text and JSON format options. Commands whose sole
caller is an LLM agent emit everything to stdout as structured markdown and
carry success/failure only in the exit code. stderr is invisible to a calling
agent's structured parsing, and exit code is the only reliable channel.
Structured markdown is the format LLMs produce and consume without quoting or
escaping problems: `**Header:** content` for key-value items, bulleted lists for
multi-item output, a `STOP:` directive for data-loss risk.

**D-2 — CLI output never prescribes destructive commands.** LLM agents treat CLI
output as instructions and execute what it suggests. Report the problem; let the
caller decide. A CLI should refuse destructive operations, not recommend them.
*Grounding:* a worktree removal command suggested `git branch -D` for an
unmerged branch; the agent followed it and permanently deleted the only copy of
unmerged changes.

**D-3 — Error messages state facts, not hypotheses.** No suggested causes ("may
have been committed already") and no recovery advice ("remove and retry") —
agents treat suggestions as instructions and rationalize past real problems. For
unrecoverable errors include `STOP:`; for recoverable ones the CLI handles
recovery itself and surfaces a warning. *Grounding:* an error without `STOP:` led
an agent to drop the file from its list and confabulate "already committed".

**D-4 — Expected states are branches, not exceptions.** EAFP is idiomatic for IO
where failure is uncommon; existence checks and availability queries are normal
control flow and get a boolean. `_git_ok(*args) -> bool` returning
`returncode == 0` replaced both a raw-subprocess LBYL idiom and an EAFP
`try/except CalledProcessError`. Broad exception types for expected conditions
mask real bugs under the same handler, so domain conditions get custom classes
(`SessionNotFoundError`) — which also satisfies the lint rule about hardcoded
exception messages without the `msg` variable dodge.
*Sources:* Real Python EAFP/LBYL; charlax/antipatterns.

**D-5 — One responsibility per error-handling layer.** The failure site collects
context and raises a typed exception; the top level displays and exits. When
both print, output duplicates or conflicts. `raise from` preserves the causal
chain without duplicating display. Error termination is a single call — `_fail(msg,
code=1) -> Never` — because separated display and exit statements drift apart.
Click's `ClickException` was considered and rejected: its hardcoded exit codes
(UsageError→2, Abort→1) do not map to this project's exit semantics.

**D-6 — A call site that explodes under Black has an API problem.** When a call
consistently takes 5+ lines after formatting, it has too many parameters for
inline use. Extract a helper whose defaults encode the common kwargs as policy.
*Reopen-if:* the formatter changes its line-joining algorithm.

**D-7 — Pydantic for all data structures, StrEnum for closed vocabularies.**
Runtime type validation, ISO 8601 timestamp handling and
`model_dump(mode="json")` serialization, rather than static analysis alone.

**D-8 — Malformed session data degrades, it does not abort.** Skip malformed
entries, log a warning, continue. Empty files skip; malformed JSON logs and
skips; a missing `sessionId` is treated as non-match; a non-existent history
directory raises `FileNotFoundError`. Partial data beats total failure, and the
warnings tell the user where to look. Optional fields use `.get(field, default)`.

**D-9 — Publication is postponed indefinitely (2026-07-17, user decision).** The
PyPI publish and the marketplace `git-subdir` entry are parked. The marketplace
manifest has no `edify` entry, so edify is uninstallable meanwhile. *Reopen-if:*
the user asks to publish; note that publish ordering is hard — `edify-cli` must
reach the index *before* the plugin version that pins it, so a plugin version can
never lead its package.

**D-10 — The plugin is a subdirectory, not a submodule.** A parent repo cannot
`git add` inside a submodule, so `git add plugin/.claude-plugin/plugin.json`
failed and `just release` could not complete a real release. Flattening removes
the boundary and the permanent gitlink-drift overhead. Merging the plugin all the
way up to the repo root was rejected: it would force the plugin to carry the
inert `src/` tree as its own content, whereas keeping `plugin/` as the plugin
root means the plugin's content is exactly `plugin/`. *Executed 2026-07-16*
(`c3c4477f`); the old `ddaanet/edify-plugin` GitHub repo was archived.

**D-11 — The venv lives in `CLAUDE_PLUGIN_DATA`, version-scoped by path.** Build
at `${CLAUDE_PLUGIN_DATA}/venv-<version>/`; a version change changes the path, so
an absent directory *is* the rebuild signal and the hook prunes non-matching
siblings. `${CLAUDE_PLUGIN_ROOT}/.venv` is more elegant — ROOT is already
version-scoped and auto-GC'd — but ROOT writability at hook time is unverifiable
from the docs, which say "treat as ephemeral" prescriptively without documenting
a read-only mount. The venv is expensive (CrossHair pulls z3); if the persistence
assumption were wrong the failure would be silent and cost a full reinstall every
session. Two lines of sibling pruning beat that risk. *Reopen-if:* one throwaway
test confirms a write into ROOT survives to the next tool call.

**D-12 — Skills reach the binary by content substitution, never a hardcoded
path.** Skill and agent markdown support `${CLAUDE_PLUGIN_ROOT}` /
`${CLAUDE_PLUGIN_DATA}` substitution in their *content*; those variables are
exported as environment variables only to hook, MCP and LSP subprocesses, not to
Bash-tool subprocesses. If `${CLAUDE_PLUGIN_DATA}` proved not to substitute in
skill content, the fix is a different substitutable mechanism, not a literal
`~/.claude/plugins/data/...` path: a rarely-exercised fallback path format drifts
and rots silently, failing exactly when the primary mechanism is already
unavailable. *Open gate:* one throwaway skill echoing the placeholder confirms
`DATA` (not just `ROOT`) substitutes.

**D-13 — Dogfooding never requires a registry publish.** The bootstrap installs
from a package index, not from PyPI specifically. Build the wheel locally, point
uv at it (`UV_FIND_LINKS`, `UV_INDEX`), prove the bootstrap green offline, then
publish and drop the override. The publish-ordering constraint binds releases,
not development.

### 6.2 Markdown and token tooling

**D-14 — remark-cli is the formatter.** Chosen 2026-01-07 over Prettier and
markdownlint-cli2: idempotent by design with fixed configuration, 100% CommonMark
compliance via micromark, correct nested code blocks, exact YAML frontmatter
preservation. Prettier is non-idempotent (documented bugs on empty sub-bullets,
mid-word underscores, extra-indent lists), strips frontmatter comments and
reduces backticks inconsistently. markdownlint-cli2 is a linter, not a formatter,
and offers no idempotency guarantee. Both Prettier and remark passed the test
corpus over three runs; Prettier's documented edge cases decided it.

**D-15 — The preprocessor runs before the formatter and fails loudly.** Claude
emits markdown-like output that is not always valid markdown: emoji-prefixed
lines that should be lists, improperly nested fences, metadata labels needing
indentation. `markdown.py` fixes structure, then remark applies style. When inner
fences are detected in non-markdown blocks the preprocessor errors out rather
than silently skipping (which hides the problem until remark fails) or auto-fixing
(which risks corrupting code content). Fix order is line-based first, then
spacing, then block-based last, because line fixes interfere with each other
otherwise and the code-block pass needs complete structure. Prefix detection is
generic — any consistent non-markup prefix — rather than a whitelist that needs
updating for each new pattern. Nested lists indent 2 spaces, matching the remark
default.

**D-16 — Model aliases resolve at runtime with a 24-hour cache.** Anything
starting with `claude-` passes through unchanged. A short alias (`sonnet`,
`haiku`, `opus`) is resolved by querying `client.models.list()`, filtering by
substring and selecting the latest `created_at`, cached in the platform user
cache directory via `platformdirs`. An unresolvable alias passes through so the
API produces the error. Every output names the resolved model ID, because aliases
auto-update and reproducibility depends on knowing which snapshot ran. Empty
files return 0 without an API call.

### 6.3 Testing

**D-17 — Patch where the object is used, not where it is defined.** Python
imports create references in the importing module's namespace, so
`monkeypatch.setattr("pkg.b.foo", mock)` works and `"pkg.a.foo"` does not.

**D-18 — RED assertions verify behavior, not structure.** `exit_code == 0`, key
existence and attribute presence are all satisfied by a stub. RED tests mock IO
and external calls and assert on output content, using `tmp_path` fixtures for
real filesystem state. TDD's "write minimal code to pass" only works if the test
requires real behavior. Corollary: when a RED phase passes unexpectedly, check
whether the assertions could distinguish correct output from empty or default
output — `assert isinstance(relevant, list)` passes on an empty list.

**D-19 — E2E with real git repos; mock only for error injection.** Git against
`tmp_path` runs in milliseconds, while subprocess mocks couple to command
strings rather than outcomes, and the interesting bugs are state transitions
mocks cannot produce. A dual suite (e2e for behavior plus mocked subprocess for
speed) buys nothing. Mock subprocess only to inject errors that are hard to
stage — lock files, permission failures.

**D-20 — Click CLIs are tested through `CliRunner`.** In-process invocation
captures output and exit code and supports an isolated filesystem. Testing via
subprocess or by calling `main()` and catching `SystemExit` is slower and
conflates process concerns with behavior.

**D-21 — Test setup fails self-diagnosingly.** `subprocess.run(..., check=True,
capture_output=True)` swallows stderr, so a `CalledProcessError` shows only a
command and an exit code, and opaque failures invite confabulation. Use
`check=False` with an explicit assertion carrying stderr, or a helper that
surfaces it.

**D-22 — GREEN verification includes lint.** The verification command is `just
check && just test`, not `just test` alone: an agent that runs only tests commits
green code with lint errors, forcing a separate fix commit.

**D-23 — A test that fails only in the suite has shared mutable state.** That is
a bug, not flakiness. Confirm with `pytest --lf`, bisect with `pytest -x`
subsets, fix the fixture cleanup or global mutation. "Passes in isolation" is a
diagnostic signal, not a resolution — merging a known ordering-dependent failure
makes every later failure dismissible.

**Presentation is not TDD'd.** Help text wording and error phrasing are brittle
as test targets and self-evident on reading; they get handled in batch at review
checkpoints instead of RED/GREEN cycles.

**Conformance work bakes exact strings into assertions.** When implementation
follows an external reference — shell prototype, API spec, exact output format —
the test assertions carry the exact expected output from that reference, and RED
prose descriptions carry the exact strings too. This is not full test code; it is
precise prose. Abstracting the string introduces translation loss and makes
"visual parity validated" claims undetectable when false.

### 6.4 Pipeline contracts

**D-24 — Execution delegates by reference to standing agents.** The orchestrator
dispatches `artisan`, `test-driver` or `corrector` with the path to a step file;
the step file names the design, outline and recall artifacts the executor needs.

*Supersedes* bespoke per-plan agent definitions (`<plan>-task`,
`<plan>-corrector`, `<plan>-tester`, `<plan>-implementer`) generated into
`.claude/agents/`. That scheme fought the platform: generated agents are not
discoverable as `subagent_type` values until session restart, which forced a
restart boundary into the middle of the pipeline and made agent-type substitution
a live failure mode.

Context reaches the executor through artifacts on disk rather than generated
agent definitions, which keeps deterministic logic out of the agent layer and
costs no flexibility — the runbook system already decides what each step needs. A
dispatch prompt is one path either way, so the orchestrator token saving that
motivated per-plan caching survives.

*Implemented 2026-08-13.* `prepare-runbook.py` writes
`plans/<name>/common-context.md` and, when the outline lives in the runbook
rather than a file, `plans/<name>/outline.md`. Each step file opens with a
`## Context` block naming whichever of design, outline and shared context exist,
and closes with an `## Execution Contract` carrying the scope and clean-tree
requirements the generated agents used to append. The orchestrator plan's
`## Phase-Agent Mapping` table names standing agents and `/orchestrate` reads
`subagent_type` from it.

*Consequences:* the tester/implementer ping-pong survives as two named instances
of `edify:test-driver`; per-cycle reviews are `edify:corrector` dispatches scoped
by prompt. The forced session restart between planning and execution is no longer
a discoverability requirement — it is kept for model tier and context budget
(D-25). The inert `max_turns` manifest column is gone; turn and duration bounds
remain platform gaps, and a column that reads as a guard while enforcing nothing
is worse than none.

**D-25 — Planning and execution run in different sessions.** They run at
different model tiers, and orchestration is long-running, so the boundary keeps
the orchestrator off a context already full of planning transcript. Handoff is
not delegatable — it needs the current agent's session context. Commit is
mechanical and can be delegated. *Reopen-if:* context budgets grow enough that
the tier argument stops binding; auto-chaining `/runbook` into `/orchestrate` was
deliberately not taken during the 2026-08-13 rewire.

**D-26 — Every transformation has a typed review gate.**

| # | Transformation | Input | Output | Gate |
|---|---|---|---|---|
| T1 | Requirements → Design | `requirements.md` or inline | `design.md`, recall artifact | `design-corrector` (opus) |
| T2 | Design → Outline | `design.md`, recall artifact | `runbook-outline.md` | `runbook-outline-corrector` (opus) |
| T2.5 | Outline → Simplified outline | `runbook-outline.md` | consolidated outline | `runbook-simplifier` (opus) |
| T3 | Outline → Phase files | `runbook-outline.md` | `runbook-phase-N.md` | `runbook-corrector` (type-aware) |
| T4 | Phase files → Runbook | `runbook-phase-*.md` | `runbook.md` | `runbook-corrector` (holistic) |
| T4.5 | Runbook → Validated runbook | phase files or runbook | validation reports | `validate-runbook.py` |
| T5 | Runbook → Step artifacts | `runbook.md` | `steps/step-*.md` | `prepare-runbook.py` |
| T6 | Steps → Implementation | `step-*.md` | code, artifacts | `corrector` at checkpoints |
| T6.5 | Design/Outline → Implementation (inline) | `design.md` or outline, classification | code, review report | `corrector` + `triage-feedback.sh` |

**D-27 — Reviewers fix everything and escalate the rest.** Every gate follows the
same protocol: fix all issues directly (critical, major, minor), label genuinely
unfixable ones `UNFIXABLE` with rationale, and let the caller grep for that
token. There are no recommendation dead-ends — fix or escalate, nothing between.
Document fixes are low-risk, which is what makes fix-all safe at planning gates.

Reviewers over-escalate by default: they label pattern-matching tasks as design
decisions requiring user input, treating uncertainty as an escalation trigger
rather than scanning existing patterns for guidance. `DEFERRED` (expected,
named in the scope statement) is distinct from `UNFIXABLE` (blocking).

**D-28 — The orchestrator delegates all reviews; execution agents never review
their own work.** This is policy, not capability. It was previously justified by
"sub-agents lack Task and Skill tools"; both halves were measured false on
2026-08-10 — sub-agents have `Skill`, and they spawn sub-agents via `Agent` (no
`Task` tool exists at any level). The rule holds *because* an execution agent is
now technically able to review its own work and must not. Implementer bias is
the reason.

**D-29 — Every review delegation carries execution context.** Required: scope IN
(what was produced), scope OUT (what is not yet done, which the reviewer must not
flag), the explicit changed-file list, and the requirements the output should
satisfy. Optional for phased work: prior state, design reference. A reviewer
validates against the current filesystem, not against execution-time state, so
omitting this produces fixes based on stale assumptions.

Where a design decision states a cross-cutting invariant — "all output to
stdout", "no data loss across all code paths" — the changed-files list is the
wrong scope. Add a verification scope naming every file participating in the
invariant, identified by grepping for the invariant's pattern.

**D-30 — Phases declare a type: `tdd`, `general` (default), or `inline`.** Type
determines expansion format (RED/GREEN cycles; task steps with script evaluation;
pass-through), review criteria (TDD discipline; step quality; vacuity and density
only), and delegation model (per-step agent dispatch; orchestrator-direct). LLM
failure-mode checks apply regardless of type. Type does not affect tier
assessment, outline generation, consolidation gates, assembly or checkpoints.

A phase qualifies as `inline` when its outcome is fully determined by instruction
plus target file state: no runtime feedback loop, all decisions pre-resolved in
design. `prepare-runbook.py` skips step-file generation for those.

**D-31 — LLM failure-mode checks run at both outline and expanded-phase level.**
Expansion re-introduces vacuous cycles and density problems that outline review
already removed. *Grounding:* an outline was fixed, then its expanded phases
contained three vacuous cycles and a missing requirement.

**D-32 — Outline review runs at opus.** A sonnet reviewer's fix-all policy
generates plausible but ungrounded corrections: confabulated operation sequences,
removed design-specified features, fabricated file sizes. Established by a 2×2
controlled experiment over generator × reviewer model with structurally
equivalent delegation prompts — sonnet review confabulated on both sonnet- and
opus-generated outlines, opus review stayed grounded on both. Root cause: sonnet
identifies non-problems as problems, then confabulates fixes, treating a
structural document that references the design as if it were standalone. Paired
fix: expansion guidance references design sections rather than reproducing
implementation detail. This runs once per plan and its errors propagate to every
execution step.

**D-33 — Consolidate identical patterns at the outline, not after expansion.**
Four cycles that each add one artifact check to the same function differ only in
fixture data, and that is visible from outline titles — expanded RED/GREEN detail
is not needed to detect it. A parametrized cycle with a table of inputs replaces
N separate rounds. Consolidating at the earliest detectable point saves the
expansion cost; post-hoc optimization of ~12 items cost five parallel agents plus
a holistic re-review.

### 6.5 Execution routing

**D-34 — Three execution tiers, grounded in environment constraints.** Tier 1
(inline): the work fits the current session's context and the agent that designed
it can execute it. Tier 2 (delegated): work exceeds inline capacity but prompt
generation is straightforward, so the orchestrator writes prompts ad hoc and
dispatches. Tier 3 (orchestrated): prompt generation itself is expensive — many
steps, layered context, cross-step dependencies — so pre-generating a runbook
amortizes it.

The Tier 1/2 boundary is **capacity**; the Tier 2/3 boundary is **orchestration
complexity**. External methodology frameworks (Cynefin, XP, Lean Startup)
validate the principle — match process weight to uncertainty — but the specific
structure derives from how this system executes, not from them. Operational
structure grounded in execution-environment constraints is grounded; the absence
of an external framework prescribing three tiers is not evidence against it.

**D-35 — Complexity, work type and tier are three independent decisions.**
Complexity (Stacey axes) determines design ceremony. Work type
(production/exploration/investigation) determines quality obligations. Tier
determines execution mechanics. They are decided at different pipeline stages:
complexity and work type at `/design` Phase 0, tier at Phase B or `/runbook`
entry.

**D-36 — Artifact destination determines ceremony, not behavioral-code presence
alone.** Prototype scripts, one-off analysis and spikes do not need runbooks, TDD
or test files even though they contain behavioral code. Design resolves the
complexity; after design a prototype is direct implementation.

**D-37 — Simple classification still routes through `/inline`.** "Direct
execution" — recall, explore, edit, done — bypasses the integration-test gate,
review dispatch, triage feedback and the deliverable-review chain. Classification
determines *design* ceremony, not *execution* ceremony.

**D-38 — Composite tasks are decomposed before classification.** Batch-classifying
an input holding N discrete work items averages heterogeneous items, so a
behavioral-code change gets masked by non-behavioral siblings. Produce a per-item
behavioral-code check; any item adding conditional branches, functions or logic
paths raises that item to Moderate minimum. Distinct from companion tasks, which
the user bundles explicitly.

**D-39 — Self-modifying work leaves the runbook pipeline.** When the planned work
edits pipeline skills or pipeline contracts, a runbook step that edits the runbook
skill creates stale-instruction risk for later steps. Structure it as an inline
task sequence instead, each task executing with fresh instruction loads. TDD
discipline is preserved — the executing session dispatches `test-driver` per
cycle. Also applies when there is no parallelization benefit or when coordination
cost exceeds error-recovery value.

**D-40 — Escalation has three tiers.** *Item-level:* a single `UNFIXABLE` item
blocks execution on a missing design decision, ambiguous requirement or external
dependency — the orchestrator stops and surfaces it with an investigation summary
and subcategory (U-REQ, U-ARCH, U-DESIGN). *Local:* the implementation needs
restructuring within the same design — delegate to `refactor` in the current
phase; design and runbook stay valid. *Global:* execution reveals a design flaw —
invalidated assumptions, accumulating same-type UNFIXABLEs, dependency cycles, an
inadequate test plan — so stop and return to planning.

### 6.6 Model selection

**D-41 — Assign model by the correctness property being verified, not by
authorship or task label.** State-machine routing, architectural wiring and
design-invariant compliance need opus; behavioral changes within a function need
sonnet; mechanical substitutions need sonnet at most, because test pass/fail is
sufficient signal. Matching the reviewer to the author's model ("haiku wrote it →
sonnet reviews it") and blanket-opus inheritance from the orchestrator are both
wrong. Haiku writes state-machine code that looks plausible and has subtle wiring
errors; opus reviewing grep-and-replace is waste.

**D-42 — Prose artifacts consumed by LLMs are opus work.** Skills, fragments,
agent definitions and design documents are instructions whose wording determines
downstream agent behavior. Assigning by "edit complexity" rather than artifact
type is the anti-pattern. The rule targets cases where design decisions happen
*during* editing — when an outline pre-resolves every decision and specifies exact
insertion points, execution is mechanical and delegation ceremony exceeds the edit
cost.

**D-43 — Discovery and audit over skills, agents and fragments need sonnet
minimum.** Haiku grades generously, misses dominant failure patterns and produces
false positives that require opus validation — double work. *Grounding:* haiku
graded 0 skills at C where sonnet found 3, missed the dominant description
anti-pattern (18/30), and produced 15 gate findings against sonnet's 12.

**D-44 — Model tier is a configurable knob, not an architectural constraint.**
Stabilize at sonnet, optimize downward once patterns are proven and failure modes
understood. Defaulting to haiku for cost before validation is the anti-pattern.

**D-45 — Tier-aware error classification.** Sonnet and opus execution agents
self-classify errors and report the classification; haiku agents report raw errors
for the orchestrator to classify. Moving all classification to the orchestrator
because haiku cannot do it ignores the capable agents and loses fidelity, since
the execution agent holds the full error context.

**Model tier naming.** Premium (opus) / standard (sonnet) / efficient (haiku),
not T1/T2/T3 — "T3" reads ambiguously as either the lowest tier or the third from
the top.

**No model-tier introspection exists.** An agent consistently misidentifies
itself as sonnet while running as opus. Do not guess: ask, stay silent, or rely
on an external signal.

### 6.7 Quality gates

**D-46 — Quality gates are layered; no single gate is trusted alone.** Four
layers, outer to inner: execution flow (the gate is anchored by a tool call so it
cannot be optimized away as prose), automated checks (`just precommit` — line
limits, lint, tests), semantic review (a corrector catches logic, integration and
design-deviation issues), and conformance (comparison against an external
reference). Each prevents a distinct failure mode. *Grounding:* a parity failure
cascade where unit tests passed 385/385 while 8 visual parity issues survived, the
review missed systemic conformance gaps because its mandate excluded reference
comparison, and the 400-line constraint was bypassed — each layer failed
independently.

Checklist when designing a new gate: is there an outer execution-flow defense, a
middle automated check, an inner semantic review, and — for external-reference
work — a conformance comparison? Do the layers have *different* failure modes? Can
any single layer's failure cause total failure?

**D-47 — Gate at the chokepoint, not with ambient rules.** Ambient rules in
always-loaded context telling agents to review artifacts are unenforceable: agents
rationalize skipping under momentum, and sub-agents never see them. A scripted
check at the commit chokepoint blocks mechanically with no judgment at the gate.
*Grounding:* ~100 lines of always-loaded context eliminated for no behavioral loss.

**D-48 — Anchor a gate with a tool call that proves work happened.** "Read X (skip
if already in context)" is not a gate — the escape hatch *is* the failure mode,
and the agent rationalizes the skip without verifying. The canonical anchor is the
recall pass: a Read of `memory/MEMORY.md` followed by Reads of the files it names.
The index Read is unskippable and the per-file Reads require knowing which entries
matter, so the pair proves selection happened. One anchor suffices — passphrase
and proof-of-Read mechanisms are redundant when the anchor proves both. The
negative path must cost the same: a null recall artifact still gets Read, so the
gate is provably reached whether or not anything was found.

Verify that the anchor tool's preconditions match the gate's runtime state. A
recall-diff keyed on `git log --since=mtime` needs intervening commits; at a
post-explore gate the exploration reports are uncommitted and the check finds
nothing.

**D-49 — Split validation into mechanical and semantic.** A script handles
deterministic checks — blocking, zero false positives. An agent enriches an
existing review for semantic checks — advisory. Bundling "does this file path map
to the right model?" with "is this task synthesis?" in one agent pass loses both
properties.

**D-50 — Fix the environment, not the prose.** Strengthening language ("no
exceptions", "MUST", scenario-specific warnings) in a rule the agent already saw
and rationalized past does not work: if the rule was clear and the agent overrode
it, clarity was not the problem. Structural fixes — resolve conflicting
directives, anchor gates with tool calls, add hooks or scripts, ensure sufficient
context at the decision point.

**D-51 — Either fail the build or do not check.** Validators that print warnings
without failing normalize deviance and create a false sense of compliance.
*Trade-off:* hard limits force immediate resolution and may need tuning.

**D-52 — Every skill step opens with a concrete tool call.** Steps carrying only
prose judgment get skipped: execution-mode cognition optimizes for "next tool
call", so a step without one registers as commentary. The D+B fix eliminates
standalone prose gates by merging each into its adjacent action step, anchors each
gate's first instruction with a Read or Bash call providing the data to evaluate,
and makes control flow explicit with if/then branch targets.

**D-53 — Negative constraints sit beside the positive guidance they qualify.** A
"don't write X" rule placed in a later cleanup phase fires after the violation is
already written. Any rule about what *not* to produce is co-located with the
instructions for what to produce.

**D-54 — A skill needs four discovery layers, not good internal documentation.**
Always-loaded context, a path-triggered `.claude/rules/` entry, in-workflow
reminders in related skills, and a directive description. Agents see only skill
listing descriptions and always-loaded context; internal skill docs are invisible
until invoked. *Grounding:* a skill with 248 lines of documentation and zero
external visibility — agents asked the user instead of consulting it.

### 6.8 Deliverable review

**D-55 — A deliverable is a production artifact that persists after execution and
affects system behavior.** Identify by comparing the plan outline's in-scope
section against the repository diff: every created or modified file that is not a
planning or execution artifact is a deliverable. The outline specifies what should
exist; the diff shows what was produced; the gap between them is findings —
missing deliverables (incompleteness) or unspecified ones (excess).

**D-56 — Each deliverable is classified into exactly one type, and the type
selects the axes.** Types: code, test, agentic prose, human documentation,
configuration.

*Universal axes:* conformance (satisfies the design spec's conditions — IEEE
1012), functional correctness and functional completeness (ISO 25010), vacuity
(does real work rather than ceremony), excess (anything unspecified).

*Code:* robustness, modularity, testability, idempotency, error signaling.
*Test:* specificity (fails for the right reason and only that), coverage,
independence (verifies behavior, not implementation).
*Agentic prose:* actionability (every step maps to a tool call or state change),
constraint precision (measurable criteria, not "relevant"/"appropriate"),
determinism, scope boundaries.
*Human documentation:* accuracy, consistency, completeness, usability.

Findings are Critical (incorrect behavior, data loss, security), Major (missing
functionality, broken references, vacuous artifact) or Minor (style, clarity,
naming).

*Sources:* [ISO/IEC 25010:2023](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010),
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
disappears from every active surface. Severity exists so report readers can assess
risk, not as skip permission for executors. "Noted in report" is not a resolution,
because reports are not read proactively.

**D-59 — Reviews report severity counts and make no merge-readiness judgment.**
A review that classifies findings as Major and then adds "doesn't block merge,
follow-up work" is sycophancy in artifact form — the reviewer softening its own
classification to avoid blocking the pipeline. The user reads the counts and
decides.

**D-60 — Route findings unconditionally to `/design`.** Conditional dispatch on
fix size or an "architectural?" judgment reintroduces judgment at a stage that
should be mechanical. `/design` triage already handles proportionality.

### 6.9 Prompt and instruction structure

**D-61 — Order by position bias.** LLMs show strong primacy bias, secondary
recency bias, and weakest attention in the middle. Critical rules go at the start,
guidance at the end, important-but-not-critical in the middle where the bulk of
content sits. *Sources:* [Serial Position Effects of
LLMs](https://arxiv.org/html/2406.15981v1), [Exploiting Primacy
Effect](https://arxiv.org/html/2507.13949), [Positional Bias in Financial
Decision-Making](https://arxiv.org/html/2508.18427). The 20/60/20 split sometimes
quoted alongside this comes from organizational change management and is *not*
validated for LLMs — treat it as a starting point (L-3).

**D-62 — Format by content type.** Discrete rules as bullets (higher adherence);
connected concepts as prose (cohesion); critical rules with visually salient
markers; examples in code blocks. *Source:* [Effect of Selection Format on LLM
Performance](https://arxiv.org/html/2503.06926).

**D-63 — Instruction density varies by model class.** Opus takes concise prose and
infers; sonnet takes clear bullets with context; haiku needs explicit steps,
salient markers and DO-NOT examples. Expansion ranges: 3-5 rules per module for
opus, 8-12 for sonnet, 12-18 for haiku.

**D-64 — Rule adherence degrades past roughly 200 rules.** The system prompt
consumes about 50, leaving ~150. Counting is marker-based so the generator defines
what a rule is, rather than a parser heuristic guessing (L-3 — the 200 figure is
an empirical observation, not a calibrated threshold).

**D-65 — Contradictions resolve by position, so hook output must reinforce
standing rules.** A hook message sits in the recency zone and a standing rule in
primacy; when they disagree, the agent follows the hook. A hook that blocks a
dangerous action must give guidance aligned with the rule it enforces — "retry
your git command, do not delete lock files" rather than a bare "retry", which
sends the agent to retry the wrong command.

**D-66 — Contents are only present if explicitly loaded.** There is no implicit
file loading. Each Read appends a new content block; "caching" is prompt-prefix
matching at the API level, not application-level deduplication.

### 6.10 Project configuration

**D-67 — `.claude/rules/` with `paths` frontmatter injects domain context.**
Documentation-only enforcement through tables in always-loaded context relies on
model attention and is unreliable; hooks cannot detect skill-loading state because
they see tool inputs, not conversation context. Rules files are passive reminders,
not enforcement — models can ignore them — but they beat always-loaded bloat.
Rules fire in the main session only; sub-agents never receive them, so domain
context must be carried explicitly into a delegation prompt.

**D-68 — `CLAUDE.md` is the project-root marker for scripts.** Not `agents/`:
subdirectories carry their own `agents/` folders (`plugin/agents/`), so a script
walking upward stops at the wrong level.

**D-69 — 400 lines is a hard per-module limit, enforced by precommit.** Review
effectiveness drops faster than linearly past ~400 LOC — reviews under 300 lines
get architectural feedback, past 600 only style comments
([Baldawa 2024](https://rishi.baldawa.com/posts/pr-throughput/cognitive-load-cliff/));
the AI-assisted sweet spot is 150-500 lines
([Faherty 2025](https://medium.com/@eamonn.faherty_58176/right-sizing-your-python-files-the-150-500-line-sweet-spot-for-ai-code-editors-340d550dcea4));
PyLint's default of 1000 is too permissive for an agent's context. The limit
provides backpressure against slop.

When a file hits the limit, look for code-quality improvements first — redundant
calls, dead code, extraction candidates. Compressing user-facing output strings or
splitting to a new file to satisfy the counter degrades output clarity or module
cohesion without addressing the cause. Splitting a module by functional
responsibility is mechanical, so `refactor` (sonnet) may do it without opus
escalation. Runbook planning should project file growth and insert split points
rather than react per cycle.

**D-70 — Fix the design problem a lint rule points at.** "No hardcoded exception
messages" answered by `msg = "..."; raise ValueError(msg)` preserves the real
problem — using `ValueError` for a domain error — while removing the signal.
"Function too long" is answered by extracting helpers, not compressing strings.

**D-71 — Agents compose behavior through `skills:` frontmatter.** Wrapping shared
guidance as a skill and referencing it from an agent definition injects the
content as prompt with no build step, so it stays current automatically.

**D-72 — What a sub-agent actually gets (measured 2026-08-10).** Sub-agents
receive `CLAUDE.md` and `memory/MEMORY.md` natively, under the same
`Contents of <path>` label the main session gets. They have the `Skill` tool, are
given the full skill listing, and resolve project-local plugin skills as well as
marketplace ones. They can spawn sub-agents through `Agent` — there is no `Task`
tool at any level.

What they lack is the automatic memory *fetch*: recall does not run below the main
session, so a body arrives only if the agent Reads it. Never instruct an agent to
Read the index — it already has it; instruct it to Read the files the index names.

Hooks do not fire in sub-agents. Nested spawning is asynchronous and its result
does not reach the parent: the tool result is a launch acknowledgement, and the
grandchild's completion surfaces in the main session while the parent goes idle.
Never design a sub-agent to consume a grandchild's return value. `Agent`
parameters are `description`, `prompt`, `subagent_type`, `name`, `model`,
`isolation` — no `max_turns`, no `run_in_background`, no `resume`. Resumption is
`SendMessage` addressed to the agent's `name`, which is why naming at spawn time
matters.

**D-73 — Agent frontmatter uses block scalars for descriptions with examples.**
YAML parsers treat unindented content after `description:` as a new field, and
invalid YAML prevents agent registration. `description: |` makes the examples part
of the value.

**D-74 — Names are chosen for discoverability first.** The word a user thinks of
when they need the capability should be the handle: "I need to ground this" →
`/ground`, not `/found`. Then recall — short common words beat etymologically
precise ones. Thematic alignment is nice and never worth a discoverability cost.
Check CLI built-ins before naming a skill (`/help`, `/plan`, `/review`, `/model`,
`/clear`, `/compact`).

**D-75 — Title-words beat kebab-case for identifiers in prose.** Measured
kebab-case at +31% drift penalty against title-words at +17% when agents get
verbose; hyphens often tokenize separately while spaces do not add overhead.

**D-76 — Script the deterministic, delegate the cognitive.** If a solution is
non-cognitive — deterministic, pattern-based — script it and auto-fix. Reserve
agent invocations for design, review and ambiguous decisions. A script that
validates metadata presence while expecting an agent to generate it has the split
backwards: deterministic standard metadata gets injected during assembly.

**D-77 — Delegate for exploration you have not done, not for context you already
hold.** If the files are already in context, executing directly beats delegating
to an agent that re-reads everything. Assess complexity once — an entry-point
skill that triages and then routes to a planning skill that re-assesses under
different labels is pure duplication.

## 7. Rejected alternatives

**Prettier and markdownlint-cli2 as the markdown formatter** — see D-14.

**Merging the plugin to the repo root** — would force the plugin to carry the
inert `src/` tree as its own content (D-10).

**Keeping `plugin/` as a submodule** — ships a live defect: `git add` inside a
submodule fails, so `just release` cannot complete (D-10).

**A stdlib venv (`python3 -m venv` + pip) for the bootstrap** — chosen 2026-07-16
and reversed 2026-07-17. A stdlib venv inherits the host interpreter, so it
required host `python3` ≥3.14 and failed loudly otherwise — unshippable on hosts
still at 3.13. uv fetches its own interpreter, removing the host floor. The price
is a uv runtime dependency, paid down by informative degradation (NFR-5).

**Requiring a separate global `uv tool install edify-cli`** — works, but couples
the plugin to an out-of-band manual step.

**Running the CLI from the `src/` tree in the same repo** — impossible: a subdir
install does not copy sibling source into the cache.

**`${CLAUDE_PLUGIN_ROOT}/.venv` for the venv** — more elegant semantics, but ROOT
writability at hook time is unverifiable from the docs (D-11).

**A hardcoded `~/.claude/plugins/data/...` fallback path in skills** — a
rarely-exercised path format drifts and rots silently (D-12).

**Click's `ClickException` for CLI failure** — hardcoded exit codes do not map to
this project's semantics (D-5).

**A JSON file as a general key-value store** — the existing models cache is a
special case (bounded, ~50 entries, TTL-refreshed); extending it to unbounded
append-heavy caches cargo-cults the storage choice. sqlite via sqlalchemy is the
answer for persistent caches: stdlib sqlite3 handles concurrent access, mapped
classes match the Pydantic convention.

**Per-plan generated agent definitions** — superseded by delegation by reference
(D-24).

**A combined time-OR-tool-count timeout signal** — OR-logic is the union of two
kill zones, so it *increases* false positives against either threshold alone.
Spinning (high activity, no convergence) needs a turn bound; hanging (no activity,
high wall-clock) needs a duration timeout. They are independent guards. Neither is
implementable today (L-4).

**A `"Bash(rm:*/index.lock)"` permission deny entry** — never fires, because `rm`
runs inside the sandbox without needing explicit permission. A PreToolUse hook
inspecting `tool_input.command` fires unconditionally.

**A PreToolUse advisory (exit 0 + `additionalContext`) as a pre-delegation gate**
— no model turn runs between the hook and tool execution on exit 0, so the spawn
dispatches, runs and completes before the agent reads the advisory. The gate would
be post-delegation. Blocking with `permissionDecision: deny` is the mechanism.

**Inlining a "top N" subset of a reference file to avoid a Read** — the agent
picks from the visible subset unaware that better matches exist, creating a
knowledge ceiling. Keep the full Read or move selection into a tool; partial
inlining is worse than both.

**Pruning the memory index on a size limit** — rejected in favour of append-only
growth. Each entry is a keyword-rich discovery surface, consolidation into domain
summaries kills keyword matching, and soft limits get treated as hard caps and
provoke aggressive pruning. (Superseded in mechanism: gitlore now owns the memory
store, and its index budget is a real loader cutoff rather than a soft limit —
see L-5.)

**Skill-description optimization for this project** — matters only where automatic
triggering operates. Every skill here is invoked explicitly, so descriptions serve
as documentation.

## 8. Limitations

**L-1 — `prepare-runbook.py` has no test coverage.** The suite reaches it only
indirectly through `validate-runbook.py`'s imports. The rewired step-file and
manifest shapes are verified only by manual runs against three runbook shapes.

**L-2 — The tier thresholds are ungrounded operational parameters.** Tier 1 <6
files, Tier 2 6-15, Tier 3 >15 or >10 TDD cycles, and the "every 3-5 cycles"
mid-execution checkpoint frequency, have no empirical calibration. The tier
*structure* is justified (D-34); the numbers inside it are not.
`plans/reports/triage-feedback-log.md` collects per-execution evidence — files
changed, agent count, behavioral code, classification verdict — for eventual
calibration.

**L-3 — Several prompt-structure figures are heuristics, not measurements.** The
20/60/20 distribution comes from organizational change management, and the
~200-rule adherence ceiling is an empirical observation without a calibrated
method behind it.

**L-4 — Turn and duration bounds do not exist.** The `Agent` tool has no
`max_turns` parameter and no duration bound, so the spinning/hanging taxonomy has
no enforcement. See `plugin/fragments/escalation-acceptance.md`.

**L-5 — `memory/MEMORY.md` exceeds Claude Code's loader cutoff.** At ~28.9 KB
against a 24.4 KB limit, tail entries never reach a session. The fix is retiring
and relocating entries, not rewording them.

**L-6 — The pipeline is unvalidated.** The weak-orchestrator pattern was claimed
on a single small execution in 2026-01, and the token-cost and reliability figures
that accompanied that claim were estimates, not measurements. It has not been
exercised end to end since the 2026-08 revival.

**L-7 — `plugin/bin/deliverable-inventory.py` diffs `merge-base HEAD main`.**
Reviewing work already committed on `main` therefore returns an empty inventory.

**L-8 — Direct `.claude/handoff-task.md` writes are hook-blocked.** `/inline`
Phase 4c and `/orchestrate` sections 3.4 and 6 still write it directly; they need
routing through the handoff checkpoint channel.

## 9. Non-goals

**Publishing to PyPI and the marketplace** — parked indefinitely by user decision
(D-9), not blocked.

**Cross-version compatibility** — there is no user base, so nothing is kept for
migration's sake.

**Model-specific instruction variants** — deferred until haiku execution quality
becomes a demonstrated problem.

**Glob expansion inside `edify tokens`** — shell expansion covers it.

**A dprint plugin replacing the markdown preprocessor** — single-pass processing
and cleaner toolchain integration would be better, but the preprocessor works and
the migration is not scheduled.

## 10. Changelog

`docs/changelog.md` — design-significant changes only: decisions reversed,
subsystems built or torn down, requirements added or dropped. Git history is the
full record; the changelog carries what explains why the project is the way it
is.
