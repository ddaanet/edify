# 2026-07-17 — Bootstrap reversed from stdlib venv to uv

The previous day's choice of a stdlib venv (`python3 -m venv` + pip) was
reversed. A stdlib venv inherits the host interpreter, so it required host
`python3` ≥3.14 and failed loudly otherwise — unshippable on hosts still at
3.13. uv fetches its own interpreter, removing the host floor. The price is a uv
runtime dependency, paid down by informative degradation when uv is absent
(NFR-5).

Publication was postponed indefinitely by user decision the same day (D-9): the
PyPI publish and the marketplace `git-subdir` entry are parked, so edify is
uninstallable meanwhile.
