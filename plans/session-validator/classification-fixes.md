# Classification: Session Validator Fix Pass

**Source:** Deliverable review findings (`plans/session-validator/reports/deliverable-review.md`)

## Per-Item Classification

| Finding | Classification | Certainty | Stability | Behavioral | Work Type | Destination |
|---------|---------------|-----------|-----------|------------|-----------|-------------|
| C-1: Porcelain parser bug | Defect | High | High | Yes (fix broken logic) | Production | production |
| C-2: H3 headings unhandled | Defect | High | High | Yes (new condition) | Production | production |
| M-4: Pipe metadata parsing | Defect | High | High | Yes (fix logic path) | Production | production |
| M-1: Warnings discarded | Moderate | High | High | Yes (new return path) | Production | production |
| M-2: Backtick path validation | Moderate | High | High | Yes (new function) | Production | production |
| 15 minor findings | Simple | High | High | No | Production | production |

## Scope Decisions

- **M-3 (NFR-2 `--fix` flag):** Deferred as separate task — full feature, not a fix
- **M-2 expanded scope:** Validate paths exist, reject out-of-tree paths, `tmp/` paths, `plans/claude` references

## Routing

Composite → `/runbook` (behavioral code in M-1/M-2, defects need test coverage, simple items merge with adjacent phases)
