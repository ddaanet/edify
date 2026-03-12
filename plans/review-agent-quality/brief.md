# Brief: Review Agent Quality

## Problem

Review and corrector agents (corrector, design-corrector, outline-corrector, runbook-corrector) exhibit two complementary failure modes: false positives (flagging non-issues) and false negatives (missing real issues). Both erode trust — false positives train operators to dismiss findings, false negatives let defects through.

The "Do NOT Flag" suppression taxonomy (plan: vet-false-positives) addressed one surface: giving correctors explicit categories to skip. But false positives persist, and missed-issue patterns have no systematic tracking or root cause analysis.

## Evidence

### False Positives

- **Exploration agents over-read:** 3-way review of runbook-phase-1.md filtered 2 false positives that a single reviewer would have accepted. Exploration agents produce false positives from pattern over-matching (`operational-practices.md`, 2026-02-18)
- **Haiku model tier:** Haiku scouts produced 15 gate findings vs sonnet's 12, with 3 false positives. Haiku grades generously and misses dominant failure patterns (`orchestration-execution.md`, 2026-02-25)
- **Validate-runbook false positives:** Lifecycle checker flagged pre-existing files as violations. 7-bug fix batch included model-tags and lifecycle false positives in prepare-runbook.py and validate-runbook.py (plan: parsing-fixes-batch)
- **Pre-existing rationalization:** Agent dismissed test failures as "pre-existing" without verifying — two instances in one session (`68963394`, `63af67bf`). `replace_all` on mock targets was syntactically correct but semantically wrong (`learnings.md`)

### False Negatives (Missed Issues)

- **Opus missed implementation-level issue:** `_git()` return value bug only caught by reading source code directly — opus reviewer missed it. Each of 3 independent reviewers found unique real issues (`operational-practices.md`, 2026-02-18)
- **Vet missed systemic conformance gaps:** Vet agent reviewed code quality but missed external reference comparison failures because the review mandate didn't include that check (`defense-in-depth.md`)
- **Corrector skip via downgrade:** Post-outline complexity re-check said "all downgrade criteria hold" — agent skipped corrector review entirely. Downgrade criteria gate complexity classification, not author-blind errors (`learnings.md`, 2026-03-12)
- **Precommit broken 9 days:** `just precommit` broken for ~845 commits due to non-existent `claudeutils validate` command. No agent noticed — failure rationalized or bypassed each time (`implementation-notes.md`, 2026-02-18)

### Existing Mitigations

- **"Do NOT Flag" taxonomy** in corrector prompts: pre-existing issues, out-of-scope items, pattern-consistent style, linter-catchable issues (plan: vet-false-positives, delivered)
- **Multi-reviewer pattern:** 3+ independent reviewers, cross-reference for agreement filtering (`operational-practices.md`)
- **2x2 diagnostic procedure:** Controlled experiment isolating model tier vs input content vs delegation prompt as defect source (`operational-practices.md`)

## Scope

Systematic audit of review agent quality across all corrector types. Two workstreams:

1. **False positive corpus:** Mine corrector reports and session history for flagged-then-dismissed findings. Categorize by root cause (rule too broad, missing context, pattern mismatch, model tier). Determine which suppression categories from the existing taxonomy actually reduce false positives vs which are unused.
2. **Missed-issue RCA:** For each post-review defect that reached commit or delivery, trace back through the review that should have caught it. Identify whether the miss was scope (review didn't look), capability (model couldn't detect), or prompt (instructions didn't ask).

Out of scope: redesigning the multi-reviewer architecture. This plan collects evidence to inform future architectural changes.

## Investigation Approach

- Extract corrector report files from `plans/*/reports/` and categorize findings by verdict (accepted vs rejected by operator)
- Cross-reference with git history: commits that followed corrector runs but contained regressions detected later
- Use session-scraper to mine session transcripts for corrector interactions, especially operator overrides of corrector findings
- Catalog the 2x2 diagnostic procedure results if any have been run
- Assess "Do NOT Flag" taxonomy coverage against observed false positive categories

## Success Criteria

- Evidence corpus with categorized false positive instances from actual corrector runs (target: 10+)
- Top 3 false positive root cause categories identified with frequency data
- At least 3 missed-issue RCAs completed with root cause classification (scope / capability / prompt)
- Gap analysis: which false positive categories are not covered by existing "Do NOT Flag" taxonomy
- Actionable recommendations ranked by expected impact

## References

- `agents/decisions/operational-practices.md` — multi-reviewer diagnostics, 2x2 controlled experiment
- `agents/decisions/orchestration-execution.md` — haiku scout false positives, model tier effects
- `agents/decisions/defense-in-depth.md` — defense layer checklist, script vs agent enforcement split
- `agents/decisions/implementation-notes.md` — precommit rationalization, vet feedback dismissal
- `agents/plan-archive.md` — vet-false-positives (delivered), parsing-fixes-batch (false positive fixes)
- `agents/learnings.md` — corrector skip via downgrade, pre-existing test failure dismissal
