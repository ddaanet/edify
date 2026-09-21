"""Shared fixtures for ``scripts/check_line_limits.sh`` contract tests.

KD-7 in ``plans/provenance-enforcement-and-routing/outline.md`` (Item 1.10).
Each test builds a throwaway fixture tree under ``tmp_path`` and runs the
script by absolute path with ``[ROOT]`` = that tree, ``cwd=tmp_path`` (never
the checkout — the script must honour ``ROOT`` rather than walking the repo
it happens to run from).
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_line_limits.sh"


def _write_lines(path: Path, count: int) -> None:
    """Write ``count`` newline-terminated filler lines to ``path``.

    The file always ends in a newline, so ``wc -l`` — what the script counts
    — reports exactly ``count`` for ``count >= 1``. Parent directories are
    created; ``path`` may contain spaces (it is never split).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(f"line {i}" for i in range(count)) + "\n"
    path.write_text(text, encoding="utf-8")


def _run_check_line_limits(
    root: Path, allowlist: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Invoke ``check_line_limits.sh`` by absolute path against ``root``.

    ``--allowlist`` precedes ``ROOT`` on the command line when given, per
    the script's ``[--allowlist FILE] [ROOT]`` usage.
    """
    args = [str(SCRIPT)]
    if allowlist is not None:
        args += ["--allowlist", str(allowlist)]
    args.append(str(root))
    return subprocess.run(
        args,
        cwd=root.parent,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_allowlist(path: Path, entries: list[tuple[str, int, str]]) -> None:
    """Write an allowlist file in the format KD-7 pins for this job.

    One entry per line: ``<path><TAB><ceiling><TAB><note>``. ``path`` is
    root-relative and may contain spaces (never split on whitespace);
    ``ceiling`` is the entry's line-count ceiling, which only ratchets
    down; ``note`` names the job that retires the entry, or ``"no job
    yet"``.

    Every fixture opens with a ``#`` comment line and a blank line, so the
    script must skip both to pass any allowlist test — a reader treating
    them as entries would look for a file literally named ``#`` and one
    named ``""``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# path\tceiling\tnote", ""]
    lines += [
        f"{entry_path}\t{ceiling}\t{note}" for entry_path, ceiling, note in entries
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
