"""Tests for markdown navigation hierarchy extraction."""

from claudeutils.when.navigation import compute_ancestors, extract_heading_hierarchy


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
