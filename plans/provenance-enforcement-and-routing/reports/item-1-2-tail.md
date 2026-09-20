# Item 1.2 tail — deliverable-review Phase 1 step 2

Job: `plans/provenance-enforcement-and-routing/`. Requirement: M-4, per KD-2.

The script half of Item 1.2 (`edify-review-range.sh`, 14 tests) landed earlier.
This is the skill rewrite: Phase 1 step 2 of `deliverable-review/SKILL.md` now
calls the script by bare name and acts on its verdict, and the parsing prose it
carried is deleted.

## New step 2, verbatim

```markdown
2. Establish the review range: run `edify-review-range.sh <artifact-path>`, by bare name — Claude Code puts every enabled plugin's `bin/` on PATH, so no path is needed. Act on the one verdict line it prints:

   | Exit | Line | Do |
   |------|------|----|
   | 0 | `RANGE: <base>..HEAD` | proceed with it |
   | 1 | `CONFLICT: base <a> != <b> inherited from <path>` | **STOP** — report both bases and the path. One of the two artifacts is wrong and the script cannot know which; do not substitute a range |
   | 1 | `NO-PROVENANCE:`, `UNRESOLVED: <base>`, `NO-PRIOR: <path>` | ask the user for the range |
   | any other | — | STOP: the script failed, no verdict |

   With the range established, run `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude'` for per-file line counts. A submodule that moved in the range is diffed inside the submodule between its two pointers
```

Deleted: reading `<Base>` from §Provenance, and the `git rev-parse <Base>^{commit}`
resolution check — both are the script's job now. Kept: the `git diff --numstat`
per-file counts with the same pathspec, and the submodule-moved note.

The verdict lines were checked against the script's own `echo`/`printf` call
sites (`edify-review-range.sh:86,94,106,113,118,136,145,150,154,159`), not only
against its header comment; they match.

No repo-relative `plugin/…` path appears in the new text — the script is named
by bare name only, with the PATH clause explaining why.

## Other hits

None. `grep -rn -i 'base\|provenance\|inherit\|range'` over
`plugin/skills/deliverable-review/` returns no other sentence claiming the skill
reads `Base:` itself or describing the inheritance check as manual. The three
other hits are unrelated: `SKILL.md:23` ("conformance baseline"), and
`references/example-report.md:129` and `:164`, which are example-report content.

## Precommit

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

Requested subject: `docs: Item 1.2 — deliverable-review establishes its range by
edify-review-range.sh`. The repo's gitmoji commit-msg hook rewrites the `docs:`
prefix, so the landed subject is `📝 Item 1.2 — deliverable-review establishes
its range by edify-review-range.sh`, matching the surrounding history.
