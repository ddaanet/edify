# code-batch report

## Item 1 — `run-project-checks` hook: BLOCKED, not applied

The first `Edit` call, targeting `plugin/portable.just` (adding the
`run-project-checks() { :; }` no-op hook plus its explanatory comment, and
the call to it from the portable `precommit` recipe immediately before
`report-end-safe "Precommit"`), returned:

```
The server-side auto mode classifier gave no verdict (it skipped this
action), so auto mode cannot determine the safety of Edit. Retrying this
action will not change that. Continue with other tasks that don't require
it; if it is essential, stop and tell the user that auto mode could not
evaluate it.
```

Verified via `git status --porcelain -- plugin/portable.just` and a re-read
of the file that the edit did not land — `plugin/portable.just` is unchanged
on disk.

Per instructions I stopped on this file (no `sed`/`python`/heredoc fallback)
and did not attempt the second `plugin/portable.just` edit or any edit to the
root `justfile`. The `justfile` half of item 1 (deleting the duplicated
`precommit` recipe and its 7-line comment, and redefining
`run-project-checks() { run-design-links; }` in the root `bash_prolog`
override) depends on the portable hook existing — applying it alone would
delete the only place `run-design-links` currently runs from `precommit`
without giving the portable recipe any way to call it, silently dropping the
design-links check from `just precommit`. I left both files untouched rather
than land that.

Read of `justfile`'s `bash_prolog` override (lines 101–233): it is a **full
copy** of the portable prolog, not a composition — it redefines every
function (`safe`, `end-safe`, `show`, `visible`, `fail`, `sync`,
`set-tmpfile`, `report`, `run-checks`, `run-pytest`, `run-line-limits`,
`report-end-safe`) plus repo-only additions (`wt-path`, `add-sandbox-dir`,
`run-design-links`). It does not source or extend `plugin/portable.just`'s
prolog at all — `set allow-duplicate-recipes`/`set allow-duplicate-variables`
is what lets the later `bash_prolog` assignment win.

### Intended diff (not applied)

`plugin/portable.just`, in the shared prolog, after `run-line-limits()` and
before `report-end-safe()`:

```diff
 run-line-limits() {
     ...
     report "line limits" ./scripts/check_line_limits.sh
 }
+# No-op hook: a consuming repo's own bash_prolog override redefines this to
+# add project-specific checks (e.g. checks against files this portable
+# module has no notion of) without touching the shared `precommit` body.
+run-project-checks() { :; }
 report-end-safe() {
```

`plugin/portable.just`, in the portable `precommit` recipe:

```diff
     report "rumdl" rumdl fmt --check -q --no-cache
     run-line-limits
+    run-project-checks
     report-end-safe "Precommit"
```

`justfile`, delete lines 64–86 (the duplicated `precommit` recipe and its
justification comment):

```diff
-# `precommit` and `dev` are defined in plugin/portable.just, which ships to
-# other projects that have no docs/decisions.md or docs/references/ — the
-# design-links check does not belong there. This overrides portable.just's
-# `precommit` (via `set allow-duplicate-recipes`, same mechanism this file
-# already uses to override its shared `bash_prolog`) to add `run-design-links`
-# for this repo only; `dev: format precommit` picks it up automatically, since
-# `just` resolves a recipe dependency by name against the final recipe set.
-# Run all checks
-[no-exit-message]
-precommit:
-    #!{{ bash_prolog }}
-    sync
-    run-checks
-    report "version consistency" python3 plugin/bin/check-version-consistency.py
-    run-pytest
-    # Non-fixing: `fmt --check` exits 1 exactly when `fmt` would rewrite a
-    # file, and `-q` drops the summary so a clean run prints nothing. Plain
-    # `rumdl check` is not equivalent — it also reports the over-column lines
-    # MD013 cannot reflow, which no `fmt` pass can clear.
-    report "rumdl" rumdl fmt --check -q --no-cache
-    run-line-limits
-    run-design-links
-    report-end-safe "Precommit"
-
```

`justfile`'s `bash_prolog` override, next to `run-design-links()` (around
line 222):

```diff
 run-design-links() {
     report "design links" ./scripts/check_design_links.sh
 }
+# Overrides portable.just's no-op hook: design-links belongs to this repo
+# only, since other consumers of portable.just have no docs/decisions.md.
+run-project-checks() { run-design-links; }
 report-end-safe() {
```

None of the above was applied. Files touched for item 1: **none**.

## Item 2 — `scripts/release.sh` marketplace description sync: DONE

### Diff

```diff
diff --git a/scripts/release.sh b/scripts/release.sh
index e394d6ba..abd8d7a9 100755
--- a/scripts/release.sh
+++ b/scripts/release.sh
@@ -189,9 +189,10 @@ bump_marketplace() {
     local mp_tmp repo_slug mp_branch mp_remote_head mp_local_head committed=0
     mp_tmp=$(mktemp)
     if [ "$marketplace_entry_exists" = 1 ]; then
-        jq --arg n "$plugin_name" --arg v "$V" \
-            '(.plugins[] | select(.name == $n) | .version) = $v' \
-            "$marketplace_json" > "$mp_tmp"
+        jq --arg n "$plugin_name" --arg v "$V" --slurpfile m "$manifest" '
+          (.plugins[] | select(.name == $n) | .version) = $v
+          | (.plugins[] | select(.name == $n) | .description) = ($m[0].description // "")
+        ' "$marketplace_json" > "$mp_tmp"
     else
         repo_slug=$(git remote get-url origin | sed -E 's#\.git$##; s#^.*[:/]([^/]+/[^/]+)$#\1#')
         jq --arg v "$V" --arg repo "$repo_slug" --arg subdir "$plugin_subdir" --slurpfile m "$manifest" '
```

Uses `--slurpfile m "$manifest"` and the `// ""` default, matching the
create-entry branch. The `cmp -s` no-change path below is untouched — the
diff only adds a second `jq` filter clause piped with `|`.

### Verification

`bump_marketplace` cannot be exercised alone: `scripts/release.sh` is a
straight-line sequence (`common_preflight` → `release_preflight`/
`resume_preflight` → `bump_commit_tag` → `push_branch` → `push_tag` →
`publish_pypi` → `create_github_release` → `bump_marketplace`) with no
subcommand dispatch, and every step ahead of `bump_marketplace` requires live
git remote/tag state, `gh` auth, and a PyPI token — none safely exercisable
here. Ran the new `jq` expression standalone instead, against a `$TMPDIR`
fixture directory holding a marketplace.json with an `edify` entry carrying a
wrong description and version, using the real
`plugin/.claude-plugin/plugin.json` as `$manifest` and `plugin_name=edify`,
`V=9.9.9`:

Input entry:

```json
{
  "name": "edify",
  "source": { "source": "github", "repo": "ddaanet/edify" },
  "description": "stale wording from an old release",
  "version": "0.1.0",
  "author": { "name": "ddaanet" },
  "repository": "https://github.com/ddaanet/edify",
  "license": "MIT"
}
```

Output entry:

```json
{
  "name": "edify",
  "source": { "source": "github", "repo": "ddaanet/edify" },
  "description": "A lean bundle of Claude Code skills and agents built around a requirements → design → runbook → build planning pipeline",
  "version": "9.9.9",
  "author": { "name": "ddaanet" },
  "repository": "https://github.com/ddaanet/edify",
  "license": "MIT"
}
```

Both `.version` and `.description` update to the manifest's current values;
all other fields pass through unchanged.

### `EDIFY_VERSION` / `sessionstart-health` grep

```
grep -n "EDIFY_VERSION\|sessionstart-health" scripts/release.sh plugin/bin/check-version-consistency.py
```

No hits in either file.

Files touched for item 2: `scripts/release.sh`.

## Full `just precommit` output

Run from the repo root with the working tree as found (other in-progress,
uncommitted work from other batches is present — this run's `precommit`
recipe is still the pre-existing duplicated one in `justfile`, unmodified by
this report, since item 1 was not applied):

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 356/361 passed, 4 failed, 1 xfail

## Failures

### tests/test_review_range_range.py::test_prior_base_uppercase_same_commit_emits_range FAILED
AssertionError: CONFLICT: base 067c024d7ba93fa569ecdbef8e85b86266746fd1 != 067C024D7BA93FA569ECDBEF8E85B86266746FD1 inherited from plans/prior-job/outline.md
assert 1 == 0

### tests/test_review_range_range.py::test_backticked_none_emits_range FAILED
AssertionError: NO-PROVENANCE:
assert 1 == 0

### tests/test_review_range_range.py::test_crlf_artifact_emits_range FAILED
AssertionError: UNRESOLVED: 067c024d7ba93fa569ecdbef8e85b86266746fd1
assert 1 == 0

### tests/test_review_range_unresolved.py::test_unresolvable_prior_base_reported FAILED
AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'UNRESOLVED: ...fffffffffff\n'
  - UNRESOLVED: ffffffffffffffffffffffffffffffffffffffff
  + CONFLICT: base 86179dafd7b3825a497cccfb597405c56c87c953 != ffffffffffffffffffffffffffffffffffffffff inherited from plans/prior-job/outline.md

# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
```

The four `tests/test_review_range_*` failures match the "expected from a
pending slice" note in the dispatch. The three `oversized-file` findings
(`corrector.md`, `outline-corrector.md`, `design-corrector.md`) are
pre-existing/concurrent — none of those files were touched by this batch
(only `scripts/release.sh` was edited; the item-1 edit to
`plugin/portable.just` did not land). `ruff`/`docformatter`/`mypy`/`rumdl`
printed nothing, so `scripts/release.sh`'s change is clean on every check
that inspects it (shell scripts aren't linted by this recipe — no
shellcheck step is wired into `precommit`).

## Files touched

- `scripts/release.sh` (item 2, applied)
- `plugin/portable.just` — edit attempted, not applied (classifier error)
- `justfile` — not touched (depends on the blocked `plugin/portable.just` edit)
