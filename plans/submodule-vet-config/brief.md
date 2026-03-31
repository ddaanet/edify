# Brief: Submodule vet config model

## 2026-03-14: Config model for submodule vet patterns

**Problem:** Commit vet check (C-1) covers `plugin/bin/**`, `plugin/skills/**/*.sh` — currently hardcoded. No configurable mechanism for submodule-specific review patterns.

**Decision deferred:** Unified parent `pyproject.toml` vs per-repo `pyproject.toml`. Requires external grounding on how multi-repo projects configure cross-repo linting/review patterns.

**Current state:** handoff-cli-tool Cycle 5.3 hardcodes plugin patterns as interim.
