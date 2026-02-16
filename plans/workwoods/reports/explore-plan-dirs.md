# Plan Directory Structure and Artifact Progression

## Summary

Plan directories in `plans/` follow a consistent progression from requirements through design, outline, phase files, and vet reports. Plan state is inferred from filesystem artifacts: requirements.md signals requirements status, outline.md signals designed, phase files signal planned status, and vet reports in `reports/` validate each stage. The `prepare-runbook.py` script orchestrates the transformation from runbook markdown into execution artifacts (steps, orchestrator plan, and plan-specific agents). Jobs.md manually tracks plan status but FR-3 (workwoods) aims to replace it with filesystem inference.

## Key Findings

### 1. Plan Directory Listing and Artifact Inventory

#### Status: Requirements Only
- **continuation-prepend** (status: requirements)
  - `problem.md` — Problem statement only

#### Status: Requirements + Exploration
- **error-handling** (status: requirements)
  - Outline complete per jobs.md notes but not in listing yet

- **feature-requests** (status: requirements)
  - GH issue research (artifact files not yet created)

- **workwoods** (status: requirements)
  - `requirements.md` — Full FR/NFR/constraints for cross-tree worktree awareness

- **remember-skill-update** (status: requirements)
  - `requirements.md` — Phase-structure requirements
  - `outline.md` — Design outline present

- **tweakcc** (status: requirements)
  - Local instances research (artifact files not yet created)

- **prototypes** (status: requirements)
  - Session extraction feature gap research (artifact files not yet created)

#### Status: Designed
- **orchestrate-evolution** (status: designed)
  - `requirements.md` — Full functional and non-functional requirements
  - `outline.md` — Design outline
  - `design.md` — Comprehensive architecture and design decisions (75+ lines)
  - `orchestrate-evolution-analysis.md` — Gap analysis document
  - `reports/` contains 7 artifacts:
    - `design-review.md` — Opus design vet report
    - `outline-review.md`, `outline-review-2.md`, `outline-review-3.md`, `outline-review-4.md` — Iterative outline reviews
    - `explore-orchestration-infra.md` — Research report
    - `red-pass-blast-radius.md` — Risk analysis report

#### Status: Planned (Runbook Assembled)
- **plugin-migration** (status: planned)
  - `requirements.md` — Functional requirements with FRs and NFRs
  - `outline.md` — Design outline
  - `design.md` — Full design document
  - `runbook.md` — Main runbook file with metadata (name, model, status)
  - `runbook-outline.md` — Outline of runbook structure
  - `runbook-phase-0.md`, `runbook-phase-1.md`, ..., `runbook-phase-6.md` — 7 phase files
  - `orchestrator-plan.md` — Orchestrator execution instructions
  - `steps/` directory contains 37 step files:
    - `step-0-1.md`, `step-1-1.md`, `step-2-1.md` through `step-2-4.md`, `step-3-1.md` through `step-3-3.md`, `step-4-1.md`, `step-4-2.md`, `step-5-1.md`, `step-5-2.md`, `step-5-3.md`, `step-6-1.md`
  - `reports/` contains 19 artifacts:
    - Design review: `design-review.md`
    - Outline reviews: `outline-review.md`, `outline-review-2.md`
    - Runbook reviews: `runbook-review.md`, `runbook-outline-review.md`
    - Phase reviews: `phase-0-review.md` through `phase-6-review.md` (7 reviews)
    - Exploration reports: `explore-hooks.md`, `explore-justfiles.md`, `explore-structure.md`, `naming-research.md`

#### Status: Designed (Pre-Execution)
- **worktree-merge-data-loss** (status: planned, runbook outline phase)
  - `requirements.md` — Implicit in design
  - `outline.md` — Design outline
  - `design.md` — Architecture and implementation design
  - `runbook-outline.md` — Runbook structure outline
  - `reports/` contains 8 artifacts:
    - Design review: `design-review.md`
    - Outline review: `outline-review.md`
    - Runbook outline reviews: `runbook-outline-review.md`, `runbook-outline-review-opus.md`
    - Exploration reports: `explore-git-history.md`, `explore-merge-logic.md`

#### Complete Plans (Archived)
- **when-recall** (status: complete)
  - `/when` memory recall system — merged to main, 2 deliverable reviews conducted

- **worktree-update** (status: complete)
  - 40 TDD cycles, recovery phases (C2-C5), merged to main

- **worktree-skill** (status: complete)
  - Design.md retained on disk for reference

### 2. Artifact Progression: State Inference from Filesystem

The plan state progression is inferred from what artifacts exist in the directory:

```
File Existence → Implied State → Next Action

No artifacts → requirements → Read requirements.md, create outline

requirements.md exists → requirements → Design → Create outline.md

outline.md exists → designed → Review outline → Create design.md

design.md exists + outline valid → designed → Plan execution → Create runbook.md

runbook.md (single file) exists → designed, design-phase → Expand to phases → Create runbook-phase-*.md files

runbook-phase-*.md files exist → planned → Prepare execution → Create steps/ + orchestrator-plan.md

steps/*.md exist + orchestrator-plan.md exists → planned, ready → Execute → Create reports/phase-*-review.md during vet

reports/phase-*-review.md exist + mtime > step mtime → vetted, valid → Merge to main
```

### 3. Vet Reports: Structure and Location

Vet reports live in `plans/<plan-name>/reports/` and follow naming conventions:

**Design-level vet reports:**
- `design-review.md` — Opus design vet, validates design against requirements
- Format: Design source, review date, reviewer, summary, issues found, fixes applied, traceability table

**Outline-level vet reports:**
- `outline-review.md`, `outline-review-2.md`, `outline-review-3.md`, `outline-review-4.md` — Iterative reviews
- Pattern: Multiple rounds suggest iterative improvement and re-vet cycles

**Runbook-level vet reports:**
- `runbook-review.md` — General runbook vet
- `runbook-outline-review.md`, `runbook-outline-review-opus.md` — Runbook outline reviews (may indicate sonnet → opus escalation)

**Phase-level vet reports:**
- `phase-0-review.md`, `phase-1-review.md`, ..., `phase-N-review.md` — Per-phase vet after execution
- Generated during orchestration after each phase completes
- Vet report path embedded in step files via `**Report Path**` metadata

**Exploration reports (research artifacts):**
- `explore-*.md` — Discovery and research reports (e.g., `explore-orchestration-infra.md`, `explore-hooks.md`, `explore-git-history.md`)
- These are created during planning phases to document research findings
- Part of the design research process

**Analysis and methodology reports (shared in plans/reports/):**
- `task-prioritization-methodology.md`
- `ground-skill-research-synthesis.md`
- `deliverable-review-prioritize.md`
- `prioritization-2026-02-16.md`
- These are cross-plan research artifacts in the shared reports directory

### 4. Phase Files: Naming and Structure

Phase files use the pattern `runbook-phase-<N>.md` where N is 0-based or 1-based (sequential):

**plugin-migration example:**
- `runbook-phase-0.md` — Phase 0: Directory Rename
- `runbook-phase-1.md` — Phase 1: [Content not read but follows pattern]
- `runbook-phase-2.md` — Phase 2
- `runbook-phase-3.md` — Phase 3
- `runbook-phase-4.md` — Phase 4
- `runbook-phase-5.md` — Phase 5
- `runbook-phase-6.md` — Phase 6

**Content structure (from plugin-migration phase 0):**
- Purpose and dependencies stated upfront
- Execution model specified (haiku, sonnet, opus)
- Estimated complexity noted
- Sub-steps numbered (0.1, 0.2, etc.) with objectives and detailed implementation steps
- Bash commands inline for direct execution or as reference

**worktree-merge-data-loss example:**
- `runbook-phase-*.md` files NOT yet created (runbook-outline.md exists, indicating outline phase not expanded)
- Next action: expand outline into phase files

### 5. prepare-runbook.py: Plan Directory Inspector and Artifact Generator

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/bin/prepare-runbook.py`

**Function:** Transforms runbook markdown into execution artifacts. Inspects plan directories to derive:
- Runbook name (from directory name: `plans/foo/` → `foo`)
- Input paths: runbook file or phase-grouped directory
- Output paths: `.claude/agents/<runbook-name>-task.md`, `plans/<runbook-name>/steps/`, `plans/<runbook-name>/orchestrator-plan.md`

**Key inspection logic:**

1. **Frontmatter parsing:** Extracts metadata (type: tdd/general/mixed, model: haiku/sonnet/opus, name)

2. **Phase file detection and assembly:** When given a directory (not a file):
   - Globs for `runbook-phase-*.md` files
   - Extracts phase numbers from filenames
   - Validates sequential numbering (accepts 0-based or 1-based, detects gaps)
   - Concatenates phase files into assembled content
   - Validates each phase file is non-empty
   - Detects runbook type from first phase file (looks for `## Cycle` (TDD) or `## Step` (general) headers)

3. **Cycle extraction (TDD runbooks):** Parses `## Cycle X.Y:` headers to extract:
   - Major and minor cycle numbers
   - Cycle title
   - Full cycle content

4. **Step extraction (general runbooks):** Parses `## Step N.N:` headers to extract:
   - Step numbers
   - Step content
   - Phase assignment (from preceding `## Phase N:` headers)

5. **File reference validation:** Extracts backtick-wrapped file paths from steps and validates existence:
   - Skips runbook itself, report paths, and paths under `plans/*/reports/`
   - Skips paths preceded by creation verbs (Create, Write, mkdir)
   - Warns on non-existent references

6. **Step metadata extraction:** Looks for `**Execution Model**: <model>` and `**Report Path**: <path>` fields within step content

7. **Step numbering validation:** Validates monotonic phase numbers (phases must not decrease)

8. **Cycle structure validation:** For TDD, validates mandatory sections:
   - RED phase (unless spike cycle with `## Cycle 0.x` or regression cycle `[regression]`)
   - GREEN phase (all cycles)
   - Stop/Error Conditions (in cycle or Common Context)
   - Dependencies section (warning only)

**Outputs generated:**

1. **Plan-specific agent:** `.claude/agents/<runbook-name>-task.md`
   - Inherits baseline (quiet-task.md for general, tdd-task.md for TDD)
   - Frontmatter: name, description, model, color, tools
   - Embeds Common Context from runbook
   - Adds "Clean tree requirement" footer (commit before reporting success)
   - Cached via prompt prefix matching

2. **Step files:** `plans/<runbook-name>/steps/step-*.md`
   - Naming: `step-N-N.md` for general, `step-X-Y.md` for cycles (Cycle X.Y)
   - Header includes: Plan reference, Execution Model, Phase number, Report Path (if specified)
   - Content: Full step body without duplication of common context
   - Execution agents read step file + plan-specific agent context from cache

3. **Orchestrator plan:** `plans/<runbook-name>/orchestrator-plan.md`
   - Lists all steps in execution order
   - Marks phase boundaries with `PHASE_BOUNDARY` notation
   - Instructs orchestrator to review between phases
   - Default orchestrator: "Execute steps sequentially, stop on error, escalate to sonnet"
   - Custom orchestrator: reads from `## Orchestrator Instructions` section in runbook

### 6. Relationship: Plan Directories ↔ jobs.md

**jobs.md structure:**
- Status values: `requirements` → `designed` → `planned` → `complete`
- Columns: Plan, Status, Notes
- Notes: Free-form status details (e.g., "Design.md complete, vet in progress")

**Correspondence:**

| jobs.md Status | Artifacts | Implied Next Action |
|---|---|---|
| `requirements` | requirements.md only | Create outline → design |
| `designed` | requirements.md, outline.md, design.md | Create runbook → planning |
| `planned` | runbook.md + phase files + steps/ + orchestrator-plan.md | Execute via /orchestrate |
| `complete` | Final vet reports, merged to main | Archived (deleted from plans/, referenced via git history) |

**Current limitation (addressed by workwoods FR-3):**
Jobs.md is manually updated by handoff skill. Status inference from filesystem would:
- Detect outline.md → designed
- Detect phase files → planned
- Detect vet reports with valid timestamps → vetted
- Eliminate manual tracking overhead
- Provide real-time status visible to all worktrees

### 7. Sample Plan Directories: Full Artifact Listing

#### Plugin Migration (16 steps, planned status)

```
plans/plugin-migration/
├── design.md                          [Design document, 150+ lines]
├── orchestrator-plan.md               [Execution instructions]
├── outline.md                         [Design outline]
├── requirements.md                    [FR/NFR/constraints]
├── runbook.md                         [Main runbook with metadata]
├── runbook-outline.md                 [Runbook structure outline]
├── runbook-phase-0.md                 [Phase 0: Directory Rename]
├── runbook-phase-1.md                 [Phase 1]
├── runbook-phase-2.md                 [Phase 2]
├── runbook-phase-3.md                 [Phase 3]
├── runbook-phase-4.md                 [Phase 4]
├── runbook-phase-5.md                 [Phase 5]
├── runbook-phase-6.md                 [Phase 6]
├── runbook-phases-4-5-6.md            [Consolidated phases]
├── steps/
│   ├── step-0-1.md                    [Step file with header]
│   ├── step-1-1.md
│   ├── step-2-1.md through step-2-4.md
│   ├── step-3-1.md through step-3-3.md
│   ├── step-4-1.md, step-4-2.md
│   ├── step-5-1.md, step-5-2.md, step-5-3.md
│   └── step-6-1.md
└── reports/
    ├── design-review.md               [Opus design vet]
    ├── explore-hooks.md               [Research report]
    ├── explore-justfiles.md           [Research report]
    ├── explore-structure.md           [Research report]
    ├── naming-research.md             [Research report]
    ├── outline-review.md              [Outline vet]
    ├── outline-review-2.md            [Iterative review]
    ├── phase-0-review.md through phase-6-review.md  [7 phase vets]
    ├── runbook-outline-review.md      [Runbook outline vet]
    └── runbook-review.md              [Runbook vet]
```

#### Orchestrate Evolution (designed status)

```
plans/orchestrate-evolution/
├── design.md                          [Architecture document]
├── orchestrate-evolution-analysis.md  [Gap analysis]
├── outline.md                         [Design outline]
├── requirements.md                    [FR/NFR/constraints]
└── reports/
    ├── design-review.md               [Opus design vet]
    ├── explore-orchestration-infra.md [Research report]
    ├── outline-review.md              [Outline vet]
    ├── outline-review-2.md            [Iterative review]
    ├── outline-review-3.md            [Iterative review]
    ├── outline-review-4.md            [Iterative review]
    └── red-pass-blast-radius.md       [Risk analysis]
```

#### Worktree Merge Data Loss (planned status, runbook outline phase)

```
plans/worktree-merge-data-loss/
├── design.md                          [Design document]
├── outline.md                         [Design outline]
├── runbook-outline.md                 [Runbook structure outline]
└── reports/
    ├── design-review.md               [Opus design vet]
    ├── explore-git-history.md         [Research report]
    ├── explore-merge-logic.md         [Research report]
    ├── outline-review.md              [Outline vet]
    ├── runbook-outline-review.md      [Runbook outline vet]
    └── runbook-outline-review-opus.md [Opus escalation review]
```

#### Workwoods (requirements status)

```
plans/workwoods/
└── requirements.md                    [FR-1 through FR-6, NFR-1 through NFR-3, constraints, open questions]
```

#### Continuation Prepend (requirements status)

```
plans/continuation-prepend/
└── problem.md                         [Problem statement only, no outline yet]
```

## Patterns

1. **Progressive artifact accumulation:** Each status level adds specific artifacts. Requirements-only plans may skip design/outline if problem statement is sufficient. Designed plans stop at design.md. Planned plans expand to phases and steps.

2. **Vet reports as validity checkpoints:** Each artifact type (design, outline, runbook, phases) has corresponding vet reports in `reports/`. Vet report mtime compared against source artifact mtime determines staleness (workwoods FR-2).

3. **Phase files enable large runbooks:** Large runbooks (plugin-migration: 7 phases, 16 steps) split into phase files before prepare-runbook.py assembles them. This avoids single monolithic files and enables parallel review of phases.

4. **Step file headers provide execution metadata:** Every step file includes a header with:
   - Plan reference (backtick-wrapped path to runbook)
   - Execution Model (haiku/sonnet/opus)
   - Phase number (for coordination across phases)
   - Report Path (where vet reports go)

5. **Orchestrator plan is stateless:** Orchestrator instructions are static (not updated during execution). Step files and vet reports provide the execution history. This enables idempotent re-orchestration of same runbook.

6. **Common Context is not duplicated:** Runbook's "Common Context" section is embedded in plan-specific agent definition, not repeated in every step. Reduces step file size and enables context caching.

7. **Research reports are first-class artifacts:** Exploration reports (`explore-*.md`) are created during planning phases and retained in reports/ as part of design documentation. They explain the reasoning behind design decisions.

8. **Jobs.md mtime indicates update recency:** Status values in jobs.md are manually updated, but timestamps show when status last changed. Workwoods FR-3 would eliminate this by inferring status from filesystem artifacts.

## Gaps and Open Questions

1. **Phase file consolidation:** Some plans have both `runbook-phase-*.md` files AND a consolidated file like `runbook-phases-4-5-6.md`. Purpose unclear — may be artifact of iterative expansion.

2. **Vet report escalation naming:** Some plans have both `*-review.md` and `*-review-opus.md` (e.g., `runbook-outline-review.md` and `runbook-outline-review-opus.md` in worktree-merge-data-loss). Pattern suggests sonnet → opus escalation, but naming convention not documented.

3. **Cycle numbering in step files:** TDD step files use `step-X-Y.md` naming (Cycle X.Y), but tests/assertions references (RED phase) may use different cycle notation. Consistency with test frameworks unclear.

4. **Report path discovery:** Step files embed Report Path metadata, but prepare-runbook.py doesn't validate that report paths are under `plans/*/reports/`. Validation happens during vet delegation, not during step file generation.

5. **Shared reports directory:** `plans/reports/` contains cross-plan research and methodology documents. Rules for when to place reports in shared vs plan-specific directories not formally documented (convention appears to be: cross-plan → shared, plan-specific → plans/*/reports/).

6. **Empty phase file handling:** prepare-runbook.py validates that phase files are non-empty and have Step/Cycle headers, but doesn't validate that phase content follows the runbook type (e.g., general phase files may reference cycles by mistake).

## Recommendations for workwoods Implementation

1. **Artifact existence checks for state inference (FR-3):**
   - `requires(requirements.md)` — state = requirements
   - `requires(outline.md)` — state = designed
   - `requires(runbook-phase-*.md | runbook.md)` — state = planned
   - `requires(steps/*.md)` — state = planned, ready to execute
   - Use Glob to scan each directory

2. **Vet staleness detection (FR-2):**
   - Read mtime of source artifact (outline.md, runbook.md, runbook-phase-*.md)
   - Read mtime of vet report (outline-review.md, phase-N-review.md)
   - `vet_is_stale = source_mtime > report_mtime`
   - Use bash `stat` or Python `Path.stat().st_mtime`

3. **Commit counting (FR-1):**
   - Use `git log -1 --format=%H -- agents/session.md` to get last handoff commit hash
   - Use `git log <hash>..HEAD --oneline` to count commits since last handoff
   - Provides stable anchor across checkout/touch operations

4. **Plan directory scanning (FR-3):**
   - Glob `plans/*/` to find all plan directories
   - Exclude `plans/reports/` (shared reports, not a plan)
   - For each plan: check artifact presence, infer status, compute next action
   - Assemble status display by aggregating across all trees

5. **Next action inference:**
   - requirements only → "Create outline" (command: `/design plans/<name>/requirements.md`)
   - outline exists → "Create design" (command: `/design plans/<name>/outline.md`)
   - design exists → "Create runbook" (command: `/runbook plans/<name>/design.md`)
   - phase files exist → "Execute runbook" (command: `/orchestrate plans/<name>/orchestrator-plan.md`)

