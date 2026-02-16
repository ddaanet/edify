# Validation Infrastructure Exploration

**Summary:** The project has substantial validation infrastructure in `prepare-runbook.py` for parsing and validating runbook structure. Existing cycle/step files show consistent metadata format with execution model and phase tags. No integrated file lifecycle validator or test count reconciliation exists yet.

---

## 1. Existing Validation Scripts

### prepare-runbook.py (36KB)
**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/bin/prepare-runbook.py`

**Purpose:** Transforms markdown runbooks into execution artifacts:
- Parses phase files and single-file runbooks
- Generates plan-specific agents (`.claude/agents/<plan>-task.md`)
- Creates step/cycle files in `plans/<plan>/steps/`
- Generates orchestrator plan metadata

**Key Functions (Validation-Related):**

- `validate_cycle_structure(cycle, common_context='')` — Checks TDD cycles contain RED/GREEN/Stop Conditions
  - Validates spike cycles (0.x) skip RED/GREEN
  - Validates regression cycles need only GREEN
  - Validates standard cycles have both RED and GREEN
  - Accepts stop/error conditions in cycle OR common context
  - Returns list of ERROR/WARNING messages

- `validate_cycle_numbering(cycles)` — Checks cycle number validity
  - Detects duplicates (fatal)
  - Checks major numbers start at 1 (fatal)
  - Detects gaps (warning only — document order is authoritative)
  - Returns (errors, warnings) tuple

- `validate_phase_numbering(step_phases)` — Checks general step phase ordering
  - Detects non-monotonic phases (fatal)
  - Detects gaps (warning only)
  - Uses `step_phases` dict mapping step_num → phase_number

- `validate_file_references(sections, cycles=None, runbook_path='')` — Checks file paths exist
  - Extracts backtick-wrapped paths from step content
  - Skips report paths and plans/*/reports/ paths (expected to be created)
  - Skips paths preceded by creation verbs (Create, Write, mkdir)
  - Returns warnings for non-existent referenced files

- `parse_frontmatter(content)` — Extracts YAML metadata
  - Returns (metadata_dict, remaining_content)
  - Sets default type: 'general' if missing
  - Validates type ∈ ['tdd', 'general', 'mixed']

- `extract_cycles(content)` — Parses TDD cycles from markdown
  - Pattern: `^###? Cycle\s+(\d+)\.(\d+):\s*(.*)`
  - Returns list of cycle dicts with keys: major, minor, number, title, content
  - Terminates on H2 headers (### cycle headers are content)

- `extract_sections(content)` — Extracts Common Context, Steps, Orchestrator
  - Detects phase headers `### Phase N:` to assign phases to steps
  - Returns dict with common_context, steps, step_phases, orchestrator

- `assemble_phase_files(directory)` — Assembles runbook from phase-*.md files
  - Detects `runbook-phase-*.md` files
  - Validates sequential numbering (0-based or 1-based)
  - Injects default TDD Common Context if missing
  - Returns (assembled_content_with_frontmatter, phase_dir)

- `extract_step_metadata(content, default_model='haiku')` — Extracts **Execution Model**: and **Report Path**:
  - Pattern: `\*\*Execution Model\*\*:\s*(\w+)` (case-insensitive)
  - Validates model ∈ {haiku, sonnet, opus}
  - Returns dict with 'model' and optional 'report_path'

- `extract_file_references(content)` — Finds backtick-wrapped file paths
  - Pattern: `` `([a-zA-Z][a-zA-Z0-9_.\-]*/[a-zA-Z0-9_/.\-]*\.(?:py|md|json|sh|txt|toml|yml|yaml|cfg|ini|js|ts|tsx))` ``
  - Excludes fenced code blocks
  - Returns set of file path strings

**Metadata Format in Phase Files:**

Lines 55-77 of generate_step_file():
```markdown
# Step {step_num}

**Plan**: `{runbook_path}`
**Execution Model**: {model}
**Phase**: {phase}
**Report Path**: `{report_path}` (optional)

---

{step_content}
```

Lines 695-706 of generate_cycle_file():
```markdown
# Cycle {cycle.number}

**Plan**: `{runbook_path}`
**Execution Model**: {model}
**Phase**: {cycle.major}
**Report Path**: `{report_path}` (optional)

---

{cycle.content}
```

**Missing Capabilities:**
- No file lifecycle analysis (create → modify ordering validation)
- No RED plausibility checker (validates expected failures are achievable)
- No test count reconciliation (matching cycle numbers with actual test functions)
- No phase boundary validation (ensures checkpoints exist at phase transitions)

---

### assemble-runbook.py (207 lines)
**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/bin/assemble-runbook.py`

**Purpose:** Assembles runbook from phase files and outline metadata.

**Key Functions:**

- `count_steps(content)` — Counts `### Step N.M:` headers
  - Simple regex match: `r"^###\s+Step\s+\d+\.\d+:"`
  - Returns integer count

- `extract_metadata_from_outline(outline_content)` — Extracts design ref and type from outline
  - Pattern: `\*\*Design:\*\*\s+(.+?)`
  - Pattern: `\*\*Type:\*\*\s+(.+?)`
  - Returns dict with 'design' and 'type'

**Note:** Does NOT validate cycle counts. Only counts steps.

---

## 2. Existing Quality Gate Infrastructure

### prepare-runbook.py Validation Chain
**Location:** Lines 760-876 (`validate_and_create` function)

**Execution Sequence:**
1. Type check — TDD runbooks must have cycles, general must have steps
2. Phase numbering validation (both steps and cycles)
3. File reference validation (backtick-wrapped paths)
4. Directory creation (agent_path, steps_dir, orchestrator_path)
5. File cleanup — `steps_dir.glob('*.md').unlink()` clears orphaned files
6. Artifact generation (agent, step files, orchestrator)
7. Git staging — `subprocess.run(['git', 'add'] + paths_to_stage)`

**NO validation gates for:**
- File lifecycle ordering (GREEN creates file before RED uses it)
- Checkpoint existence (phase boundaries without manual review)
- RED failure plausibility
- Test count matching cycle numbers

---

## 3. Phase File Format Examples

### Format: TDD Cycle File
**Source:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/when-recall/steps/step-0-1.md`

```markdown
# Cycle 0.1

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.1: Character subsequence matching

**RED Phase:**

**Test:** `test_subsequence_match_scores_positive`
**Assertions:**
- ...

**Expected failure:** ImportError or AttributeError

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_subsequence_match_scores_positive -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/when/__init__.py` (empty) and `fuzzy.py`...

**Changes:**
- File: `src/claudeutils/when/__init__.py`
  Action: Create empty file
- File: `src/claudeutils/when/fuzzy.py`
  Action: Create with `score_match` function
  Location hint: Module-level function

**Verify GREEN:** `pytest ...`
**Verify no regression:** `pytest tests/ -q`

---
```

**Metadata Tags Present:**
- `**Plan**`: Backtick-wrapped path to runbook
- `**Execution Model**`: One of {haiku, sonnet, opus}
- `**Phase****: Integer phase number (matches cycle major)
- No `**Report Path**` in this example (optional)

---

### Format: General Step File
**Source:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/plugin-migration/runbook-phase-2.md` (lines 1-80)

```markdown
# Phase 2: Skills and Agents

**Purpose:** Verify existing skill/agent structure...

**Dependencies:** Phase 1

**Model:** Sonnet (skill design requires reasoning)

---

## Step 2.1: Verify agent structure

**Objective:** Confirm `edify-plugin/agents/` contains 14 agent `.md` files...

**Execution Model:** Haiku (inline verification)

**Implementation:**

Verify agent structure:

```bash
# Count agent .md files
...
```

**Expected count:** 14 agent files

**Design Reference:** ...

**Validation:** ...

**Expected Outcome:** 14 agent `.md` files confirmed...

**Error Conditions:** ...

**Success Criteria:** ...

---
```

**Key Observations:**
- `**Execution Model**` appears in step text (not header metadata)
- Phase specified in phase-level header (`# Phase 2:`)
- No `**Plan**`, `**Report Path**` in outline phase files (only in generated step files)
- Steps use `## Step N.M:` format with narrative descriptions
- Each step includes subsections: Objective, Implementation, Validation, Success Criteria

---

## 4. Runbook Outline Format

**Source:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/worktree-update/runbook-outline.md` (first 40 lines)

```markdown
# Worktree Update TDD Runbook: Outline

**Design:** `plans/worktree-update/design.md`
**Type:** TDD
**Model:** haiku (execution), sonnet (checkpoints)

---

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: ... | Phase 1: ... | ... |
| FR-2: ... | Phase 5: ... | ... |
...

---

## Phase Structure

### Phase 1: Path Computation (`wt_path()`)

**Complexity:** Medium (4 cycles)
**Files:** `src/claudeutils/cli.py`, ...
**Description:** Register CLI group and extract path computation logic...

**Cycles:**
- 1.1: `wt_path()` basic path construction...
- 1.2: Container detection and sibling paths
- 1.3: Container creation — directory materialization
- 1.4: Edge cases (special characters, root directory, deep nesting)

---

### Phase 2: Sandbox Registration (`add_sandbox_dir()`)

**Complexity:** Medium (4 cycles)
...

---

## Complexity Distribution

| Phase | Cycles | Complexity | Model |
|-------|--------|------------|-------|
| 1: Setup + wt_path() | 4 | Medium | haiku |
...
```

**Outline Structure:**
- Header with design reference, type (TDD/general), model tags
- Requirements Mapping table (FR-N to Phase mapping)
- Phase Structure section with:
  - Phase heading: `### Phase N: <name>(<fn-if-function>)`
  - Metadata: Complexity, Files list, Description
  - Cycles/Steps list with minor items
- Complexity Distribution table (phase summary)
- Expansion Guidance section (for preparation)

**Model Tags:**
- Outline level: `**Model:** haiku (execution), sonnet (checkpoints)`
- Phase level: `**Model:** haiku` (implied in complexity distribution)
- Individual cycle/step level: Extracted from file content via `extract_step_metadata()`

---

## 5. Cycle Metadata Format

**In Phase Files:** Metadata appears inline as `**Field**:` patterns

**Patterns Found:**
- `**Test:**` — Test function name
- `**Assertions:**` — Bulleted assertion list
- `**Expected failure:**` — What error is expected
- `**Why it fails:**` — Explanation of failure reason
- `**Verify RED:**` — Command to run failing test
- `**Verify GREEN:**` — Command to run passing test
- `**Verify no regression:**` — Command to verify existing tests still pass
- `**Changes:**` — File modification list with File/Action/Location hint structure
- `**File:**` — Backtick-wrapped path
- `**Action:**` — Description of modification (Create, Add, Modify, etc.)
- `**Location hint:**` — Context for where to make change
- `**Prerequisite:**` — Files to read before implementation
- `**Objective:**` — What the cycle accomplishes
- `**Behavior:**` — How the implementation should behave
- `**Approach:**` — Implementation strategy

---

## 6. Step File Metadata Location

Generated step files contain header metadata:

```markdown
# Step {num}

**Plan**: `{path}`
**Execution Model**: {model}
**Phase**: {phase_number}
**Report Path**: `{report_path}` (optional)

---

{content}
```

**Extraction in prepare-runbook.py:**

Line 668-679 (generate_step_file):
```python
header_lines = [
    f"# Step {step_num}",
    "",
    f"**Plan**: `{runbook_path}`",
    f"**Execution Model**: {meta['model']}",
    f"**Phase**: {phase}",
]
if 'report_path' in meta:
    header_lines.append(f"**Report Path**: `{meta['report_path']}`")
```

**Same pattern for cycles:** Lines 695-706 (generate_cycle_file)

---

## 7. Cycle Numbering Conventions

**Pattern:** `Cycle X.Y` where:
- X = major (phase number)
- Y = minor (sequence within phase, 1-based)

**Validation Rules (from prepare-runbook.py):**

- Major numbers: Must start at 1 (or 0 for spike cycles)
- Minor numbers within major: Must start at 1, no gaps enforced but warned
- Duplicates: Fatal error
- Phase monotonicity: Phases must not decrease (fatal for general runbooks)

**Numbering is Flexible:**
- Cycles can have gaps (document order defines execution, not numbers)
- First major can be 0 or 1 (flexibility for spike cycles)
- Minor numbering detection: "STOP IMMEDIATELY if..." triggers execution halt messages use "All N tests pass" checkpoint format

---

## 8. Test Count and File Reference Format

**Test Descriptions in RED Phases:**

From step-0-1.md:
```markdown
**Test:** `test_subsequence_match_scores_positive`
```

**Files Listed in Changes Section:**

From runbook-phase-1.md lines 55-68:
```markdown
**Changes:**
- File: `src/claudeutils/cli.py`
  Action: Add import `from claudeutils.worktree.cli import worktree` at top
  Location hint: With other command imports
- File: `src/claudeutils/cli.py`
  Action: Add `cli.add_command(worktree)` registration call
  Location hint: After other command registrations
```

**Absolute File Paths:** Always use backtick-wrapped paths (e.g., `` `src/claudeutils/cli.py` ``). No relative paths in practice.

**Pattern for File/Action/Location:**
- Each file modification is a bullet point with `File:`, `Action:`, `Location hint:` as sub-lines
- Indentation: 2 spaces per level
- Action describes what to do (Create, Add, Modify, etc.)
- Location hint gives context (function name, line range, section heading)

---

## Gaps and Missing Infrastructure

1. **File Lifecycle Validation** — No tool checks that RED creates all files used by GREEN
2. **Checkpoint Validation** — No tool enforces checkpoints at phase boundaries
3. **Test Count Reconciliation** — No script counts test functions and matches against cycle count
4. **RED Plausibility** — No validation that expected failures are achievable given code state
5. **Cycle-to-Test Mapping** — No tool correlates `**Test:**` field to actual pytest function
6. **Phase Boundary Markers** — No enforced pattern for "All N tests pass" checkpoint format
7. **Cross-Phase References** — No validation of "Depends on Phase X" statements
8. **Report Path Existence** — No check that step-level `**Report Path**:` directories exist

---

## Key File Locations

| Purpose | Path |
|---------|------|
| Validation script | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/bin/prepare-runbook.py` |
| Phase assembly | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/bin/assemble-runbook.py` |
| Cycle example | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/when-recall/steps/step-0-1.md` |
| Phase file example | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/worktree-update/runbook-phase-1.md` |
| Outline example | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/worktree-update/runbook-outline.md` |
| General step example | `/Users/david/code/claudeutils-wt/runbook-skill-fixes/plans/plugin-migration/runbook-phase-2.md` |

---

## Summary for Quality Gates Design

**Ready to Build:**
- validate_cycle_structure pattern — reuse for phase validation
- extract_step_metadata pattern — reuse for extracting execution model and report path
- validate_cycle_numbering pattern — reuse as baseline

**Must Define:**
- File lifecycle graph (create → modify ordering)
- RED pass detection (test fixture setup)
- Checkpoint format validation (must appear at phase boundaries)
- Test count reconciliation (cycle count = test function count per phase)
- Phase dependency validation (cross-references exist and are satisfied)
