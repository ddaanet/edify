### Phase 2: Vet Staleness Detection (type: tdd)

**Purpose:** Implement vet staleness detection via mtime comparison using established naming conventions.

**Scope:**
- `src/claudeutils/planstate/vet.py` - Vet status detection
- `tests/test_planstate_vet.py` - Test coverage with mtime manipulation

**Dependencies:** Phase 1 (planstate module must exist for integration)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Medium (mtime logic + naming convention handling)

**Weak Orchestrator Metadata:**
- Model: sonnet
- Total Cycles: 5
- Restart required: No

---

## Cycle 2.1: Source→report mapping for all convention types (parametrized)

**Prerequisite:** Read design Vet Chain Conventions table for standard naming patterns.

**RED Phase:**

**Test:** `test_source_report_mapping_conventions`
**Assertions (parametrized):**
- outline.md → reports/outline-review.md mapping detected
- design.md → reports/design-review.md mapping detected
- runbook-outline.md → reports/runbook-outline-review.md mapping detected
- runbook-phase-1.md → reports/phase-1-review.md mapping detected

**Expected failure:** ImportError or NameError (vet module doesn't exist)

**Why it fails:** No vet.py module or get_vet_status() function

**Verify RED:** `pytest tests/test_planstate_vet.py::test_source_report_mapping_conventions -v`

**GREEN Phase:**

**Implementation:** Create vet.py with get_vet_status() that scans source artifacts and maps to report paths

**Behavior:**
- Scan plan_dir for recognized source artifacts (outline.md, design.md, etc.)
- For each source, derive expected report path via naming convention
- Check if report exists at expected path
- Create VetChain for each source→report pair

**Approach:** Mapping table (dict) from source filename to report filename pattern

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Create module with get_vet_status(plan_dir: Path) -> VetStatus
  Location hint: New file

- File: `src/claudeutils/planstate/models.py`
  Action: Define VetStatus and VetChain dataclasses (if not already in Phase 1)
  Location hint: After PlanState definition

- File: `tests/test_planstate_vet.py`
  Action: Create parametrized test with tmp_path, test all four standard mappings
  Location hint: New file, use @pytest.mark.parametrize

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_source_report_mapping_conventions -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---

## Cycle 2.2: Phase-level fallback glob (runbook-phase-N naming variants)

**RED Phase:**

**Test:** `test_phase_level_fallback_glob`
**Assertions:**
- runbook-phase-3.md → reports/phase-3-review.md found (primary pattern)
- runbook-phase-3.md → reports/checkpoint-3-vet.md found (fallback pattern)
- runbook-phase-3.md → reports/phase-3-review-opus.md found (escalation variant)
- Most recent report wins when multiple patterns match (highest mtime)

**Expected failure:** Only primary pattern works, fallback glob not implemented

**Why it fails:** Hardcoded report paths don't handle naming variance

**Verify RED:** `pytest tests/test_planstate_vet.py::test_phase_level_fallback_glob -v`

**GREEN Phase:**

**Implementation:** Glob for phase-level reports when primary pattern not found

**Behavior:**
- Try primary pattern first: reports/phase-N-review.md
- If not found, glob: reports/*N*{review,vet}*.md for phase number N
- Parse filenames to extract phase number, filter matches
- If multiple matches, use highest mtime

**Approach:** Extract phase number from runbook-phase-N.md, glob with number in pattern

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add fallback glob logic for phase-level reports in get_vet_status()
  Location hint: In source→report mapping, after primary pattern check fails

- File: `tests/test_planstate_vet.py`
  Action: Create test with multiple report naming variants (phase-3-review, checkpoint-3-vet, phase-3-review-opus)
  Location hint: New test function, use os.utime() to set different mtimes

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_phase_level_fallback_glob -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---

## Cycle 2.3: Mtime comparison (stale = source_mtime > report_mtime)

**RED Phase:**

**Test:** `test_mtime_comparison_staleness`
**Assertions:**
- VetChain.stale == False when report_mtime > source_mtime (fresh)
- VetChain.stale == True when source_mtime > report_mtime (stale)
- VetChain.source_mtime matches expected mtime from test setup
- VetChain.report_mtime matches expected mtime from test setup

**Expected failure:** stale field always False or not computed correctly

**Why it fails:** Mtime comparison logic not implemented

**Verify RED:** `pytest tests/test_planstate_vet.py::test_mtime_comparison_staleness -v`

**GREEN Phase:**

**Implementation:** Use Path.stat().st_mtime to get filesystem mtimes and compare

**Behavior:**
- Get source_mtime via `source_path.stat().st_mtime`
- Get report_mtime via `report_path.stat().st_mtime` (if report exists)
- Compute stale as `source_mtime > report_mtime`
- Store both mtimes in VetChain

**Approach:** Path.stat() returns stat_result with st_mtime attribute (float, Unix timestamp)

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add mtime extraction and comparison in VetChain creation
  Location hint: When constructing VetChain objects in get_vet_status()

- File: `tests/test_planstate_vet.py`
  Action: Create test using os.utime() to set known mtimes (source newer and source older)
  Location hint: New test function, set mtimes explicitly before calling get_vet_status()

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_mtime_comparison_staleness -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---

## Cycle 2.4: Missing report handling (report_mtime = None → stale = True)

**RED Phase:**

**Test:** `test_missing_report_treated_as_stale`
**Assertions:**
- VetChain.stale == True when report file doesn't exist
- VetChain.report == None when report doesn't exist
- VetChain.report_mtime == None when report doesn't exist
- VetStatus.any_stale == True when any chain has stale=True

**Expected failure:** Exception or wrong stale value when report missing

**Why it fails:** Code assumes report exists, doesn't handle missing case

**Verify RED:** `pytest tests/test_planstate_vet.py::test_missing_report_treated_as_stale -v`

**GREEN Phase:**

**Implementation:** Check if report exists before getting mtime, treat missing as stale

**Behavior:**
- If report path doesn't exist: report=None, report_mtime=None, stale=True
- If report exists: get mtime normally, compare with source
- any_stale computed as: any(chain.stale for chain in chains)

**Approach:** Use Path.exists() before Path.stat()

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add existence check before mtime extraction, handle None case
  Location hint: In VetChain creation, before report_mtime extraction

- File: `src/claudeutils/planstate/models.py`
  Action: Add any_stale: bool convenience field to VetStatus
  Location hint: VetStatus dataclass

- File: `tests/test_planstate_vet.py`
  Action: Create test with source artifact but no report file
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_missing_report_treated_as_stale -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---

## Cycle 2.5: Iterative review handling (highest-numbered or highest-mtime wins)

**RED Phase:**

**Test:** `test_iterative_review_highest_wins`
**Assertions:**
- outline.md with reports/outline-review.md and reports/outline-review-3.md → outline-review-3.md used (highest number)
- If no numbers: use highest mtime among matching reports
- Escalation variants (*-opus.md) treated as additional reviews, highest mtime among all variants wins
- VetChain.report contains the winning report filename

**Expected failure:** Uses first report found or alphabetically first, not highest numbered or newest

**Why it fails:** No logic to compare review iteration numbers or mtimes

**Verify RED:** `pytest tests/test_planstate_vet.py::test_iterative_review_highest_wins -v`

**GREEN Phase:**

**Implementation:** Extract iteration numbers from filenames, use highest; fallback to mtime comparison

**Behavior:**
- Glob for all matching reports (e.g., reports/outline-review*.md)
- Extract iteration number from filename (outline-review-3.md → 3)
- If numbers found: use highest number
- If no numbers or tie: use highest mtime
- Escalation variants included in glob results

**Approach:** Regex to extract numbers, sort by (number, mtime) tuple

**Changes:**
- File: `src/claudeutils/planstate/vet.py`
  Action: Add report selection logic (glob, number extraction, mtime comparison)
  Location hint: In source→report mapping, after finding report candidates

- File: `tests/test_planstate_vet.py`
  Action: Create test with multiple review files (outline-review.md, outline-review-2.md, outline-review-3.md, outline-review-opus.md)
  Location hint: New test function, use os.utime() to set mtimes for tie-breaking

**Verify GREEN:** `pytest tests/test_planstate_vet.py::test_iterative_review_highest_wins -v`
**Verify no regression:** `pytest tests/test_planstate_vet.py -v`

---

## Phase 2 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that get_vet_status() correctly detects staleness for all naming patterns
3. Integration check: Verify Phase 1 infer_state() can call get_vet_status() and populate gate field
4. Commit: All Phase 2 implementations and tests

**Expected state:**
- vet.py module exists with get_vet_status() function
- All 5 tests pass in test_planstate_vet.py
- Naming convention handling covers standard patterns + fallback globs
- Iterative review selection uses highest number or newest mtime
- Phase 1 integration point works (gate attachment)
