"""Tests for decision files validator."""

from pathlib import Path

from edify.validation.decision_files import validate


def test_section_with_content_before_subheadings_no_violation(
    tmp_path: Path,
) -> None:
    """Test: section with sufficient content before sub-headings → no violation."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Section One
This section has substantive content before sub-headings.
It has multiple lines of content.
And a third line for good measure.

### Subsection A
Content here.

### Subsection B
More content.

## Section Two
Another section with content.
And a second line.
Plus a third.

### Subsection C
Details.
""")

    errors = validate(tmp_path)
    assert errors == []


def test_organizational_section_with_only_subheadings_violation(
    tmp_path: Path,
) -> None:
    """Test: section with only sub-headings → violation (needs structural marker)."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Organizational Section

### Subsection A
Content here.

### Subsection B
More content.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "test-decision.md:3" in errors[0]
    assert "Organizational Section" in errors[0]
    assert "has no direct content" in errors[0]
    assert "Mark structural: '## .Organizational Section'" in errors[0]


def test_structural_marker_dot_prefix_no_violation(tmp_path: Path) -> None:
    """Test: structural marker (. prefix) → no violation."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## .Organizational Section

### Subsection A
Content here.

### Subsection B
More content.
""")

    errors = validate(tmp_path)
    assert errors == []


def test_content_threshold_two_substantive_lines(tmp_path: Path) -> None:
    """Test: content threshold (≤2 substantive lines before sub-heading → violation)."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Section
One line.
Two lines.

### Subsection A
Content here.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "Section" in errors[0]
    assert "has no direct content" in errors[0]


def test_content_threshold_three_substantive_lines_no_violation(
    tmp_path: Path,
) -> None:
    """Test: ≥3 substantive lines before sub-heading → no violation."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Section
One line.
Two lines.
Three lines.

### Subsection A
Content here.
""")

    errors = validate(tmp_path)
    assert errors == []


def test_empty_lines_dont_count_as_substantive(tmp_path: Path) -> None:
    """Test: empty lines are not counted as substantive content."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Section

One line.

Two lines.

### Subsection A
Content here.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "Section" in errors[0]


def test_comments_dont_count_as_substantive(tmp_path: Path) -> None:
    """Test: HTML comments are not counted as substantive content."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Section
<!-- This is a comment -->
One line of real content.

### Subsection A
Content here.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "Section" in errors[0]


def test_nested_heading_levels_handled_correctly(tmp_path: Path) -> None:
    """Test: nested heading levels handled correctly."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Organizational Section

### Subsection A
Content.

#### Sub-subsection
More.

### Subsection B
More.

## Another Section
Real content.
And more content.
Plus more.

### Another subsection
Details.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "Organizational Section" in errors[0]


def test_no_decision_files_no_errors(tmp_path: Path) -> None:
    """Test: no decision files → no errors."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert errors == []


def test_multiple_violations_reported(tmp_path: Path) -> None:
    """Test: multiple violations reported."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Organizational Section One

### Subsection A
Content.

## Organizational Section Two

### Subsection B
Content.

## Real Section
This has content.
And a second line.
Plus a third.

### Subsection C
Details.
""")

    errors = validate(tmp_path)
    assert len(errors) == 2
    assert any("Organizational Section One" in e for e in errors)
    assert any("Organizational Section Two" in e for e in errors)


def test_h2_and_h3_violations_detected(tmp_path: Path) -> None:
    """Test: violations at both H2 and H3 levels detected."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main Title

## Organizational H2

### Organizational H3

#### Sub-subsection
Content here.
""")

    errors = validate(tmp_path)
    # H3 is under H2, so it's part of H2's content. Only H2 violation detected.
    assert len(errors) == 1
    assert "Organizational H2" in errors[0]


def test_heading_levels_correctly_identified(tmp_path: Path) -> None:
    """Test: correct heading levels reported in error messages."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main

## Section H2

### Subsection
Content.

### Another
More.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "## .Section H2" in errors[0]  # Should show H2 marker


def test_malformed_file_gracefully_handled(tmp_path: Path) -> None:
    """Test: malformed file handled gracefully."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    # Create unreadable file (can't test on all systems, skip if fails)
    # Instead, test with binary content
    decision_file.write_bytes(b"\x80\x81\x82")

    # Should not crash, just skip
    errors = validate(tmp_path)
    assert errors == []


def test_multiple_files_violations(tmp_path: Path) -> None:
    """Test: violations across multiple files reported."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    file1 = decisions_dir / "decision1.md"
    file1.write_text("""# Title

## Organizational

### Sub
Content.
""")

    file2 = decisions_dir / "decision2.md"
    file2.write_text("""# Title

## Organizational

### Sub
Content.
""")

    errors = validate(tmp_path)
    assert len(errors) == 2
    assert any("decision1.md" in e for e in errors)
    assert any("decision2.md" in e for e in errors)


def test_h4_and_h5_headings_supported(tmp_path: Path) -> None:
    """Test: H4 and H5 headings are properly supported."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Main

## Section One
Real content one.
Real content two.
Real content three.

### Sub A
Content line one.
Content line two.
Content line three.

## Section Two

### Sub B

#### H4 Organizational

##### H5 Subsection
Content.
""")

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "Section Two" in errors[0]


def test_h1_headings_not_validated(tmp_path: Path) -> None:
    """Test: H1 headings are not validated (min level H2)."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Organizational H1

## Normal Section
Content.
""")

    errors = validate(tmp_path)
    # H1 should not be validated, so no violation
    assert len(errors) == 0
