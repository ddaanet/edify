---
name: deliverable-review
description: >-
  Review production artifacts after plan execution. Triggers on "review deliverables",
  "deliverable review", "artifact review", or after completing plan execution.
  Two-layer review (delegated per-file + interactive cross-project) producing
  severity-classified report grounded in ISO 25010 / IEEE 1012.
allowed-tools:
  - Agent
  - Read
  - Bash
  - Write
user-invocable: true
---

# Review Production Artifacts

Review production artifacts against a design specification to identify
conformance gaps, correctness issues, coverage holes, and excess artifacts.

## Prerequisites

`ls plans/<plan>` — branch on what it lists. Neither `design.md` nor
`outline.md` present → STOP: there is no conformance baseline, and a review
without one reports an empty gap analysis as a clean one.

- **Design artifact** — the conformance baseline. Take the first that exists:
  `plans/<plan>/design.md`, else `plans/<plan>/outline.md`. The agentic-prose
  route produces only an outline, so a `design.md`-only prerequisite leaves that
  route's work unreviewable
- **Plan directory** — for report output (`plans/<plan>/reports/`)

## Process

### Phase 1: Inventory

1. Read the design artifact's Scope section (IN/OUT) to establish expected
   deliverables
2. Establish the review range: run `edify-review-range.sh <artifact-path>`, by
   bare name — Claude Code puts every enabled plugin's `bin/` on PATH, so no
   path is needed. Act on the one verdict line it prints:

   | Exit | Line | Do |
   |------|------|----|
   | 0 | `RANGE: <base>..HEAD` | proceed with it |
   | 1 | `CONFLICT: base <a> != <b> inherited from <path>` | **STOP** — report both bases and the path. One of the two artifacts is wrong and the script cannot know which; do not substitute a range |
   | 1 | `NO-PROVENANCE:`, `UNRESOLVED: <base>`, `NO-PRIOR: <path>` | ask the user for the range |
   | any other | — | STOP: the script failed, no verdict |

   With the range established, run
   `git diff --numstat <range> -- . ':!plans' ':!tmp' ':!.claude/handoff-*'` for
   line counts. A submodule that moved in the range is diffed inside the
   submodule between its two pointers
3. Classify each deliverable by artifact type:

| Type | Pattern | Review axes |
|------|---------|-------------|
| Code | `*.py` source | Universal + robustness, modularity, testability, idempotency, error signaling |
| Test | `test_*.py` | Universal + specificity, coverage, independence |
| Agentic prose | `SKILL.md`, agent defs | Universal + actionability, constraint precision, determinism, scope boundaries |
| Human docs | Fragments, references, `docs/` | Universal + accuracy, consistency, completeness, usability |
| Configuration | Justfile, pyproject, `.claude/settings.json`, `.claude/rules/*.md` | Universal only |

Universal axes (all types): conformance, functional correctness, functional
completeness, vacuity, excess.

Full axis definitions: `references/axes.md`

### Phase 2: Gap Analysis

Compare inventory against the design artifact's In-scope items:
- **Missing deliverables** — specified but not produced
- **Unspecified deliverables** — produced but not in design scope
- **Excess** in unspecified is acceptable only where the deliverable itself
  states why it exists — an edge case named in a test docstring, a defensive
  branch with a comment. Unexplained excess is a finding.

### Phase 3: Per-Deliverable Review

Two-layer review. Layer 1 is optional (scales to large deliverable sets). Layer
2 is mandatory (catches what delegation cannot).

#### Layer 1: Delegated Per-File Review (optional)

Gate on total changed lines from Phase 1 inventory. The three thresholds below
are an **ungrounded starting point** — no measurement supports them:

| Total lines | Strategy |
|-------------|----------|
| < 500 | **Skip Layer 1** — Layer 2 handles full review |
| 500–2000 | Two opus agents: code+test, prose+config |
| > 2000 | Three opus agents: code, test, prose+config |

When Layer 1 applies, partition deliverables by type and launch the review
agents in a single message — that is what makes them parallel. Each agent
receives:
- Files to review (with line counts)
- Design reference path
- Applicable review axes for its artifact types
- Output report path: `plans/<plan>/reports/deliverable-review-<type>.md`,
  `<type>` being `code`, `tests`, `prose` or `config` — one per partition,
  joined with `-` where a partition covers two

Each agent follows `../../fragments/delegation.md`: quiet execution (report to
the named file, return the filepath or an error), `Bash` in its tool list for
search, and the recall artifact resolved by path rather than inlined.

#### Layer 2: Interactive Full-Artifact Review (mandatory)

Always runs in main session with full cross-project context.

**Scope depends on whether Layer 1 ran:**

| Layer 1 | Layer 2 scope |
|---------|---------------|
| Skipped (< 500 lines) | Full review: per-file axes AND cross-cutting checks |
| Ran | Cross-cutting focus: issues delegation cannot catch |

**Cross-cutting checks (always):**
- Path consistency across documents
- API contract alignment between modules
- Naming convention uniformity
- Fragment convention compliance — each `plugin/fragments/` file opens with an
  `## ` heading naming its rule and states the rule before its rationale
- Other skills' allowed-tools and frontmatter cross-reference validation

**Per-file review (when Layer 1 skipped):**
- Read each deliverable and evaluate against type-specific axes
- Record findings with: file and enclosing symbol (no line numbers — a later fix
  pass reads the finding after the code has moved), axis violated, severity,
  description

**Why interactive is mandatory:** Delegated agents lack cross-project context —
fragment conventions, other skills' configurations, inter-file consistency.
Layer 2 forms its own judgement by reading deliverables directly against the
design spec, never by reading a delegation report first. The judgements are
independent; Phase 4 merges the findings.

### Phase 4: Report

Where Layer 1 ran, Read each `plans/<plan>/reports/deliverable-review-<type>.md`
it produced and merge its findings into the consolidated set, deduplicating
against Layer 2's own. Attribute each merged finding to its sub-report.

Write the consolidated report to `plans/<plan>/reports/deliverable-review.md`.

**Report structure:**

```markdown
# Deliverable Review: <plan-name>

**Date:** <date — from `date -I`>
**Methodology:** deliverable-review skill, references/axes.md

## Inventory
[Table: type, file, lines]
[Design conformance summary]

## Critical Findings
[Numbered, with file and enclosing symbol, design requirement, impact]

## Major Findings
[Same format]

## Minor Findings
[Grouped by category, brief]

## Gap Analysis
[Table: design requirement, status (covered/missing) with the finding id]

## Summary
[Severity counts, assessment]

## Sub-reports
[Paths of every Layer 1 report merged in Phase 4; omit when Layer 1 skipped]
```

**Severity classification** — `references/axes.md` defines the three levels; the
extensions below are this skill's, not that file's:
- **Critical** — incorrect behavior, data loss, security, unimplemented design
  requirement
- **Major** — missing functionality, broken references, vacuous artifact, test
  gap for specified scenario
- **Minor** — style, clarity, naming, robustness edge case

**Next steps:**

Report severity counts only. No merge-readiness language — the user reads
severity counts and decides what to act on. The report is the deliverable; the
skill does not queue follow-up work or record lifecycle state.

## References

- **Methodology** — full axis definitions, ISO/IEEE sources:
  `references/axes.md`
- **Example report** — completed review with all sections:
  `references/example-report.md`
