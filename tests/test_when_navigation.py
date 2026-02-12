"""Tests for markdown navigation hierarchy extraction."""

from claudeutils.when.index_parser import WhenEntry
from claudeutils.when.navigation import (
    compute_ancestors,
    compute_siblings,
    extract_heading_hierarchy,
    format_navigation,
)


def test_extract_heading_hierarchy() -> None:
    """Extract heading hierarchy with parent mapping and levels."""
    # Basic hierarchy: H2 with H3 children
    content = """\
## Section A
Some text here.
### Sub A1
Content for A1.
### Sub A2
Content for A2.
## Section B
"""
    hierarchy = extract_heading_hierarchy(content)

    # Sub A1 and Sub A2 should have "Section A" as parent
    assert hierarchy["Sub A1"].parent == "Section A"
    assert hierarchy["Sub A2"].parent == "Section A"

    # Verify levels
    assert hierarchy["Section A"].level == 2
    assert hierarchy["Sub A1"].level == 3
    assert hierarchy["Sub A2"].level == 3
    assert hierarchy["Section B"].level == 2

    # Nested H4: A -> B -> C
    content2 = """\
## A
### B
#### C
"""
    hierarchy2 = extract_heading_hierarchy(content2)
    assert hierarchy2["C"].parent == "B"
    assert hierarchy2["B"].parent == "A"
    assert hierarchy2["C"].level == 4
    assert hierarchy2["B"].level == 3
    assert hierarchy2["A"].level == 2


def test_compute_ancestors() -> None:
    """Compute ancestor links for heading hierarchy."""
    content = """\
## Test Organization
### Mock Patching
#### Mock Patching Pattern
Some content here.
## Another Section
"""

    # H3 under H2: should have parent H2 and file link
    ancestors = compute_ancestors("Mock Patching", "testing.md", content)
    assert ancestors == ["/when .Test Organization", "/when ..testing.md"]

    # H4 under H3 under H2: should have grandparent H2, parent H3, and file link
    ancestors = compute_ancestors("Mock Patching Pattern", "testing.md", content)
    assert ancestors == [
        "/when .Test Organization",
        "/when .Mock Patching",
        "/when ..testing.md",
    ]

    # H2 (top-level): should have only file link
    ancestors = compute_ancestors("Test Organization", "testing.md", content)
    assert ancestors == ["/when ..testing.md"]


def test_flat_h2_file_ancestors() -> None:
    """Handle flat H2 files with no nesting (all headings at same level)."""
    # Flat H2 file: all headings are H2, no H3 nesting
    content = """\
## Oneshot Workflow Pattern

Pattern description here.

## TDD Workflow Integration

Another section here.

## Handoff Pattern

More content.
"""

    # For H2 heading in flat file, ancestor should be only the file link
    ancestors = compute_ancestors(
        "Oneshot Workflow Pattern", "workflow-core.md", content
    )
    assert ancestors == ["/when ..workflow-core.md"]

    # Another H2 in same flat file
    ancestors = compute_ancestors(
        "TDD Workflow Integration", "workflow-core.md", content
    )
    assert ancestors == ["/when ..workflow-core.md"]

    # Verify hierarchy extraction produces flat list (all H2, no parents)
    hierarchy = extract_heading_hierarchy(content)
    assert hierarchy["Oneshot Workflow Pattern"].parent is None
    assert hierarchy["Oneshot Workflow Pattern"].level == 2
    assert hierarchy["TDD Workflow Integration"].parent is None
    assert hierarchy["TDD Workflow Integration"].level == 2
    assert hierarchy["Handoff Pattern"].parent is None
    assert hierarchy["Handoff Pattern"].level == 2


def test_compute_siblings() -> None:
    """Compute sibling entries under the same parent heading."""
    content = """\
## Test Organization
### Mock Patching Pattern
Content here.
### Testing Strategy
More content.
### Success Metrics
Even more content.
## Another Section
### Different Parent
This entry has a different parent.
"""

    entries = [
        WhenEntry(
            operator="when",
            trigger="mock patching pattern",
            extra_triggers=[],
            line_number=1,
            section="testing.md",
        ),
        WhenEntry(
            operator="when",
            trigger="testing strategy",
            extra_triggers=[],
            line_number=2,
            section="testing.md",
        ),
        WhenEntry(
            operator="when",
            trigger="success metrics",
            extra_triggers=[],
            line_number=3,
            section="testing.md",
        ),
        WhenEntry(
            operator="when",
            trigger="different parent",
            extra_triggers=[],
            line_number=4,
            section="testing.md",
        ),
    ]

    # Target: "Mock Patching Pattern" under "Test Organization"
    # Expected siblings: "Testing Strategy" and "Success Metrics" (same parent)
    # Excluded: "Different Parent" (different parent), target itself
    siblings = compute_siblings("Mock Patching Pattern", content, entries)
    assert len(siblings) == 2
    assert "/when testing strategy" in siblings
    assert "/when success metrics" in siblings
    assert "/when mock patching pattern" not in siblings
    assert "/when different parent" not in siblings

    # Test with target that has no siblings
    content_no_siblings = """\
## Test Organization
### Mock Patching Pattern
Content here.
"""
    entries_single = [
        WhenEntry(
            operator="when",
            trigger="mock patching pattern",
            extra_triggers=[],
            line_number=1,
            section="testing.md",
        ),
    ]
    siblings_empty = compute_siblings(
        "Mock Patching Pattern", content_no_siblings, entries_single
    )
    assert siblings_empty == []


def test_structural_headings_skipped_as_nav_targets() -> None:
    """Structural headings excluded from sibling grouping."""
    content = """\
## .Test Organization
### Mock Patching Pattern
Some content here.
## Another Section
### Real Test Pattern
More content here.
"""

    # Test 1: ancestor walk includes structural headings
    ancestors = compute_ancestors("Mock Patching Pattern", "testing.md", content)
    assert "/when ..Test Organization" in ancestors or "/when ..testing.md" in ancestors
    assert ancestors[-1] == "/when ..testing.md"

    # Test 2: HeadingInfo for ".Test Organization" has is_structural=True flag
    hierarchy = extract_heading_hierarchy(content)
    assert hierarchy[".Test Organization"].is_structural is True

    # Test 3: compute_siblings excludes entries under structural parent headings
    entries = [
        WhenEntry(
            operator="when",
            trigger="mock patching",
            extra_triggers=[],
            line_number=1,
            section="testing.md",
        ),
        WhenEntry(
            operator="when",
            trigger="real test pattern",
            extra_triggers=[],
            line_number=1,
            section="testing.md",
        ),
    ]

    # Mock heading associations for entries
    # Entry 0 is under ".Test Organization" (structural)
    # Entry 1 is under "Another Section" (semantic)
    siblings = compute_siblings("Mock Patching Pattern", content, entries)
    # Should be empty because the structural heading has no sibling grouping
    assert siblings == []


def test_format_navigation_output() -> None:
    """Format navigation links with ancestor and sibling sections."""
    # Test with both ancestors and siblings
    ancestors = ["/when .Test Organization", "/when ..testing.md"]
    siblings = ["/when testing strategy", "/when success metrics"]
    result = format_navigation(ancestors, siblings)
    expected = """\
Broader:
/when .Test Organization
/when ..testing.md

Related:
/when testing strategy
/when success metrics"""
    assert result == expected

    # Test with only ancestors
    result_ancestors_only = format_navigation(
        ["/when .Test Organization", "/when ..testing.md"], []
    )
    expected_ancestors = """\
Broader:
/when .Test Organization
/when ..testing.md"""
    assert result_ancestors_only == expected_ancestors

    # Test with only siblings
    result_siblings_only = format_navigation(
        [], ["/when testing strategy", "/when success metrics"]
    )
    expected_siblings = """\
Related:
/when testing strategy
/when success metrics"""
    assert result_siblings_only == expected_siblings

    # Test with no links
    result_empty = format_navigation([], [])
    assert result_empty == ""
