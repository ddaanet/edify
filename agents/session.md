# Session Handoff: 2026-02-24

**Status:** Context optimization test completed — reads accumulate, no dedup. `/recall` skip-tracking confirmed necessary.

## Completed This Session

**Recall pass pipeline (prior sessions, carried forward):**
- `plans/recall-pass/requirements.md` — 10 FRs, 3 NFRs, 5 constraints
- `plans/recall-pass/outline.md` — 10 key decisions, all open questions resolved
- 4 pipeline skill files edited with recall artifact generation, augmentation, injection, and review recall (47 insertions across design, runbook, orchestrate, deliverable-review skills)

**`/recall` skill — interactive recall pass:**
- Created `agent-core/skills/recall/SKILL.md` — manual recall for interactive sessions
- Naming: 5 brainstorm rounds with opus brainstorm-name agent → `/recall` selected (transparent, self-documenting, ecosystem identity)
- 5-mode taxonomy designed through discussion:
  - default (section-level, 1-2 passes), deep (aggressive saturation, 4 passes), broad (whole-file Read), all (deep+broad), everything (full corpus)
- Broad mode uses direct Read tool (not when-resolve.py) — file-level loading doesn't benefit from section resolution overhead
- Tail-recursive design: skill self-invokes until zero new entries found (mechanical exit condition). Defeats agent loop short-circuiting — skill continuation drives iteration, not prompt instructions.
- Symlinked via `just sync-to-parent`

**brainstorm-name agent fix:**
- Fixed YAML frontmatter: added `description: |` block scalar (without it, `model`/`color`/`tools` fields were consumed as description text)
- Added `# Artifact Naming Specialist` title heading

**Read tool context optimization test (T1):**
- Ran T1 (whole-file dedup) from `plans/reports/recall-context-optimization-test.md`
- Result: no dedup — baseline 37k → +25k first read → +25k second read (identical files)
- Confirms `implementation-notes.md` decision: "Each Read appends new content block. No application-level dedup."
- Skipped T2–T5: T1 is decisive for the core question
- Results written to `plans/reports/recall-context-optimization-results.md`
- Updated `/recall` SKILL.md: removed false "redundant context is cheap" claim from broad mode (line 101)

## Pending Tasks

- [x] **Recall pass requirements** — implemented via Tier 2 delegation
- [ ] **Sync-to-parent sandbox documentation** — update references to document required sandbox bypass | haiku
- [ ] **Rename when-resolve.py to claudeutils _recall** — consolidate into CLI, remove `..file` syntax | sonnet
- [x] **Read tool context optimization test** — run `plans/reports/recall-context-optimization-test.md` protocol in fresh session, results inform `/recall` skip-tracking logic | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

## Next Steps

Sync-to-parent sandbox documentation (haiku) or rename when-resolve.py (sonnet).

## Reference Files

- `agent-core/skills/recall/SKILL.md` — interactive recall skill (5 modes)
- `plans/reports/recall-context-optimization-results.md` — T1 test results (no dedup confirmed)
- `plans/reports/recall-context-optimization-test.md` — Read deduplication test protocol
- `plans/recall-pass/outline.md` — pipeline recall pass design (10 key decisions)
