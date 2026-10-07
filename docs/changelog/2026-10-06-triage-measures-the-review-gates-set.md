# 2026-10-06 — Triage measures the review gate's set; a committed failed fix no longer reverts by default

The round-2 deliverable review of `plans/build-fixes/` found triage measuring
something other than the run. D-90 recorded triage as taking
`changed-files.sh`'s `BASE:` and running two raw `<base> HEAD` diffs. Those
diffs counted the job's own `plans/<job>/` record and the exempt paths. On
build-fixes' own base the raw diff held 103 files, 69 of them under
`plans/build-fixes/`, against 34 from `changed-files.sh`. The behavioural-code
grep also matched report prose. The report count took the item reports on disk
with the rest, and since every item now leaves one, every Simple run would log
`underclassified` and the Complex `overclassified` branch could not be reached.
The script conformed to D-90's letter, so the error was in the design record,
not the code.

`plans/review-fixes-2/` makes triage measure the set the review gate reviewed.
`triage-feedback.sh <job>` takes no base, runs `changed-files.sh` itself and
counts its list: files changed is the list's length, and behavioural code is
read from the `<base> HEAD` diff of those paths only. The report count still
looks past the list, at the reports the range adds, minus the one every item
leaves and the review reports. The list drops the triage log,
`plans/reports/triage-feedback-log.md`, as pipeline record — by name, since an
Investigation's deliverable also lands under `plans/reports/` — and the count
drops `tdd-audit.md`, because a finished job re-invoked would run triage again
after its closing commit had landed both, and log a second row on the changed
evidence. A second copy of the list's filters inside triage was rejected: a copy
drifts, as D-90 already argued of prose copies. The triage log keeps its
columns, so rows from before this change sit beside rows measured the new way
(L-2).

The same review found the rollback protocol reverting a committed failed fix
with no decision, and the 2026-10-03 entry stating the opposite policy. Nothing
reverts by default now, committed or not: a committed failed fix escalates to my
human partner with the commits since the last clean commit, and only the commits
they choose are reverted (D-92). The pass also made work with no `Item N.M` one
item, Item 1.1, so every run leaves an item report and a `NO-BASE:` at finishing
is a fault (D-88), recorded the `sandbox-lies` plugin as optional, with the mask
re-run never firing without it (D-91), and stated the review gate's skill row in
one wording across its three texts (D-93).
