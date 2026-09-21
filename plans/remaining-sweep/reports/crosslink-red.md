# RED — `scripts/check_design_links.sh` (Slice k=1)

Stub created at `scripts/check_design_links.sh`: executable, `set -euo
pipefail; exit 0` — runs, prints nothing, exits 0. Verified directly (`./scripts/check_design_links.sh` and `./scripts/check_design_links.sh
/tmp` both exit 0 with empty stdout/stderr) before writing any test.

## Real line shapes derived

Read `plans/design-doc-split/reports/split-report.md`,
`plans/design-doc-split/reports/independent-review.md`,
`docs/decisions.md`, `docs/references/testing.md`,
`docs/references/cli-and-package.md`, `docs/references/quality-gates.md`,
and (for house style) `scripts/check_line_limits.sh` with
`tests/test_line_limits.py` / `tests/line_limits_helpers.py`.

- **Node definition** — a bolded paragraph lead: `**D-<n> — <conclusion>.**`
  followed by explanation prose in the same paragraph, e.g.
  `docs/references/testing.md:10`:
  `**D-17 — Patch where the object is used, not where it is defined.**
  Python imports create...`. Un-ID'd conclusions also exist (`**Model tier
  naming: ...**` in `agent-instructions.md`) but the contract only asks for
  `D-<n>` IDs, so these are out of scope for the invariants.
- **Index line** — `- **D-<n>** — <conclusion>.`
  (`docs/decisions.md:15`: `- **D-1** — Two output conventions, split by
  consumer.`).
- **Group** — `## <Group Name>` then a blank line then
  `Argued in \`docs/references/<file>.md\`.` (`docs/decisions.md:11-13`).
  This is the exact shape invariant 5 (`missing-node`) reads.
- **Rejected-alternatives line** — `*Rejected:* <name>; <name>; ...`, one
  line per group, only on groups that have rejected alternatives
  (`docs/decisions.md:33-39`). Not covered by the five invariants the brief
  named — a node's `## Rejected alternatives` section isn't ID-addressed so
  there's nothing to cross-link.

### Contract deviation found and resolved: invariant 4 needed wrap-joining

The brief flagged invariant 4 (conclusion-mismatch) as needing confirmation.
A first pass (regex per physical line, no cross-line join) found 14 false
positives — 14 IDs with "missing" index lines or "mismatched" conclusions.
All 14 were paragraph wrapping: both node leads and index lines wrap across
two physical lines under `just format`'s 80-column reflow, e.g.:

```
docs/references/cli-and-package.md:99-100
**D-12 — Skills reach the binary by content substitution, never a hardcoded
path.** Skill and agent markdown support ...

docs/decisions.md:140-141
- **D-54** — A skill needs four discovery layers, not good internal
  documentation.
```

After joining wrapped paragraph lines before matching, re-ran across all 85
`D-`/`L-` ids in the real tree: 0 missing index lines, 0 orphan index lines,
0 mismatches. The invariant holds, but only as: strip the node conclusion's
trailing `.` before the closing `**`, and check it is a **prefix** of the
index conclusion (not equality) — confirmed by the one real case that
exercises the difference, D-31 (superseded): node lead is `LLM failure-mode
checks at every planning level.`, index line is `LLM failure-mode checks at
every planning level (superseded 2026-09-01: one planning level, so the
check runs once).` — node text (period stripped) is a strict prefix of the
index text, not an exact match.

**This is load-bearing for the real (GREEN) implementation**: reading
`docs/decisions.md` or a node line-by-line without joining wrapped
paragraphs will misreport ~14 real IDs as `unindexed-decision` /
`orphan-index-line` / `conclusion-mismatch` false positives. Recorded here
so GREEN does not re-discover it by making `test_design_links_real_repo_root`
red for the wrong reason.

### `ROOT` default

The brief's contract says "ROOT defaults to the repo root"; the sibling gate
`check_line_limits.sh` instead defaults to `.` (cwd), not a git-root lookup.
I did not pin this in a test — `test_design_links_real_repo_root` passes
`ROOT` explicitly (`REPO_ROOT`) rather than relying on default-arg
resolution, sidestepping the ambiguity. GREEN should follow
`check_line_limits.sh`'s `.` default for consistency unless told otherwise;
flagging rather than deciding since it's a discrepancy between the brief's
own wording and the codebase's established pattern.

## Test list

`tests/test_design_links.py` (12 tests) + `tests/design_links_helpers.py`
(fixture builders, sibling helper module per the `line_limits_helpers.py`
convention):

1. `test_design_links_reports_unindexed_decision`
2. `test_design_links_reports_orphan_index_line`
3. `test_design_links_reports_duplicate_definition`
4. `test_design_links_reports_duplicate_index_line`
5. `test_design_links_reports_conclusion_mismatch`
6. `test_design_links_reports_missing_node`
7. `test_design_links_exit2_missing_decisions`
8. `test_design_links_exit2_missing_references_dir`
9. `test_design_links_exit2_outranks_exit1`
10. `test_design_links_clean_tree_reports_signoff`
11. `test_design_links_handles_node_path_with_space`
12. `test_design_links_real_repo_root`

Each fixture is built with `_write_decisions_md` / `_write_node` from real
bullet/bold-lead shapes above (388/357 lines under the 400 cap for a `tests/`
module — 357 for the test module, 99 for the helper). Assertions parse
violation lines via `_violation_lines` (`<kind>: <ID or path>: <detail>`,
split on `": "` with maxsplit 2) and check `(kind, id)` membership rather
than exact detail text, since detail wording is explicitly free-form in the
contract.

`test_design_links_real_repo_root` does not assert exact counts (No
Estimates / no invented thresholds — the real counts will drift as
decisions are added) — it asserts the sign-off line's *shape* via
`SIGNOFF_RE`, which is itself derived directly from the contract's own
worked example (`design-links: 83 decisions indexed, defined once,
conclusions match, N nodes present`).

## Proof of RED

```
$ cd /Users/david/code/edify && UV_CACHE_DIR="$TMPDIR/uv-cache" just test tests/test_design_links.py
```

Full output:

```
# Test Report

**Summary:** 0/12 passed, 12 failed

## Failures

### tests/test_design_links.py::test_design_links_reports_unindexed_decision FAILED

    tests/test_design_links.py:68: in test_design_links_reports_unindexed_decision
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1
    E    +  where 0 = CompletedProcess(args=['/Users/david/code/edify/scripts/check_design_links.sh', '.../root'], returncode=0, stdout='', stderr='').returncode

### tests/test_design_links.py::test_design_links_reports_orphan_index_line FAILED

    tests/test_design_links.py:97: in test_design_links_reports_orphan_index_line
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1

### tests/test_design_links.py::test_design_links_reports_duplicate_definition FAILED

    tests/test_design_links.py:129: in test_design_links_reports_duplicate_definition
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1

### tests/test_design_links.py::test_design_links_reports_duplicate_index_line FAILED

    tests/test_design_links.py:158: in test_design_links_reports_duplicate_index_line
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1

### tests/test_design_links.py::test_design_links_reports_conclusion_mismatch FAILED

    tests/test_design_links.py:184: in test_design_links_reports_conclusion_mismatch
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1

### tests/test_design_links.py::test_design_links_reports_missing_node FAILED

    tests/test_design_links.py:200: in test_design_links_reports_missing_node
        assert result.returncode == 1, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 1

### tests/test_design_links.py::test_design_links_exit2_missing_decisions FAILED

    tests/test_design_links.py:216: in test_design_links_exit2_missing_decisions
        assert result.returncode == 2, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 2

### tests/test_design_links.py::test_design_links_exit2_missing_references_dir FAILED

    tests/test_design_links.py:230: in test_design_links_exit2_missing_references_dir
        assert result.returncode == 2, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 2

### tests/test_design_links.py::test_design_links_exit2_outranks_exit1 FAILED

    tests/test_design_links.py:259: in test_design_links_exit2_outranks_exit1
        assert result.returncode == 2, result.stdout + result.stderr
    E   AssertionError:
    E   assert 0 == 2

### tests/test_design_links.py::test_design_links_clean_tree_reports_signoff FAILED

    tests/test_design_links.py:302: in test_design_links_clean_tree_reports_signoff
        assert result.stdout.splitlines() == [
    E   AssertionError:
    E   assert [] == ['design-link...odes present']
    E
    E     Right contains one more item: 'design-links: 2 decisions indexed, defined once, conclusions match, 2 nodes present'

### tests/test_design_links.py::test_design_links_handles_node_path_with_space FAILED

    tests/test_design_links.py:336: in test_design_links_handles_node_path_with_space
        assert result.stdout.splitlines() == [
    E   AssertionError:
    E   assert [] == ['design-link...odes present']
    E
    E     Right contains one more item: 'design-links: 1 decisions indexed, defined once, conclusions match, 1 nodes present'

### tests/test_design_links.py::test_design_links_real_repo_root FAILED

    tests/test_design_links.py:355: in test_design_links_real_repo_root
        assert any(SIGNOFF_RE.match(line) for line in result.stdout.splitlines()), (
    E   AssertionError:
    E   assert False
```

0/12 passed, 0 errored — every test FAILED on its own assertion, none
vacuously passed against the inert stub.

## Per-test: what the failing assertion proves absent

1. **unindexed-decision** — `returncode == 1` fails (got 0): stub never
   detects the node's D-1 has no index line.
2. **orphan-index-line** — same shape: stub never detects the index's D-2
   has no defining node.
3. **duplicate-definition** — same: stub never detects D-1 defined in two
   nodes.
4. **duplicate-index-line** — same: stub never detects two index lines for
   D-1.
5. **conclusion-mismatch** — same: stub never compares index vs. node
   conclusion text.
6. **missing-node** — same: stub never checks an `Argued in` path resolves
   to a real file.
7. **exit2-missing-decisions** — `returncode == 2` fails (got 0): stub
   never checks `docs/decisions.md` exists before proceeding.
8. **exit2-missing-references-dir** — same, for the references directory.
9. **exit2-outranks-exit1** — same: stub can't rank a run-failure over a
   content violation because it detects neither.
10. **clean-tree-signoff** — `stdout.splitlines() == [...]` fails (got
    `[]`): stub emits no sign-off line at all, so a genuinely clean tree is
    indistinguishable from a broken checker — exactly what "never a bare OK"
    guards against.
11. **node-path-with-space** — same shape as #10, isolating space-safety:
    stub emits nothing regardless of whether spaces would have been handled.
12. **real-repo-root** — `any(SIGNOFF_RE.match(...))` fails (`False`): run
    against the actual `docs/decisions.md` and `docs/references/*.md`
    (verified clean by the independent review), the stub still prints
    nothing, so no line matches the sign-off pattern. This is the one test
    that will also validate the invariants against production data once
    GREEN lands.

All 12 fail for the reason the stub's own docstring states — it is
unimplemented — not for an unrelated fixture or environment defect.
