# Inbound Reference Map: Pipeline Simplification

Mechanical mapping of pipeline machinery references across the codebase.
Generated: Sat Aug 29 12:08:50 CEST 2026

---

## `prepare-runbook`

**Hit count: 75**

- docs/changelog.md:38 — `prepare-runbook.py` used to generate into `.claude/agents/` are gone — they
- docs/superpowers/design/plugin-transition-evaluation.md:237 — - `source-not-generated.md:3` names `prepare-runbook.py` — deleted. Memory's
- docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:84 — | `plugin/bin/prepare-runbook.py` | `resolve_recall_entries` docstring — memory files, not "memory and decision files"
- docs/superpowers/specs/2026-03-30-runbook-warnings-directory-aware-design.md:5 — `validate_file_references()` in `prepare-runbook.py` checks backtick-wrapped file paths against the filesystem. For gree
- docs/superpowers/specs/2026-03-30-runbook-warnings-directory-aware-design.md:28 — - `plugin/bin/prepare-runbook.py` — add parent-directory check in `validate_file_references()`
- docs/superpowers/specs/2026-03-30-runbook-warnings-directory-aware-design.md:29 — - `tests/test_prepare_runbook_fenced.py` — add test: existing-parent warns, non-existent-parent silent
- docs/design.md:18 — **Next** — test coverage for `plugin/bin/prepare-runbook.py`; the suite reaches
- docs/design.md:68 — | FR-19 | Generate step artifacts and an orchestrator manifest from a runbook | Partial | `bin/prepare-runbook.py` · **
- docs/design.md:143 — Scripts: `plugin/bin/prepare-runbook.py` (runbook → step artifacts) and
- docs/design.md:379 — *Implemented 2026-08-13.* `prepare-runbook.py` writes
- docs/design.md:420 — | T5 | Runbook → Step artifacts | `runbook.md` | `steps/step-*.md` | `prepare-runbook.py` |
- docs/design.md:464 — design. `prepare-runbook.py` skips step-file generation for those.
- docs/design.md:923 — **L-1 — `prepare-runbook.py` has no test coverage.** The suite reaches it only
- agents/learnings.md:126 — - Anti-pattern: Reusing a plan name for rework (e.g., `handoff-cli-tool` for both original implementation and rework). `
- plugin/docs/general-workflow.md:156 — Run `prepare-runbook.py` to create
- plugin/docs/general-workflow.md:254 — - **Tier 3** (Full Runbook): Executes 4-point runbook prep process, delegates review to `edify:runbook-corrector`, invok
- plugin/docs/general-workflow.md:336 — Agent: Invokes /runbook, creates the runbook, runs prepare-runbook.py
- plugin/docs/general-workflow.md:431 — 2. Re-run `prepare-runbook.py` (idempotent, overwrites artifacts)
- plugin/docs/general-workflow.md:463 — - Generate execution artifacts via `prepare-runbook.py`
- plugin/docs/general-workflow.md:475 — ## Script: `prepare-runbook.py`
- plugin/docs/general-workflow.md:477 — **Location:** `plugin/bin/prepare-runbook.py`
- plugin/docs/general-workflow.md:483 — prepare-runbook.py plans/foo/runbook.md
- plugin/docs/tdd-workflow.md:94 — **Next step:** Run `prepare-runbook.py` to generate execution artifacts.
- plugin/docs/tdd-workflow.md:137 — **After /runbook (runbook reviewed and finalized), run prepare-runbook.py:**
- plugin/docs/tdd-workflow.md:139 — python3 plugin/bin/prepare-runbook.py plans/<feature-name>/runbook.md
- plugin/docs/tdd-workflow.md:157 — 1. `prepare-runbook.py` writes a step file per cycle half, each carrying a `## Context` block naming the design, outline
- plugin/docs/tdd-workflow.md:289 — 4. **Regenerate step files** - If runbook.md changed, re-run `prepare-runbook.py`
- plugin/docs/tdd-workflow.md:352 — - Execute steps sequentially without prepare-runbook.py
- plugin/docs/tdd-workflow.md:370 — - Run `prepare-runbook.py` to create runbook artifacts
- plugin/bin/prepare-runbook.py:21 — prepare-runbook.py <runbook-file.md>
- plugin/bin/prepare-runbook.py:22 — prepare-runbook.py <directory-with-phase-files>
- plugin/bin/prepare-runbook.py:25 — prepare-runbook.py plans/foo/runbook.md
- plugin/bin/prepare-runbook.py:32 — prepare-runbook.py plans/foo/
- plugin/bin/prepare-runbook.py:36 — prepare-runbook.py plans/tdd-test/runbook.md
- plugin/bin/prepare-runbook.py:1050 — f"Generated from `{runbook_path}` by prepare-runbook.py. "
- plugin/bin/prepare-runbook.py:1080 — f"prepare-runbook.py. Edit the runbook, not this file.\n\n{body}\n"
- plugin/bin/prepare-runbook.py:1783 — "Usage: prepare-runbook.py <runbook-file.md> OR <directory-with-phase-files>",
- plugin/bin/validate-runbook.py:12 — "prepare_runbook", Path(__file__).parent / "prepare-runbook.py"
- plugin/skills/orchestrate/SKILL.md:16 — **Prerequisites:** Runbook prepared with `/runbook` (artifacts created by `prepare-runbook.py`)
- plugin/skills/orchestrate/SKILL.md:31 — The artifacts a step file names under `## Context` (`design.md`, `outline.md`, `common-context.md`) are written by `prep
- plugin/skills/orchestrate/SKILL.md:286 — There is no agent cleanup step. `prepare-runbook.py` installs nothing into `.claude/agents/`; the plan's generated artif
- plugin/skills/runbook/SKILL.md:7 — allowed-tools: Agent, Read, Write, Edit, Skill, Bash(mkdir:*, plugin/bin/prepare-runbook.py, echo:*|pbcopy)
- plugin/skills/runbook/SKILL.md:13 — - Tier 3: Execution runbook at plans/<job-name>/runbook.md, ready for prepare-runbook.py
- plugin/skills/runbook/SKILL.md:26 — **Workflow context:** Part of implementation workflow (see `docs/design.md` §6.4 "Pipeline contracts" for full pipeline
- plugin/skills/runbook/SKILL.md:37 — **Type does NOT affect:** Tier assessment, outline generation, consolidation gates, assembly (prepare-runbook.py auto-de
- plugin/skills/runbook/SKILL.md:54 — prepare-runbook.py auto-detects per-file via headers (`## Cycle X.Y:` vs `## Step N.M:`). Inline phases have no step/cyc
- plugin/skills/runbook/SKILL.md:159 — **Key distinction from Tier 3:** No prepare-runbook.py, no step files, no orchestrator plan. The planner acts as ad-hoc 
- plugin/skills/runbook/references/tier3-expansion-process.md:3 — **CRITICAL: This step is MANDATORY. Use `prepare-runbook.py` to create execution artifacts.**
- plugin/skills/runbook/references/tier3-expansion-process.md:7 — **Step 1: Run prepare-runbook.py**:
- plugin/skills/runbook/references/tier3-expansion-process.md:9 — plugin/bin/prepare-runbook.py plans/{name}/runbook.md
- plugin/skills/runbook/references/tier3-expansion-process.md:22 — **Why a fresh session:** planning and execution run at different model tiers, and orchestration is long-running — the 
- plugin/skills/runbook/references/tier3-expansion-process.md:138 — **Full orchestration (Tier 3, prepare-runbook.py):** `prepare-runbook.py` reads `plans/<job>/recall-artifact.md` during 
- plugin/skills/runbook/references/tier3-expansion-process.md:152 — Entries without `(phase N)` suffix are shared. `prepare-runbook.py` errors if a phase tag references a nonexistent or in
- plugin/skills/runbook/references/tier3-expansion-process.md:169 — - Forgetting to run prepare-runbook.py after review
- plugin/skills/runbook/references/tier3-expansion-process.md:179 — - Always run prepare-runbook.py to create artifacts
- plugin/skills/runbook/references/tier3-expansion-process.md:219 — - Phase-neutral entries only here. Phase-specific entries use `(phase N)` tag in recall artifact — `prepare-runbook.py
- plugin/skills/runbook/references/examples.md:231 — - Frontmatter with `type: tdd` enables prepare-runbook.py detection
- plugin/skills/runbook/references/examples.md:242 — - prepare-runbook.py splits into individual cycle files
- plugin/skills/runbook/references/tier3-planning-process.md:248 — **Discriminator:** The `## Execution Model` section encodes dispatch protocol (which agents, what context each receives,
- plugin/skills/runbook/references/tier3-planning-process.md:256 — 1. Do not promote to runbook format, do not run prepare-runbook.py -- the outline IS the execution plan
- plugin/skills/runbook/references/tier3-planning-process.md:283 — - Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header. prepare-runbook.py uses this 
- plugin/skills/runbook/references/tier3-planning-process.md:334 — **After all phases are finalized, validate phase files are ready, then delegate to prepare-runbook.py.**
- plugin/skills/runbook/references/tier3-planning-process.md:354 — **IMPORTANT -- Do NOT manually assemble:** Phase files remain separate until prepare-runbook.py processes them. Manual c
- plugin/skills/runbook/references/tier3-planning-process.md:356 — **Fallback header injection:** prepare-runbook.py injects missing `### Phase N:` headers from filenames during assembly.
- plugin/skills/runbook/references/tdd-cycle-planning.md:102 — Common TDD stop/error conditions (auto-injected by prepare-runbook.py into Common Context)
- plugin/skills/runbook/references/error-handling.md:35 — | **prepare-runbook.py missing** | Script not found | Report expected path, provide manual guidance, WARNING (proceed) |
- plugin/skills/runbook/references/error-handling.md:97 — ### prepare-runbook.py incompatibility
- plugin/skills/runbook/references/error-handling.md:103 — **Example:** "Compatibility issue: Cycle IDs have non-numeric chars ('Cycle 1.A'). prepare-runbook.py needs numeric only
- plugin/skills/review-plan/SKILL.md:422 — /design → /runbook → edify:runbook-corrector (fix-all) → [escalate if needed] → prepare-runbook.py → /orchestr
- plugin/agents/refactor.md:160 — plugin/bin/prepare-runbook.py plans/<runbook-name>/runbook.md
- plugin/README.md:77 — | `prepare-runbook.py` | Expand a runbook into per-step files, shared context, and an orchestrator plan |
- CLAUDE.md:57 — **Always edit source files, never generated output.** When a file is produced by a generator (prepare-runbook.py, skill 
- CLAUDE.md:183 — `plugin/bin/prepare-runbook.py` and `validate-runbook.py`. Pipeline docs are in
- plugin/skills/review/references/example-execution.md:21 — - plugin/bin/prepare-runbook.py (new file)
- plugin/skills/review/references/example-execution.md:42 — 1. prepare-runbook.py: Consider adding --help flag example to docstring

## `validate-runbook`

**Hit count: 23**

- docs/design.md:19 — it only indirectly through `validate-runbook.py`'s imports.
- docs/design.md:69 — | FR-20 | Check runbook structure deterministically | Done | `bin/validate-runbook.py` · `test_validate_runbook_reporti
- docs/design.md:144 — `validate-runbook.py` (deterministic structural checks).
- docs/design.md:419 — | T4.5 | Runbook → Validated runbook | phase files or runbook | validation reports | `validate-runbook.py` |
- docs/design.md:924 — indirectly through `validate-runbook.py`'s imports. The rewired step-file and
- tests/test_validate_runbook_reporting.py:1 — """Tests for validate-runbook.py report outcomes.
- tests/test_validate_runbook_reporting.py:16 — from tests.fixtures.validate_runbook_fixtures import VALID_TDD
- tests/test_validate_runbook_reporting.py:18 — SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "validate-runbook.py"
- tests/test_validate_runbook_reporting.py:40 — spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
- tests/fixtures/validate_runbook_fixtures.py:1 — """Fixture constants for test_validate_runbook.py."""
- plugin/bin/validate-runbook.py:429 — """Entry point for validate-runbook CLI."""
- plugin/bin/validate-runbook.py:430 — parser = argparse.ArgumentParser(prog="validate-runbook")
- plugin/skills/design/SKILL.md:173 — | /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/design/SKILL.md:174 — | /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/references/tier3-outline-process.md:18 — - Phase 3.5: Pre-execution validation via `validate-runbook.py`
- plugin/skills/runbook/references/tier3-planning-process.md:472 — plugin/bin/validate-runbook.py model-tags plans/<job>/
- plugin/skills/runbook/references/tier3-planning-process.md:473 — plugin/bin/validate-runbook.py lifecycle plans/<job>/
- plugin/skills/runbook/references/tier3-planning-process.md:474 — plugin/bin/validate-runbook.py test-counts plans/<job>/
- plugin/skills/runbook/references/tier3-planning-process.md:475 — plugin/bin/validate-runbook.py red-plausibility plans/<job>/
- plugin/skills/runbook/references/tier3-planning-process.md:476 — plugin/bin/validate-runbook.py verify-green-paths plans/<job>/
- plugin/skills/runbook/references/tier3-planning-process.md:505 — **Graceful degradation:** If `validate-runbook.py` doesn't exist, skip Phase 3.5 and proceed to Phase 4 with warning. Su
- plugin/README.md:78 — | `validate-runbook.py` | Check a runbook's structure before execution |
- CLAUDE.md:183 — `plugin/bin/prepare-runbook.py` and `validate-runbook.py`. Pipeline docs are in

## `split-execution-plan`

**Hit count: 3**

- plugin/scripts/split-execution-plan.py:9 — Usage: python split-execution-plan.py <plan-file.md> <output-dir>
- plugin/scripts/split-execution-plan.py:133 — print("Usage: python split-execution-plan.py <plan-file.md> <output-dir>")
- plugin/README.md:82 — Plus `scripts/split-execution-plan.py`, used by `/runbook` during expansion.

## `runbook-corrector`

**Hit count: 30**

- docs/design.md:138 — `design-corrector`, `outline-corrector`, `runbook-corrector`,
- docs/design.md:417 — | T3 | Outline → Phase files | `runbook-outline.md` | `runbook-phase-N.md` | `runbook-corrector` (type-aware) |
- docs/design.md:418 — | T4 | Phase files → Runbook | `runbook-phase-*.md` | `runbook.md` | `runbook-corrector` (holistic) |
- plugin/docs/general-workflow.md:148 — Delegate to `edify:runbook-corrector` for validation:
- plugin/docs/general-workflow.md:254 — - **Tier 3** (Full Runbook): Executes 4-point runbook prep process, delegates review to `edify:runbook-corrector`, invok
- plugin/docs/tdd-workflow.md:135 — **Review completed:** /runbook automatically delegates review to runbook-corrector agent before finalization.
- plugin/fragments/error-classification.md:21 — | **Inter-Agent Misalignment** | Agent deviates from specification or provided context (MASFT FC2) | Vet confabulation (
- plugin/skills/design/SKILL.md:173 — | /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/design/SKILL.md:174 — | /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/SKILL.md:26 — **Workflow context:** Part of implementation workflow (see `docs/design.md` §6.4 "Pipeline contracts" for full pipeline
- plugin/skills/runbook/references/tier3-outline-process.md:16 — - Phase 3: Final holistic cross-phase review via `runbook-corrector`
- plugin/skills/runbook/references/tier3-planning-process.md:308 — - Delegate to `edify:runbook-corrector` (fix-all mode)
- plugin/skills/runbook/references/tier3-planning-process.md:422 — Delegate to `edify:runbook-corrector` (fix-all mode) for cross-phase consistency:
- plugin/skills/runbook/references/tier3-planning-process.md:453 — 2. On terminal action "apply", /proof dispatches runbook-corrector automatically
- plugin/skills/runbook/references/tier3-planning-process.md:486 — - Any exit 2 (red-plausibility only): optionally delegate semantic analysis to `edify:runbook-corrector`, then proceed
- plugin/skills/review-plan/SKILL.md:8 — Use when the `edify:runbook-corrector` agent reaches its review-criteria step. This skill is the
- plugin/skills/review-plan/SKILL.md:10 — `edify:runbook-corrector`, which invokes this skill.
- plugin/skills/review-plan/SKILL.md:413 — **Automatic:** `/runbook` Phase 1 (per-phase) and Phase 3 (final) delegate to `edify:runbook-corrector`, which invokes t
- plugin/skills/review-plan/SKILL.md:414 — **Manual:** Dispatch `edify:runbook-corrector` with a runbook/phase file path — this skill is not user-invocable direc
- plugin/skills/review-plan/SKILL.md:422 — /design → /runbook → edify:runbook-corrector (fix-all) → [escalate if needed] → prepare-runbook.py → /orchestr
- plugin/skills/inline/SKILL.md:138 — Planning artifacts → runbook-corrector (not this gate).
- plugin/skills/inline/references/review-dispatch-template.md:47 — - **Constraint:** This template is for implementation changes only. Planning artifacts (runbooks, outlines, designs) rou
- plugin/agents/runbook-outline-corrector.md:61 — Recommendation: Use `edify:outline-corrector` for design outlines, or `edify:runbook-corrector` for full runbooks
- plugin/agents/design-corrector.md:65 — Recommendation: Use corrector for runbook review, or runbook-corrector for runbook phase review
- plugin/agents/corrector.md:119 — Details: This agent reviews implementation changes, not planning artifacts. Use runbook-corrector for runbook review.
- plugin/agents/corrector.md:121 — Recommendation: runbook-corrector is designed for document review with full fix-all capability
- plugin/agents/runbook-corrector.md:2 — name: runbook-corrector
- plugin/agents/runbook-corrector.md:119 — **Pre-existing issues** — Defects in the outline or design that the runbook faithfully reproduces. The runbook-correct
- plugin/agents/runbook-corrector.md:127 — **Inherited design decisions** — Architectural choices made in the design document. The runbook implements these; the 
- plugin/README.md:58 — | `runbook-corrector` | Corrector specialized for runbooks |

## `runbook-outline-corrector`

**Hit count: 10**

- plugin/skills/design/references/design-content-rules.md:41 — - Prevention: catches naming mismatches (e.g., `outline-corrector` vs `runbook-outline-corrector`) before they propagate
- docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:12 — `outline-corrector`, `runbook-outline-corrector`). The copies have drifted in
- docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:81 — | `corrector`, `design-corrector`, `outline-corrector`, `runbook-outline-corrector` | same |
- docs/design.md:139 — `runbook-outline-corrector`, `runbook-simplifier`), the executors (`artisan`,
- docs/design.md:415 — | T2 | Design → Outline | `design.md`, recall artifact | `runbook-outline.md` | `runbook-outline-corrector` (opus) |
- plugin/agents/runbook-outline-corrector.md:2 — name: runbook-outline-corrector
- plugin/agents/design-corrector.md:144 — - Flag mismatches: agent referenced but file doesn't exist, or name is a near-miss typo (e.g., `outline-corrector` vs `r
- plugin/skills/runbook/SKILL.md:131 — 2. **Review:** Delegate to `edify:runbook-outline-corrector` (fix-all mode). Specify Tier 2 format in prompt — no requ
- plugin/skills/runbook/references/tier3-planning-process.md:96 — - Delegate to `edify:runbook-outline-corrector` (fix-all mode)
- plugin/README.md:59 — | `runbook-outline-corrector` | Corrector specialized for runbook outlines |

## `review-plan` (skill)

**Hit count: 19**

- docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:11 — `orchestrate`, `review-plan`) and four agents (`corrector`, `design-corrector`,
- docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:80 — | `requirements`, `design`, `orchestrate`, `review-plan` SKILL.md | fallback paragraph → invocation; drop `agents/deci
- docs/design.md:61 — | FR-12 | Review every pipeline transformation at a typed gate | Done (prose) | `skills/review-plan/`, `agents/*correcto
- docs/design.md:133 — or `inline` (Tier 1/2), with `review-plan` and `review` as quality gates.
- plugin/skills/design/SKILL.md:173 — | /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/design/SKILL.md:174 — | /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/references/tier3-planning-process.md:239 — Check for common planning defects (criteria from review-plan skill Section 11)
- plugin/skills/runbook/references/tier3-planning-process.md:512 — - `verify-green-paths` *(any runbook)*: Flags `**Verify GREEN:**` / `**Verify RED:**` lines carrying specific pytest pat
- plugin/skills/runbook/references/anti-patterns.md:36 — | **Downstream reference in bootstrapping** | "Apply same criteria as outline-corrector" (agent not yet updated) | "Appl
- plugin/skills/review-plan/SKILL.md:2 — name: review-plan
- plugin/skills/review-plan/SKILL.md:399 — Read `plugin/skills/review-plan/references/report-template.md` and write the
- plugin/skills/review-plan/references/review-examples.md:3 — Violation and correct examples for review-plan criteria.
- plugin/README.md:31 — | `/review-plan` | Review runbook quality: TDD discipline, step clarity, LLM failure modes |
- CLAUDE.md:178 — - **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), wi
- README.md:42 — (or `/inline` for small work), with `/review-plan` and `/review` as the
- plugin/agents/runbook-corrector.md:64 — Invoke `Skill(skill: "edify:review-plan")` and follow it. Key focus areas:
- plugin/agents/runbook-corrector.md:89 — - Model assignment: Artifact-type override violations, complexity-model mismatches (advisory — see review-plan skill)
- plugin/agents/runbook-corrector.md:140 — 4. Invoke `Skill(skill: "edify:review-plan")` for detailed analysis
- plugin/agents/runbook-corrector.md:146 — Read `plugin/skills/review-plan/references/report-template.md`. It defines the

## `runbook-outline.md` (artifact)

**Hit count: 32**

- docs/design.md:415 — | T2 | Design → Outline | `design.md`, recall artifact | `runbook-outline.md` | `runbook-outline-corrector` (opus) |
- docs/design.md:416 — | T2.5 | Outline → Simplified outline | `runbook-outline.md` | consolidated outline | `runbook-simplifier` (opus) |
- docs/design.md:417 — | T3 | Outline → Phase files | `runbook-outline.md` | `runbook-phase-N.md` | `runbook-corrector` (type-aware) |
- plugin/bin/assemble-runbook.py:5 — Reads runbook-outline.md for metadata and all runbook-phase-N.md files,
- plugin/bin/assemble-runbook.py:78 — outline_file = runbook_path / "runbook-outline.md"
- plugin/skills/runbook/SKILL.md:12 — - Tier 2: Approved runbook outline at plans/<job-name>/runbook-outline.md
- plugin/skills/runbook/SKILL.md:130 — 1. Write `plans/<job>/runbook-outline.md` using Tier 2 outline format (below)
- plugin/skills/runbook/SKILL.md:132 — 3. **Proof:** Invoke `/proof plans/<job>/runbook-outline.md`
- plugin/skills/runbook/SKILL.md:146 — **Execution:** `/inline` executes from the approved `runbook-outline.md`. No `runbook.md` generated.
- plugin/skills/runbook/references/tier3-planning-process.md:61 — - File: `plans/<job>/runbook-outline.md`
- plugin/skills/runbook/references/tier3-planning-process.md:92 — - Commit `runbook-outline.md` to create clean checkpoint
- plugin/skills/runbook/references/tier3-planning-process.md:161 — - Input: `plans/<job>/runbook-outline.md` (post-0.85 state)
- plugin/skills/runbook/references/tier3-planning-process.md:182 — 1. Invoke `/proof plans/<job>/runbook-outline.md` — user validates post-simplification outline before expansion
- plugin/skills/runbook/references/tier3-planning-process.md:281 — - **Read Expansion Guidance:** Check `plans/<job>/runbook-outline.md` for `## Expansion Guidance` section.
- plugin/agents/runbook-outline-corrector.md:7 — - "Review runbook-outline.md before expanding to full runbook"
- plugin/agents/runbook-outline-corrector.md:53 — - File MUST be `runbook-outline.md` (not `outline.md`, not `runbook.md`)
- plugin/agents/runbook-outline-corrector.md:59 — Details: Expected runbook-outline.md, found <filename>
- plugin/agents/runbook-outline-corrector.md:68 — 2. Outline file: `plans/<job>/runbook-outline.md`
- plugin/agents/runbook-outline-corrector.md:240 — 2. Append "## Expansion Guidance" section to end of runbook-outline.md
- plugin/agents/runbook-outline-corrector.md:293 — **Artifact**: plans/<job>/runbook-outline.md
- plugin/agents/runbook-outline-corrector.md:440 — - Use **Edit** to apply fixes to runbook-outline.md
- plugin/agents/runbook-outline-corrector.md:464 — - Artifact type checking (runbook-outline.md only)
- plugin/agents/runbook-outline-corrector.md:510 — 7. Verify runbook-outline.md was edited with all fixes
- plugin/agents/runbook-outline-corrector.md:511 — 8. Verify "## Expansion Guidance" section appended to runbook-outline.md
- plugin/agents/runbook-outline-corrector.md:515 — 1. **Validate inputs** (requirements exist, design exists, artifact is runbook-outline.md)
- plugin/agents/runbook-outline-corrector.md:520 — 6. **Append expansion guidance** to runbook-outline.md (transmit recommendations to expansion step)
- plugin/agents/runbook-outline-corrector.md:522 — 8. **Update runbook-outline.md** with all fixes applied
- plugin/agents/runbook-corrector.md:58 — - If outline exists (`plans/<plan-name>/runbook-outline.md`), check for requirements mapping
- plugin/agents/runbook-simplifier.md:18 — user: "Simplify runbook-outline.md before expansion"
- plugin/agents/runbook-simplifier.md:50 — - `plans/<job>/runbook-outline.md` (post-0.85 state)
- plugin/agents/runbook-simplifier.md:104 — **Outline:** plans/<job>/runbook-outline.md
- plugin/agents/runbook-simplifier.md:150 — - **Outline-only modification:** Only modify runbook-outline.md and create report

## `orchestrator-plan`

**Hit count: 13**

- plugin/docs/general-workflow.md:159 — - Orchestrator plan (`plans/<name>/orchestrator-plan.md`)
- plugin/docs/general-workflow.md:489 — - `plans/foo/orchestrator-plan.md` (orchestrator instructions and phase-agent mapping)
- plugin/bin/prepare-runbook.py:7 — 3. Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)
- plugin/bin/prepare-runbook.py:29 — #   plans/foo/orchestrator-plan.md
- plugin/bin/prepare-runbook.py:39 — #   plans/tdd-test/orchestrator-plan.md
- plugin/bin/prepare-runbook.py:983 — orchestrator_path: plans/foo/orchestrator-plan.md
- plugin/bin/prepare-runbook.py:989 — orchestrator_path = path.parent / "orchestrator-plan.md"
- plugin/bin/prepare-runbook.py:1794 — "  - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)",
- plugin/docs/tdd-workflow.md:145 — - `plans/<feature-name>/orchestrator-plan.md` (execution index and phase-agent mapping)
- plugin/skills/orchestrate/SKILL.md:21 — ls -1 plans/<name>/orchestrator-plan.md
- plugin/skills/orchestrate/SKILL.md:26 — - `plans/<name>/orchestrator-plan.md` — structured step list and phase-agent mapping
- plugin/skills/orchestrate/SKILL.md:36 — Read plans/<name>/orchestrator-plan.md
- plugin/skills/runbook/SKILL.md:54 — prepare-runbook.py auto-detects per-file via headers (`## Cycle X.Y:` vs `## Step N.M:`). Inline phases have no step/cyc

## `Tier 3`

**Hit count: 27**

- docs/design.md:132 — Pipeline skills: `requirements` → `design` → `runbook` → `orchestrate` (Tier 3)
- docs/design.md:497 — dispatches. Tier 3 (orchestrated): prompt generation itself is expensive — many
- docs/design.md:928 — files, Tier 2 6-15, Tier 3 >15 or >10 TDD cycles, and the "every 3-5 cycles"
- agents/learnings.md:41 — - Root cause: Gate structure frames memory-index scan as "fallback" when it's the primary path for moderate tasks. Artif
- plugin/docs/general-workflow.md:205 — - **After orchestration (Tier 3):** Use `corrector` — orchestrator has no context, agent applies critical/major fixes 
- plugin/docs/general-workflow.md:209 — - **Few/simple fixes** → Apply directly (Tier 1/2) or already applied (Tier 3)
- plugin/docs/general-workflow.md:254 — - **Tier 3** (Full Runbook): Executes 4-point runbook prep process, delegates review to `edify:runbook-corrector`, invok
- plugin/docs/tdd-workflow.md:357 — ### Tier 3: Full Runbook
- plugin/docs/tdd-workflow.md:374 — **Note:** Tier 3 refactoring is rare. Most TDD refactoring is Tier 1 or 2.
- plugin/fragments/continuation-passing.md:98 — | `/orchestrate` | `["/handoff:handoff", "/commit-commands:commit"]` | Runbook execution (Tier 3) |
- plugin/skills/runbook/SKILL.md:13 — - Tier 3: Execution runbook at plans/<job-name>/runbook.md, ready for prepare-runbook.py
- plugin/skills/runbook/SKILL.md:71 — This override applies to Tier 2 delegation (model parameter), Tier 3 step assignment (Execution Model field), and the Ex
- plugin/skills/runbook/SKILL.md:159 — **Key distinction from Tier 3:** No prepare-runbook.py, no step files, no orchestrator plan. The planner acts as ad-hoc 
- plugin/skills/runbook/SKILL.md:169 — ### Tier 3: Full Runbook
- plugin/skills/runbook/SKILL.md:192 — - Tier 3: no prepend (Phase 4 prepares artifacts; orchestration runs in a fresh session at a different model tier)
- plugin/skills/runbook/references/tier3-outline-process.md:1 — ## Planning Process (Tier 3 Only)
- plugin/skills/runbook/references/tier3-expansion-process.md:138 — **Full orchestration (Tier 3, prepare-runbook.py):** `prepare-runbook.py` reads `plans/<job>/recall-artifact.md` during 
- plugin/skills/runbook/references/tier3-planning-process.md:1 — # Tier 3 Planning Process
- plugin/skills/runbook/references/tier3-planning-process.md:3 — Full planning process for Tier 3 runbooks: Phase 0.5 through Phase 3.5.
- plugin/skills/runbook/references/tier3-planning-process.md:155 — **Mandatory** for all Tier 3 runbooks.
- plugin/skills/runbook/references/tier3-planning-process.md:466 — **Mandatory** for all Tier 3 runbooks.
- plugin/skills/runbook/references/tier3-planning-process.md:494 — Tier 3 runbook whose phases are all general is validated by
- plugin/skills/inline/SKILL.md:19 — Covers Tier 1 (direct) and Tier 2 (delegated) execution — same lifecycle, different scale. Tier 3 uses /orchestrate.
- plugin/agents/refactor.md:73 — **Tier 3:** Restructure module architecture → separate runbook
- plugin/agents/refactor.md:122 — **Tier 3 (full runbook):**
- plugin/README.md:29 — | `/orchestrate` | Execute a prepared runbook with mechanical verification gates (Tier 3) |
- CLAUDE.md:178 — - **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), wi

## `Tier 2`

**Hit count: 19**

- docs/design.md:495 — it can execute it. Tier 2 (delegated): work exceeds inline capacity but prompt
- docs/design.md:501 — The Tier 1/2 boundary is **capacity**; the Tier 2/3 boundary is **orchestration
- docs/design.md:928 — files, Tier 2 6-15, Tier 3 >15 or >10 TDD cycles, and the "every 3-5 cycles"
- plugin/docs/general-workflow.md:253 — - **Tier 2** (Lightweight): Delegates to artisan agents, reviews, commits
- plugin/docs/tdd-workflow.md:338 — ### Tier 2: Simple Runbook
- plugin/skills/runbook/SKILL.md:12 — - Tier 2: Approved runbook outline at plans/<job-name>/runbook-outline.md
- plugin/skills/runbook/SKILL.md:71 — This override applies to Tier 2 delegation (model parameter), Tier 3 step assignment (Execution Model field), and the Ex
- plugin/skills/runbook/SKILL.md:106 — A single-file prototype assessed against exploration conventions → minimal scope (Tier 2 may suffice). Same script ass
- plugin/skills/runbook/SKILL.md:110 — ### Tier 2: Lightweight Delegation
- plugin/skills/runbook/SKILL.md:130 — 1. Write `plans/<job>/runbook-outline.md` using Tier 2 outline format (below)
- plugin/skills/runbook/SKILL.md:131 — 2. **Review:** Delegate to `edify:runbook-outline-corrector` (fix-all mode). Specify Tier 2 format in prompt — no requ
- plugin/skills/runbook/SKILL.md:135 — **Tier 2 outline format:**
- plugin/skills/runbook/SKILL.md:191 — - Tier 2: prepend `/inline plans/<job> execute`
- plugin/skills/runbook/references/tier3-expansion-process.md:136 — **Lightweight orchestration (Tier 2):** Orchestrator dispatches agents directly. Each agent Reads the files listed in th
- plugin/skills/inline/SKILL.md:19 — Covers Tier 1 (direct) and Tier 2 (delegated) execution — same lifecycle, different scale. Tier 3 uses /orchestrate.
- plugin/skills/inline/SKILL.md:84 — ### Delegated Execution (Tier 2)
- plugin/skills/inline/SKILL.md:110 — **No mid-execution checkpoints.** Corrector (Phase 4a) is the sole semantic review. Post-step lint catches mechanical is
- plugin/agents/refactor.md:72 — **Tier 2:** Split large function → 3 manual edits with verification
- plugin/agents/refactor.md:117 — **Tier 2 (simple steps):**

## `Tier 1`

**Hit count: 21**

- docs/design.md:60 — | FR-11 | Wrap Tier 1/2 work in a lifecycle: pre-work → execute → corrector → triage → deliverable-review | Done
- docs/design.md:133 — or `inline` (Tier 1/2), with `review-plan` and `review` as quality gates.
- docs/design.md:493 — **D-34 — Three execution tiers, grounded in environment constraints.** Tier 1
- docs/design.md:501 — The Tier 1/2 boundary is **capacity**; the Tier 2/3 boundary is **orchestration
- docs/design.md:927 — **L-2 — The tier thresholds are ungrounded operational parameters.** Tier 1 <6
- agents/learnings.md:41 — - Root cause: Gate structure frames memory-index scan as "fallback" when it's the primary path for moderate tasks. Artif
- plugin/docs/general-workflow.md:206 — - **After direct/lightweight work (Tier 1/2):** Use `corrector` — caller has context to evaluate and apply fixes from 
- plugin/docs/general-workflow.md:209 — - **Few/simple fixes** → Apply directly (Tier 1/2) or already applied (Tier 3)
- plugin/docs/general-workflow.md:252 — - **Tier 1** (Direct): Implements directly, vets, commits
- plugin/docs/tdd-workflow.md:317 — ### Tier 1: Script-Based Refactoring
- plugin/docs/tdd-workflow.md:374 — **Note:** Tier 3 refactoring is rare. Most TDD refactoring is Tier 1 or 2.
- plugin/fragments/continuation-passing.md:97 — | `/inline` | `["/handoff:handoff", "/commit-commands:commit"]` | Inline execution lifecycle (Tier 1/2) |
- plugin/skills/inline/SKILL.md:6 — /runbook route Tier 1/2 execution-ready work. Wraps corrector dispatch,
- plugin/skills/inline/SKILL.md:17 — Sequence the lifecycle for execution-ready work: context loading, implementation, corrector review, triage feedback, del
- plugin/skills/inline/SKILL.md:19 — Covers Tier 1 (direct) and Tier 2 (delegated) execution — same lifecycle, different scale. Tier 3 uses /orchestrate.
- plugin/skills/inline/SKILL.md:80 — ### Direct Execution (Tier 1)
- plugin/skills/requirements/SKILL.md:252 — - Very clear scope + simple (Tier 1/2) → `/runbook plans/<job>/requirements.md`
- plugin/README.md:30 — | `/inline` | Sequence inline execution — pre-work, execute, post-work (Tier 1/2) |
- CLAUDE.md:178 — - **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), wi
- plugin/agents/refactor.md:71 — **Tier 1:** Extract repeated code pattern → sed/awk script
- plugin/agents/refactor.md:112 — **Tier 1 (script-based):**

## `assemble-runbook`

**Hit count: 5**

- plugin/bin/assemble-runbook.py:62 — def assemble_runbook(runbook_dir: str) -> str:
- plugin/bin/assemble-runbook.py:201 — print("Usage: assemble-runbook.py <runbook-directory>", file=sys.stderr)
- plugin/bin/assemble-runbook.py:202 — print("Example: assemble-runbook.py plans/workflow-feedback-loops", file=sys.stderr)
- plugin/bin/assemble-runbook.py:205 — result = assemble_runbook(sys.argv[1])
- plugin/README.md:79 — | `assemble-runbook.py` | Reassemble a split runbook directory into a single document |

## `tier3-expansion-process`

**Hit count: 1**

- plugin/skills/runbook/references/tier3-outline-process.md:25 — When past outline sufficiency (Phase 0.95), Read `references/tier3-expansion-process.md` for Phase 4 (artifact preparati

## `tier3-planning-process`

**Hit count: 1**

- plugin/skills/runbook/references/tier3-outline-process.md:3 — **Full process detail:** Read `references/tier3-planning-process.md` for Phases 0.5-3.5 (discovery, outline generation, 

## `tier3-outline-process`

**Hit count: 1**

- plugin/skills/runbook/SKILL.md:181 — **Sequence:** Read `references/tier3-outline-process.md` for the planning process overview and outline generation (Phase

## `runbook-phase`

**Hit count: 26**

- docs/design.md:417 — | T3 | Outline → Phase files | `runbook-outline.md` | `runbook-phase-N.md` | `runbook-corrector` (type-aware) |
- docs/design.md:418 — | T4 | Phase files → Runbook | `runbook-phase-*.md` | `runbook.md` | `runbook-corrector` (holistic) |
- plugin/bin/prepare-runbook.py:18 — - Phase-grouped runbooks (runbook-phase-*.md files in a directory)
- plugin/bin/prepare-runbook.py:33 — # Detects runbook-phase-*.md files, assembles them, then creates same artifacts
- plugin/bin/prepare-runbook.py:872 — Detects runbook-phase-*.md files, sorts by phase number,
- plugin/bin/prepare-runbook.py:877 — directory: Path to directory containing runbook-phase-*.md files
- plugin/bin/prepare-runbook.py:886 — # Find all phase files: runbook-phase-*.md
- plugin/bin/prepare-runbook.py:887 — phase_files = sorted(dir_path.glob("runbook-phase-*.md"))
- plugin/bin/prepare-runbook.py:893 — match = re.search(r"runbook-phase-(\d+)\.md", path.name)
- plugin/bin/prepare-runbook.py:1484 — content += f"- Phase file: {phase_dir}/runbook-phase-{p}.md\n"
- plugin/bin/prepare-runbook.py:1657 — return str(Path(phase_dir) / f"runbook-phase-{phase_num}.md")
- plugin/bin/prepare-runbook.py:1805 — "  - Phase-grouped runbooks (runbook-phase-*.md files in directory)",
- plugin/bin/prepare-runbook.py:1824 — if not list(input_path.glob("runbook-phase-*.md"))
- plugin/bin/prepare-runbook.py:1826 — f"ERROR: No runbook-phase-*.md files found in directory: {input_path}",
- plugin/bin/assemble-runbook.py:5 — Reads runbook-outline.md for metadata and all runbook-phase-N.md files,
- plugin/bin/assemble-runbook.py:112 — runbook_path.glob("runbook-phase-*.md"),
- plugin/bin/assemble-runbook.py:117 — print(f"Error: No runbook-phase-*.md files found in {runbook_dir}", file=sys.stderr)
- plugin/skills/runbook/references/tier3-planning-process.md:282 — - File: `plans/<job>/runbook-phase-N.md`
- plugin/skills/runbook/references/tier3-planning-process.md:300 — - No phase file generated (`runbook-phase-N.md` not written for inline phases)
- plugin/skills/runbook/references/tier3-planning-process.md:304 — - Commit `runbook-phase-N.md` to create clean checkpoint
- plugin/skills/runbook/references/tier3-planning-process.md:339 — - Verify all phase files exist (`runbook-phase-1.md` through `runbook-phase-N.md`)
- plugin/skills/runbook/references/tier3-planning-process.md:452 — 1. Invoke `/proof plans/<job>/runbook-phase-*.md` — present expanded phase content for structured user review
- plugin/skills/review-plan/SKILL.md:65 — 1. **Infer the plan directory** from the reviewed file path — reviewing `plans/foo/runbook-phase-1.md` or `plans/foo/r
- plugin/agents/outline-corrector.md:143 — **Cross-component interface check:** For each component that consumes another's output, verify the interface is compatib
- plugin/agents/runbook-corrector.md:10 — - "Review runbook-phase-1.md for quality"
- plugin/agents/runbook-corrector.md:53 — **Phase file exception:** When reviewing a phase file (`runbook-phase-N.md`), SKIP the outline review check. Phase files

## `verify-red`

**Hit count: 2**

- plugin/skills/orchestrate/SKILL.md:108 — plugin/skills/orchestrate/scripts/verify-red.sh <test_file_path>
- plugin/skills/orchestrate/SKILL.md:296 — - **Verification scripts:** `plugin/skills/orchestrate/scripts/verify-step.sh`, `verify-red.sh`

## `verify-step`

**Hit count: 3**

- plugin/skills/orchestrate/SKILL.md:146 — just test && plugin/skills/orchestrate/scripts/verify-step.sh
- plugin/skills/orchestrate/SKILL.md:160 — plugin/skills/orchestrate/scripts/verify-step.sh
- plugin/skills/orchestrate/SKILL.md:296 — - **Verification scripts:** `plugin/skills/orchestrate/scripts/verify-step.sh`, `verify-red.sh`

## `common-context`

**Hit count: 34**

- docs/design.md:380 — `plans/<name>/common-context.md` and, when the outline lives in the runbook
- plugin/docs/general-workflow.md:158 — - Shared context (`plans/<name>/common-context.md`)
- plugin/docs/general-workflow.md:488 — - `plans/foo/common-context.md` (shared context and resolved recall)
- plugin/docs/tdd-workflow.md:144 — - `plans/<feature-name>/common-context.md` (shared context and resolved recall)
- plugin/docs/tdd-workflow.md:157 — 1. `prepare-runbook.py` writes a step file per cycle half, each carrying a `## Context` block naming the design, outline
- plugin/bin/prepare-runbook.py:6 — 2. Shared context (plans/<runbook-name>/common-context.md)
- plugin/bin/prepare-runbook.py:28 — #   plans/foo/common-context.md (when the runbook has a Common Context)
- plugin/bin/prepare-runbook.py:333 — def validate_cycle_structure(cycle, common_context="")
- plugin/bin/prepare-runbook.py:338 — common_context: Content from Common Context section (for inherited sections)
- plugin/bin/prepare-runbook.py:373 — common_lower = common_context.lower()
- plugin/bin/prepare-runbook.py:626 — 'common_context': (section_content or None),
- plugin/bin/prepare-runbook.py:634 — "common_context": None,
- plugin/bin/prepare-runbook.py:708 — if current_section == "common_context"
- plugin/bin/prepare-runbook.py:709 — sections["common_context"] = content_str
- plugin/bin/prepare-runbook.py:733 — current_section = "common_context"
- plugin/bin/prepare-runbook.py:1031 — def write_common_context(plan_dir, common_context, runbook_path)
- plugin/bin/prepare-runbook.py:1032 — """Write shared step context to plans/<name>/common-context.md.
- plugin/bin/prepare-runbook.py:1034 — `common_context` already carries any resolved recall appended by the
- plugin/bin/prepare-runbook.py:1037 — body = (common_context or "").strip()
- plugin/bin/prepare-runbook.py:1047 — path = plan_dir / "common-context.md"
- plugin/bin/prepare-runbook.py:1163 — if sections.get("common_context")
- plugin/bin/prepare-runbook.py:1164 — step_items.append(("Common Context", sections["common_context"]))
- plugin/bin/prepare-runbook.py:1643 — context_path = write_common_context(
- plugin/bin/prepare-runbook.py:1644 — plan_dir, sections["common_context"], runbook_path
- plugin/bin/prepare-runbook.py:1790 — "  - Shared context (plans/<runbook-name>/common-context.md)",
- plugin/bin/prepare-runbook.py:1881 — common_context = "\n".join(common_parts)
- plugin/bin/prepare-runbook.py:1886 — messages = validate_cycle_structure(cycle, common_context)
- plugin/bin/prepare-runbook.py:1920 — current_cc = sections.get("common_context") or ""
- plugin/bin/prepare-runbook.py:1921 — sections["common_context"] = (
- plugin/skills/orchestrate/SKILL.md:31 — The artifacts a step file names under `## Context` (`design.md`, `outline.md`, `common-context.md`) are written by `prep
- plugin/skills/orchestrate/SKILL.md:219 — **Shared context:** plans/<name>/common-context.md
- plugin/skills/review-plan/SKILL.md:54 — - **Common Context** (`## Common Context` in runbook) — project paths, constraints, cross-step dependencies. Written t
- plugin/scripts/split-execution-plan.py:71 — def extract_common_context(content: str, steps: dict[int, tuple[int, int]], format_type: Literal["phase", "step"]) -> st
- plugin/scripts/split-execution-plan.py:156 — context = extract_common_context(content, steps, format_type)

## `manifest`

**Hit count: 20**

- scripts/release.sh:29 — manifest="plugin/.claude-plugin/plugin.json"
- scripts/release.sh:54 — [ -f "$manifest" ] || die "$manifest not found — run from the repo root"
- scripts/release.sh:66 — plugin_name=$(jq -r .name "$manifest")
- scripts/release.sh:84 — manifest_version=$(jq -r .version "$manifest")
- scripts/release.sh:99 — ' "$manifest")
- scripts/release.sh:105 — V=$(jq -r .version "$manifest")
- scripts/release.sh:119 — git add "$manifest" pyproject.toml uv.lock
- scripts/release.sh:123 — note "manifest + tag: $tag created locally"
- scripts/release.sh:187 — jq --arg v "$V" --arg repo "$repo_slug" --slurpfile m "$manifest" '
- docs/superpowers/design/plugin-transition-evaluation.md:103 — | Two versions in lockstep | **Absent** — single-manifest model, `manifest=".claude-plugin/plugin.json"` hardcoded roo
- docs/design.md:16 — manifest shapes.
- docs/design.md:68 — | FR-19 | Generate step artifacts and an orchestrator manifest from a runbook | Partial | `bin/prepare-runbook.py` · **
- docs/design.md:232 — manifest has no `edify` entry, so edify is uninstallable meanwhile. *Reopen-if:*
- docs/design.md:392 — (D-25). The inert `max_turns` manifest column is gone; turn and duration bounds
- docs/design.md:925 — manifest shapes are verified only by manual runs against three runbook shapes.
- docs/marketplace.md:9 — | `ddaanet/claude-plugins` | Marketplace manifest | `/Users/david/code/claude-plugins` |
- package-lock.json:91 — "npm-pick-manifest": "^9.0.0",
- package-lock.json:2036 — "node_modules/npm-pick-manifest": {
- package-lock.json:2038 — "resolved": "https://registry.npmjs.org/npm-pick-manifest/-/npm-pick-manifest-9.1.0.tgz",
- plugin/README.md:75 — | `bump-plugin-version.py` | Bump the plugin manifest version |

## `steps/` (pipeline path segment)

**Hit count (pipeline-related): 14**

- plugin/skills/orchestrate/SKILL.md:22 — ls -1 plans/<name>/steps/step-*.md 2>/dev/null || true
- plugin/skills/orchestrate/SKILL.md:27 — - `plans/<name>/steps/step-*.md` — absent only for all-inline runbooks
- plugin/skills/orchestrate/SKILL.md:71 — prompt: "Execute step from: plans/<name>/steps/<step-file>"
- plugin/skills/orchestrate/SKILL.md:98 — prompt: "Execute test spec from: plans/<name>/steps/<test-file>"
- plugin/skills/orchestrate/SKILL.md:126 — **Step file:** plans/<name>/steps/<test-file>
- plugin/skills/orchestrate/SKILL.md:138 — prompt: "Execute implementation from: plans/<name>/steps/<impl-file>"
- plugin/skills/runbook/references/tier3-planning-process.md:70 — - Inline phases use bullet items (no numbered steps/cycles)
- plugin/skills/review/references/review-axes.md:33 — - Extract all file paths referenced in steps/cycles
- plugin/agents/runbook-outline-corrector.md:124 — - Within each phase, steps/cycles must be ordered foundation-first: existence → structure → behavior → refinement
- plugin/agents/runbook-outline-corrector.md:136 — - Flag gaps >10 steps/cycles or >2 phases without a checkpoint
- plugin/agents/runbook-outline-corrector.md:188 — - **Complete:** Requirement maps to specific steps/cycles with clear notes
- plugin/agents/runbook-outline-corrector.md:403 — - All requirements traced to steps/cycles
- plugin/agents/runbook-outline-corrector.md:458 — - Every requirement must map to steps/cycles
- plugin/agents/corrector.md:294 — - Extract all file paths referenced in steps/cycles

## `tdd-workflow.md`

**Hit count: 1**

- plugin/README.md:65 — Pipeline reference in `docs/`: `general-workflow.md` and `tdd-workflow.md` for

## `general-workflow.md`

**Hit count: 2**

- plugin/docs/tdd-workflow.md:546 — - **docs/general-workflow.md**: General workflow documentation
- plugin/README.md:65 — Pipeline reference in `docs/`: `general-workflow.md` and `tdd-workflow.md` for

## `error-handling.md`

**Hit count: 4**

- docs/superpowers/design/plugin-transition-evaluation.md:195 — | `error-handling.md` | "Errors never pass silently — no `\|\| true`, no `2>/dev/null`" + "No sed escape" |
- docs/superpowers/design/plugin-transition-evaluation.md:229 — the deleted `_worktree` CLI); `error-handling.md:15`'s sed rationale (the rule
- docs/superpowers/design/plugin-transition-evaluation.md:316 — - `plugin/fragments/error-handling.md:11` — "In bash scripts using
- plugin/skills/runbook/references/tier3-expansion-process.md:258 — - **`references/error-handling.md`** — Error catalog, edge cases, recovery protocols

## `anti-patterns.md`

**Hit count: 1**

- plugin/skills/runbook/references/tier3-expansion-process.md:257 — - **`references/anti-patterns.md`** — Patterns to avoid with corrections

## `patterns.md`

**Hit count: 6**

- plugin/skills/design/SKILL.md:174 — | /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/references/tier3-expansion-process.md:128 — **Detailed guidance:** See `references/patterns.md` for TDD granularity criteria and numbering, `references/general-patt
- plugin/skills/runbook/references/tier3-expansion-process.md:255 — - **`references/patterns.md`** — TDD granularity criteria, numbering, common patterns
- plugin/skills/runbook/references/tier3-expansion-process.md:256 — - **`references/general-patterns.md`** — General-step granularity, prerequisite validation, step structure
- plugin/skills/runbook/references/tier3-expansion-process.md:257 — - **`references/anti-patterns.md`** — Patterns to avoid with corrections
- plugin/agents/scout.md:68 — plans/design-workflow-enhancement/reports/explore-agent-patterns.md

## `examples.md`

**Hit count: 9**

- docs/superpowers/design/plugin-transition-evaluation.md:295 — - **It ships a defect.** `SKILL.md:187` and `references/examples.md:68`:
- docs/superpowers/design/plugin-transition-evaluation.md:304 — in if condition") without retracting the broken example, and `examples.md:84-86`
- plugin/skills/review-plan/SKILL.md:76 — **Violation:** GREEN phase contains implementation code — prescribes exact code, agent becomes copier. See `references
- plugin/skills/review-plan/SKILL.md:95 — Hints for sequencing are acceptable; prescriptive code blocks are violations. See `references/review-examples.md` Sectio
- plugin/skills/review-plan/SKILL.md:107 — **Must have:** Specific test name, expected failure message, file location, why it will fail. See `references/review-exa
- plugin/skills/review-plan/SKILL.md:115 — Read `references/review-examples.md` Section 5 for indicator lists and correct prose patterns.
- plugin/skills/review-plan/SKILL.md:123 — Read `references/review-examples.md` Section 5.5 for acceptable vs unacceptable patterns.
- plugin/skills/review-plan/SKILL.md:221 — See `references/review-examples.md` Section 10.5 for good/bad examples of both.
- plugin/skills/runbook/references/tier3-expansion-process.md:259 — - **`references/examples.md`** — Complete runbook examples (TDD and general)

## `tdd-cycle-planning`

**Hit count: 3**

- plugin/skills/design/SKILL.md:173 — | /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/references/tier3-outline-process.md:21 — **TDD cycle planning:** When expanding TDD phases in Phase 1, Read `references/tdd-cycle-planning.md` for RED/GREEN spec
- plugin/skills/runbook/references/tier3-planning-process.md:289 — Read `references/tdd-cycle-planning.md` for cycle numbering, RED/GREEN specification formats, assertion quality requirem

## `general-patterns`

**Hit count: 3**

- plugin/skills/design/SKILL.md:174 — | /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
- plugin/skills/runbook/references/tier3-expansion-process.md:128 — **Detailed guidance:** See `references/patterns.md` for TDD granularity criteria and numbering, `references/general-patt
- plugin/skills/runbook/references/tier3-expansion-process.md:256 — - **`references/general-patterns.md`** — General-step granularity, prerequisite validation, step structure

## `conformance-validation`

**Hit count: 1**

- plugin/skills/runbook/references/tier3-outline-process.md:23 — **Conformance validation:** When design includes external references, Read `references/conformance-validation.md` for ma

## `3-5 cycles`

**Hit count: 1**

- docs/design.md:928 — files, Tier 2 6-15, Tier 3 >15 or >10 TDD cycles, and the "every 3-5 cycles"

## Design citations (D-XX, L-X outside docs/design.md)

---

## Directory Inventory

### Plugin Skills References

#### orchestrate/references/
- plugin/skills/orchestrate/references/common-scenarios.md (29 lines)
- plugin/skills/orchestrate/references/progress-tracking.md (40 lines)

#### orchestrate/scripts/
- plugin/skills/orchestrate/scripts/verify-red.sh (29 lines)
- plugin/skills/orchestrate/scripts/verify-step.sh (28 lines)

#### inline/references/
- plugin/skills/inline/references/review-dispatch-template.md (82 lines)

#### review-plan/references/
- plugin/skills/review-plan/references/report-template.md (68 lines)
- plugin/skills/review-plan/references/review-examples.md (114 lines)

---

## Justfile Recipes Referencing Pipeline Scripts

(no hits)

---

## Full `runbook` References (sample)

### tests/

Files mentioning 'runbook': 2

/Users/david/code/edify/tests/test_validate_runbook_reporting.py:1:"""Tests for validate-runbook.py report outcomes.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:16:from tests.fixtures.validate_runbook_fixtures import VALID_TDD
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:18:SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "validate-runbook.py"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:40:    spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:47:    tmp_path: Path, runbook: Path, *args: str
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:50:        [sys.executable, str(SCRIPT), *args, str(runbook)],
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:68:    """A TDD-only check on a general runbook reports NOT-APPLICABLE, not PASS.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:73:    runbook = tmp_path / "general.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:74:    runbook.write_text(GENERAL_RUNBOOK)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:76:    result = _run(tmp_path, runbook, subcommand)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:89:    """The same check on a TDD runbook reports a real outcome, never N/A.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:94:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:95:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:97:    _run(tmp_path, runbook, subcommand)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:105:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:106:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:108:    result = _run(tmp_path, runbook, "model-tags", "--skip-model-tags", "no venv")
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:119:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:120:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:123:        [sys.executable, str(SCRIPT), "model-tags", str(runbook), "--skip-model-tags"],
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:135:    """A non-cycle check applies to any runbook, so it never reports N/A."""
/Users/david/code/edify/tests/fixtures/validate_runbook_fixtures.py:1:"""Fixture constants for test_validate_runbook.py."""

### pyproject.toml

(no hits)

### README.md

41:- **Pipeline** — `/requirements` → `/design` → `/runbook` → `/orchestrate`

### CLAUDE.md

57:**Always edit source files, never generated output.** When a file is produced by a generator (prepare-runbook.py, skill expansion, template rendering), edit the source that produces it. Changes to generated files are overwritten on next generation.
178:- **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), with `review-plan` and `review` as the quality gates.
183:`plugin/bin/prepare-runbook.py` and `validate-runbook.py`. Pipeline docs are in
190:and the runbook system already supplies the flexibility they were built for.
---

## Justfile Recipes Referencing Pipeline Scripts

(no hits)

---

## Full `runbook` References (sample)

### tests/

Files mentioning 'runbook': 2

/Users/david/code/edify/tests/test_validate_runbook_reporting.py:1:"""Tests for validate-runbook.py report outcomes.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:16:from tests.fixtures.validate_runbook_fixtures import VALID_TDD
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:18:SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "validate-runbook.py"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:40:    spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:47:    tmp_path: Path, runbook: Path, *args: str
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:50:        [sys.executable, str(SCRIPT), *args, str(runbook)],
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:68:    """A TDD-only check on a general runbook reports NOT-APPLICABLE, not PASS.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:73:    runbook = tmp_path / "general.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:74:    runbook.write_text(GENERAL_RUNBOOK)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:76:    result = _run(tmp_path, runbook, subcommand)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:89:    """The same check on a TDD runbook reports a real outcome, never N/A.
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:94:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:95:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:97:    _run(tmp_path, runbook, subcommand)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:105:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:106:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:108:    result = _run(tmp_path, runbook, "model-tags", "--skip-model-tags", "no venv")
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:119:    runbook = tmp_path / "tdd.md"
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:120:    runbook.write_text(VALID_TDD)
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:123:        [sys.executable, str(SCRIPT), "model-tags", str(runbook), "--skip-model-tags"],
/Users/david/code/edify/tests/test_validate_runbook_reporting.py:135:    """A non-cycle check applies to any runbook, so it never reports N/A."""
/Users/david/code/edify/tests/fixtures/validate_runbook_fixtures.py:1:"""Fixture constants for test_validate_runbook.py."""

### pyproject.toml

(no hits)

### README.md

41:- **Pipeline** — `/requirements` → `/design` → `/runbook` → `/orchestrate`

### CLAUDE.md

57:**Always edit source files, never generated output.** When a file is produced by a generator (prepare-runbook.py, skill expansion, template rendering), edit the source that produces it. Changes to generated files are overwritten on next generation.
178:- **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), with `review-plan` and `review` as the quality gates.
183:`plugin/bin/prepare-runbook.py` and `validate-runbook.py`. Pipeline docs are in
190:and the runbook system already supplies the flexibility they were built for.

---

## Design citations (D-XX, L-X outside docs/design.md)

### D-34
**Files: 1**

### D-24
**Files: 3**

*(Full citation search requires extensive scanning; see files in plugin/agents/, plugin/skills/ for design references)*
