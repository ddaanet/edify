# Item 1.2 slice 1 — test review (RED phase)

Verdict: **RED confirmed.**

## Pytest before fixes

```
# Test Report

**Summary:** 0/1 passed, 1 failed

## Failures

### tests/test_review_range.py::test_first_pass_emits_range FAILED

```python
tests/test_review_range.py:77: in test_first_pass_emits_range
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
E   AssertionError: assert '' == 'RANGE: 4125c...b4244..HEAD\n'
E
E     - RANGE: 4125c25d643b03550745f77b7aa0be608a3b4244..HEAD
```
```

One test, FAILED on the stdout assertion. No PASSED, no ERROR — the stub
resolves by bare name and exits 0, so the red is on the assertion and not on
a missing script or a PATH problem.

## Findings

### 1. Critical — the fixture could not discriminate a script that ignores the artifact

`_init_repo` made a **single** commit, so the repo's first commit *was*
`HEAD`. The assertion `stdout == f"RANGE: {sha}..HEAD\n"` was therefore
satisfied by a script that never reads `Base:` at all and simply emits
`git rev-parse HEAD`. That is precisely the recomputation
`design-content-rules.md` §Provenance forbids and the error KD-2's script
exists to prevent — the test named it and could not fail on it.

Measured, not reasoned. I mutated the stub to the wrong-reason script:

```bash
cd "$(dirname "$1")"
printf 'RANGE: %s..HEAD\n' "$(git rev-parse HEAD)"
```

- Against the **original single-commit fixture**: the assertion **passes**
  (verified by replaying that fixture against the mutated script —
  `would the assertion pass? True`).
- Against the **fixed fixture**: FAILS, with the two shas visibly different:

```
E   AssertionError: assert 'RANGE: 7204b...66c6f..HEAD\n' == 'RANGE: 88431...5f67d..HEAD\n'
E     - RANGE: 88431fba6d3f83a50c513ffb5c00c2ccf3a5f67d..HEAD
E     + RANGE: 7204bf4642ce23e98c22e9acf8912c2dd1e66c6f..HEAD
```

The stub was reverted to inert immediately after; `plugin/bin/edify-review-range.sh`
is byte-identical to how the RED phase left it and shellcheck is clean.

**Change:** `_init_repo` now makes two commits and returns the **first**
commit's sha (still "the repo's first commit", as the slice specifies), with
the reason stated in its docstring. This also gives slices 2, 3 and 7 the
"later commit than the prior's" they need.

### 2. Major — `_run_git` violated D-21 (test setup fails self-diagnosingly)

`subprocess.run(..., check=True, capture_output=True)` swallows stderr, so a
fixture failure surfaces as a bare `CalledProcessError` naming a command and
an exit code. `docs/design.md` D-21 names this exact shape.

**Change:** `_run_git` uses `check=False` with an explicit assertion carrying
both streams, and returns stdout (which also removed the duplicated inline
`subprocess.run` for `rev-parse`).

### 3. Major — the throwaway repo inherited user and system git config

Local `user.name`/`user.email` were set, which the brief asked for, but the
repo still read `~/.gitconfig` and `/etc/gitconfig`. A global `core.hooksPath`
or `commit.gpgsign=true` — neither present on this box, both common
elsewhere and in CI — would break `git commit` in the fixture and make the
test fail for a reason unrelated to the SUT.

**Change:** `_run_git` sets `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to
`os.devnull`, and `git init` gained `-b main` so the now-unset
`init.defaultBranch` does not emit its hint. This is hardening against an
environment I did not observe here; it is not a defect I reproduced.

### 4. Minor — no way to vary the artifact body (reusability, per the brief)

The artifact body was written inline in the test. Slices 2–8 need a prior
artifact, a differing `Base:`, missing sections, a wrapped `Derived from:`
and a spaced path.

**Change:** extracted `_write_artifact(path, derived_from, base)`, which
creates parent directories and emits the `## Provenance` shape. It is
deliberately minimal — it parameterises the two fields slices 2, 3 and 7
vary. Slices 4 (no section), 5 (unresolvable base) and 8 (wrapped value) will
need their own writers or extra parameters; **flagged, not designed now.**

### 5. Minor — `PATH` joined with a literal `:`

**Change:** `os.pathsep`. Cosmetic on Linux; no behavioural difference here.

## Checks that were already correct

- `sha` is the fixture's own `git rev-parse` output, full 40 hex chars, not
  hardcoded and not truncated.
- Exit code **is** asserted (`result.returncode == 0`), with stdout+stderr
  attached to the failure message.
- The artifact carries `- **Derived from:** none` and ``- **Base:** `<sha>` ``
  under a `## Provenance` heading — the shape
  `design-content-rules.md` §Provenance Section prescribes, backtick-quoted
  sha included.
- Invocation is by **bare name** — `["edify-review-range.sh", str(artifact)]`
  — with `PATH` built from the checkout's `plugin/bin`, and `cwd` set to
  `tmp_path / "elsewhere"`, outside the git repo. The artifact is an absolute
  path.
- `check=False` and `text=True` on the SUT call; no `shell=True`; no
  `2>/dev/null`; no `# noqa`.
- The `## Requirements` heading after §Provenance gives the parser a section
  terminator to stop at, which slices 4 and 8 will lean on.

## Pytest after fixes

```
# Test Report

**Summary:** 0/1 passed, 1 failed

## Failures

### tests/test_review_range.py::test_first_pass_emits_range FAILED

```python
tests/test_review_range.py:104: in test_first_pass_emits_range
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
E   AssertionError: assert '' == 'RANGE: 654b6...ca484..HEAD\n'
E
E     - RANGE: 654b6c3a22fadb6fd375efe31b2fdd2bd7dca484..HEAD
```
```

Still red, still on the stdout assertion, still no ERROR.

## Lint

- `ruff check tests/test_review_range.py` — All checks passed (one D205 was
  introduced by my `_write_artifact` docstring and fixed).
- `mypy tests/test_review_range.py` — clean.
- `docformatter -c tests/test_review_range.py` — exit 0.
- `shellcheck plugin/bin/edify-review-range.sh` — clean.

## Scope

Touched `tests/test_review_range.py` only. The stub was mutated and reverted
for the probe in finding 1 and is unchanged on disk. Nothing committed;
`git status --porcelain` shows the same three untracked paths as at start.
