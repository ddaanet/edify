---
name: review
description: >-
  Review in-progress changes for quality and correctness — uncommitted work,
  recent commits, or partial branch work. Triggers on /review, "review my
  changes", "review this work", "check my changes before commit". Not for a
  finished plan's deliverables — that is /deliverable-review — and not for a
  PR, which is the built-in code-review.
allowed-tools:
  - Read
  - Write
  - Bash(git:*, rg:*, ls:*)
user-invocable: true
---

# Review Changes for Quality

Review in-progress work for quality, correctness, and adherence to project
standards. This skill examines uncommitted changes, recent commits, or partial
branch work to identify issues and suggest improvements.

**Distinction:** This skill reviews work-in-progress in the main session. The
built-in `code-review` targets a diff, PR, branch or path at a chosen effort
level; `security-review` is its security counterpart.

## Review Process

**Example execution:** Read `references/example-execution.md` for a complete
review interaction flow.

### 1. Determine Scope

Infer the scope, state it in one line, and proceed. Do not open with a question
— the tree answers it in most cases:

| State | Scope |
|---|---|
| User named files, a commit range or a design document | What they named |
| Dirty tree | Uncommitted changes (staged + unstaged) — **the default** |
| Clean tree, commits ahead of `main` | Those commits |
| Clean tree, nothing ahead | Ask (below) |

State the inference before gathering — "Reviewing uncommitted changes, 4 files"
— so a wrong guess costs one correction instead of a whole review.

When the scope is genuinely undetermined, ask inline in numbered prose with a
stated default, in one turn:

```
Nothing uncommitted and nothing ahead of main. What should I review?
1. The last N commits (default: 5)
2. Specific files — name them
3. Changes against a design document — name it
```

Never reach for `AskUserQuestion`. It renders the exchange as a picker, which
hides the user's own prompting from the transcript; numbered prose keeps the
question and the answer readable in the thread and lets the default carry the
turn when the user does not care.

### 2. Gather Changes

**For uncommitted changes:**
```bash
git status
git diff HEAD  # Shows both staged and unstaged
```

**For recent commits:**
```bash
git log -N --oneline  # List recent commits
git diff HEAD~N..HEAD  # Show changes in last N commits
git log -N -p  # Show commits with diffs
```

**For current branch:**
```bash
git log main..HEAD --oneline  # Commits on branch
git diff main...HEAD  # Changes since branch point
```

**For specific files:**
```bash
git diff HEAD <file1> <file2> ...
```

**For a design document:**
```bash
ls plans/*/design.md plans/*/outline.md   # locate the plan's artifact
git diff HEAD                              # changes to judge against it
```

### 3. Analyze Changes

**Review axes:** Read `references/review-axes.md` for the full 10-category
checklist (code quality, design conformity, functional completeness, project
standards, runbook file references, self-referential modification, security,
testing, documentation, completeness).

**Common scenarios:** Read `references/common-scenarios.md` for handling
secrets, multi-concern changes, pattern violations, already-committed work, and
large changesets.

### 4. Provide Feedback

**Report format and assessment criteria:** Read `references/review-template.md`
and write the report by it.

### 5. Output Review

**Write review to file:**
- Reviewing a plan's work → `plans/[plan-name]/reports/review-report.md`
- Otherwise → project-local `tmp/review-report-[timestamp].md` (gitignored)

**Return summary to user:**
- Overall assessment
- Count of issues (critical/major/minor)
- Key action items
- Path to full review

## Constraints

- **Bash** for git commands and read-only search (`rg`, `rg --files`), **Read**
  for examining files, **Write** for review output
- Do NOT use Edit to fix issues (review only)
- Review exactly what user requested — do not expand scope
- Be specific, actionable, constructive
- Flag secrets as CRITICAL — never log or output secret values

## Integration with General Workflow

**This skill and the corrector agent share review criteria, not interaction
model.** They are not interchangeable:

- **This skill** runs in the main session with a user present, so it can infer
  scope from the tree and ask inline when it cannot.
- **`edify:corrector`** runs delegated, with no user to ask (see
  `plugin/agents/corrector.md`). Its scope must arrive in the dispatch prompt,
  and it applies fixes directly.

So the review *axes* (`references/review-axes.md`) are shared; the scoping step
is not. A delegated reviewer that reaches for a question has hit a
dispatch-prompt defect, not a decision point.

In workflow contexts, prefer agent delegation. **Direct invocation** is for when
the user asks for a review in conversation.

**Workflow stages:**
1. `/requirements` — capture requirements
2. `/design` — triage and design; routes to `/runbook` or straight to `/build`
3. `/runbook` — decompose into phases of typed items
4. `/build` — execute the planned work, runbook or not
5. corrector — review and fix changes before commit
6. `/commit-commands:commit` — commit changes

## Execution Context for Review Delegations

When delegating to corrector, Read `../../fragments/review-requirement.md` and
include the scope context it specifies — §Execution Context is the authority for
the field list and the rationale.

