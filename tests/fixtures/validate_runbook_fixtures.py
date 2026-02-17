"""Fixture constants for test_validate_runbook.py."""

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
