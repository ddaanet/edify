# Session Handoff: 2026-03-10

**Status:** A/B test infrastructure built. Blocked on human curation + annotation before experiment run.

## Completed This Session

**A/B test infrastructure:**
- Built 5 prototype scripts in `plans/prototypes/ab-*.py` — all CLI-arg driven, no hardcoded paths
- Variant generator: parses `memory-index.md`, produces A (bare) and B (to) variants, 62 /how entries, validated equivalence
- Task selector: extracts 20 task contexts from session history (3 from /how sessions, 17 diverse), two-strategy merge
- Forced selection harness: calls Claude API per (task, variant) pair, temperature 0, supports `--dry-run`/`--resume`
- Analysis script: McNemar's test on paired binary outcomes, per-entry sensitivity (ProSA-inspired)
- Ground truth annotation: generates markdown template, parses back to JSON
- Generated initial data: variants, task contexts, annotation template in `plans/reports/ab-test/`
- Pipeline README with blocking human steps as checkboxes (file: plans/reports/ab-test/README.md)

**Previous sessions (carried forward):**
- Grounding complete: Q1 matcher deficiency confirmed, Q2 requires empirical A/B (methodology grounded Strong)
- Discuss protocol revised: stress-test → research-your-claims

## In-tree Tasks

- [x] **Restart grounding** — `/ground` | sonnet
  - Both questions grounded. Q1: matcher deficiency confirmed. Q2: requires A/B test (methodology grounded).
- [!] **Verb form AB test** — see `plans/reports/ab-test/README.md` | sonnet
  - Infrastructure built. Blocked on human: curate task-contexts.json, annotate ground-truth.md
  - After human steps: run harness then analysis (commands in README)

## Worktree Tasks

- [ ] **Fix prefix tolerance** — `src/claudeutils/when/fuzzy.py` | sonnet
  - Zero tolerance for prefix noise (0.0 scores on one-token mismatch). Separate from format decision.

## Reference Files

- `plans/reports/ab-test/README.md` — pipeline, blocking human steps, commands
- `plans/reports/ab-test/` — generated data (variants, tasks, annotation template)
- `plans/reports/how-verb-form-ab-methodology.md` — A/B test methodology (Strong grounding)
- `plans/reports/how-verb-form-grounding.md` — synthesis report (Moderate grounding)
- `plans/prototypes/ab-variant-generator.py` — generates index variants A/B
- `plans/prototypes/ab-task-selector.py` — extracts task contexts from sessions
- `plans/prototypes/ab-harness.py` — forced selection API harness
- `plans/prototypes/ab-analysis.py` — McNemar's test + per-entry sensitivity
- `plans/prototypes/ab-ground-truth.py` — annotation template generator/parser
- `src/claudeutils/when/fuzzy.py` — production fuzzy matcher
- `src/claudeutils/when/resolver.py` — `removeprefix("to ")` band-aid at line 196

## Next Steps

Human curates task contexts and annotates ground truth, then agent runs harness + analysis. See `plans/reports/ab-test/README.md`.
