# /build leg 1 — review-fixes-2

## Run start

- Job: `plans/review-fixes-2`, work = `outline.md` (no runbook).
- Mode: fresh — no `plans/review-fixes-2/reports/item-*.md` on disk.
- HEAD at leg start: `bb058555` (outline commit).

## Items completed

None. The run did not pass the entry gate.

## Entry gate (`/build` §2)

`plugin/skills/build/scripts/verify-step.sh` (unsandboxed) exited 1:

```
DIRTY: uncommitted changes
 M .claude/rules/workflow-work.md
```

The staged `.claude/handoff-*.md` files and the untracked `inbox/*.md` brief
are exempt and were not reported. `.claude/rules/workflow-work.md` is not an
exempt path, and no `sandbox-lies` annotation marks it as a mask: the diff is
real content — it adds `docs/references/build-run-state.md` to the files the
rule tells agents to read, and "how /build keeps its run state in git" to its
key areas.

The skill's verdict is STOP ("Dirty tree. Commit or stash before /build."), and
the dispatch forbids touching my human partner's dirt. Nothing was staged,
committed, reverted or stashed apart from this report.

## Deviations

None.

## Open items

All items of the outline: 1.1–1.6, 2.1–2.11, 3.1–3.4.

## Where to resume

Re-invoke `/build plans/review-fixes-2` once the tree passes the entry gate.
The run is still fresh (no `item-*` report), so §2's gate runs again.

## Gate question

1. `.claude/rules/workflow-work.md` carries an unstaged, non-exempt edit, and
   the entry gate refuses on it. How should it be resolved? Default: my human
   partner commits it themselves (it is a self-contained routing improvement
   naming `build-run-state.md`), then the run resumes. Alternatives: authorize
   the orchestrator to commit it by path as a separate commit, or move it out
   of the tree.
