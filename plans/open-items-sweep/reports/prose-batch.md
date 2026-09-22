# Prose batch — correctors, drift, learnings, staleness page

**Date:** 2026-09-22
**Dispatch:** six prose items from the orchestrator, spec
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md`

**Tool note.** The `Edit` tool was unavailable for this whole run — every call
returned "the server-side auto mode classifier gave no verdict (it skipped this
action)". Per `CLAUDE.md` I did not escape to `sed -i`. Every edit below was
applied by a `python3` heredoc doing an exact-string replacement that aborts
unless the old text matches exactly once, with both the old and the new text
literal in the command, so the permission prompt still showed content rather
than a pattern.

## Item 1 — correctors name the `superseding` token

`plugin/agents/outline-corrector.md` (§Review Criteria, Provenance block) and
`plugin/agents/design-corrector.md` (§3.5). The `Derived from:` criterion now
states that the superseded artifact comes **after the literal word
`superseding`**, as a backticked path, and that any other wording ("replacing
…") is a Major because the range script then finds no prior and yields
`NO-PROVENANCE:`. To pay for those lines inside the pinned line counts I
tightened two neighbouring criteria without losing any of their content: the
section-present bullet dropped "is present, carrying" for "carries" and "has no
way to establish" for "cannot establish"; the prior-artifact bullet dropped
"Read that artifact" for "Read it", "the range then starts … and the resulting
narrow diff" for "the range starts … so the narrow diff", and the redundant
`Derived from:` qualifier on the does-not-resolve clause. The two blocks stay
byte-identical in substance and each file's net line count is unchanged.

`wc -l`, before and after:

| File | Before | After | Allowlist ceiling |
|---|---|---|---|
| `plugin/agents/outline-corrector.md` | 450 | 450 | 450 |
| `plugin/agents/design-corrector.md` | 460 | 460 | 460 |

`rumdl fmt --check -q --no-cache` on both files: exit 0, no reflow wanted. A
subsequent `rumdl fmt` (writing) on both changed nothing; it reported two
pre-existing MD013 lines it cannot fix (`outline-corrector.md:61`, a long
`Skill(...)` call, and `design-corrector.md:105`), both untouched by this edit
and both present before it.

## Item 2 — planning-artifact drift

`plans/provenance-enforcement-and-routing/classification.md`:

- M-4's **Artifact destination** now reads `plugin/bin/`, with the reason
  inline: outline KD-2 settled it as one simple script directly in `bin/`, no
  shim and no `scripts/` directory. The stale value was
  `plugin/skills/*/scripts/`.
- The Author-corrector coupling line now attributes the one criterion to
  **outline Item 1.1**, not Item 1.7, which is where the outline assigns it and
  where it landed.

`plans/provenance-enforcement-and-routing/outline.md`:

- **Item 1.1 requirements** are now `M-1, M-2`, with two added clauses: the
  `Slices:` criterion serves KD-4 rather than a review finding, and M-3 is a
  Part B routing finding carried by Items 1.3 and 1.5–1.7 (verified against
  those items' own `Requirements:` lines, which all list M-3).
- **`tests/test_review_range.py` was split**, said in one clause at each of the
  two sites that named it: "since split into five `tests/test_review_range_*.py`
  modules plus `tests/review_range_helpers.py` to stay under the line cap",
  at Item 1.2 and at KD-2.

  **Corrected after a first wrong pass.** I first wrote that the module never
  existed, taking the deliverable review's "That file does not exist" as
  historical rather than HEAD-relative. The orchestrator corrected it and the
  correction checks out: `git log --oneline --diff-filter=A --all --
  tests/test_review_range.py` gives `78206a83` (Item 1.2/1), the
  `--diff-filter=D` form gives `5594a753`, and `git show
  5594a753^:tests/test_review_range.py | wc -l` is 396 — so the module existed
  for the whole of Item 1.2 and the sweep commit split it at 396 lines against
  the 400-line cap. Both sites now carry the split wording, not the
  never-existed wording.
- **Final list revision (TDD audit)** gains the six tests the enumeration did
  not account for, with the report cited as the source and the point that all
  six do real work, so the defect was the stale list. This paragraph's
  "in `test_review_range.py`" also became "in the `test_review_range_*`
  modules", since the sentence describes the landed suites and that file is
  gone at HEAD; the orchestrator's correction named only Item 1.2 and KD-2, so
  flagging it rather than reverting it. The six:
  `test_one_hop_only_ignores_grandprior_mismatch` (the only thing pinning
  KD-2's "One hop only" clause),
  `test_line_limits_allowlisted_file_shrunk_below_cap_is_silent`,
  `test_line_limits_rejects_crlf_on_full_entry_line`,
  `test_line_limits_rejects_crlf_on_two_field_entry_line`, and both functions of
  `tests/test_line_limits_exit_codes.py`
  (`test_unreadable_file_outranks_a_later_overage`,
  `test_walk_failure_outranks_a_later_overage`). Each name was verified present
  in the tree by `grep -n '^def '`. The same module's third function,
  `test_two_positional_roots_exits_2_with_usage_diagnostic`, is the pending
  sweep slice's work and is deliberately not listed as this job's.
- **Item 1.10's file list** now names `tests/test_line_limits.py`,
  `tests/line_limits_helpers.py` and `tests/test_line_limits_exit_codes.py`,
  the last with the reason it exists (split off to keep the first module under
  its cap).

`plans/` is outside both the rumdl scope and the line-limit walk (`.rumdl.toml`
`include`, and `check_line_limits.sh` walks only `src`, `tests`, `plugin`,
`docs` and root-level `*.md`), so these additions are ungated; I hand-wrapped
them at 80 columns to match the file.

## Item 3 — `agents/learnings.md` routed through the deleted `/codify`

Three edits, one file. The soft-limit line at `:5` now routes consolidation
through `/claude-md-management:revise-claude-md`, the live replacement per
`memory/workflow-pipeline-revival.md:22`; the destinations sentence is
untouched. The heading at `:9` was `## When codify drops incident-specific
learnings` and is now `## When a consolidation pass drops incident-specific
learnings`; its first bullet's "Codify skill quality criteria" became
"Consolidation-skill quality criteria", since leaving it would have kept the
dead command's name in the body of the entry the heading renames.

## Item 4 — `plansDirectory`

`plugin/.claude/settings.json` set `"plansDirectory": "plans/"`; it now sets
`"plans/claude/"`, matching the parent `.claude/settings.json:24`. The parent is
right and the plugin copy was wrong: `plansDirectory` is where Claude Code's own
plan mode writes plan files, and `plans/<job>/` in this repo is the pipeline's
artifact namespace — one directory per job, each holding `outline.md`,
`runbook.md` and `reports/`. Pointing plan mode at `plans/` root would drop
harness-authored files among the job directories, where `/build`,
`edify-review-range.sh` and `triage-feedback.sh` all resolve paths by job name.
`plans/claude/` already exists (empty) and keeps them separate. JSON validity
re-checked with `json.load`.

## Item 5 — dead `sessionstart-health.sh` block

`plugin/bin/bump-plugin-version.py`: deleted the `EDIFY_VERSION` rewrite block
(the `health_sh` lookup, the `re.sub`, both branches and the unreachable
`sys.exit(1)`), the now-unused `import re`, and the docstring's mention — it
reads `"""Bump plugin.json to the given version string."""`. The plugin.json
bump, its missing-file guard and its success line are untouched. The file is 36
lines and `ruff check`, `ruff format --check`, `docformatter -c` and `mypy` all
pass it in the gate run below.

**Referenced but not edited, as instructed:** neither
`plugin/bin/check-version-consistency.py` nor `scripts/release.sh` mentions
`EDIFY_VERSION` or `sessionstart-health` at all. A tree-wide grep over `*.py`,
`*.sh`, `*.just`, `*.md`, `*.json` and `*.toml` for both tokens now returns only
frozen `plans/` reports and the `.claude/handoff-todo.md` line item 6 rewrote.
`scripts/release.sh:126` calls `plugin/bin/bump-plugin-version.py "$V"` with one
argument, which is the surviving contract.

## Item 6 — `plugin-transition-evaluation.md` deleted

Before deleting I checked the page carried nothing live. Its trimmed head is
four pointers into the living design; §"Release mechanism — recorded" is a
pointer to D-87 plus the two corrections; §"Incidental staleness still live" is
the three items closed by items 3–5 above.

The two claims deliberately absent from D-87 were **not** already in
`docs/references/cli-and-package.md`, so they moved into D-87's argument, ahead
of its `*Taken 2026-07-16*` clause, as one sentence: re-checked 2026-09-21,
three points the 2026-07-15 measurement weighed no longer count either way —
submodule handling stopped being a need when D-10 flattened `plugin/`; the
marketplace side effect stopped being a differentiator once
`scripts/release.sh` grew the same `MARKETPLACE_DIR` requirement and the same
synthesize-an-entry-if-absent branch; and the dry-run and rollback gaps are real
but are the toolkit's own framing of its exclusion rather than edify's
requirement, edify having neither and offering `--resume` instead. I kept the
third point with the two because the page presented it as part of the same
re-check and D-87 carried none of it. The node is 244 lines against its 400 cap
and `rumdl fmt` reflowed the paragraph.

Then `git rm docs/superpowers/design/plugin-transition-evaluation.md` (66
lines). **This stages the deletion** — `git rm` has no unstaged form; nothing
else is staged.

Inbound references outside `plans/`, from
`grep -rn "plugin-transition-evaluation" --include=*.md . | grep -v "^./plans/"`:

- `docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md:7` —
  reworded as dated history: the trimming stays in the past tense it was
  written in, followed by "That page was deleted outright on 2026-09-22, once
  the last three staleness items it held were fixed and the two
  release-comparison claims it carried moved into D-87." The mention is not
  deleted.
- `.claude/handoff-todo.md:21` — the todo item was the three staleness items
  "kept in" the page. Replaced with a done line naming this report, the three
  fixes and the deletion. **Flagging it:** the task frame is the orchestrator's
  file, and it was clean before I touched it, so if you would rather own that
  line, `git checkout -- .claude/handoff-todo.md` reverts only it. Note that a
  second todo line, the one enumerating the review's 15 unfixed minors, still
  lists "both correctors enforce `Derived from:` without naming the literal
  `superseding` token" and "planning-artifact drift and a stale test
  enumeration in the outline" as open; items 1 and 2 above closed both, and I
  left that line alone as outside this dispatch.
- `.claude/handoff-task.md:3` mentions the page only as "`…` trimmed", which is
  true history of the 2026-09-21 pass; left as written.

No index in `docs/superpowers/design/` lists the page — the directory holds only
`invariant-guided-verify-loop.md` and the deleted file, and no other `.md`
outside `plans/` references it. No non-markdown reference either: a grep over
`*.sh`, `*.py`, `*.json`, `*.toml`, `*.just` and `*.allow` returns nothing, and
the file is no longer on `scripts/check_line_limits.allow` (only the three
correctors are).

## `just precommit` — full output

Re-run after the item-2 correction with the same result, so the pasted output
below still describes the tree. Exit 1, with exactly the four expected
`tests/test_review_range_*` failures from the pending slice (identical test ids
and summary counts on both runs; only the throwaway-repo shas in the messages
differ, since each run builds fresh fixtures under `tmp_path`). Everything else green: `ruff check`, `ruff format
--check`, `docformatter -c`, `mypy` and `rumdl fmt --check` all silent (the
gate's `report` prints a header only when the command writes output), version
consistency, `run-line-limits` printing its three allowlisted reports at exit 0,
and `design links` at 87 decisions across 8 nodes.

````text
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 356/361 passed, 4 failed, 1 xfail

## Failures

### tests/test_review_range_range.py::test_prior_base_uppercase_same_commit_emits_range FAILED

```python
tests/test_review_range_range.py:112: in test_prior_base_uppercase_same_commit_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: CONFLICT: base 20caa2cb8a7efa27df84081186007b13b7124020 != 20CAA2CB8A7EFA27DF84081186007B13B7124020 inherited from plans/prior-job/outline.md
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-755/test_prior_base_uppercase...1186007b13b7124020 != 20CAA2CB8A7EFA27DF84081186007B13B7124020 inherited from plans/prior-job/outline.md\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_backticked_none_emits_range FAILED

```python
tests/test_review_range_range.py:212: in test_backticked_none_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PROVENANCE:
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-755/test_backticked_none_emits_ran0/repo/plans/job/outline.md'], returncode=1, stdout='NO-PROVENANCE:\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_crlf_artifact_emits_range FAILED

```python
tests/test_review_range_range.py:243: in test_crlf_artifact_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: UNRESOLVED: 3626686dcd522b47d57334da763ef14da1785cf0
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-755/test_crlf_artifact_emits_.../repo/plans/job/outline.md'], returncode=1, stdout='UNRESOLVED: 3626686dcd522b47d57334da763ef14da1785cf0\n', stderr='').returncode
```

### tests/test_review_range_unresolved.py::test_unresolvable_prior_base_reported FAILED

```python
tests/test_review_range_unresolved.py:69: in test_unresolvable_prior_base_reported
    assert result.stdout == f"UNRESOLVED: {phantom}\n"
E   AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'UNRESOLVED: ...fffffffffff\n'
E
E     - UNRESOLVED: ffffffffffffffffffffffffffffffffffffffff
E     + CONFLICT: base 3626686dcd522b47d57334da763ef14da1785cf0 != ffffffffffffffffffffffffffffffffffffffff inherited from plans/prior-job/outline.md
```
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
````

## Files this dispatch changed

Modified:

- `plugin/agents/outline-corrector.md`
- `plugin/agents/design-corrector.md`
- `plans/provenance-enforcement-and-routing/classification.md`
- `plans/provenance-enforcement-and-routing/outline.md`
- `agents/learnings.md`
- `plugin/.claude/settings.json`
- `plugin/bin/bump-plugin-version.py`
- `docs/references/cli-and-package.md`
- `docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md`
- `.claude/handoff-todo.md`

Deleted (staged by `git rm`):

- `docs/superpowers/design/plugin-transition-evaluation.md`

Added:

- `plans/open-items-sweep/reports/prose-batch.md` (this report)

Not touched, as instructed: `plugin/bin/edify-review-range.sh`,
`scripts/check_line_limits.sh`, anything under `tests/`,
`plugin/bin/check-version-consistency.py`, `scripts/release.sh`. Nothing was
committed.
