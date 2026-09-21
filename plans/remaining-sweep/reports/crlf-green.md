# GREEN: CRLF allowlist diagnostic

No commit — orchestrator commits.

## Order tests were made to pass

Both target tests were made to pass by the same single change (one CR check
inserted before the ceiling-integer check), verified one at a time per the
dispatch:

1. `tests/test_line_limits.py::test_line_limits_rejects_crlf_on_full_entry_line`
   — run alone, passed.
2. `tests/test_line_limits.py::test_line_limits_rejects_crlf_on_two_field_entry_line`
   — run alone, passed.

## Diff

```diff
diff --git a/scripts/check_line_limits.sh b/scripts/check_line_limits.sh
index c90d5cce..78960d4f 100755
--- a/scripts/check_line_limits.sh
+++ b/scripts/check_line_limits.sh
@@ -79,6 +79,10 @@ if [ -f "$ALLOWLIST" ]; then
         case "$entry_path" in
         \#*) continue ;;
         esac
+        if [[ "$entry_path" == *$'\r'* || "$ceiling" == *$'\r'* || "$_note" == *$'\r'* ]]; then
+            echo "check_line_limits: $ALLOWLIST: line $line_no: entry has a carriage return (CRLF line ending)" >&2
+            exit 2
+        fi
         if ! [[ "$ceiling" =~ ^[0-9]+$ ]]; then
             echo "check_line_limits: $ALLOWLIST: line $line_no: ceiling is not an integer: $ceiling" >&2
             exit 2
```

The check runs after the comment-line skip (`\#*) continue`) and before the
existing ceiling-integer regex, on all three `read` targets
(`entry_path`, `ceiling`, `_note`) so a CR landing on any of them — the note
field in the three-field case, the ceiling field in the two-field case — is
caught by one check instead of three separate per-field checks. `$'\r'`
glob-pattern matching (`[[ ... == *$'\r'* ]]`) is bash-3.2-safe; no bash-4
feature used.

`scripts/check_line_limits.allow` was read; its header comment documents
format and ratchet rules only, no error conditions — left unchanged.

## Comment and blank-line CR cases

- **CR-only "blank" line** (a line containing only `\r` before the `\n` that
  `read` strips): reachable, and now caught as malformed. `read -r
  entry_path ceiling _note` on `"\r\n"` leaves `entry_path="$'\r'"` — a
  one-character string, not empty — so the existing `[ -z "$entry_path" ] &&
  continue` blank-line skip does **not** catch it (that skip only catches a
  truly empty first field, i.e. a line that is just `\n`). It falls through
  the comment-line case too (`\r` does not start with `#`), reaching the new
  CR check, which exits 2 with the carriage-return diagnostic. This is a
  natural consequence of the minimal check, not added behaviour: no special
  case was written for it.
- **CRLF comment line** (e.g. `# foo\r\n`): not reachable by the new check.
  `entry_path` is the whole field `"# foo\r"`, which matches the existing
  `\#*) continue` case and is skipped *before* the new CR check runs — same
  as any other comment line today. No behaviour change for comments.

## Full gate outputs

### `just test`

```
# Test Report

**Summary:** 333/334 passed, 1 xfail
✓ Tests OK
```

(Both new CRLF tests are counted within `333/334 passed`; verified
individually above and confirmed present via the two isolated `-k` runs.)

### `just lint`

```
# Test Report

**Summary:** 333/334 passed, 1 xfail
✓ Lint OK
```

### `just precommit`

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 285 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✓ Precommit OK
```

All nine `oversized-file` lines are pre-existing entries in
`scripts/check_line_limits.allow` (unmodified by this slice) — reported per
the script's documented behaviour ("still reported ... but only fails the
run if it also exceeds its ceiling") and not failures. No new warnings from
this change. Precommit exits clean.
