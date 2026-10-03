# 2026-10-03 — `/build` reads its run state from report history; dirt is finished, not reverted

The deliverable review of `plans/build-defects/` found `/build`'s run state
resting on a file nothing protected. The run's base lived in
`tmp/build-baseline`, and the test for a resumed run sat in a node the hub
reached only once it already knew the run was resumed. A fresh-session
`/build plans/<job>` that did not say "resume" recaptured the baseline, and
every earlier item dropped out of the review gate, triage and phase 1's base. A
run killed between a phase's last item and its boundary commit resumed past the
boundary, and the next phase's base then resolved to nothing. Separately, the
no-owner cleanup `git checkout -- . && git clean -fd` reverted the
`.claude/handoff-*.md` and deleted the `inbox/*.md` dirt the clean-tree rule
declares legitimate.

`plans/build-fixes/` moved the state into what the run already commits. Every
item leaves a report that rides its commit (D-86), so an item report on disk is
the resume test (D-88). The run's base is the parent of the commit that added
the first one. A phase boundary has landed when the run holds a commit touching
its corrector report (D-89). One script, `changed-files.sh`, derives the base
and the changed-files list wherever they are needed (D-90), so nothing is
captured, stored or deleted. Commit subjects stay human labels naming the job
(D-94), because a typo in a convention must not break resume.

Dirt after an item is now that item's unfinished work (D-92). The owning agent
finishes it, or a fresh dispatch composed from the item does, and anything left
escalates. A revert happens only by my human partner's decision, path by path.
The clean-tree rule this protects (D-91), and the review gate's four fixed
groups (D-93), were recorded as decisions in the same pass. The seven decisions
form a new node, `docs/references/build-run-state.md`, because they did not fit
in `pipeline-contracts.md` under its 400-line cap.
