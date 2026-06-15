# L7 Vacuity Warning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `edify check` report the per-condition budget on every `verified` result and warn (stderr + JSON `vacuity_warning`) when the verdict used CrossHair's unspecified default budget.

**Architecture:** All changes live in `src/edify/check_cli.py` (`handle_check`, `_print_human`), which already receive `per_condition_timeout`. The pure core (`check.py`: `CheckResult`, `parse_crosshair_output`, `build_crosshair_argv`) is untouched, preserving NFR1/NFR2 and the CrossHair-verified parse contract (D9). The warning is derived from `(result.status is VERIFIED, per_condition_timeout is None)` — no invented number, no second CrossHair run.

**Tech Stack:** Python 3.14, Click, pytest + pytest-mock, icontract/CrossHair (`edify check`). Spec: `docs/superpowers/specs/2026-06-15-l7-vacuity-warning-design.md`.

---

### Task 1: JSON `budget` + `vacuity_warning` fields

**Files:**
- Modify: `src/edify/check_cli.py` (`handle_check`, JSON branch)
- Test: `tests/test_cli_check.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_cli_check.py`:

```python
def test_handle_check_verified_json_flags_vacuity_no_timeout(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verified with no --timeout sets vacuity_warning=true, budget=null in JSON."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py", json_output=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["budget"] is None
    assert payload["vacuity_warning"] is True


def test_handle_check_verified_json_no_warning_with_timeout(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verified with --timeout reports the budget and clears vacuity_warning."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py", per_condition_timeout=30.0, json_output=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["budget"] == 30.0
    assert payload["vacuity_warning"] is False


def test_handle_check_refuted_json_not_vacuous(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Refuted is never vacuous, even with no --timeout."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.REFUTED,
            target="foo.py",
            findings=(Finding(location="foo.py:3", message="bad"),),
        ),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py", json_output=True)
    payload = json.loads(capsys.readouterr().out)
    assert payload["vacuity_warning"] is False
    assert payload["budget"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `just test tests/test_cli_check.py -k vacuit -v`
Expected: FAIL with `KeyError: 'budget'` / `KeyError: 'vacuity_warning'`.

- [ ] **Step 3: Implement the JSON fields**

In `src/edify/check_cli.py`, change the signature of `handle_check` to compute the flag, and add the two keys to the JSON payload. The full updated `handle_check`:

```python
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
    vacuity_warning = (
        result.status is CheckStatus.VERIFIED and per_condition_timeout is None
    )
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
                    "budget": per_condition_timeout,
                    "vacuity_warning": vacuity_warning,
                }
            )
        )
    else:
        _print_human(result, per_condition_timeout)
    sys.exit(_EXIT_CODES[result.status])
```

Note: `_print_human(result, per_condition_timeout)` gains an argument here — Task 2 updates `_print_human` itself. Until then it will not match; if running Task 1 in isolation, temporarily call `_print_human(result)` and switch in Task 2. (Subagent-driven execution does Task 1 then Task 2 back-to-back, so prefer the two-arg call shown above and complete Task 2 before running the human-path tests.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `just check && just test tests/test_cli_check.py -k vacuit -v`
Expected: the three new JSON tests PASS; lint clean.

- [ ] **Step 5: Commit**

```bash
git add src/edify/check_cli.py tests/test_cli_check.py
git commit -m "feat: add budget and vacuity_warning to edify check --json"
```

---

### Task 2: Human-readable budget line + stderr vacuity warning

**Files:**
- Modify: `src/edify/check_cli.py` (`_print_human`)
- Test: `tests/test_cli_check.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_cli_check.py`:

```python
def test_handle_check_verified_warns_on_stderr_no_timeout(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verified with no --timeout emits a vacuity warning to stderr."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py")
    captured = capsys.readouterr()
    assert "default budget" in captured.out
    assert "--timeout" in captured.err
    assert "vacuous" in captured.err


def test_handle_check_verified_reports_budget_with_timeout(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verified with --timeout reports the budget and emits no stderr warning."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py", per_condition_timeout=30.0)
    captured = capsys.readouterr()
    assert "30" in captured.out
    assert captured.err == ""


def test_handle_check_refuted_no_warning(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Refuted with no --timeout emits no vacuity warning to stderr."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.REFUTED,
            target="foo.py",
            findings=(Finding(location="foo.py:3", message="bad"),),
        ),
    )
    with pytest.raises(SystemExit):
        handle_check("foo.py")
    assert "vacuous" not in capsys.readouterr().err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `just test tests/test_cli_check.py -k "warns or reports_budget or refuted_no_warning" -v`
Expected: FAIL — `_print_human` takes one positional arg (TypeError) or the stderr/budget text is absent.

- [ ] **Step 3: Implement the budget line and warning**

Replace `_print_human` in `src/edify/check_cli.py` with:

```python
_VACUITY_WARNING = (
    "warning: verified at CrossHair's default budget (no --timeout given); "
    "this verdict may be vacuous if the contract's interesting paths were "
    "never explored. Re-run with --timeout to harden it."
)


def _print_human(result: CheckResult, per_condition_timeout: float | None) -> None:
    """Print a human-readable rendering of a check result."""
    if result.status is CheckStatus.VERIFIED:
        if per_condition_timeout is None:
            print(
                f"verified: {result.target} "
                "(no counterexample within CrossHair's default budget)"
            )
            print(_VACUITY_WARNING, file=sys.stderr)
        else:
            print(
                f"verified: {result.target} "
                f"(no counterexample within {per_condition_timeout} s "
                "per-condition budget)"
            )
    elif result.status is CheckStatus.REFUTED:
        print(f"refuted: {result.target}")
        for finding in result.findings:
            print(f"  {finding.location}: {finding.message}")
    else:
        print(f"error: {result.target}", file=sys.stderr)
        if result.detail:
            print(result.detail, file=sys.stderr)
```

If Task 1 left a temporary one-arg `_print_human(result)` call in `handle_check`, switch it to `_print_human(result, per_condition_timeout)` now.

- [ ] **Step 4: Run the full check suite to verify pass and no regressions**

Run: `just check && just test tests/test_cli_check.py -v`
Expected: all tests PASS (new + the original `test_handle_check_verified_exits_zero` which asserts `"verified" in out` — still true); lint clean.

- [ ] **Step 5: Commit**

```bash
git add src/edify/check_cli.py tests/test_cli_check.py
git commit -m "feat: report budget and warn on vacuous verified in edify check"
```

---

### Task 3: Update the living design doc

**Files:**
- Modify: `docs/superpowers/design/invariant-guided-verify-loop.md`

- [ ] **Step 1: Add the new FR**

In the FR table, add a row after FR11 (renumber not required — append as FR12):

```markdown
| FR12 | A `verified` result reports the per-condition budget; with no `--timeout` it warns (stderr + JSON `vacuity_warning`) that the verdict used CrossHair's default budget and may be vacuous. | Done | `check_cli.py:handle_check`, `_print_human` · `test_cli_check.py::test_handle_check_verified_warns_on_stderr_no_timeout`, `::test_handle_check_verified_json_flags_vacuity_no_timeout` |
```

- [ ] **Step 2: Amend FR5**

Change the FR5 row's requirement text to note the added JSON keys:

```markdown
| FR5 | `--json` emits `{status, target, findings, detail, budget, vacuity_warning}`; default is human-readable. | Done | `check_cli.py:handle_check`, `_print_human` · `test_cli_check.py::test_handle_check_refuted_exits_one_json`, `::test_handle_check_verified_json_flags_vacuity_no_timeout` |
```

- [ ] **Step 3: Update the L7 disposition**

Change the L7 row's disposition (rightmost cell) to record the resolution:

```markdown
| L7 | **Default-budget `verified` can be vacuous.** When `--timeout` is omitted no `--per_condition_timeout` reaches CrossHair, and on a target whose interesting paths need specific synthesized input (e.g. two matching backticks) the default budget may never reach them — returning `verified` while the contract holds only emptily. Demonstrated in D10: a contract-violating bug passed at default budget, refuted only at `--timeout 30`. | **Surfaced (FR12, 2026-06-15):** `edify check` now reports the budget and warns when a `verified` used CrossHair's default budget (stderr + JSON `vacuity_warning`). A minimum-budget floor and an auto-probe vacuity guard were deliberately rejected — a fixed floor is an ungrounded threshold (D10 only flipped one target at 30 s), and auto-probing belongs in `formalize`, not the `check` primitive. The falsification-probe discipline still backs it. |
```

- [ ] **Step 4: Add a history-table row**

Add to the history table at the bottom:

```markdown
| 2026-06-15 | L7 hardened by surfacing, not fixing or detecting: `edify check` reports the per-condition budget on a `verified` result and warns (stderr + JSON `vacuity_warning`) when the verdict used CrossHair's default budget (FR12). Minimum-budget floor and auto-probe both rejected as ungrounded / misplaced. Spec: `specs/2026-06-15-l7-vacuity-warning-design.md`. |
```

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/design/invariant-guided-verify-loop.md
git commit -m "docs: record L7 vacuity-warning surfacing (FR12) in living design"
```

---

## Self-Review

**Spec coverage:**
- §3 verified-only behavior + budget line → Task 2. ✓
- §3 stderr warning, no asserted default value → Task 2 (`_VACUITY_WARNING` names no number). ✓
- §4 JSON `budget` + `vacuity_warning` → Task 1. ✓
- §5 logic in `check_cli.py`, `check.py` untouched → Tasks 1–2 touch only `check_cli.py`. ✓
- §6 testing matrix (verified±timeout, refuted, error) → Tasks 1–2 tests cover verified-no-timeout, verified-timeout, refuted; error path already covered by `test_handle_check_error_exits_two` (its stderr has no "vacuous" — implicitly fine, JSON `vacuity_warning` false because status≠VERIFIED). ✓
- §7 out-of-scope (no floor, no auto-probe, no core change) → respected; no task adds them. ✓
- §8 living-design updates → Task 3. ✓

**Placeholder scan:** No TBD/TODO; every code step shows full code. The cross-task note about the temporary one-arg call is an explicit ordering instruction, not a placeholder.

**Type consistency:** `handle_check(target, *, per_condition_timeout=None, json_output=False)` unchanged signature; `_print_human(result, per_condition_timeout)` — two-arg form used consistently in Task 1 (handle_check call) and Task 2 (definition). JSON keys `budget`/`vacuity_warning` named identically across Task 1 code and Task 3 doc rows.
