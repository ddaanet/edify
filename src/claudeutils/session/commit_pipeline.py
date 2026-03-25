"""Commit pipeline: staging, validation, commit execution."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from claudeutils.git import discover_submodules
from claudeutils.session.commit import CommitInput, CommitInputError
from claudeutils.session.commit_gate import validate_files, vet_check


@dataclass
class CommitResult:
    """Result of commit pipeline execution."""

    success: bool
    output: str


def _run_precommit(cwd: Path | None = None) -> tuple[bool, str]:
    """Run ``just precommit`` and return (passed, output).

    Module-level for ``monkeypatch.setattr`` in tests.
    """
    result = subprocess.run(
        ["just", "precommit"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip()
    if result.stderr.strip():
        output += "\n" + result.stderr.strip()
    return result.returncode == 0, output


def _run_lint(cwd: Path | None = None) -> tuple[bool, str]:
    """Run ``just lint`` and return (passed, output).

    Module-level for ``monkeypatch.setattr`` in tests.
    """
    result = subprocess.run(
        ["just", "lint"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip()
    if result.stderr.strip():
        output += "\n" + result.stderr.strip()
    return result.returncode == 0, output


def _stage_files(files: list[str], *, cwd: Path | None = None) -> None:
    """Stage listed files via git add."""
    subprocess.run(
        ["git", "add", "--", *files],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def _git_commit(
    message: str,
    *,
    amend: bool = False,
    no_edit: bool = False,
    cwd: Path | None = None,
) -> str:
    """Run git commit and return output."""
    cmd = ["git", "commit"]
    if amend:
        cmd.append("--amend")
    if no_edit:
        cmd.append("--no-edit")
    else:
        cmd.extend(["-m", message])
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _partition_by_submodule(
    files: list[str],
    submodule_paths: list[str],
) -> tuple[dict[str, list[str]], list[str]]:
    """Split files into submodule buckets and parent files.

    Submodule file paths are made relative to the submodule root.
    """
    submod_files: dict[str, list[str]] = {}
    parent_files: list[str] = []
    for f in files:
        matched = False
        for sub in submodule_paths:
            if f.startswith(sub + "/"):
                rel = f[len(sub) + 1 :]
                submod_files.setdefault(sub, []).append(rel)
                matched = True
                break
        if not matched:
            parent_files.append(f)
    return submod_files, parent_files


def _commit_submodule(
    path: str,
    files: list[str],
    message: str,
    *,
    options: set[str] | None = None,
    cwd: Path | None = None,
) -> str:
    """Stage and commit files within a submodule."""
    opts = options or set()
    sub_cwd = Path(cwd or ".") / path
    subprocess.run(
        ["git", "add", "--", *files],
        cwd=sub_cwd,
        check=True,
        capture_output=True,
    )
    cmd = ["git", "commit"]
    if "amend" in opts:
        cmd.append("--amend")
    if "no-edit" in opts:
        cmd.append("--no-edit")
    else:
        cmd.extend(["-m", message])
    result = subprocess.run(
        cmd,
        cwd=sub_cwd,
        capture_output=True,
        text=True,
        check=True,
    )
    # Stage the updated submodule pointer in the parent
    subprocess.run(
        ["git", "add", "--", path],
        cwd=cwd,
        check=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _validate(ci: CommitInput, *, cwd: Path | None = None) -> CommitResult | None:
    """Run validation gate.

    Returns error result or None on success.
    """
    if "just-lint" in ci.options:
        passed, output = _run_lint(cwd=cwd)
        label = "Lint"
    else:
        passed, output = _run_precommit(cwd=cwd)
        label = "Precommit"

    if not passed:
        return CommitResult(
            success=False,
            output=f"**{label}:** failed\n\n{output}",
        )

    if "no-vet" not in ci.options:
        vr = vet_check(ci.files, cwd=cwd)
        if not vr.passed:
            if vr.reason == "unreviewed":
                files_list = "\n".join(f"- {f}" for f in vr.unreviewed_files)
                detail = f"unreviewed files\n{files_list}"
            elif vr.reason == "stale":
                detail = f"stale report\n{vr.stale_info}"
            else:
                detail = vr.reason or "unknown"
            return CommitResult(
                success=False,
                output=f"**Vet check:** {detail}",
            )

    return None


def _strip_hints(text: str) -> str:
    """Remove git hint/advice lines and continuations."""
    lines = text.split("\n")
    result: list[str] = []
    prev_was_hint = False

    for line in lines:
        is_hint = line.startswith(("hint:", "advice:"))
        if is_hint:
            prev_was_hint = True
        elif prev_was_hint and line and line[0] in (" ", "\t"):
            if line[0] == "\t" or (line[0] == " " and len(line) > 1 and line[1] == " "):
                prev_was_hint = True  # tab/double-space = continuation, filter
            else:
                # Single-space indent: not a hint continuation, but keep
                # hint context active (next line may be a continuation).
                prev_was_hint = True
                result.append(line)
        else:
            prev_was_hint = False
            result.append(line)

    return "\n".join(result)


def format_commit_output(
    *,
    submodule_outputs: dict[str, str] | None = None,
    parent_output: str = "",
    warnings: list[str] | None = None,
) -> str:
    """Format commit output with labels and warnings."""
    parts: list[str] = []

    if warnings:
        parts.extend(f"**Warning:** {w}" for w in warnings)
        parts.append("")

    if submodule_outputs:
        for path, out in submodule_outputs.items():
            parts.append(f"{path}:")
            parts.append(_strip_hints(out))

    if parent_output:
        parts.append(_strip_hints(parent_output))

    return "\n".join(parts)


def _error(label: str, exc: subprocess.CalledProcessError) -> CommitResult:
    """Build failure result from subprocess error."""
    detail = exc.stderr or f"exit code {exc.returncode}"
    return CommitResult(
        success=False,
        output=f"**Error:** {label}: {detail}",
    )


def _validate_inputs(
    ci: CommitInput,
    parent_files: list[str],
    submod_files: dict[str, list[str]],
    *,
    cwd: Path | None,
) -> CommitResult | None:
    """Validate files and submodule messages.

    None on success.
    """
    amend = "amend" in ci.options
    no_edit = "no-edit" in ci.options

    if ci.message is None and not no_edit:
        msg = "No commit message provided"
        raise CommitInputError(msg)

    if parent_files:
        validate_files(parent_files, amend=amend, cwd=cwd)
    for path, files in submod_files.items():
        sub_cwd = Path(cwd or ".") / path
        validate_files(files, amend=amend, cwd=sub_cwd)

    for path in submod_files:
        if path not in ci.submodules:
            msg = f"Files under {path}/ but no ## Submodule {path} section"
            raise CommitInputError(msg)
    return None


def commit_pipeline(
    ci: CommitInput,
    *,
    cwd: Path | None = None,
) -> CommitResult:
    """Execute commit pipeline: stage, validate, commit."""
    amend = "amend" in ci.options
    no_edit = "no-edit" in ci.options

    submod_paths = discover_submodules(cwd=cwd)
    submod_files, parent_files = _partition_by_submodule(ci.files, submod_paths)

    err = _validate_inputs(ci, parent_files, submod_files, cwd=cwd)
    if err:
        return err

    warnings: list[str] = [
        f"Submodule message provided but no changes found for: {path}. Ignored."
        for path in ci.submodules
        if path not in submod_files
    ]

    # Stage parent files before validation so precommit sees staged state
    try:
        if parent_files:
            _stage_files(parent_files, cwd=cwd)
    except subprocess.CalledProcessError as e:
        return _error("staging failed", e)

    # Validation gate — before any irrevocable commits
    err = _validate(ci, cwd=cwd)
    if err:
        return err

    # Commit each submodule (after validation passes)
    submodule_outputs: dict[str, str] = {}
    for path, files in submod_files.items():
        try:
            sub_output = _commit_submodule(
                path,
                files,
                ci.submodules[path],
                options=ci.options,
                cwd=cwd,
            )
        except subprocess.CalledProcessError as e:
            return _error(f"submodule {path} failed", e)
        submodule_outputs[path] = sub_output

    assert ci.message is not None or no_edit
    try:
        parent_output = _git_commit(
            ci.message or "", amend=amend, no_edit=no_edit, cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        return _error("git commit failed", e)

    return CommitResult(
        success=True,
        output=format_commit_output(
            submodule_outputs=submodule_outputs or None,
            parent_output=parent_output,
            warnings=warnings or None,
        ),
    )
