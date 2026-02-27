#!/usr/bin/env python3
"""Test git diff --stat output format."""

import subprocess
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp) / "repo"
    repo.mkdir()

    # Init repo
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        capture_output=True,
        check=True,
    )

    # Initial commit
    (repo / "dummy.txt").write_text("initial")
    subprocess.run(
        ["git", "add", "dummy.txt"], cwd=repo, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "initial"], cwd=repo, capture_output=True, check=True
    )
    baseline = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()

    # Add file
    (repo / "newfile.txt").write_text("new")
    subprocess.run(
        ["git", "add", "newfile.txt"], cwd=repo, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "add file"], cwd=repo, capture_output=True, check=True
    )

    # Show diff
    result = subprocess.run(
        ["git", "diff", "--stat", baseline],
        cwd=repo,
        capture_output=True,
        check=True,
        text=True,
    )
    print("Full output:")
    print(repr(result.stdout))
    print()
    print("Lines:")
    lines = result.stdout.strip().split("\n")
    for i, line in enumerate(lines):
        print(f"{i}: {repr(line)}")
    print()
    print(f"Total lines: {len(lines)}")
    print(f"First N-1 lines: {len(lines) - 1}")
