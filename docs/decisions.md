# Edify — decision index

Every decision this project has taken, one conclusion line each, grouped by the
node in `docs/references/` that argues it, with each group's rejected
alternatives by name. Read this whole when weighing or adding a decision; open
the node before changing a mechanism a decision governs.

What the system is — requirements, architecture, limitations, non-goals — is in
`docs/design.md`.

## CLI and package

Argued in `docs/references/cli-and-package.md`.

- **D-1** — Two output conventions, split by consumer.
- **D-2** — CLI output never prescribes destructive commands.
- **D-3** — Error messages state facts, not hypotheses.
- **D-4** — Expected states are branches, not exceptions.
- **D-5** — One responsibility per error-handling layer.
- **D-6** — A call site that explodes under Black has an API problem.
- **D-7** — Pydantic for all data structures, StrEnum for closed vocabularies.
- **D-8** — Malformed session data degrades, it does not abort.
- **D-9** — Publication is postponed indefinitely (2026-07-17, user decision)
  (reversed 2026-08-04: `edify-cli` 0.0.3 shipped and the marketplace entry
  exists).
- **D-10** — The plugin is a subdirectory, not a submodule.
- **D-11** — The venv lives in `CLAUDE_PLUGIN_DATA`, version-scoped by path.
- **D-12** — Skills reach the binary by content substitution, never a hardcoded
  path.
- **D-13** — Dogfooding never requires a registry publish.
- **D-14** — remark-cli is the formatter.
- **D-15** — The preprocessor runs before the formatter and fails loudly.
- **D-16** — Model aliases resolve at runtime with a 24-hour cache.
- **D-87** — The release recipe is edify's own, because the shared plugin
  toolkit excludes hybrid repos by design.

*Rejected:* Prettier and markdownlint-cli2 as the markdown formatter; merging
the plugin to the repo root; keeping `plugin/` as a submodule; a stdlib venv
(`python3 -m venv` + pip) for the bootstrap; requiring a separate global
`uv tool install edify-cli`; running the CLI from the `src/` tree in the same
repo; `${CLAUDE_PLUGIN_ROOT}/.venv` for the venv; a hardcoded
`~/.claude/plugins/data/...` fallback path in skills; Click's `ClickException`
for CLI failure; a JSON file as a general key-value store; extending
`claude-plugin-dev` to cover hybrid repos; un-hybridising edify so the toolkit
fits; adopting the toolkit on the grounds that its exclusion predates the merge.

## Testing

Argued in `docs/references/testing.md`.

- **D-17** — Patch where the object is used, not where it is defined.
- **D-18** — RED assertions verify behavior, not structure.
- **D-19** — E2E with real git repos; mock only for error injection.
- **D-20** — Click CLIs are tested through `CliRunner`.
- **D-21** — Test setup fails self-diagnosingly.
- **D-22** — GREEN verification includes lint.
- **D-23** — A test that fails only in the suite has shared mutable state.
- Presentation is not TDD'd.
- Conformance work bakes exact strings into assertions.

## Pipeline contracts

Argued in `docs/references/pipeline-contracts.md`.

- **D-24** — Execution delegates by reference to standing agents.
- **D-25** — Planning and execution run in different sessions.
- **D-26** — Every transformation has a typed review gate.
- **D-27** — Reviewers fix everything and escalate the rest.
- **D-28** — The orchestrator delegates all reviews; execution agents never
  review their own work.
- **D-29** — Every review delegation carries execution context.
- **D-30** — Phases declare a type: `tdd` or `general` (default).
- **D-31** — LLM failure-mode checks at every planning level (superseded
  2026-09-01: one planning level, so the check runs once).
- **D-32** — Runbook review runs at opus.
- **D-33** — Consolidate identical patterns before `/proof`.
- **D-80** — Every `/design` artifact records the base commit its deliverable
  starts from.
- **D-84** — A GREEN dispatch carries one slice's behaviour; a slice already
  implemented is proven by mutation.
- **D-85** — The recall checkpoint resolves skills alongside memory files, and
  Reads the index when the index is not in context.
- **D-86** — A report rides the commit whose work it reports, and names no hash
  (the commit is resolved from `git log --diff-filter=A` over the report path).

*Rejected:* per-plan generated agent definitions; a two-stage runbook expanded
into step files for a weak orchestrator; per-test RED/GREEN dispatch; whole-task
batching without a separate RED dispatch; a deterministic runbook validator.

## Build run state

Argued in `docs/references/build-run-state.md`.

- **D-88** — A `/build` run is resumed when it holds an item report, and report
  history gives its base.
- **D-89** — A phase boundary has landed when the run holds a commit touching
  its corrector report.
- **D-90** — A changed-files list is the committed diff since the base, minus
  the exempt paths and the job's own record, and one script produces it.
- **D-91** — Any change is dirt, except three paths dirty by convention.
- **D-92** — Dirt is unfinished work to examine and finish; nothing reverts by
  default.
- **D-93** — Review-gate groups are four fixed rows, with fixed slugs.
- **D-94** — `/build` commit subjects name the job, and are labels only.

*Rejected:* a baseline file, `tmp/build-baseline-<job>`, for the run's base;
commit subjects as the resume or boundary key; a committed start marker; a
stored phase base, or `HEAD~N`; the changed-files query and the exempt regex
spelled out in prose at each site; filtering or gitignoring the sandbox-mask
names; reverting dirt by default; a `verify-step.sh --revert` mode; a listing
token guarding the revert; a mechanical item scope for dirt; a new review group
per file kind; `edify:design-corrector` as the design-graph reviewer.

## Execution routing

Argued in `docs/references/execution-routing.md`.

- **D-34** — One execution skill, `/build`, whatever the work arrived as.
- **D-81** — Three planning artifacts, two design routes, one execution skill.
- **D-35** — Complexity, work type and route are three independent decisions.
- **D-82** — The route asks whether the work needs the runbook layer, not
  whether it is prose.
- **D-83** — A behavioural change is a tdd item wherever it is written, and
  `/build` fires on `Slices:`.
- **D-36** — Artifact destination determines ceremony, not behavioral-code
  presence alone.
- **D-37** — Simple classification still routes through `/build`.
- **D-38** — Composite tasks are decomposed before classification.
- **D-39** — Self-modifying work leaves the runbook pipeline.
- **D-40** — Escalation has three tiers.

*Rejected:* a combined time-OR-tool-count timeout signal.

## Agent instructions and model choice

Argued in `docs/references/agent-instructions.md`.

- **D-41** — Assign model by the correctness property being verified, not by
  authorship or task label.
- **D-79** — Two dispatches are fixed, and a runbook item carries no model.
- **D-42** — Prose artifacts consumed by LLMs are opus work.
- **D-43** — Discovery and audit over skills, agents and fragments need sonnet
  minimum.
- **D-44** — Model tier is a configurable knob, not an architectural constraint.
- **D-45** — Tier-aware error classification.
- Model tier naming: premium / standard / efficient, not T1/T2/T3.
- No model-tier introspection exists.
- **D-61** — Order by position bias.
- **D-62** — Format by content type.
- **D-63** — Instruction density varies by model class.
- **D-64** — Rule adherence degrades past roughly 200 rules.
- **D-65** — Contradictions resolve by position, so hook output must reinforce
  standing rules.
- **D-66** — Contents are only present if explicitly loaded.
- **D-78** — Skills ask inline in numbered prose, never through
  `AskUserQuestion`.

*Rejected:* inlining a "top N" subset of a reference file to avoid a Read.

## Quality gates

Argued in `docs/references/quality-gates.md`.

- **D-46** — Quality gates are layered; no single gate is trusted alone.
- **D-47** — Gate at the chokepoint, not with ambient rules.
- **D-48** — Anchor a gate with a tool call that proves work happened.
- **D-49** — Split validation into mechanical and semantic.
- **D-50** — Fix the environment, not the prose.
- **D-51** — Either fail the build or do not check.
- **D-52** — Every skill step opens with a concrete tool call.
- **D-53** — Negative constraints sit beside the positive guidance they qualify.
- **D-54** — A skill needs four discovery layers, not good internal
  documentation.

*Rejected:* a `"Bash(rm:*/index.lock)"` permission deny entry; a PreToolUse
advisory (exit 0 + `additionalContext`) as a pre-delegation gate.

## Deliverable review

Argued in `docs/references/deliverable-review.md`.

- **D-55** — A deliverable is a production artifact that persists after
  execution and affects system behavior.
- **D-56** — Each deliverable is classified into exactly one type, and the type
  selects the axes.
- **D-57** — Holistic review catches what per-step review structurally cannot.
- **D-58** — Every finding resolves to a fix or a tracked task.
- **D-59** — Reviews report severity counts and make no merge-readiness
  judgment.
- **D-60** — Route findings unconditionally to `/design`.

## Project configuration

Argued in `docs/references/project-configuration.md`.

- **D-67** — `.claude/rules/` with `paths` frontmatter injects domain context.
- **D-68** — `CLAUDE.md` is the project-root marker for scripts.
- **D-69** — A file's line cap is picked from its path, enforced by precommit.
- **D-70** — Fix the design problem a lint rule points at.
- **D-71** — Agents compose behavior through `skills:` frontmatter.
- **D-72** — What a sub-agent actually gets (measured 2026-08-10).
- **D-73** — Agent frontmatter uses block scalars for descriptions with
  examples.
- **D-74** — Names are chosen for discoverability first.
- **D-75** — Title-words beat kebab-case for identifiers in prose.
- **D-76** — Script the deterministic, delegate the cognitive.
- **D-77** — Delegate for exploration you have not done, not for context you
  already hold.

*Rejected:* pruning the memory index on a size limit; skill-description
optimization for this project.
