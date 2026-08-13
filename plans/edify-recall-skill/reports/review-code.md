# Code Review: recall skill — docstring and doc listing edits

**Baseline:** ce4d03d4109ac79cb306b326edc748061a5299cb
**Files reviewed:** `plugin/bin/prepare-runbook.py`, `CLAUDE.md`, `plugin/README.md`

## Diff against baseline

```diff
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -176,7 +176,7 @@ Source in `src/edify/`. Four tools:
 In `plugin/skills/`, invoked via slash command.

 - **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate` (Tier 3) or `inline` (Tier 1/2), with `review-plan` and `review` as the quality gates.
-- **Standalone:** `proof`, `ground`, `deliverable-review`, `formalize`.
+- **Standalone:** `proof`, `ground`, `deliverable-review`, `formalize`, `recall`.

--- a/plugin/README.md
+++ b/plugin/README.md
@@ -39,6 +39,7 @@ conversation. Each lives in `skills/<name>/SKILL.md`.
 | `/deliverable-review` | Post-execution artifact review, severity-classified against ISO 25010 / IEEE 1012 |
 | `/ground` | Ground a methodology in external research before asserting it (diverge–converge) |
 | `/formalize` | Verify a Python function against intent via an icontract contract checked with `edify check` (CrossHair) |
+| `/recall` | Select and Read relevant memory-index entries for the current task or a given topic |

--- a/plugin/bin/prepare-runbook.py
+++ b/plugin/bin/prepare-runbook.py
@@ -128,7 +128,7 @@ def _parse_artifact_path(entry_line):

 def resolve_recall_entries(paths, repo_root=None):
-    """Read the memory and decision files named in the recall artifact.
+    """Read the memory files named in the recall artifact.

     Returns the concatenated file contents, each under a heading naming its
     source path. Missing files warn and are skipped -- a stale artifact
```

## Findings

None. All three edits match the design spec exactly.

- **`resolve_recall_entries` docstring**: body (unchanged, lines 130-149) resolves whatever
  repo-relative paths the artifact names, with no filtering by content category — it never
  distinguished "memory" from "decision" files at runtime. The old wording described a corpus
  split that doesn't exist in the code; the new first line is accurate and requires no logic
  change.
- **`CLAUDE.md`**: `recall` appended to the Standalone skills list, matching the existing
  comma-separated backtick-list style.
- **`plugin/README.md`**: new `/recall` row added to the Standalone table, consistent in format
  (pipe-delimited, `/name` + one-line description, no trailing period) with adjacent rows.
- No unintended code changes in `prepare-runbook.py` — diff is docstring-only.
- No stray edits in any of the three files.

## Verdict

APPROVED — no fixes needed.
