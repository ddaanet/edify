"""Shared fixtures for ``scripts/check_line_limits.sh`` contract tests.

KD-7 in ``plans/provenance-enforcement-and-routing/outline.md`` (Item 1.10).
Each test builds a throwaway fixture tree under ``tmp_path`` and runs the
script by absolute path with ``[ROOT]`` = that tree, ``cwd=tmp_path`` (never
the checkout — the script must honour ``ROOT`` rather than walking the repo
it happens to run from).
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal

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


def _run_check_line_limits(  # noqa: PLR0913 — `root` plus five independent
    # toggles, each documented in the docstring below and each selecting a
    # different invocation shape (argv, argv[0], CWD or PATH); bundling them
    # into a struct would only add an indirection layer for this file's own
    # tests, the sole caller.
    root: Path,
    allowlist: Path | None | Literal["default"] = None,
    path_prepend: Path | None = None,
    script: Path | None = None,
    *,
    omit_root: bool = False,
    second_root: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke ``check_line_limits.sh`` by absolute path against ``root``.

    ``--allowlist`` precedes ``ROOT`` on the command line when given, per
    the script's ``[--allowlist FILE] [ROOT]`` usage.

    When the caller supplies no ``allowlist`` (the default, ``None``), an
    empty allowlist is written outside ``root`` (so the allowlist file
    itself is never walked or counted) and passed explicitly — the script
    must never fall through to its own ``scripts/check_line_limits.allow``
    sidecar here, or a test would pass or fail depending on that file's
    contents rather than the fixture it declares.

    ``allowlist="default"`` opts a test into the script's own
    default-sidecar resolution instead: no ``--allowlist`` flag is emitted
    at all, so the script falls to ``SCRIPT_DIR/check_line_limits.allow``
    beside whichever ``script`` ran. Exercising that branch against a
    sidecar the test controls requires a *relocated copy* of the script
    (pass one via ``script=``): ``SCRIPT_DIR`` is derived from the invoked
    script's own location (``BASH_SOURCE``), so only relocating the script
    itself moves where its default sidecar resolves. Passing an explicit
    ``Path`` here does not exercise this branch — it sets
    ``ALLOWLIST_EXPLICIT=1`` and skips it, which is a different code path.

    ``script``, when given, is the script binary to invoke in place of the
    canonical ``scripts/check_line_limits.sh`` — typically a copy relocated
    under ``tmp_path`` so its own ``SCRIPT_DIR``-derived sidecar resolution
    points somewhere the test controls.

    ``omit_root``, when true, drops the ``ROOT`` positional argument
    entirely and runs with ``cwd=root`` (rather than ``root.parent``), so
    the script's own default (``ROOT="."`` when no positional is given) is
    what resolves the fixture tree, rather than an argument the test
    supplies.

    ``path_prepend``, when given, is put ahead of the real ``PATH`` so a
    fixture-supplied shim (a ``wc`` wrapper, for instance) is what the
    script's subshells resolve.

    ``second_root``, when given, is appended as a *second* positional
    argument after ``root`` — usage is ``[--allowlist FILE] [ROOT]``, one
    optional ``ROOT``, so this exercises what the script does when given
    two.
    """
    script_path = script if script is not None else SCRIPT
    args = [str(script_path)]
    if allowlist is None:
        allowlist = root.parent / "_empty_allowlist_for_test.txt"
        if not allowlist.exists():
            allowlist.write_text("", encoding="utf-8")
        args += ["--allowlist", str(allowlist)]
    elif allowlist != "default":
        args += ["--allowlist", str(allowlist)]
    if not omit_root:
        args.append(str(root))
    if second_root is not None:
        args.append(str(second_root))
    env = None
    if path_prepend is not None:
        env = os.environ.copy()
        env["PATH"] = f"{path_prepend}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        args,
        cwd=root if omit_root else root.parent,
        capture_output=True,
        text=True,
        check=False,
        env=env,
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


def _write_padded_wc_shim(bin_dir: Path) -> None:
    """Write a ``wc`` wrapper that left-pads its count like BSD/macOS ``wc``.

    Reproduces F-1 (``check_line_limits.sh:124``'s unguarded ``wc -l``) on a
    Linux box, where GNU ``wc -l <file`` — reading a redirected file from
    stdin, with no filename argument — prints a bare count. That BSD/macOS
    ``wc`` left-pads that same call into a fixed-width field is the claim
    F-1 rests on and is unverified on macOS (this box is Linux); the shim
    does not reproduce a measured BSD output, it pins robustness against
    *any* padding ``wc`` might emit, which is why the exact field width
    below is not itself a claim about BSD's behaviour. The wrapper execs the
    real ``wc``, located once by absolute path so it never recurses into
    itself once ``bin_dir`` sits ahead of it on ``PATH``, and reformats only
    the ``-l``-reading-stdin shape the script actually calls; every other
    invocation passes straight through.
    """
    real_wc = shutil.which("wc")
    assert real_wc is not None, "wc not found on PATH"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shim = bin_dir / "wc"
    shim.write_text(
        "#!/usr/bin/env bash\n"
        "# Left-pads a bare `wc -l` count into an 8-char field, the way\n"
        "# BSD/macOS wc does, to reproduce F-1 on a Linux box.\n"
        'if [ "$#" -eq 1 ] && [ "$1" = "-l" ]; then\n'
        f'    count=$("{real_wc}" -l | tr -d " ")\n'
        '    printf "%8s\\n" "$count"\n'
        "    exit 0\n"
        "fi\n"
        f'exec "{real_wc}" "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
