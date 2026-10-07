# Review: Item 2.4 slice 1 — test review

**Scope**: `tests/test_build_prose_git_log.py` (uncommitted, new) and
`plans/review-fixes-3/reports/item-2-4-s1-red.md`. The six scanned prose
files are the SUT and are out of scope; none was edited.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The RED is genuine. All six cases from the five unflagged files fail on the
hash-only assertion `assert not stray`, with a `Good "git" signature …` line
on stdout. The three `finishing.md` cases pass. The extraction found all nine
`git log … --format=%H` commands in the six files, which I checked by grep.
The fixes harden the test for the state after GREEN. The fixture now asserts
its own discriminating state. A command the extractor misses now fails
instead of being dropped. A wrapped inline span is now found. Config injected
through the environment can no longer turn off `log.showSignature`.

**Overall Assessment**: Ready

## Mechanical first check

Before the fixes, `.venv/bin/pytest -p no:markdown_report
tests/test_build_prose_git_log.py` gave 6 failed and 3 passed. Each failure
was at the `assert not stray` line. There was no ERROR, no extraction or
placeholder failure, and no non-zero exit. This matches the RED report's
table.

Coverage was checked by running `command grep -n 'git log'` on each scanned
file and comparing the result with the extracted list.

| File | `git log` with `--format=%H` (line) | Extracted |
|---|---|---|
| phase-boundary.md | 31–32 (fence, continuation) | :1 |
| tdd-slice.md | 57–58 (fence, continuation) | :1 |
| escalation.md | 105 (inline span in a list item) | :1 |
| tdd-auditor.md | 87–88 (indented fence in a list item, continuation) | :1 |
| build-run-state.md | 28–29, 46–47 (fences, continuations) | :1, :2 |
| finishing.md | 17, 18 (fence), 142 (inline span) | :1, :2, :3 |

The other `git log` mentions are excluded on purpose: they carry no
`--format=%H`, as KD-7 scopes it. They are escalation.md:78,
tdd-auditor.md:60–61 and 227, and build-run-state.md:189.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Nothing guards the fixture's discriminating state once GREEN lands**
   - Location: `signed_repo` fixture
   - Problem: once GREEN lands, all nine cases pass. They pass for the right
     reason only if every commit a command matches is signed and the
     reader's config prints signature lines. Nothing asserted either
     condition. If `log.showSignature` were dropped from the fixture, or
     signing silently stopped verifying, every case would pass vacuously.
     The `finishing.md` cases have never shown that they discriminate.
     Neither have the other cases after GREEN.
   - Fix: after the commits, the fixture asserts two things. First,
     `git log --no-show-signature --format=%G?` returns `G` for all seven
     commits, so every commit is good-signed and verified against
     `allowed_signers`. Second, a bare `git log -1 --format=%H` prints at
     least one non-hash line. These checks pin the state that a passing case
     can only pass by suppressing the signature itself. They also answer
     "is the signing real, and does `log.showSignature` produce the lines":
     the only signature source left is the repo-local `log.showSignature`
     (see issue 3), since no prose command carries `--show-signature`.
   - **Status**: FIXED

2. **The coverage tripwire fired only on zero commands**
   - Location: `pytest_generate_tests`, `_extract`
   - Problem: the `<file>:none` sentinel caught only a file that yielded no
     command at all. Suppose a file already has one extracted command and
     gains a second in a shape the extractor misses. The new command was
     dropped silently. Such shapes include `hash=$(git log …)`, `$ git log`,
     `git -C x log`, a double-backtick span, a block ending on a trailing
     `\`, or a span wrapped across a line. The question was whether a future
     unflagged command would be caught. It would be caught only in the
     shapes the extractor already handles.
   - Fix: added `_flag_count(rel)`, which counts the raw `--format=%H`
     occurrences in the file. This is KD-7's own predicate, independent of
     the parsing. When the file yields no command, or the extracted count
     differs from the raw count, a failing `<file>:missed` case is added.
     Its message gives both numbers. The current counts are 1, 1, 1, 1, 2
     and 3, all matched, so this adds no case today. A probe on a scratch
     document with a `$(git log -1 --format=%H …)` line extracted 2 of 3,
     which would fire the case.
   - **Status**: FIXED

3. **Config injected through the environment was not insulated**
   - Location: `_git_env`
   - Problem: the environment carried `GIT_CONFIG_PARAMETERS` and the
     `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` family, as
     set by `git -c` or a wrapper. These override repo-local config, so they
     can turn `log.showSignature` off for every case. Nulling
     `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` does not stop them.
   - Fix: `_git_env` now drops every inherited `GIT_CONFIG*` variable and
     then sets `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to `os.devnull`.
     I verified this by running the file with `GIT_CONFIG_COUNT=1
     GIT_CONFIG_KEY_0=log.showSignature GIT_CONFIG_VALUE_0=false`: still 6
     failed and 3 passed on the same assertion. The change is local to this
     module. The sibling helpers do not depend on `log.showSignature` and
     were left unchanged.
   - **Status**: FIXED

### Minor Issues

1. **An inline span wrapped across a line break was dropped or mispaired**
   - Location: `_extract` (`SPAN` was `` `([^`\n]*)` ``, applied per line)
   - Problem: a span that opens on one line and closes on the next was not
     found. Its closing backtick then paired with the next span's opening
     one, which shifted the pairing for the rest of that line.
   - Fix: prose lines are now gathered into blank-line-delimited
     paragraphs. Spans are paired within each paragraph by `_spans` with
     `` `([^`]*)` ``, and their whitespace is collapsed. A probe found
     ``git log --format=%H\n-- plans/<job>/x.md`` wrapped over two lines.
     The order of extraction is unchanged, so the ids are the same.
   - **Status**: FIXED

2. **A trailing continuation at the end of a block was discarded**
   - Location: `_join_block`
   - Problem: if a block's last line ended in `\`, the pending text was
     never added to the output.
   - Fix: any pending text is flushed after the loop. Issue 2's tripwire
     would also catch this case.
   - **Status**: FIXED

3. **Constants were defined above the functions that read them**
   - Location: `SCANNED`, `SHA`, `SPAN`, `FENCE`
   - Problem: the shared convention puts definitions after their users,
     constants included.
   - Fix: each constant now sits after its first reader. `REPO_ROOT` and
     `SCANNED` come after `pytest_generate_tests`, `SHA` after the test,
     `FENCE` after `_extract`, and `SPAN` after `_spans`.
   - **Status**: FIXED

4. **Two docstring summaries were longer than 70 characters**
   - Location: the module docstring (74) and `signed_repo` (72, which is 82
     columns at 4 indent)
   - Fix: both were reworded to 66 and 61 characters, with nothing cut.
     Each now has a body that says what it guards.
   - **Status**: FIXED

5. **`REPO_ROOT` was imported from an unrelated helper module**
   - Location: `from tests.triage_feedback_helpers import REPO_ROOT`
   - Problem: this coupled the module to the triage helpers, and used an
     absolute import where the sibling modules either import from their own
     helpers or define the constant themselves.
   - Fix: it is now defined locally as
     `REPO_ROOT = Path(__file__).resolve().parents[1]`.
   - **Status**: FIXED

6. **mypy flagged the `cases` list**
   - Location: `pytest_generate_tests`
   - Problem: the type of `cases` was inferred from its first append,
     `(rel, None)`, so appending `(rel, str)` was an arg-type error.
   - Fix: annotated `cases: list[tuple[str, str | None]]` and
     `ids: list[str]`. `just check` passes.
   - **Status**: FIXED

## Confirmed sound (no change)

- **Non-empty stdout.** Every unflagged command matched signed commits and
  printed their signature lines. build-run-state.md:1 printed two, for
  `item-1-1.md` and `item-1-1-s1-green.md`. The finishing commands match
  commits 3, 5 and 6, which the new `%G?` guard proves good-signed.
- **Skips** match the outline exactly. Each has a reason: `ssh-keygen`
  absent, or git older than 2.34. The version regex parses
  `git version 2.39.5 (Apple Git-154)`. One limit: because the fixture is
  module-scoped, a skip also skips the `:missed` sentinel.
- **ssh and agent insulation.** `user.signingkey` is a key file, so git runs
  `ssh-keygen -Y sign -f <key>` and needs no agent. `SSH_AUTH_SOCK` is
  removed. `GNUPGHOME` is irrelevant under `gpg.format=ssh`.
- **macOS portability.** `ssh-keygen -q -t ed25519 -N "" -f`, `os.devnull`,
  `git init -b` (≥2.28) and the `shlex.split` handling of `':(glob)…'` all
  work on both platforms.
- **Placeholder table and leftover check.** They match the outline. The
  leftover-`<…>` assertion keeps the table in step with the prose.
- No `KD-N` or plan-item IDs appear in the code. D-88 is the durable
  citation. The module is 261 lines, under the cap.

## Fixes Applied

- `tests/test_build_prose_git_log.py`:
  - `signed_repo`: a `%G?` all-`G` guard and a guard that `log.showSignature`
    emits a line (major 1).
  - `pytest_generate_tests` and the test: a `<file>:missed` sentinel driven
    by `_flag_count` (major 2).
  - `_git_env`: inherited `GIT_CONFIG*` variables dropped (major 3).
  - `_extract` and the new `_spans`: span pairing per paragraph (minor 1).
  - `_join_block`: trailing continuation flushed (minor 2).
  - Constants moved below their readers (minor 3).
  - Docstring summaries shortened to 70 characters or fewer (minor 4).
  - `REPO_ROOT` defined locally (minor 5).
  - `cases`/`ids` annotated (minor 6).

## Final run

`.venv/bin/pytest -p no:markdown_report -rA
tests/test_build_prose_git_log.py`:

```
PASSED ...[finishing.md:1]
PASSED ...[finishing.md:2]
PASSED ...[finishing.md:3]
FAILED ...[phase-boundary.md:1]
FAILED ...[tdd-slice.md:1]
FAILED ...[escalation.md:1]
FAILED ...[tdd-auditor.md:1]
FAILED ...[build-run-state.md:1]
FAILED ...[build-run-state.md:2]
========================= 6 failed, 3 passed in 4.80s ==========================
```

Every failure is at `assert not stray`, because a `Good "git" signature for
test@example.com with ED25519 key SHA256:…` line appears on stdout ahead of
the hash. build-run-state.md:1 has two such lines. The fixture's new guards
held. `just check` reports `Checks OK`, covering ruff, docformatter and mypy.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| m14 / KD-7 (each command prints hash lines only, whatever the reader's `log.showSignature`) | Pinned, red today | the five unflagged files red at `assert not stray`; `finishing.md` green; the fixture proves signing and showSignature are active |
| Extraction: fence, continuation, inline span; every file yields at least one | Satisfied | the coverage table above; the `:missed` sentinel also catches undercounts |
| Fixture: repo-local SSH signing, null global and system config, seven commits in order | Satisfied | `signed_repo` |
| Skip conditions with reasons | Satisfied | `signed_repo` head |
