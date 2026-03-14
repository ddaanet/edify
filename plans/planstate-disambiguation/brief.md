# Brief: Planstate disambiguation

## 2026-03-14: review-pending has two meanings

`review-pending` planstate is set by both `/proof` (transient, artifact under human review) and post-execution (deliverable awaiting `/deliverable-review`).

**Problem:** `_status` CLI checks for `review-pending` and suggests `/deliverable-review` — wrong action during a proof session.

**Evidence:** `plans/handoff-cli-tool/lifecycle.md` shows `review-pending` set by `/proof` twice.

**Options:** Separate states (`proof-pending` vs `review-pending`), or `_status` filters by lifecycle context (what set the state).

**Affects:** `_status` implementation (handoff-cli-tool), `/proof` skill lifecycle writes.
