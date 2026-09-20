# Item 1.2 slice 1 — RED

## Fixture design

`tests/test_review_range.py` builds everything under `tmp_path`:

- `_init_repo(repo)`: `mkdir`, `git init -q`, sets `user.name`/`user.email`
  locally, writes `README.md`, commits it, and returns the full sha of that
  first commit via `git rev-parse HEAD`.
- The test then creates `plans/job/outline.md` inside that repo with a
  `## Provenance` section: `**Derived from:** none` and `**Base:** \`<sha>\``
  (the design-content-rules.md / outline.md shape).
- `_run_review_range(artifact, cwd)` runs `edify-review-range.sh` **by bare
  name** via `subprocess.run(["edify-review-range.sh", str(artifact)], cwd=cwd,
  env=env, capture_output=True, text=True, check=False)`, with
  `env["PATH"] = f"{BIN_DIR}:{env.get('PATH', '')}"` where
  `BIN_DIR = Path(__file__).resolve().parents[1] / "plugin" / "bin"`.
- The test's `cwd` is `tmp_path / "elsewhere"` — a sibling directory outside
  the git repo — and the artifact is passed as an absolute path, matching the
  "repo located from the artifact's directory" contract in KD-2.

## Test body

`test_first_pass_emits_range`: builds the repo and artifact as above, runs
the script from `elsewhere`, and asserts `result.returncode == 0` and
`result.stdout == f"RANGE: {sha}..HEAD\n"` (exact match, trailing newline
included).

## Stub

`plugin/bin/edify-review-range.sh`: `#!/usr/bin/env bash`, `set -euo
pipefail`, executable, and inert — no parsing, no output, exits 0 printing
nothing. GREEN implements the contract.

## Verbatim pytest output (red)

```
# Test Report

**Summary:** 0/1 passed, 1 failed

## Failures

### tests/test_review_range.py::test_first_pass_emits_range FAILED

```python
tests/test_review_range.py:77: in test_first_pass_emits_range
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
E   AssertionError: assert '' == 'RANGE: 0ec82...8cd4c..HEAD\n'
E     
E     - RANGE: 0ec82dd0b4a563d861e5639308c3ed629ac8cd4c..HEAD
```
```

The failure is on the stdout assertion (stub prints nothing) — not an error
from a missing script or a PATH problem — confirming the fixture and PATH
wiring are correct and the red is genuine.

## Lint

- `ruff check tests/test_review_range.py` — all checks passed (a D205 summary-line
  issue was found and fixed by splitting the module docstring's first line).
- `mypy tests/test_review_range.py` — no output, clean.
- `shellcheck plugin/bin/edify-review-range.sh` — no output, clean.

(`ruff check plugin/bin/` also flagged pre-existing issues in
`bump-plugin-version.py` and `check-version-consistency.py`, unrelated to
this slice and out of scope — not touched.)

## Scope

Touched: `plugin/bin/edify-review-range.sh` (stub only),
`tests/test_review_range.py`. Nothing committed — stub and test left
uncommitted per instructions.
