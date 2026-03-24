# Classification: Fix handoff-cli RC9 findings

**Date:** 2026-03-24
**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (RC9: 0C/1M/10m)
**Plan status:** reviewed
**Round:** 9

## Composite Decomposition

| # | Finding | Behavioral? | Classification | Action |
|---|---------|-------------|----------------|--------|
| M-1 | `vet_check` path resolution bug (commit_gate.py:159) | Yes — changes path resolution condition | Moderate | `Path(f).exists()` → `(Path(cwd or ".") / f).exists()` |
| m-1 | Bare `pytest.raises(CleanFileError)` without match (test_session_commit.py:257) | No — tightens test assertion | Simple | Add `match=` |
| m-2 | Bare `pytest.raises(SessionFileError)` without match (test_session_parser.py:147) | No | Simple | Add `match=` |
| m-3 | Bare `pytest.raises(CalledProcessError)` without match (test_commit_pipeline_errors.py:26) | No | Simple | Add `match=` or returncode check |
| m-4 | Redundant `len > 0` assertion (test_session_handoff.py:45) | No — removes assertion | Simple | Remove `assert len(result.completed_lines) > 0` |
| m-5 | Redundant `len > 0` assertion (test_session_parser.py:57) | No | Simple | Remove `assert len(...) > 0` |
| m-6 | Fixture uses bold-colon format not `### ` headings (test_session_handoff.py:31) | No — string change | Simple | Update fixture to canonical `### ` heading format |
| m-7 | `step_reached` vestigial field (handoff/pipeline.py:20) | No — dead code removal | Simple | Remove field and all set sites |
| m-8 | `_AGENT_CORE_PATTERNS` hardcoded submodule name (commit_gate.py:138) | N/A — design-level deferral per outline.md C-1 | Pending task | Track; no fix this round |
| m-9 | `_git_output` lacks porcelain-safety docstring warning (commit_gate.py:31-43) | No — adds docstring | Simple | Add `.strip()` porcelain warning to docstring |
| m-10 | `format_commit_output` unconditional parent append (commit_pipeline.py:234) | Yes — adds conditional branch | Moderate | Wrap `parts.append(...)` with `if parent_output:` guard |

## Overall

- **Classification:** Mixed — Simple (m-1..m-7, m-9) + Moderate (M-1, m-10)
- **Implementation certainty:** High (all fixes have specific file:line and expected behavior)
- **Requirement stability:** High — RC9 findings with concrete locations and fix mechanisms
- **Behavioral code check:** M-1 and m-10 change production logic paths
- **Work type:** Production
- **Artifact destination:** production (src + tests)
- **Evidence:** RC9 deliverable-review.md; recall entries: behavioral-code-as-simple, composite-task, deliverable-review-resolution

## Routing

Moderate items present → `/runbook plans/handoff-cli-tool`
- TDD phases: M-1 (path resolution fix), m-10 (conditional guard)
- General phases: m-1..m-7, m-9 (test fixes and simple code changes)
- m-8: pending task (C-1 design deferral for submodule config model)
