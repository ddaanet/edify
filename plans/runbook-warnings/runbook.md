# Runbook: Runbook Warnings

**Plan:** plans/runbook-warnings
**Tier:** 2 (Lightweight Delegation)
**Type:** TDD

## Problem

`validate_file_references()` in `prepare-runbook.py` checks each step's backtick-wrapped file paths against the current filesystem. For greenfield plans where steps create new files, this produces ~95 false-positive warnings (files that prior steps will create). Real issues (genuine path typos) are buried in noise.

## Approach

Add cross-step awareness to the validator:
1. Extract file-creation declarations from all step/cycle content (new function)
2. Build a plan-wide "will-be-created" set before per-step validation
3. Suppress warnings for paths in the will-be-created set
4. Keep warnings for files genuinely absent from both filesystem and plan declarations

Existing same-step suppression (create-verb pattern, lines 1249-1252) stays unchanged — it's a fast path that avoids the cross-step lookup.

## Files

- `plugin/bin/prepare-runbook.py` — production code
- `tests/test_prepare_runbook_fenced.py` — existing test file (extend with new test class)

## Recall Constraints

- "When splitting validation into mechanical and semantic" — creation-declaration extraction is deterministic (mechanical); keep it scriptable with zero false positives
- "When testing CLI tools" — Click test harness; but this is a script, not CLI — use importlib pattern from existing tests
- "When writing test descriptions in prose" — prose with specific assertions, ≤70 char docstrings

---

## Phase 1: Cross-step file-creation awareness (type: tdd)

### Cycle 1.1: extract_creation_declarations

**Bootstrap:** Add `extract_creation_declarations(content)` stub to `prepare-runbook.py` returning `set()`. Place after `extract_file_references` (line ~1202). Do not commit.

---

**RED Phase:**

**Test:** `test_extract_creation_declarations_basic`
**Assertions:**
- `extract_creation_declarations("Create `src/foo.py` with module stub")` returns set containing `"src/foo.py"`
- `extract_creation_declarations("Write `src/bar/baz.py` with config")` returns set containing `"src/bar/baz.py"`
- `extract_creation_declarations("mkdir `src/utils/helpers.py`")` returns set containing `"src/utils/helpers.py"`
- `extract_creation_declarations("No creation verbs here, just `src/ref.py` reference")` returns empty set
- `extract_creation_declarations("Create `src/a.py` and Write `src/b.py`")` returns set with both paths

**Expected failure:** `AssertionError` — stub returns empty set for all inputs

**Why it fails:** Stub returns `set()`, tests expect populated sets for creation-verb content.

**Verify RED:** `pytest tests/test_prepare_runbook_fenced.py::TestExtractCreationDeclarations::test_extract_creation_declarations_basic -v`

---

**GREEN Phase:**

**Implementation:** Parse creation-verb + backtick-path patterns from content.

**Behavior:**
- Find all backtick-wrapped paths preceded by creation verbs (Create, Write, mkdir)
- Apply same file-extension filter as `extract_file_references`
- Exclude paths inside fenced code blocks (reuse `strip_fenced_blocks`)

**Approach:** Regex similar to existing `create_pattern` but extracting all matches rather than checking a specific ref. Pattern: `(?:Create|Write|mkdir)\s[^`]*\`(path-with-extension)\`` applied to fence-stripped content.

**Changes:**
- File: `plugin/bin/prepare-runbook.py`
  Action: Replace stub with regex extraction using `strip_fenced_blocks` + findall
  Location hint: after `extract_file_references` function (~line 1202)

**Verify GREEN:** `just green`

### Cycle 1.2: Creation declarations exclude fenced blocks

**RED Phase:**

**Test:** `test_creation_declarations_ignores_fenced_blocks`
**Assertions:**
- Content with `Create \`src/real.py\`` outside fence + `Create \`src/fake.py\`` inside triple-backtick fence → returns only `{"src/real.py"}`
- Content with creation inside 4-backtick fence → returns empty set (only fenced content)

**Expected failure:** `AssertionError` — if strip_fenced_blocks not applied, fenced paths leak through

**Why it fails:** Without fence stripping, regex matches paths inside fenced code blocks too.

**Verify RED:** `pytest tests/test_prepare_runbook_fenced.py::TestExtractCreationDeclarations::test_creation_declarations_ignores_fenced_blocks -v`

---

**GREEN Phase:**

**Implementation:** Verify fence stripping is correctly applied in cycle 1.1 implementation.

**Behavior:**
- Content inside fenced blocks (```, `````, ~~~) must not produce creation declarations
- Same fence semantics as `extract_file_references` (CommonMark: closing fence ≥ opening count)

**Approach:** If cycle 1.1 already uses `strip_fenced_blocks`, this should pass. If not, add the call.

**Verify GREEN:** `just green`

### Cycle 1.3: Plan-wide suppression in validate_file_references

**RED Phase:**

**Test:** `test_validate_file_references_suppresses_prior_step_creations`
**Assertions:**
- Build sections dict with two steps: step "1.1" content declares `Create \`src/new_module.py\``, step "1.2" content references `\`src/new_module.py\`` (no creation verb)
- `validate_file_references(sections)` returns no warnings for `src/new_module.py` (suppressed because step 1.1 declares creation)
- A genuinely absent file `\`src/nonexistent.py\`` referenced in step "1.2" still produces a warning
- Warning text for genuinely absent file contains "not declared in plan" (distinguishable from plan-declared paths)

**Expected failure:** `AssertionError` — current implementation warns about `src/new_module.py` because it doesn't exist on filesystem and cross-step awareness is missing

**Why it fails:** `validate_file_references` checks only same-step create-verb context. Cross-step creation declarations are invisible.

**Verify RED:** `pytest tests/test_prepare_runbook_fenced.py::TestValidateFileReferencesCreations::test_validate_file_references_suppresses_prior_step_creations -v`

---

**GREEN Phase:**

**Implementation:** Collect plan-wide creation declarations before per-step validation loop.

**Behavior:**
- Before the per-step loop, call `extract_creation_declarations` on each step's content
- Union all results into a `plan_created` set
- In the per-step loop, after existing skip checks, check if ref is in `plan_created` → skip
- For remaining warnings (genuinely absent), append "(not declared in plan)" to message text

**Approach:** Add a collection pass before line 1231. Modify the warning message at line 1257.

**Changes:**
- File: `plugin/bin/prepare-runbook.py`
  Action: Add plan-wide collection pass + modify validation logic in `validate_file_references`
  Location hint: lines 1213-1260

**Verify GREEN:** `just green`

### Cycle 1.4: Cycle-based creation declarations

**RED Phase:**

**Test:** `test_validate_file_references_suppresses_cycle_creations`
**Assertions:**
- Build input with cycles (not steps): cycle "1.1" content declares `Create \`src/cycle_mod.py\``, cycle "1.2" references `\`src/cycle_mod.py\``
- `validate_file_references(sections, cycles=cycles)` returns no warning for `src/cycle_mod.py`
- Genuinely absent `\`src/missing.py\`` still warns

**Expected failure:** `AssertionError` — if collection pass only processes `sections["steps"]` and not cycles

**Why it fails:** Cycles are passed separately from sections; creation collection must include both.

**Verify RED:** `pytest tests/test_prepare_runbook_fenced.py::TestValidateFileReferencesCreations::test_validate_file_references_suppresses_cycle_creations -v`

---

**GREEN Phase:**

**Implementation:** Extend collection pass to include cycle content.

**Behavior:**
- Collection pass iterates same `step_items` list (which already includes both cycles and steps)
- Extract creation declarations from each item's content

**Approach:** The `step_items` list (lines 1217-1222) already combines cycles and steps. Use the same list for the collection pass.

**Changes:**
- File: `plugin/bin/prepare-runbook.py`
  Action: Ensure collection pass uses `step_items` (covers both cycles and steps)
  Location hint: collection pass added in cycle 1.3

**Verify GREEN:** `just green`
