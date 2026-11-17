---
name: review
description: "Runs the per-commit review loop: a delegated medium code review of each commit as it lands, triage of its findings, and fix commits reviewed the same way until only lows remain. Use right after a commit that adds, changes or deletes content lands. Not for the pre-release review, which is edify:release."
---

# Per-commit review

## Where reviews happen

Each commit is reviewed as it lands. Work happens on `dev`; a release is a
review of `dev` against `main`, run by `edify:release`. A plan whose
multi-commit change needs a review of its own names a separate branch, and the
user's approval of the plan is the prompt to create it, so branch-diffing tools
(`/codex:review`, anything expecting a PR) have a base.

Never ask whether to move `main`, and never carry it as pending on a say-so: in
a handoff or todo, record what review a branch has and has not had. Checked out
on `main` anyway, commit there and say so; this is no licence to switch
branches.

## The loop

1. Right after a commit that adds, changes or deletes content lands, dispatch a
   `/code-review medium` of that commit to an agent. The review sits on the
   critical path, so it runs before the next slice starts.
2. Triage its findings (next section) before anything is fixed.
3. Send out only the high and medium findings. The fix is a commit of its own.
4. Review that fix commit the same way, and repeat until a pass returns only
   lows.

Doc drift is the exception: fix it without a re-review.

## Triage

Assign severity at triage, never from the reviewer, which often reports none. A
finding is high or medium when a reader following the text would do the wrong
thing: a command that fails, a claim a probe or primary source contradicts, two
places prescribing opposite actions. Phrasing, wrapping, placement, redundancy
and "could be clearer" are low. Verify a finding against its source before
accepting it.

Decline a finding that guards a state nothing in practice produces: a fix for a
rare state can itself regress a real case.

Lows are the exhaust of the loop. A reviewer asked for findings always returns
some and does not weigh simplicity, and every fix adds surface the next round
mines. List them as declined; never dispatch them.

## Where a fix goes

A per-commit fix goes back to the reviewer that found it, by `SendMessage` to
the agent id its dispatch returned, while that reviewer's context is under about
150k tokens; past that, a fresh agent with `name` unset takes it. A release fix
goes to fresh agents partitioned by file, since the release reviewers cannot
take a fix. A review fix is its own commit, never an amend.

An implementer that would depart from its brief stops and asks rather than
deciding, and the dispatcher does not accept the departure on its argument
alone.

## A fix lists cases only when the list is closed

A list in prose reads as complete, so each case it misses is the next review's
medium finding. Where the cases are open-ended, state the rule that produces
them.

Test for it at triage, before dispatching a fix: a finding that names a case the
text missed, or one that lands on what the previous fix added, means the space
is open and the fix is the rule, not one more case. Such rounds read as
progress, because every probe in them is real, so the count of rounds is no
signal; only the test is.

Where no probe-backed rule exists, or a second review round running hits the
same sentence, drop the list or the stated cause instead of refining it. Keep
what the reader acts on, hedge any effect that must stay ("can ... or fail"),
and grep every copy of the dropped wording in the same fix. Refining one
sentence can fail to converge over many rounds; dropping the enumeration or the
claim is what ends the loop green.
