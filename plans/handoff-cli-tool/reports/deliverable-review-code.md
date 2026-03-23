# Code Deliverable Review (RC4)

**Reviewer:** Opus 4.6 [1M]
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Scope:** 26 code files per review manifest. Full conformance review.

## Round 3 Fix Verification

| Finding | Fix Status |
|---------|-----------|
| F-1 Parallel detection ignores blockers | FIXED — `status/cli.py:99` passes `data.blockers`; `parse.py:156` calls `extract_blockers` |
| F-2 Stale vet output lacks file detail | FIXED — `commit_gate.py:163-176` returns per-file paths with timestamps |
| F-3 Duplicate `_fail` in worktree/cli | FIXED — removed; imports from `git.py` |
| F-4 ▶ line format deviation | Acknowledged — format differs from design but is denser; not a correctness issue |
| F-5 Handoff parser strips blank lines | FIXED — `parse.py:48-57` preserves internal blank lines, strips only leading/trailing |
| F-6 Double read in status CLI | FIXED — `status/cli.py:53,58` reads once, passes `content=` to parser |
| F-7 Old section name substring match | FIXED — `status/cli.py:25` uses `re.search(r"^## Pending Tasks", ..., re.MULTILINE)` |
| F-8 `_strip_hints` continuation lines | Acknowledged — low impact for commit use case |

All 6 actionable fixes verified. No regressions from fix application.

## New Findings

### Critical

None.

### Major

1. **commit_gate.py:108-129,141 — `vet_check` ignores `cwd` parameter:** `_load_review_patterns()` reads `Path("pyproject.toml")` and `_find_reports()` globs `Path("plans")` — both resolve relative to process CWD, not a configurable root. The rest of `commit_gate.py` (`validate_files`, `_dirty_files`, `_head_files`) consistently accept and propagate `cwd`. `vet_check()` itself accepts no `cwd`, and `commit_pipeline._validate` which holds `cwd` cannot pass it through. If the pipeline is invoked with `cwd != None`, vet check reads wrong config and wrong reports.
   - **Axis:** Robustness / API consistency
   - **Severity justification:** The CLI always runs from project root (process CWD = repo root), so this does not cause production failures today. However, tests that use `tmp_path` repos may need `monkeypatch.chdir` to work around this inconsistency. The inconsistency with the rest of the module's API makes it a latent defect.

2. **worktree/cli.py:308 — hardcoded `"agent-core"` in `_is_submodule_dirty` call:** Design S-2 states "Replaces `-C agent-core` literals with iteration over discovered submodules." The extraction to `git.py` was done correctly (parametric `path` argument), but this call site reintroduces a hardcoded submodule name instead of iterating `discover_submodules()`. The `_is_submodule_dirty` function was designed to be called per-submodule in a loop.
   - **Axis:** Conformance (design S-2)
   - **Severity justification:** Only one submodule exists today (`agent-core`), so behavior is correct. But the design explicitly required eliminating hardcoded names for future-proofing.

### Minor

1. **worktree/cli.py:104,176 — except tuple parentheses removed:** Diff changed `except (FileNotFoundError, subprocess.CalledProcessError):` to `except FileNotFoundError, subprocess.CalledProcessError:` (same at line 176). Valid in Python 3.14+ (PEP 758) but unconventional. The parenthesized form is universal Python idiom and clearer.
   - **Axis:** Robustness (readability)

2. **commit_pipeline.py:34,49 — precommit/lint stderr discarded:** `_run_precommit` and `_run_lint` return only `result.stdout.strip()`. Some lint tools write diagnostics to stderr. Design says failure output should include "gate-specific diagnostic output."
   - **Axis:** Functional completeness

3. **git.py:24 — `_git()` strips stdout unconditionally:** The shared `_git()` helper applies `.strip()`. Per the porcelain-format learning, `_dirty_files` and `git_status` correctly avoid `_git()`, but any future caller using `_git("status", "--porcelain")` would get silently broken output. A docstring warning would prevent regression.
   - **Axis:** Robustness (defensive documentation)

4. **handoff/cli.py:57-59 — markdown headers inside code fence:** `git_changes()` returns markdown with `## Parent` / `## Submodule:` headers. Handoff CLI wraps in `` ```...``` `` code fence. Headers inside code fences render as literal text, losing structural formatting.
   - **Axis:** Conformance (H-3 diagnostic output)

5. **status/render.py:44 — ▶ line format differs from design:** Design: `▶ <task> (<model>) | Restart: <yes/no>` with command on next indented line. Implementation: `▶ {name} — \`{cmd}\` | {model} | restart: {restart}` — command inline, model not parenthesized, lowercase `restart`. Plan status also missing from ▶ task (shown for other tasks).
   - **Axis:** Conformance (carried from F-4)

6. **commit_pipeline.py:91 — `allowed` expression relies on subtle precedence:** `dirty | _head_files(cwd) if amend else dirty` parses as `dirty | (_head_files(cwd) if amend else dirty)`. Both branches produce correct results (`dirty | head` when amend, `dirty | dirty` when not). Parenthesizing the ternary would clarify intent and prevent future bugs from expression modification.
   - **Axis:** Robustness (readability)

## Conformance Summary

| Design Section | Status |
|---------------|--------|
| S-1: Package structure | Conforms |
| S-2: `_git()` extraction + submodule discovery | Partial — extraction done, one hardcoded call site remains (M-2) |
| S-3: Output/error conventions | Conforms |
| S-4: Session.md parser | Conforms |
| S-5: Git changes utility | Conforms |
| H-1: Domain boundaries | Conforms |
| H-2: Committed detection | Conforms |
| H-3: Diagnostic output | Conforms (minor formatting issue m-4) |
| H-4: State caching | Conforms |
| C-1: Scripted vet check | Conforms (cwd gap M-1) |
| C-2: Submodule coordination | Conforms |
| C-3: Input validation | Conforms |
| C-4: Validation levels | Conforms |
| C-5: Amend semantics | Conforms |
| ST-0: Worktree-destined tasks | Conforms |
| ST-1: Parallel group detection | Conforms (blockers now wired) |
| ST-2: Preconditions and degradation | Conforms |
| Registration in `cli.py` | Conforms |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 6 |

No critical issues. Two major findings: M-1 (vet check `cwd` gap — API inconsistency, no production impact today) and M-2 (hardcoded `"agent-core"` contradicts design S-2's elimination of hardcoded submodule names). Six minor findings covering style, documentation, formatting, and readability.

All 6 actionable round 3 fixes verified with no regressions.
