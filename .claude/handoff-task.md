## Current task

The /inline + /orchestrate -> /build merge is complete against `plans/build-skill/outline.md`: the skill is composed, every inbound reference repointed, continuation passing retired, and the design record, changelog and stale-name map updated. `/build` has not yet been exercised — a skill listing resolves at startup, so the merge session could not invoke it; a `handoff:restart` or any fresh session can.

Next thread is the /design skill work in the todo, starting with removing its direct-execution path. That removal is what the merge was making possible: /build is now a lean hub whose simple case is fast, so /design no longer needs to special-case executing in the design session.

`plans/README.md` still describes the retired `prepare-runbook.py` / `steps/` / `orchestrator-plan.md` generator; only its `/orchestrate` line was corrected. `memory/MEMORY.md` sits at 26715 bytes against the 25600-byte loader cap, so its last two index entries never reach a session — the audit pass for that was dropped from the list deliberately, not forgotten.