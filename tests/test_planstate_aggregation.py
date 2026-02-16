"""Tests for planstate aggregation module."""

from claudeutils.planstate.aggregation import TreeInfo, _parse_worktree_list


def test_parse_worktree_list_porcelain() -> None:
    """Parse git worktree list --porcelain output into TreeInfo objects."""
    porcelain = (
        "worktree /path/to/main\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /path/to/wt/slug\n"
        "branch refs/heads/slug\n"
        "\n"
    )

    result = _parse_worktree_list(porcelain)

    assert len(result) == 2
    assert result[0] == TreeInfo(
        path="/path/to/main", branch="main", is_main=True, slug=None
    )
    assert result[1] == TreeInfo(
        path="/path/to/wt/slug", branch="slug", is_main=False, slug="slug"
    )


def test_main_tree_detection() -> None:
    """Detect main tree (is_main=True, slug=None) and worktree slugs."""
    porcelain = (
        "worktree /path/to/main\n"
        "branch refs/heads/main\n"
        "\n"
        "worktree /path/wt/worktree-1\n"
        "branch refs/heads/feature-1\n"
        "\n"
        "worktree /path/wt/worktree-2\n"
        "branch refs/heads/feature-2\n"
        "\n"
    )

    result = _parse_worktree_list(porcelain)

    assert len(result) == 3
    # First tree is main
    assert result[0].is_main is True
    assert result[0].slug is None
    # Second tree is worktree
    assert result[1].is_main is False
    assert result[1].slug == "worktree-1"
    # Third tree is worktree
    assert result[2].is_main is False
    assert result[2].slug == "worktree-2"
