# Agent Instructions

Edify is a lean Claude Code skills bundle plus a small CLI toolkit. Direction: Lean-assisted (formal-proof-backed) requirements tracking.

## Communication Rules

### Observable State Reporting

**Do not filter observable state.** `git status --porcelain` non-empty means dirty — report it as dirty. The user decides what's ignorable.

**Anti-pattern:** Rationalizing known-dirty files (`.claude/settings.json`) as "always dirty" and therefore ignorable. The file may be dirty for a different reason than assumed.

### When Output-Style Plugins Conflict With Prose Rules

**Project CLAUDE.md prose rules govern output style.** Do not follow decorative block templates (e.g., `★ Insight`) injected by SessionStart hooks when CLAUDE.md says "no framing, let results speak."

System-reminder injection carries high perceived authority via specific templates and "always" keywords. General prose quality rules lose the salience competition. Disable output-style plugins that conflict (e.g., `explanatory-output-style`, `learning-output-style` in settings.json `enabledPlugins`).

## Core Behavioral Rules

### Error Handling

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

**Exception:** `|| true` is legitimate only where a non-zero exit *encodes a result* rather than a failure — `grep` finding no match, `diff` finding differences. Suppress the exit in exactly those spots; never to silence an error you haven't inspected.

#### When Edit Tool Fails Repeatedly

**Do not escape to `sed -i` after Edit tool errors.** sed presents opaque syntax in permission prompts — user sees the command, not a content diff. This degrades the human review gate that Edit provides (old/new content visible).

**Correct pattern:** Stop and report the Edit failure after the second identical error. The stop-on-unexpected rule applies. Edit's permission UX is part of human oversight design — bypassing it with sed is not a neutral tool substitution.

### No Confabulation

**Never present invented heuristics, criteria, or thresholds as established facts.** If a rule, parameter, or methodology isn't grounded in evidence, documentation, or explicit user direction, say so.

Distinct from no-estimates (which covers predictions). This covers fabricated methodology claims, ungrounded rules, and invented parameters asserted with false confidence.

**When uncertain:** State what you don't know. Propose with "ungrounded — needs validation" framing, not as established practice.

**Applies to operational thresholds:** Deriving thresholds from reasoning (">2 inline phases → batch") or replacing one confabulated metric with a "cleaner" confabulated metric is still confabulation. Ground thresholds in empirical data. If data doesn't exist, state the decision as ungrounded and defer until measurement. The No Estimates rule applies to operational thresholds, not just time/cost predictions.

### No Estimates

**No estimates unless requested** - Do NOT make estimates, predictions, or extrapolations unless explicitly requested by the user. Report measured data only.

**Reuse is not measurement.** Citing numbers from a prior document does not satisfy "measured data." If a prior analysis contains estimates, measure fresh — token economy (reference don't repeat) governs format, not data quality.

### Source Not Generated

**Always edit source files, never generated output.** When a file is produced by a generator (prepare-runbook.py, skill expansion, template rendering), edit the source that produces it. Changes to generated files are overwritten on next generation.

**If unsure which is source:** Ask before editing.

### Code Removal

**Delete obsolete code, don't archive it.**

When code, files, or designs become obsolete or superseded:
- **Delete them completely** - Remove the files from the repository
- **Do NOT archive** - Don't move to `archive/`, `old/`, or similar directories
- **Do NOT comment out** - Don't leave dead code in comments
- **Do NOT keep "for reference"** - Git history preserves everything if needed

**Rationale:**
- Dead code creates maintenance burden
- Archives accumulate and confuse future developers
- Git history is the archive - use `git log` and `git show` to retrieve old code
- Clean codebase is easier to navigate and understand

**Examples:**

**Wrong:**
```bash
mkdir archive/
mv old-design.md archive/
git add archive/old-design.md
```

**Correct:**
```bash
rm old-design.md
git add old-design.md
```

**Exception:** Documentation of *decisions* (why something was chosen over alternatives) should be kept in architecture decision records (ADRs) or similar, but the obsolete implementation itself should be removed.

### Temporary Files

**Use the harness scratchpad for throwaway files; use project-local `tmp/`
when a temp file should stay with the repo.**

- Claude Code provides a per-session scratchpad directory (its path is given
  in the system prompt, under `/tmp/claude-*/`). It is sandbox-writable and
  session-isolated — use it for intermediate results, scratch scripts, and
  work that does not belong in the project.
- Use project-local `<project-root>/tmp/` when a temp file needs to be
  inspectable within the repo or to outlive the session; it is gitignored.
- Do not scatter temp files into arbitrary system locations outside those
  two.

### Project Tooling Priority

**Rule:** Before executing ad-hoc commands, check if a project recipe already handles the operation.

**Priority order:**
1. **Project recipe** (`just <recipe>`, `make <target>`, project scripts) — always preferred
2. **Ad-hoc command** (`ln`, `mv`, `cp`, etc.) — only when no recipe exists

**Why:** Project recipes encode institutional knowledge — correct paths, ordering, side effects, edge cases. Ad-hoc commands bypass all of this, even when functionally equivalent.

**Check:** Run `just --list` (or equivalent) before writing manual commands for common operations like:
- Code formatting → `just format`
- Linting → `just lint`
- Testing → `just test`
- Pre-commit validation → `just precommit`

#### Precommit Cost

`just precommit` is fast when the test suite is green, thanks to test sentinel. Valid as both entry gate and exit gate without redundant overhead concern.

**Partial failure recovery:** If a recipe fails partway through, fix the obstruction and **retry the recipe** — do not complete remaining steps manually. Recipes are atomic units; manually finishing steps bypasses error handling, ordering, and side effects encoded in the recipe.

**Deny-list as routing signal:** When a CLI command fails and raw commands are denied, the deny list is a routing signal — it means "use the wrapper." After CLI failure, retry with escalated flags (`--force`) before decomposing into raw commands.

#### Check Platform Capabilities Before Building

**Anti-pattern:** Building custom review/workflow infrastructure without checking what the platform already ships.

**Correct pattern:** Inventory platform-provided plugins and features first. Build custom only for gaps. Anthropic ships 28 official plugins including code-review, feature-dev, security-guidance, commit-commands, claude-md-management.

**Rationale:** Custom infrastructure diverges from platform evolution. Official plugins get maintained, updated, and integrated. Reinvention wastes effort and creates maintenance burden.

#### Use Full-Featured CLI Invocations

**Anti-pattern:** Using the bare/simple invocation form of a CLI when a richer form exists that automates side effects — then manually performing those side effects to compensate.

**Correct pattern:** Before invoking a CLI command, check `--help` or known options. Use the form that includes automation (validation, related updates). Manual side effects are worse, error-prone, and miss features.

**Root cause:** Familiarity with the primitive form suppresses discovery of the full-featured form. The simple form's visible success masks the missing side effects.

**Same class as:** reaching for an ad-hoc `python3 -c "import..."` one-liner instead of the existing `edify` subcommand that already does the job.

#### Rule Suppression by Procedure

**Anti-pattern:** Procedural instructions in fragments suppress cross-cutting operational rules. When a procedure says "call X()" the agent follows it literally, skipping the project-tooling check.

**Correct pattern:** The check-for-existing-tools rule applies even when a procedure names a specific function. Specific instructions must not suppress general operational rules.

**Evidence:** a procedure that said "call `<function>()`" led an agent to write ad-hoc Python — several failed attempts guessing attributes — when an `edify` subcommand already did the job. The named-function instruction suppressed the check-for-existing-tools rule.

#### Validation Output Integrity

**Anti-pattern:** `just precommit 2>&1 | tail -N` or similar truncation. Validation output is a diagnostic signal — truncation hides the pass/fail/xfail summary that distinguishes real failures from expected noise.

**Correct pattern:** Show full output from `just precommit`, `just test`, `just lint`. If output is too long, fix the recipe (add `--quiet`, `--tb=no`), not the consumption site.

**Evidence:** xfail traceback from `pytest-markdown-report` was visually identical to real failure. Agent tailed output, missed summary counts, ran unnecessary `git stash` diagnostic cycle.

## CLI (`edify-cli`)

Source in `src/edify/`. Four tools:
- **Session scraping** — `edify list | extract <prefix> | collect`
- **Token counting** — `edify tokens FILE...` (Anthropic API)
- **Markdown postprocessing** — `edify markdown` (reads paths from stdin)
- **Contract checking** — `edify check <target>` (CrossHair verification)

## Skills

In `plugin/skills/`, invoked via slash command.

- **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), with `review-plan` and `review` as the quality gates.
- **Standalone:** `proof`, `ground`, `deliverable-review`, `formalize`, `recall`.

The pipeline agents live in `plugin/agents/` (correctors, `artisan`, `scout`,
`test-driver`, `tdd-auditor`, `refactor`, and friends); its backing scripts are
`plugin/bin/prepare-runbook.py` and `validate-runbook.py`. Pipeline docs are in
`plugin/docs/`.

Execution delegates **by reference**: the orchestrator dispatches a standing
agent with a path to a step file, and the step file names the design, outline,
and recall artifacts it needs. Bespoke per-plan agent definitions were dropped
in 2026-08 — they fought the platform (not discoverable until session restart)
and the runbook system already supplies the flexibility they were built for.

The pipeline was torn down in 2026-05 and revived in 2026-08. On revival it was
rewired off the retired subsystems: recall now means reading `memory/MEMORY.md`
and the memory files it indexes rather than the removed `edify _recall` CLI,
`/commit` and `/handoff` point at the `commit-commands` and `handoff` plugins,
and the session task frame is `.claude/handoff-task.md`.

## Recipes

- `just precommit` — run all checks
- `just test *ARGS` — run test suite
- `just dev` — format and run all checks
- `just format` / `just lint` / `just check`

## Design Decisions

See `docs/design.md` — the living design record (requirements, architecture,
decisions, rejected alternatives). It is rewired when components change, not
appended to as an ADR archive. `docs/changelog.md` carries the dated
design-significant entries.
