"""Tests for compound inline type tags in prepare-runbook.py."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

extract_sections = _mod.extract_sections
detect_phase_types = _mod.detect_phase_types


class TestCompoundInlineTypeTags:
    """Compound type tags like (type: inline, model: sonnet) detected."""

    def test_detect_phase_types_compound_tag(self) -> None:
        """detect_phase_types recognizes inline with trailing metadata."""
        content = """\
### Phase 1: Core behavior (type: tdd)

## Cycle 1.1: Load config

Some cycle content.

### Phase 2: Contract updates (type: inline, model: sonnet)

- Update contracts

### Phase 3: Prose fixes (type: inline, model: opus)

- Fix prose
"""
        result = detect_phase_types(content)
        assert result[2] == "inline", f"Phase 2 should be inline, got {result.get(2)}"
        assert result[3] == "inline", f"Phase 3 should be inline, got {result.get(3)}"

    def test_extract_sections_compound_tag(self) -> None:
        """extract_sections detects compound-tagged inline phases."""
        content = """\
## Common Context

**Project:** test

---

### Phase 1: Contract updates (type: inline, model: sonnet)

- Update contracts

### Phase 2: Core behavior (type: tdd)

## Cycle 2.1: Load config

**RED Phase:**
Test load_config.
**Verify RED:** `pytest tests/test_load.py -v`

---

**GREEN Phase:**
Implement load_config.
**Verify GREEN:** `pytest tests/test_load.py -v`
"""
        sections = extract_sections(content)
        assert 1 in sections["inline_phases"], (
            f"Phase 1 should be in inline_phases, got {sections['inline_phases']}"
        )
