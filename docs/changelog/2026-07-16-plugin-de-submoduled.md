# 2026-07-16 — Plugin de-submoduled

`plugin/` stopped being a git submodule and became a plain tracked subdirectory
of the package repo (D-10, commit `c3c4477f`). The submodule shipped a live
defect: a parent repo cannot `git add` inside a submodule, so
`git add plugin/.claude-plugin/plugin.json` failed and `just release` could not
complete a real release. The old `ddaanet/edify-plugin` GitHub repo was
archived.
