# Edify Check / Verify-Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `edify check` subcommand that verifies a Python target against its
icontract contract via CrossHair, plus a `formalize` skill that drives a
propose-contract → check → repair loop with the in-context agent holding intent.

**Architecture:** A pure core (`check.py`: result types + CrossHair-output
parsing + argv building) wrapped by a thin CLI handler (`check_cli.py`:
subprocess + formatting + exit codes), wired into the existing Click group in
`cli.py`. CrossHair is invoked as a subprocess; its exit codes (0/1/2) map
directly to `verified`/`refuted`/`error`. The `formalize` skill is prose that
orchestrates the loop and asks the user when intent is ambiguous.

**Tech Stack:** Python 3.14, Click, `crosshair-tool` (symbolic execution + Z3),
`icontract` (`@require`/`@ensure`), pytest + pytest-mock, uv, ruff (ALL) + mypy
(strict). Spec: `docs/superpowers/specs/2026-06-08-invariant-guided-verify-loop-design.md`.

## File Structure

- Create `src/edify/check.py` — pure: `CheckStatus`, `Finding`, `CheckResult`,
  `build_crosshair_argv()`, `parse_crosshair_output()`. No subprocess, no I/O.
- Create `src/edify/check_cli.py` — `run_crosshair()` (subprocess) and
  `handle_check()` (formatting + exit codes).
- Modify `src/edify/cli.py` — register the `check` command.
- Modify `src/edify/exceptions.py` — add `CrossHairUnavailableError`.
- Modify `pyproject.toml` — add `crosshair-tool` and `icontract` deps.
- Create `tests/fixtures/check_targets/head_buggy.py` and `head_fixed.py` — seed.
- Create `tests/test_check_parse.py`, `tests/test_check_argv.py`,
  `tests/test_cli_check.py`, `tests/test_check_e2e.py`.
- Create `plugin/skills/formalize/SKILL.md` — the loop skill.
- Modify `CLAUDE.md` — list the new skill and subcommand.

**Seed choice note:** the spec floated `average(xs)` for the spec-refinement
demo, but floats make it a flaky *verifier* target (CrossHair will try `nan`/
`inf` and large-int float-rounding, breaking the "fixed verifies" claim). We use
integer `head(xs)` instead — deterministic, and it still demonstrates the
spec-refinement branch (the fix is adding `@require len(xs) > 0`, not changing
code).

**v0 scoping note (grounded refinement of spec §3):** the positional `TARGET`
is passed straight to `crosshair check` (it already accepts a file path or a
dotted `module.func`), so we expose `edify check TARGET` rather than a separate
`--file/--target` split. Status is derived from CrossHair's exit code
(0/1/2 → verified/refuted/error). A distinct `unknown` status is folded into
`verified` for v0 because CrossHair has no separate exit code for "couldn't
decide" — a timeout returns 0 (no counterexample within budget), which is
exactly our honest definition of `verified`. Vacuous-`verified` (target has no
contract) detection is deferred (noted in Task 8 skill discipline instead).

---

### Task 1: Dependencies + seed fixtures + characterize CrossHair

**Files:**
- Modify: `pyproject.toml` (dependencies)
- Create: `tests/fixtures/check_targets/__init__.py`
- Create: `tests/fixtures/check_targets/head_buggy.py`
- Create: `tests/fixtures/check_targets/head_fixed.py`

- [ ] **Step 1: Add dependencies**

In `pyproject.toml`, add to the `dependencies` list (keep alphabetical-ish with
the existing entries):

```toml
    "crosshair-tool>=0.0.104",
    "icontract>=2.6.0",
```

- [ ] **Step 2: Sync and confirm CrossHair runs under Python 3.14**

Run: `just setup` (or `uv sync`)
Then run: `uv run crosshair --version`
Expected: prints a version, exit 0.

**GATE:** If `uv sync` fails resolving `crosshair-tool` for Python 3.14, or
`crosshair --version` errors, **STOP and report** — CrossHair may not yet
support 3.14. Do not work around silently. (Fallback to discuss with the user:
pin a compatible interpreter for a `check`-only extra, or defer.)

- [ ] **Step 3: Create the seed fixtures**

`tests/fixtures/check_targets/__init__.py`:

```python
"""Fixture targets for `edify check` end-to-end tests."""
```

`tests/fixtures/check_targets/head_buggy.py`:

```python
"""Seed (buggy): head with no precondition.

CrossHair refutes this on the empty list (``xs[0]`` raises ``IndexError``),
demonstrating the spec-refinement branch: the fix is to add a precondition.
"""

from icontract import ensure


@ensure(lambda xs, result: result == xs[0])
def head(xs: list[int]) -> int:
    """Return the first element of xs."""
    return xs[0]
```

`tests/fixtures/check_targets/head_fixed.py`:

```python
"""Seed (fixed): head with a precondition. CrossHair verifies it."""

from icontract import ensure, require


@require(lambda xs: len(xs) > 0)
@ensure(lambda xs, result: result == xs[0])
def head(xs: list[int]) -> int:
    """Return the first element of xs."""
    return xs[0]
```

- [ ] **Step 4: Characterize real CrossHair output (record, do not assert yet)**

Run: `uv run crosshair check --report_verbose tests/fixtures/check_targets/head_buggy.py; echo "exit=$?"`
Expected: a line matching `tests/fixtures/check_targets/head_buggy.py:<line>: error: <message>` on stdout, and `exit=1`.

Run: `uv run crosshair check --report_verbose tests/fixtures/check_targets/head_fixed.py; echo "exit=$?"`
Expected: no `error:` lines, `exit=0`.

If the observed line format or exit codes differ from the above, note the actual
strings — Tasks 4 and 7 assert against this format; adjust those assertions to
the recorded reality before proceeding.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock tests/fixtures/check_targets/
git commit -m "feat: add crosshair/icontract deps and head seed fixtures"
```

---

### Task 2: Result types (`check.py`)

**Files:**
- Create: `src/edify/check.py`
- Test: `tests/test_check_parse.py`

- [ ] **Step 1: Write the failing test**

`tests/test_check_parse.py`:

```python
"""Tests for CrossHair output parsing and check result types."""

from edify.check import CheckResult, CheckStatus, Finding


def test_check_result_defaults() -> None:
    """A CheckResult has empty findings and detail by default."""
    result = CheckResult(status=CheckStatus.VERIFIED, target="foo.py")
    assert result.status is CheckStatus.VERIFIED
    assert result.target == "foo.py"
    assert result.findings == ()
    assert result.detail == ""


def test_finding_fields() -> None:
    """A Finding carries a location and a message."""
    finding = Finding(location="foo.py:3", message="boom")
    assert finding.location == "foo.py:3"
    assert finding.message == "boom"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `just test tests/test_check_parse.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'edify.check'`.

- [ ] **Step 3: Write minimal implementation**

`src/edify/check.py`:

```python
"""Core types and parsing for the ``edify check`` verification command."""

import enum
from dataclasses import dataclass, field


class CheckStatus(enum.StrEnum):
    """Outcome of a CrossHair verification run."""

    VERIFIED = "verified"
    REFUTED = "refuted"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    """A single counterexample CrossHair reported."""

    location: str
    message: str


@dataclass(frozen=True)
class CheckResult:
    """Structured result of checking a target against its contract."""

    status: CheckStatus
    target: str
    findings: tuple[Finding, ...] = ()
    detail: str = field(default="")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `just test tests/test_check_parse.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/edify/check.py tests/test_check_parse.py
git commit -m "feat: add check result types"
```

---

### Task 3: Build CrossHair argv (`check.py`)

**Files:**
- Modify: `src/edify/check.py`
- Test: `tests/test_check_argv.py`

- [ ] **Step 1: Write the failing test**

`tests/test_check_argv.py`:

```python
"""Tests for building the CrossHair invocation argv."""

from edify.check import build_crosshair_argv


def test_argv_basic() -> None:
    """argv invokes `crosshair check --report_verbose` on the target."""
    assert build_crosshair_argv("foo.py") == [
        "crosshair",
        "check",
        "--report_verbose",
        "foo.py",
    ]


def test_argv_with_timeout() -> None:
    """A per-condition timeout is passed as a CrossHair option before target."""
    assert build_crosshair_argv("pkg.mod.fn", per_condition_timeout=5.0) == [
        "crosshair",
        "check",
        "--report_verbose",
        "--per_condition_timeout=5.0",
        "pkg.mod.fn",
    ]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `just test tests/test_check_argv.py -v`
Expected: FAIL with `ImportError: cannot import name 'build_crosshair_argv'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/edify/check.py`:

```python
def build_crosshair_argv(
    target: str,
    *,
    per_condition_timeout: float | None = None,
) -> list[str]:
    """Build the argv for invoking CrossHair's check command on a target.

    Args:
        target: A file path or a dotted ``module.func`` CrossHair target.
        per_condition_timeout: Optional CrossHair ``--per_condition_timeout``.

    Returns:
        The argv list to pass to ``subprocess.run``.
    """
    argv = ["crosshair", "check", "--report_verbose"]
    if per_condition_timeout is not None:
        argv.append(f"--per_condition_timeout={per_condition_timeout}")
    argv.append(target)
    return argv
```

- [ ] **Step 4: Run test to verify it passes**

Run: `just test tests/test_check_argv.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/edify/check.py tests/test_check_argv.py
git commit -m "feat: add crosshair argv builder"
```

---

### Task 4: Parse CrossHair output (`check.py`)

**Files:**
- Modify: `src/edify/check.py`
- Test: `tests/test_check_parse.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_check_parse.py`:

```python
from edify.check import parse_crosshair_output


def test_exit_zero_is_verified() -> None:
    """Exit code 0 means no counterexample within budget → verified."""
    result = parse_crosshair_output(0, "", "", target="foo.py")
    assert result.status is CheckStatus.VERIFIED
    assert result.findings == ()


def test_exit_one_parses_findings() -> None:
    """Exit code 1 parses `file:line: error: msg` lines into findings."""
    stdout = (
        "foo.py:3: error: false when calling head(xs = []) (which raises "
        "IndexError: list index out of range)\n"
    )
    result = parse_crosshair_output(1, stdout, "", target="foo.py")
    assert result.status is CheckStatus.REFUTED
    assert len(result.findings) == 1
    assert result.findings[0].location == "foo.py:3"
    assert "IndexError" in result.findings[0].message


def test_exit_two_is_error_with_detail() -> None:
    """Exit code 2 is an error; stderr is preserved as detail."""
    result = parse_crosshair_output(2, "", "Traceback: boom", target="foo.py")
    assert result.status is CheckStatus.ERROR
    assert result.detail == "Traceback: boom"


def test_findings_ignore_non_error_lines() -> None:
    """Non-matching stdout lines are ignored when collecting findings."""
    stdout = "Analyzing 1 function\nfoo.py:3: error: bad\n"
    result = parse_crosshair_output(1, stdout, "", target="foo.py")
    assert len(result.findings) == 1
    assert result.findings[0].message == "bad"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `just test tests/test_check_parse.py -v`
Expected: FAIL with `ImportError: cannot import name 'parse_crosshair_output'`.

- [ ] **Step 3: Write minimal implementation**

Add to the top imports of `src/edify/check.py` (with the existing imports):

```python
import re
```

Append to `src/edify/check.py`:

```python
_FINDING_RE = re.compile(r"^(?P<location>.+?:\d+): error: (?P<message>.*)$")


def parse_crosshair_output(
    exit_code: int,
    stdout: str,
    stderr: str,
    *,
    target: str,
) -> CheckResult:
    """Map a CrossHair run to a CheckResult.

    Exit codes (CrossHair contract): 0 = no counterexample within budget,
    1 = counterexample(s) found, 2 (or other) = error.

    Args:
        exit_code: CrossHair process return code.
        stdout: Captured standard output (machine-readable error lines).
        stderr: Captured standard error (context for errors).
        target: The target that was checked, echoed into the result.

    Returns:
        A CheckResult whose status reflects the exit code.
    """
    if exit_code == 0:
        return CheckResult(status=CheckStatus.VERIFIED, target=target)
    if exit_code == 1:
        findings = tuple(
            Finding(
                location=match.group("location"),
                message=match.group("message"),
            )
            for line in stdout.splitlines()
            if (match := _FINDING_RE.match(line.strip()))
        )
        return CheckResult(
            status=CheckStatus.REFUTED,
            target=target,
            findings=findings,
            detail=stdout.strip(),
        )
    return CheckResult(
        status=CheckStatus.ERROR,
        target=target,
        detail=(stderr.strip() or stdout.strip()),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `just test tests/test_check_parse.py -v`
Expected: PASS (6 passed total in the file).

- [ ] **Step 5: Commit**

```bash
git add src/edify/check.py tests/test_check_parse.py
git commit -m "feat: parse crosshair output into check results"
```

---

### Task 5: CLI handler + exception (`check_cli.py`, `exceptions.py`)

**Files:**
- Modify: `src/edify/exceptions.py`
- Create: `src/edify/check_cli.py`
- Test: `tests/test_cli_check.py`

- [ ] **Step 1: Write the failing test**

`tests/test_cli_check.py`:

```python
"""Integration tests for the check CLI handler (subprocess mocked)."""

import json

import pytest
from pytest_mock import MockerFixture

from edify.check import CheckResult, CheckStatus, Finding
from edify.check_cli import handle_check, run_crosshair
from edify.exceptions import CrossHairUnavailableError


def test_run_crosshair_maps_subprocess(mocker: MockerFixture) -> None:
    """run_crosshair runs the argv and parses the result."""
    completed = mocker.Mock(returncode=1, stdout="foo.py:3: error: bad", stderr="")
    mocker.patch("edify.check_cli.subprocess.run", return_value=completed)

    result = run_crosshair("foo.py")

    assert result.status is CheckStatus.REFUTED
    assert result.findings[0].message == "bad"


def test_run_crosshair_missing_binary(mocker: MockerFixture) -> None:
    """A missing crosshair executable raises CrossHairUnavailableError."""
    mocker.patch("edify.check_cli.subprocess.run", side_effect=FileNotFoundError)
    with pytest.raises(CrossHairUnavailableError):
        run_crosshair("foo.py")


def test_handle_check_verified_exits_zero(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A verified result prints a check line and exits 0."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py")
    assert exc.value.code == 0
    assert "verified" in capsys.readouterr().out


def test_handle_check_refuted_exits_one_json(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A refuted result with --json prints structured findings and exits 1."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.REFUTED,
            target="foo.py",
            findings=(Finding(location="foo.py:3", message="bad"),),
        ),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py", json_output=True)
    assert exc.value.code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "refuted"
    assert payload["findings"][0]["location"] == "foo.py:3"


def test_handle_check_error_exits_two(
    mocker: MockerFixture,
) -> None:
    """An error result exits with code 2."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.ERROR, target="foo.py", detail="boom"
        ),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py")
    assert exc.value.code == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `just test tests/test_cli_check.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'edify.check_cli'`.

- [ ] **Step 3: Write the exception**

Append to `src/edify/exceptions.py`:

```python
class CrossHairUnavailableError(ClaudeUtilsError):
    """Raised when the CrossHair executable cannot be found."""

    def __init__(self) -> None:
        """Initialize with an actionable install hint."""
        super().__init__(
            "CrossHair is not available. Run `uv sync` "
            "(crosshair-tool is a project dependency)."
        )
```

- [ ] **Step 4: Write the handler**

`src/edify/check_cli.py`:

```python
"""CLI handler for the ``check`` subcommand."""

import json
import subprocess  # noqa: S404
import sys

from edify.check import (
    CheckResult,
    CheckStatus,
    build_crosshair_argv,
    parse_crosshair_output,
)
from edify.exceptions import CrossHairUnavailableError

_EXIT_CODES = {
    CheckStatus.VERIFIED: 0,
    CheckStatus.REFUTED: 1,
    CheckStatus.ERROR: 2,
}


def run_crosshair(
    target: str,
    *,
    per_condition_timeout: float | None = None,
) -> CheckResult:
    """Run CrossHair on a target and return a structured result.

    Raises:
        CrossHairUnavailableError: if the crosshair executable is missing.
    """
    argv = build_crosshair_argv(target, per_condition_timeout=per_condition_timeout)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, check=False)  # noqa: S603
    except FileNotFoundError as exc:
        raise CrossHairUnavailableError from exc
    return parse_crosshair_output(
        proc.returncode, proc.stdout, proc.stderr, target=target
    )


def _print_human(result: CheckResult) -> None:
    """Print a human-readable rendering of a check result."""
    if result.status is CheckStatus.VERIFIED:
        print(f"verified: {result.target} (no counterexample within budget)")
    elif result.status is CheckStatus.REFUTED:
        print(f"refuted: {result.target}")
        for finding in result.findings:
            print(f"  {finding.location}: {finding.message}")
    else:
        print(f"error: {result.target}", file=sys.stderr)
        if result.detail:
            print(result.detail, file=sys.stderr)


def handle_check(
    target: str,
    *,
    per_condition_timeout: float | None = None,
    json_output: bool = False,
) -> None:
    """Run a check and exit with a status-derived code.

    Exit codes: 0 verified, 1 refuted, 2 error.
    """
    result = run_crosshair(target, per_condition_timeout=per_condition_timeout)
    if json_output:
        print(
            json.dumps(
                {
                    "status": result.status.value,
                    "target": result.target,
                    "findings": [
                        {"location": f.location, "message": f.message}
                        for f in result.findings
                    ],
                    "detail": result.detail,
                }
            )
        )
    else:
        _print_human(result)
    sys.exit(_EXIT_CODES[result.status])
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `just test tests/test_cli_check.py -v`
Expected: PASS (5 passed).

- [ ] **Step 6: Commit**

```bash
git add src/edify/check_cli.py src/edify/exceptions.py tests/test_cli_check.py
git commit -m "feat: add check CLI handler and crosshair runner"
```

---

### Task 6: Wire the `check` command (`cli.py`)

**Files:**
- Modify: `src/edify/cli.py`
- Test: `tests/test_cli_check.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_cli_check.py`:

```python
from click.testing import CliRunner

from edify.cli import cli


def test_check_help_lists_target_and_json() -> None:
    """`edify check --help` documents the TARGET arg and --json flag."""
    result = CliRunner().invoke(cli, ["check", "--help"])
    assert result.exit_code == 0
    assert "TARGET" in result.output
    assert "--json" in result.output


def test_check_command_invokes_handler(mocker: MockerFixture) -> None:
    """`edify check foo.py` routes to run_crosshair with that target."""
    spy = mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    result = CliRunner().invoke(cli, ["check", "foo.py"])
    assert result.exit_code == 0
    spy.assert_called_once_with("foo.py", per_condition_timeout=None)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `just test "tests/test_cli_check.py::test_check_help_lists_target_and_json" -v`
Expected: FAIL — `check` is not a registered command (exit_code != 0 / "No such command").

- [ ] **Step 3: Wire the command**

In `src/edify/cli.py`, add to the imports (next to the other handler imports):

```python
from edify.check_cli import handle_check
```

Add this command (place it after the `tokens` command definition):

```python
@cli.command(help="Verify a Python target against its icontract contract")
@click.argument("target")
@click.option(
    "--timeout",
    "per_condition_timeout",
    type=float,
    default=None,
    help="Per-condition timeout in seconds (CrossHair --per_condition_timeout)",
)
@click.option("--json", "json_output", is_flag=True, help="Output JSON")
def check(
    target: str,
    per_condition_timeout: float | None,
    *,
    json_output: bool,
) -> None:
    """Check TARGET (file path or dotted module.func) against its contract."""
    handle_check(
        target,
        per_condition_timeout=per_condition_timeout,
        json_output=json_output,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `just test tests/test_cli_check.py -v`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
git add src/edify/cli.py tests/test_cli_check.py
git commit -m "feat: register edify check command"
```

---

### Task 7: End-to-end test against the real seed (no mocks)

**Files:**
- Create: `tests/test_check_e2e.py`

- [ ] **Step 1: Write the test**

`tests/test_check_e2e.py`:

```python
"""End-to-end checks invoking real CrossHair on the seed fixtures.

These run the actual solver and are slower than the mocked tests.
"""

from pathlib import Path

from edify.check import CheckStatus
from edify.check_cli import run_crosshair

_FIXTURES = Path(__file__).parent / "fixtures" / "check_targets"


def test_buggy_head_is_refuted() -> None:
    """The no-precondition head is refuted (empty-list counterexample)."""
    result = run_crosshair(
        str(_FIXTURES / "head_buggy.py"), per_condition_timeout=10.0
    )
    assert result.status is CheckStatus.REFUTED
    assert result.findings


def test_fixed_head_is_verified() -> None:
    """Adding the precondition makes head verify."""
    result = run_crosshair(
        str(_FIXTURES / "head_fixed.py"), per_condition_timeout=10.0
    )
    assert result.status is CheckStatus.VERIFIED
```

- [ ] **Step 2: Run the test**

Run: `just test tests/test_check_e2e.py -v`
Expected: PASS (2 passed). If `test_buggy_head_is_refuted` reports VERIFIED, the
recorded format/exit codes from Task 1 Step 4 differ — reconcile the parser
(Task 4) with the real output before continuing. If timing is flaky, raise
`per_condition_timeout`.

- [ ] **Step 3: Commit**

```bash
git add tests/test_check_e2e.py
git commit -m "test: end-to-end crosshair check on seed fixtures"
```

---

### Task 8: The `formalize` skill

**Files:**
- Create: `plugin/skills/formalize/SKILL.md`

- [ ] **Step 1: Write the skill**

`plugin/skills/formalize/SKILL.md`:

```markdown
---
name: formalize
description: >-
  Verify a Python function against its intended behavior by writing an icontract
  contract and checking it with `edify check` (CrossHair), repairing in a loop.
  Triggers on "formalize", "verify this function", "add a contract and check it",
  or after writing a function whose correctness matters. The in-context agent
  holds intent and asks the user when behavior is ambiguous; CrossHair owns the
  deduction.
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - AskUserQuestion
user-invocable: true
---

# Formalize and Check a Function

Drive a propose-contract -> check -> repair loop around one Python function.
The verifier (`edify check`, backed by CrossHair) owns deduction. You own
*intent*: what the function should guarantee. Verification proves code meets a
contract; it does NOT prove the contract is the right one. That judgment is
yours, and when intent is genuinely ambiguous you ASK rather than guess.

## Procedure

1. **Establish intent.** Derive what the target function should guarantee from
   the conversation and the surrounding code. If the intended behavior is
   genuinely ambiguous (edge cases, error handling, empty inputs), use
   `AskUserQuestion` — do not invent a specification.

2. **Write the contract.** Add `icontract` decorators to the function:
   `@require(lambda <args>: <precondition>)` and
   `@ensure(lambda <args>, result: <postcondition>)`. A target needs at least
   one pre/post-condition or CrossHair will not analyze it.

3. **Check.** Run:

   ```
   edify check <file-or-dotted-target> --json
   ```

   The result status is one of `verified`, `refuted`, or `error`.

4. **Interpret — the core judgment:**
   - `verified` — no counterexample within CrossHair's search budget. Report and
     stop. State the honest guarantee level: bounded path-exploration, not a
     total proof.
   - `refuted` — read the counterexample (falsifying input + location), then
     decide *why* it failed:
     - **code bug** — the implementation is wrong: fix the code.
     - **spec bug** — the contract was wrong or too strong: fix the contract.
     - **intent ambiguity** — the counterexample exposes a case the user has not
       decided (e.g. "what should this do on an empty list?"): STOP and ask.
     Then loop back to step 3.
   - `error` — surface it. A common cause is a target with no contract (CrossHair
     analyzed nothing); add a contract. Never report `error` as success.

5. **Loop with a cap.** Do at most a small fixed number of repair iterations
   (e.g. 5). If you hit the cap, STOP and report the honest state: the last
   counterexample and what remains unresolved. Never upgrade `refuted` or an
   error to "verified".

## Disciplines

- Ambiguity about intent -> ask, never guess.
- Every counterexample gets an explicit code-bug vs spec-bug triage.
- No "verified" claim without a `verified` result from `edify check`.
- A `verified` result is bounded, not a soundness/termination proof — say so.

## Backend

`edify check` wraps CrossHair (symbolic execution + Z3). It is the deduction
oracle; this skill is the intent-holder. See
`docs/superpowers/specs/2026-06-08-invariant-guided-verify-loop-design.md`.
```

- [ ] **Step 2: Verify the skill is discoverable**

Run: `rg -n "name: formalize" plugin/skills/formalize/SKILL.md`
Expected: matches the frontmatter line.

- [ ] **Step 3: Commit**

```bash
git add plugin/skills/formalize/SKILL.md
git commit -m "feat: add formalize verify-loop skill"
```

---

### Task 9: Docs + full precommit

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update the skill and CLI lists in CLAUDE.md**

In `CLAUDE.md`, in the CLI section, add `check` to the tool list:

```markdown
- **Contract checking** — `edify check <target>` (CrossHair verification)
```

In the Skills section, add `formalize` to the invocable skills list:

```markdown
In `plugin/skills/`, invoked via slash command: `proof`, `ground`,
`requirements`, `deliverable-review`, `token-efficient-bash`, `formalize`.
```

- [ ] **Step 2: Run the full precommit gate**

Run: `just precommit`
Expected: full output, all green (ruff clean, mypy clean, pytest all pass / 1
xfail as before). Show the complete output — do not truncate. If ruff/mypy flag
the new files, fix them and re-run `just precommit` (do not finish steps
manually).

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: list edify check and formalize in CLAUDE.md"
```

---

## Self-Review

**Spec coverage:**
- §1 backend = CrossHair → Tasks 1,4,5,7. ✓
- §2 validation-vs-verification principle → encoded in Task 8 skill. ✓
- §3 `edify check` CLI (input, action, structured output, icontract, exit codes,
  no-contract error) → Tasks 2–6. **Deviation recorded:** positional `TARGET`
  replaces `<file> --target` (CrossHair targets natively); `unknown` folded into
  `verified` (no CrossHair exit code for it); vacuous-`verified`/no-contract
  detection deferred to the skill discipline rather than the CLI. All three are
  documented in the scoping notes above.
- §4 `formalize` skill (intent, contract, check, interpret, loop+cap) → Task 8. ✓
- §5 seed → Task 1, **changed from `average` to `head`** (float flakiness),
  rationale recorded. ✓
- §6 testing (TDD, fixtures with known verdicts, precommit green) → all tasks +
  Task 9. ✓
- §7 non-goals → not built (no eval harness, no Nagini, single function, no
  requirements-skill changes). ✓

**Placeholder scan:** no TBD/TODO; every code/test step shows complete content;
every command has an expected result. ✓

**Type consistency:** `CheckStatus`, `Finding(location,message)`,
`CheckResult(status,target,findings,detail)`, `build_crosshair_argv`,
`parse_crosshair_output(exit_code,stdout,stderr,*,target)`, `run_crosshair`,
`handle_check` are used identically across Tasks 2–7. ✓
