# 2026-08-04 — The publication postponement is reversed

`edify-cli` 0.0.3 went to PyPI through `just release`, three weeks after
publication was parked indefinitely (D-9, 2026-07-17). The `ddaanet` marketplace
gained an `edify` entry with a `git-subdir` source (`url: ddaanet/edify`,
`path: plugin`), so edify became installable. Releases 0.1.0, 0.1.1 and 0.2.0
followed.

**Why the postponement was lifted is not recorded anywhere in this repo.** The
nearest thing to a reason is that the publish was verified end to end through
the SessionStart bootstrap resolving from PyPI rather than from a local wheel —
an occasion, not a rationale. The reversal is a fact; its motivation is lost.

What survived the reversal is the ordering constraint D-9 warned about: the
bootstrap installs `edify-cli==<plugin version>`, so the package must reach the
index before the plugin version that pins it. `scripts/release.sh` encodes that
by splicing the PyPI publish between the tag push and the GitHub release, with
the marketplace bump last.

Being published still does not mean being consumed. Nothing outside this repo
installs either artifact, so compatibility remains a non-reason for keeping
anything (`docs/design.md` §9).
