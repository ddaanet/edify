"""Fixture constants for test_validate_runbook.py."""

# Non-markdown file under artifact path — should NOT trigger model-tags violation
NON_MARKDOWN_ARTIFACT = """\
---
title: Script Runbook
---

# Phase 1: Skills setup (type: tdd)

---

## Cycle 1.1: add script

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `agent-core/skills/commit/format-message.sh`
  Action: Create

---
"""

# Pre-existing file modified without creation — should be OK with known_files
LIFECYCLE_KNOWN_FILE = """\
---
title: Known File Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: update existing

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `src/existing.py`
  Action: Modify

---
"""

VIOLATION_MODEL_TAGS = """\
---
title: Violation Runbook
---

# Phase 1: Skills setup (type: tdd)

---

## Cycle 1.1: add skill

**Execution Model**: Haiku

**GREEN Phase:**

**Changes:**
- File: `agent-core/skills/myskill/SKILL.md`
  Action: Create

---
"""

VALID_TDD = """\
---
title: Example Runbook
---

# Phase 1: Core module (type: tdd)

**Target files:**
- `src/module.py` (new)

---

## Cycle 1.1: scaffold

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_foo`

Expects `ImportError` on `src.module`.

**Expected failure:** `ImportError`

**Verify RED:** `pytest tests/test_example.py::test_foo -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Create

**Verify GREEN:** `pytest tests/test_example.py::test_foo -v`

---

## Cycle 1.2: extend

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_bar`

**Verify RED:** `pytest tests/test_example.py::test_bar -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Modify

**Verify GREEN:** `pytest tests/test_example.py::test_bar -v`

**Checkpoint:** All 2 tests pass.

---
"""

VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE = """\
---
title: Lifecycle Violation Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: scaffold

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `src/widget.py`
  Action: Modify

---
"""

VIOLATION_LIFECYCLE_DUPLICATE_CREATE = """\
---
title: Duplicate Create Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: scaffold

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Create

---

# Phase 2: Extension (type: tdd)

---

## Cycle 2.1: duplicate create

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Create

---
"""

VIOLATION_TEST_COUNTS_PARAMETRIZED = """\
---
title: Parametrized Test Counts Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: parametrized test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_foo[param1]`

**Verify RED:** `pytest tests/test_example.py::test_foo -v`

---

## Cycle 1.2: second param

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_foo[param2]`

**Verify RED:** `pytest tests/test_example.py::test_foo -v`

**Checkpoint:** All 1 tests pass.

---
"""

VIOLATION_RED_IMPLAUSIBLE = """\
---
title: Red Implausible Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: create widget

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_create_widget`

**Verify RED:** `pytest tests/test_example.py::test_create_widget -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/widget.py`
  Action: Create

**Verify GREEN:** `pytest tests/test_example.py::test_create_widget -v`

---

## Cycle 1.2: use widget

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_use_widget`

**Expected failure:** ImportError on 'widget' not importable

**Verify RED:** `pytest tests/test_example.py::test_use_widget -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/widget.py`
  Action: Modify

**Verify GREEN:** `pytest tests/test_example.py::test_use_widget -v`

---
"""

AMBIGUOUS_RED_PLAUSIBILITY = """\
---
title: Ambiguous Red Plausibility Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: create widget

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_create_widget`

**Verify RED:** `pytest tests/test_example.py::test_create_widget -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/widget.py`
  Action: Create

**Verify GREEN:** `pytest tests/test_example.py::test_create_widget -v`

---

## Cycle 1.2: widget validates input

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_widget_validates_input`

**Expected failure:** ValueError — widget raises on invalid input

**Verify RED:** `pytest tests/test_example.py::test_widget_validates_input -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/widget.py`
  Action: Modify

**Verify GREEN:** `pytest tests/test_example.py::test_widget_validates_input -v`

---
"""

# Verify GREEN with specific pytest paths — should trigger verify-green-paths violation
VIOLATION_VERIFY_GREEN_PATHS = """\
## Cycle 1.1: scaffold
**Verify GREEN:** `pytest tests/test_example.py::TestFoo::test_bar -v`
"""

# Verify GREEN with universal recipe — should pass verify-green-paths
VALID_VERIFY_GREEN_PATHS = """\
## Cycle 1.1: scaffold
**Verify GREEN:** `just green`
"""

VIOLATION_TEST_COUNTS = """\
---
title: Test Counts Violation Runbook
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: first test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_alpha`

**Verify RED:** `pytest tests/test_example.py::test_alpha -v`

---

## Cycle 1.2: second test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_beta`

**Verify RED:** `pytest tests/test_example.py::test_beta -v`

---

## Cycle 1.3: third test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_gamma`

**Verify RED:** `pytest tests/test_example.py::test_gamma -v`

**Checkpoint:** All 5 tests pass.

---
"""
