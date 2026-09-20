# Item 1.10, slices 1-2 — RED

Batched per the dispatch instructions: today's `scripts/check_line_limits.sh`
takes no `ROOT` argument and only walks `src`/`tests` for `*.py`, so slice 1's
fixture (a clean tree with a 10-line `SKILL.md` and a 10-line `notes.md`, no
Python files) passes vacuously against it — there is nothing for the current
script to find under `src`/`tests` regardless of `ROOT`. Slice 2 supplies the
genuine red.

## Fixture design

`tests/test_line_limits.py`:

- `_write_lines(path, count)` — writes `count` lines of filler text
  (`line 0`, `line 1`, ...) to `path`, creating parent directories.
- `_run_check_line_limits(root)` — invokes `scripts/check_line_limits.sh` by
  absolute path (`REPO_ROOT / "scripts" / "check_line_limits.sh"`, from
  `Path(__file__).resolve().parents[1]`) with `[ROOT]` = the fixture tree,
  `cwd=root.parent` (i.e. `tmp_path`, never the checkout — proves the script
  honours the `ROOT` argument rather than defaulting to walking the repo it
  happens to run from), `capture_output=True, text=True, check=False`.

Both tests build their fixture tree under `tmp_path / "root"`.

## Test bodies

```python
def test_line_limits_passes_clean_tree(tmp_path: Path) -> None:
    """A clean tree of small files exits 0 with no ``oversized-file:`` line."""
    root = tmp_path / "root"
    _write_lines(root / "plugin" / "skills" / "x" / "SKILL.md", 10)
    _write_lines(root / "docs" / "notes.md", 10)

    result = _run_check_line_limits(root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert not any(
        line.startswith("oversized-file:") for line in result.stdout.splitlines()
    ), result.stdout


def test_line_limits_fails_markdown_over_400(tmp_path: Path) -> None:
    """A 401-line non-``SKILL.md`` markdown file exits 1 naming the overage.

    The reported path is root-relative (``docs/notes.md``, not an absolute
    path) — that is what a reader of ``just precommit`` output needs, since
    an absolute path would vary by checkout location.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)

    result = _run_check_line_limits(root)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout
```

**Note on the reported-path assertion:** the interface spec says
`oversized-file: <path>: <n> lines > <cap>` without specifying whether
`<path>` is root-relative or absolute. The test asserts root-relative
(`docs/notes.md`), because that's what a reader of `just precommit` output
needs — an absolute path varies by checkout location and clutters output for
every invocation.

## Verbatim pytest output

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_line_limits.py -v

Summary: 1/2 passed, 1 failed

Failures:

tests/test_line_limits.py::test_line_limits_fails_markdown_over_400 FAILED

tests/test_line_limits.py:61: in test_line_limits_fails_markdown_over_400
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 1
E    +  where 0 = CompletedProcess(args=['/Users/david/code/edify/scripts/check_line_limits.sh', '/tmp/claude-1000/pytest-of-david/pytest-524/test_line_limits_fails_markdow0/root'], returncode=0, stdout='', stderr='').returncode

Passes:

tests/test_line_limits.py::test_line_limits_passes_clean_tree
```

Slice 1 (`test_line_limits_passes_clean_tree`) PASSED — expected, vacuous:
the current script finds no `*.py` under `src`/`tests` in the fixture tree
regardless of `ROOT`, and never looks at `SKILL.md`/`notes.md` at all.

Slice 2 (`test_line_limits_fails_markdown_over_400`) FAILED on its exit-code
assertion (`0 == 1`) — the script exits 0 and prints nothing for a 401-line
`docs/notes.md`, since it doesn't walk markdown outside `agents/decisions/`
and doesn't accept `ROOT`. Genuine red, landing on the assertion rather than
a fixture exception.

## Lint output

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH ruff check tests/test_line_limits.py
All checks passed!

$ PATH=/Users/david/code/edify/.venv/bin:$PATH mypy tests/test_line_limits.py
(no output — clean)

$ PATH=/Users/david/code/edify/.venv/bin:$PATH docformatter --diff tests/test_line_limits.py
(no output — clean; used --diff rather than -c since docformatter is
configured in-place = true in pyproject.toml)
```

One round of fixes was needed before lint was clean: import order
(`subprocess` before `from pathlib import Path`) and a line-length wrap in
`_write_lines`.

## Scope

Touched: `tests/test_line_limits.py` (new) only.
`scripts/check_line_limits.sh` was not modified — the script exists and no
stub was needed.
