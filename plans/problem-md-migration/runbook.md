# Problem.md Migration Runbook

**Tier:** 2 (Lightweight Delegation)
**Model:** sonnet
**Type:** general

## Context

Remove `problem.md` as a recognized plan artifact. Rename 12 existing files to `brief.md`, remove recognition from planstate/validation code, update all enumeration sites, add precommit rejection gate.

Post-migration, `_derive_next_action` templates work correctly: `briefed` → `brief.md`, `requirements` → `requirements.md`. No dynamic resolution needed — the bug only manifested with the now-eliminated `problem.md` artifact type.

## Steps

### Step 1: Git renames (12 files)

`git mv` each `problem.md` → `brief.md`:

ar-how-verb-form, ar-idf-weighting, ar-threshold-calibration, design-pipeline-evolution, diagnose-compression-loss, markdown-migration, parallel-orchestration, quality-grounding, research-backlog, review-agent-quality, skill-agent-bootstrap, worktree-lifecycle-cli

Verify: all 12 renames staged, no `problem.md` files remain under `plans/`.

### Step 2: Production code — remove problem.md recognition

**inference.py** (`src/edify/planstate/inference.py`):
- `_collect_artifacts`: remove `"problem.md"` from the filename list (line 20)
- `_determine_status`: remove `(plan_dir / "problem.md").exists()` from the briefed-status check (line 87). After migration, only `requirements.md` needs checking alongside `brief.md`

**task_plans.py** (`src/edify/validation/task_plans.py`):
- `_RECOGNIZED_ARTIFACTS`: remove `"problem.md"` from the set (line 8)

**focus-session.py** (`plugin/bin/focus-session.py`):
- Remove or update `problem.md` reference (line 183)

Verify: `grep -r 'problem\.md' src/ plugin/bin/` returns no hits.

### Step 3: Agentic prose — update enumeration sites

All changes are mechanical removal/replacement of `problem.md` from lists:

- `plugin/fragments/execute-rule.md`: remove `problem.md` from artifact list (line 216), update example task path if still referencing problem.md
- `plugin/skills/design/SKILL.md`: remove from requirements source list (line 30)
- `plugin/skills/reflect/SKILL.md`: replace `problem.md` with `brief.md` in example (line 88)
- `plugin/skills/design/references/write-outline.md`: replace `problem.md` with `brief.md` in escape hatch (line 108)
- `plugin/skills/design/references/research-protocol.md`: replace `problem.md` with `brief.md` in escape hatch (line 35)

Verify: `grep -r 'problem\.md' plugin/` returns no hits (excluding this plan's own files).

### Step 4: Test updates

**test_planstate_inference.py** (`tests/test_planstate_inference.py`):

Update existing parametrized cases:
- `requirements-problem-only` (line 42-47): remove — problem.md no longer recognized, plan becomes empty (returns None)
- `requirements-brief-plus-problem` (line 60-65): update to `brief-only` since problem.md ignored → only brief.md recognized → status `briefed`

Add new test case:
- `problem-md-only-not-recognized`: create plan with only `problem.md`, assert `infer_state` returns `None` (not a recognized artifact)

Verify: `just test tests/test_planstate_inference.py` passes.

### Step 5: Session.md path updates

Update ~10 task command references from `/design plans/<slug>/problem.md` to `/design plans/<slug>/brief.md` for all affected plans.

Verify: `grep 'problem\.md' agents/session.md` returns only the problem-md-migration plan's own references (brief.md content describing the migration).

### Step 6: Precommit verification

Run `just precommit` to confirm all validators pass with the changes.
