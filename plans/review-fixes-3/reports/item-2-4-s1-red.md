# Item 2.4 slice 1 — RED

Test file: `tests/test_build_prose_git_log.py` (208 lines, ruff check and format clean). No SUT edits (the SUT is the prose). Uncommitted.

Run: `.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py` gave 6 failed, 3 passed.

## Per-case results

All ids are `test_read_git_log_commands_print_hashes_only_on_signed_history[<id>]`.

| id | result | failing assertion |
|---|---|---|
| phase-boundary.md:1 | FAIL | `assert not stray`: stdout line `Good "git" signature for test@example.com with ED25519 key SHA256:…` |
| tdd-slice.md:1 | FAIL | same hash-only assertion, one signature line |
| escalation.md:1 | FAIL | same, one signature line |
| tdd-auditor.md:1 | FAIL | same, one signature line |
| build-run-state.md:1 | FAIL | same, two signature lines (two commits match the glob) |
| build-run-state.md:2 | FAIL | same, one signature line |
| finishing.md:1 | PASS | already flagged |
| finishing.md:2 | PASS | already flagged |
| finishing.md:3 | PASS | already flagged |

Every failure is the hash-only assertion. There is no extraction error, leftover placeholder, git non-zero exit or fixture error. The exit-0, non-empty and no-leftover-placeholder assertions all held first.

## Extracted commands (placeholders unsubstituted)

- phase-boundary.md:1: `git log -1 --format=%H <run base>..HEAD -- plans/<job>/reports/phase-<P>-corrector.md`
- tdd-slice.md:1: `git log --diff-filter=A --format=%H -- plans/<job>/reports/item-N-M-s<k>-green.md`
- escalation.md:1 (inline span): `git log --format=%H -- plans/<job>/reports/<name>.md`
- tdd-auditor.md:1: `git log --diff-filter=A --format=%H -- plans/<job>/reports/item-N-M-s<k>-green.md` (indented fence inside a list item)
- build-run-state.md:1 (D-88): `git log --no-renames --diff-filter=A --reverse --format=%H -- ':(glob)plans/<job>/reports/item-*'`
- build-run-state.md:2 (D-89): `git log -1 --format=%H <run base>..HEAD -- plans/<job>/reports/phase-<P>-corrector.md`
- finishing.md:1: `git log -1 --no-show-signature --format=%H -- ':(glob)plans/<job>/reports/item-*'`
- finishing.md:2: `git log -1 --no-show-signature --format=%H <L>..HEAD -- ':(glob)plans/<job>/reports/review-*.md'`
- finishing.md:3 (inline span): `git log -1 --no-show-signature --format=%H <L>..HEAD -- plans/<job>/reports/final-review.md`

`tdd-auditor.md` also has `git log -- plans/<job>/<hosting file>` (line 61). It carries no `--format=%H`, so it is not extracted, as the outline says. `<hosting file>` stays in the placeholder table, unused by any extracted command.

## Design notes

- The placeholder table is exactly the outline's. It missed no placeholder, so I did not extend it. Every command ran against the fixture.
- Parametrization is in `pytest_generate_tests`, so the helpers sit after their users. A scanned file that yields no command becomes a `<file>:none` case that fails, so an empty extraction cannot pass vacuously.
- The fixture is module-scoped. It makes an `ssh-keygen -t ed25519 -N ''` key and `allowed_signers` under `tmp_path_factory`, with the repo-local config the slice lists. The seven signed commits follow the slice's order.
- Every git call (fixture and commands) runs with `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` set to `os.devnull`, and `SSH_AUTH_SOCK` removed from the environment.
- The test skips with a reason when `ssh-keygen` is absent or git is older than 2.34. Neither skip fired here.
- The fixture computes `<L>` and `<run base>` with `git log -1 --no-show-signature --format=%H`, so its own parsing does not depend on the flag under test.

## Mutation proof

None needed. The red is genuine: the unflagged prose commands fail on the signature lines. `finishing.md`'s three flagged commands pass, which shows the check discriminates between flagged and unflagged commands.

## Fixtures tried and rejected

- Reading the base and `<L>` with a bare `git log --format=%H` in the fixture: rejected, because with `log.showSignature=true` it would put signature lines in the value it parses. It uses `--no-show-signature`.
- A separate "every file yields a command" test: rejected in favour of the `<file>:none` sentinel case inside the one parametrized test.
- A bare `rev-parse :/path` lookup for the item commit: written and discarded before the first run. It is not a path-limited log lookup.
