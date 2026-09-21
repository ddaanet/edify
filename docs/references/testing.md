# Testing

Decisions governing the test suite: what a RED assertion must prove, when a real
git repo beats a mock, how Click CLIs are exercised, and how test setup reports
its own failures. Read this before writing or changing tests.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

**D-17 — Patch where the object is used, not where it is defined.** Python
imports create references in the importing module's namespace, so
`monkeypatch.setattr("pkg.b.foo", mock)` works and `"pkg.a.foo"` does not.

**D-18 — RED assertions verify behavior, not structure.** `exit_code == 0`, key
existence and attribute presence are all satisfied by a stub. RED tests mock IO
and external calls and assert on output content, using `tmp_path` fixtures for
real filesystem state. TDD's "write minimal code to pass" only works if the test
requires real behavior. Corollary: when a RED phase passes unexpectedly, check
whether the assertions could distinguish correct output from empty or default
output — `assert isinstance(relevant, list)` passes on an empty list.

**D-19 — E2E with real git repos; mock only for error injection.** Git against
`tmp_path` runs in milliseconds, while subprocess mocks couple to command
strings rather than outcomes, and the interesting bugs are state transitions
mocks cannot produce. A dual suite (e2e for behavior plus mocked subprocess for
speed) buys nothing. Mock subprocess only to inject errors that are hard to
stage — lock files, permission failures.

**D-20 — Click CLIs are tested through `CliRunner`.** In-process invocation
captures output and exit code and supports an isolated filesystem. Testing via
subprocess or by calling `main()` and catching `SystemExit` is slower and
conflates process concerns with behavior.

**D-21 — Test setup fails self-diagnosingly.**
`subprocess.run(..., check=True, capture_output=True)` swallows stderr, so a
`CalledProcessError` shows only a command and an exit code, and opaque failures
invite confabulation. Use `check=False` with an explicit assertion carrying
stderr, or a helper that surfaces it.

**D-22 — GREEN verification includes lint.** The verification command is
`just check && just test`, not `just test` alone: an agent that runs only tests
commits green code with lint errors, forcing a separate fix commit.

**D-23 — A test that fails only in the suite has shared mutable state.** That is
a bug, not flakiness. Confirm with `pytest --lf`, bisect with `pytest -x`
subsets, fix the fixture cleanup or global mutation. "Passes in isolation" is a
diagnostic signal, not a resolution — merging a known ordering-dependent failure
makes every later failure dismissible.

**Presentation is not TDD'd.** Help text wording and error phrasing are brittle
as test targets and self-evident on reading; they get handled in batch at review
checkpoints instead of a slice of their own.

**Conformance work bakes exact strings into assertions.** When implementation
follows an external reference — shell prototype, API spec, exact output format —
the test assertions carry the exact expected output from that reference, and RED
prose descriptions carry the exact strings too. This is not full test code; it
is precise prose. Abstracting the string introduces translation loss and makes
"visual parity validated" claims undetectable when false.
