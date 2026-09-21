# RED: CRLF allowlist diagnostic

Tests added to `/Users/david/code/edify/tests/test_line_limits.py`
(`tests/test_line_limits.py:304-378`; file is 380 lines, under the 400 cap):

- `test_line_limits_rejects_crlf_on_full_entry_line`
- `test_line_limits_rejects_crlf_on_two_field_entry_line`

Both fixtures write a real allowlist file to a `tmp_path` via `Path.write_bytes`
(not the shared `_write_allowlist` helper, which cannot embed a raw `\r`), then
run the unmodified `scripts/check_line_limits.sh` against a clean 10-line
target tree so the only thing under test is allowlist parsing.

Ran alone, against the unchanged script:

```
$ just test tests/test_line_limits.py -k "crlf" -v
```

Full untruncated output:

```
# Test Report

**Summary:** 0/2 passed, 2 failed

## Failures

### tests/test_line_limits.py::test_line_limits_rejects_crlf_on_full_entry_line FAILED

```python
tests/test_line_limits.py:330: in test_line_limits_rejects_crlf_on_full_entry_line
    assert result.returncode == 2, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 2
E    +  where 0 = CompletedProcess(args=['/Users/david/code/edify/scripts/check_line_limits.sh', '--allowlist', '/tmp/.../allowlist.txt', '/tmp/.../root'], returncode=0, stdout='', stderr='').returncode
```

### tests/test_line_limits.py::test_line_limits_rejects_crlf_on_two_field_entry_line FAILED

```python
tests/test_line_limits.py:364: in test_line_limits_rejects_crlf_on_two_field_entry_line
    assert (
E   AssertionError: check_line_limits: <allowlist>: line 1: ceiling is not an integer: 401
E
E   assert ('carriage return' in 'check_line_limits: <allowlist>: line 1: ceiling is not an integer: 401\n' or 'crlf' in 'check_line_limits: <allowlist>: line 1: ceiling is not an integer: 401\n')
E    +  where 'check_line_limits: <allowlist>: line 1: ceiling is not an integer: 401\n' = <built-in method lower of str object>()
E    +  and   'check_line_limits: <allowlist>: line 1: ceiling is not an integer: 401\n' = <built-in method lower of str object>()
```
```

(Temp paths above are elided to `/tmp/...`; the actual run showed full
`pytest-of-david/pytest-NNN/...` paths — unchanged from what the harness
printed, only shortened here for readability.)

The full 12-test file, run without `-k`, still passes its 10 pre-existing
tests unmodified with only these two new ones red:

```
## Passes

- tests/test_line_limits.py::test_line_limits_passes_clean_tree
- tests/test_line_limits.py::test_line_limits_fails_markdown_over_400
- tests/test_line_limits.py::test_line_limits_fails_skill_hub_over_200
- tests/test_line_limits.py::test_line_limits_reports_allowlisted_without_failing
- tests/test_line_limits.py::test_line_limits_allowlisted_file_shrunk_below_cap_is_silent
- tests/test_line_limits.py::test_line_limits_fails_allowlisted_file_over_ceiling
- tests/test_line_limits.py::test_line_limits_allowlists_a_spaced_path
- tests/test_line_limits.py::test_line_limits_matches_allowlist_paths_exactly
- tests/test_line_limits.py::test_line_limits_skips_frozen_docs
- tests/test_line_limits.py::test_line_limits_checks_living_superpowers_docs
- tests/test_line_limits.py::test_line_limits_fails_when_find_cannot_walk
- tests/test_line_limits.py::test_line_limits_handles_spaced_path
```

## Why each failure proves the behaviour is absent

### `test_line_limits_rejects_crlf_on_full_entry_line`

Fixture: allowlist line `docs/notes.md\t401\tno job yet\r\n` — three fields,
CR immediately before the final `\n`.

Failing assertion: `assert result.returncode == 2` — actual `0`.

Why this proves the behaviour is absent: `read -r entry_path ceiling _note`
splits on `\t`, and the CR lands on the *last* named variable, `_note`
(verified directly: `a=[docs/notes.md] b=[401] c=[no job yet<CR>]`). `_note`
is never validated or used — the script only regex-checks `ceiling`, which
here is a clean `401`. So today the malformed line is silently accepted as a
normal entry: exit 0, no diagnostic at all. The required behaviour treats any
CR in an allowlist line as malformed regardless of which field it lands in;
today's script does not, and the assertion catches exactly that gap.

### `test_line_limits_rejects_crlf_on_two_field_entry_line`

Fixture: allowlist line `docs/notes.md\t401\r\n` — two fields (no `note`,
which the script's read loop already tolerates: a short line leaves `_note`
empty without error, so a real-world two-field entry parses today without
complaint on that account). The CR here lands directly on `ceiling`, verified
directly: `a=[docs/notes.md] b=[401<CR>] c=[]`.

First two assertions (`returncode == 2`, `"line 1" in diagnostic`) already
pass unmodified — today's integer regex on `ceiling` already rejects
`"401\r"` and already exits 2 naming the line number. The RED is on the third
assertion:

```
assert (
    "carriage return" in diagnostic.lower() or "crlf" in diagnostic.lower()
), diagnostic
```

Failing with the actual diagnostic `check_line_limits: <allowlist>: line 1:
ceiling is not an integer: 401`. This proves the current diagnostic never
names the carriage return / CRLF condition — it blames "ceiling is not an
integer" instead, which is exactly the misleading message the slice requires
removing. (A fourth assertion, `"ceiling is not an integer" not in
diagnostic`, is not reached in this run since pytest stops at the first
failure, but the third assertion alone is sufficient proof.)

Note on test construction: both wording checks compare against `diagnostic =
result.stderr.replace(str(allowlist), "<allowlist>")`, not raw `result.stderr`.
Without that substitution the checks would have a false-pass hazard: pytest
derives each test's `tmp_path` directory name from the test function name,
which contains the substring `"crlf"`, and the script's own diagnostic embeds
the allowlist's full path (`$ALLOWLIST`) — so `"crlf" in stderr.lower()` would
spuriously match the *temp directory name*, not the script's wording. This was
caught empirically (first draft showed test 2 passing an assertion it should
have failed) and fixed by stripping the allowlist path out of `stderr` before
the wording check.
