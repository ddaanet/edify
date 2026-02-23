# Test Plan: Fenced Code Block Awareness in prepare-runbook.py

**Bug:** `extract_sections()` and `extract_cycles()` parse markdown headers inside fenced code blocks as real section boundaries, causing duplicate step/cycle errors.

**Production file:** `agent-core/bin/prepare-runbook.py`
**Test file:** `tests/test_prepare_runbook_fenced.py`

## References

**Learnings (agents/learnings.md):**
- "When phase files contain example fixture content with H2 headers" — documents the bug, workaround (inline backtick descriptions instead of code blocks)
- "When inline phases are appended to last step file" — related `extract_sections()` refactoring (save_current closure, phase boundary handling)
- "When TDD cycles grow a shared test file past line limits" — keep new test file under 400 lines

**Decision files:**
- `agents/decisions/implementation-notes.md` § "How to Format Runbook Phase Headers" — `### Phase N` (H3) for phases, `## Step N.M:` (H2) for steps; prepare-runbook.py regex matches `^## Step`
- `agents/decisions/pipeline-contracts.md` § "When Declaring Phase Type" — tdd/general/inline per-phase typing, expansion format, orchestration delegation model
- `agents/decisions/implementation-notes.md` § "When Editing Runbook Step Or Agent Files" — edit source phase files, not generated output
- `agents/decisions/testing.md` § "When Preferring E2E Over Mocked Subprocess" — real git repos in tmp_path fixtures
- `agents/decisions/workflow-planning.md` § "How to Write Green Phase Descriptions" — behavioral requirements with approach hints, not prescriptive code

**Existing codebase patterns:**
- `extract_file_references()` (prepare-runbook.py:689) — existing fence stripping via `re.sub(r"```.*?```", ...)`, works for 3-backtick only
- `src/claudeutils/markdown_parsing.py` — full segment parser with `_extract_fence_info()`, `_find_fenced_block_end()`, nested fence tracking (evaluated for reuse — too heavy, pydantic dependency, wrong abstraction for line-by-line header parsing)
- `tests/test_prepare_runbook_inline.py:322` — `TestGeneralThenInlineBleed` class, integration test pattern for `validate_and_create()` pipeline

**Existing test files (line counts):**
- `tests/test_prepare_runbook_inline.py` — 367 lines
- `tests/test_prepare_runbook_mixed.py` — 380 lines
- `tests/test_prepare_runbook_orchestrator.py` — 200 lines
- `tests/test_prepare_runbook_phase_context.py` — 223 lines

**CommonMark spec (Context7: /websites/spec_commonmark_0_31_2, § 4.5 Fenced code blocks):**
- Opening fence: ≥3 consecutive backticks or tildes, may have info string
- Closing fence: same character type, ≥ opening count, NO info string (only spaces/tabs)
- Backtick info strings cannot contain backticks
- Tilde and backtick fences do not cross-close
- Up to 3 spaces of indentation before fence markers

---

## New helpers (built during GREEN phases)

- `_fence_tracker()` — returns callable tracking fence state line-by-line, supports backtick and tilde fences per CommonMark § 4.5
- `strip_fenced_blocks(content)` — removes fenced block content using tracker, preserves line count for position stability

---

## Cycle 1: Integration — `extract_sections()` ignores fenced step headers

**RED:**
```python
def test_extract_sections_ignores_step_header_inside_fence():
    content = dedent("""\
        ### Phase 1: Core (type: general)

        ## Step 1.1: Real step

        Implementation details.

        Here is an example runbook:

        ```markdown
        ## Step 2.1: Example step

        This is just documentation.
        ```

        ## Step 1.2: Another real step

        More implementation.
    """)
    sections = extract_sections(content)
    assert sections is not None
    assert "1.1" in sections["steps"]
    assert "1.2" in sections["steps"]
    assert "2.1" not in sections["steps"]
    assert len(sections["steps"]) == 2
```

**Expected failure:** `"2.1" not in sections["steps"]` fails — parser extracts the fenced header.

**GREEN:** Implement `_fence_tracker()` (3-backtick only). Wire into `extract_sections()` second pass — skip header detection when `tracker(line)` is True. Minimal: only backtick fences, only the second pass.

**Regression:** `just test tests/test_prepare_runbook_inline.py tests/test_prepare_runbook_mixed.py`

---

## Cycle 2: Integration — `extract_cycles()` ignores fenced cycle headers

**RED:**
```python
def test_extract_cycles_ignores_cycle_header_inside_fence():
    content = dedent("""\
        ## Cycle 1.1: Real cycle

        ### RED Phase
        Test something.

        ### GREEN Phase
        Implement something.

        Example of a cycle definition:

        ```markdown
        ## Cycle 1.2: Example cycle

        ### RED Phase
        Example test.
        ```

        ## Cycle 1.3: Another real cycle

        ### RED Phase
        Test more.
    """)
    cycles = extract_cycles(content)
    numbers = [c["number"] for c in cycles]
    assert "1.1" in numbers
    assert "1.3" in numbers
    assert "1.2" not in numbers
    assert len(cycles) == 2
```

**Expected failure:** `"1.2" not in numbers` fails.

**GREEN:** Wire `_fence_tracker()` into `extract_cycles()` — skip cycle header and H2 terminator detection when inside fence. Content accumulation continues.

**Regression:** `just test tests/test_prepare_runbook_mixed.py`

---

## Cycle 3: `extract_sections()` first pass — fenced phase headers ignored

**RED:**
```python
def test_extract_sections_ignores_inline_phase_inside_fence():
    content = dedent("""\
        ### Phase 1: Core (type: general)

        ## Step 1.1: Real step

        Example runbook structure:

        ```
        ### Phase 2: Infrastructure (type: inline)

        Edit some files.
        ```

        ## Step 1.2: Second step

        More work.
    """)
    sections = extract_sections(content)
    assert sections is not None
    assert len(sections["inline_phases"]) == 0
    assert len(sections["steps"]) == 2
```

**Expected failure:** `len(sections["inline_phases"]) == 0` fails — first pass detects fenced phase as inline.

**GREEN:** Wire `_fence_tracker()` into `extract_sections()` first pass (phase detection loop and inline phase extraction loop).

**Regression:** `just test tests/test_prepare_runbook_inline.py`

---

## Cycle 4: 4+ backtick fences — inner 3-backtick not treated as fence boundary

**RED:**
```python
def test_extract_sections_handles_four_backtick_fences():
    content = dedent("""\
        ### Phase 1: Core (type: general)

        ## Step 1.1: Real step

        Example with nested fences:

        ````markdown
        Here is a code example:

        ```python
        print("hello")
        ```

        ## Step 2.1: This is inside the outer fence

        Still inside.
        ````

        ## Step 1.2: Another real step

        More work.
    """)
    sections = extract_sections(content)
    assert sections is not None
    assert "1.1" in sections["steps"]
    assert "1.2" in sections["steps"]
    assert "2.1" not in sections["steps"]
    assert len(sections["steps"]) == 2
```

**Expected failure:** After Cycle 1 fix, the inner ``` closes the fence prematurely, exposing `## Step 2.1:` to the parser.

**GREEN:** Extend `_fence_tracker()` to track backtick count — closing fence requires ≥ opening count and no info string.

**Regression:** `just test tests/test_prepare_runbook_fenced.py` (cycles 1-3 still pass)

---

## Cycle 5: Tilde fences

**RED:**
```python
def test_extract_sections_handles_tilde_fences():
    content = dedent("""\
        ### Phase 1: Core (type: general)

        ## Step 1.1: Real step

        ~~~
        ## Step 2.1: Inside tilde fence
        ~~~

        ## Step 1.2: Another real step

        Work.
    """)
    sections = extract_sections(content)
    assert sections is not None
    assert "2.1" not in sections["steps"]
    assert len(sections["steps"]) == 2


def test_extract_sections_backtick_does_not_close_tilde():
    content = dedent("""\
        ### Phase 1: Core (type: general)

        ## Step 1.1: Real step

        ~~~
        ```
        ## Step 2.1: Still inside tilde fence
        ```
        ~~~

        ## Step 1.2: Real step two

        Work.
    """)
    sections = extract_sections(content)
    assert sections is not None
    assert "2.1" not in sections["steps"]
    assert len(sections["steps"]) == 2
```

**Expected failure:** Tilde fences not tracked by `_fence_tracker()`.

**GREEN:** Add tilde support — track fence character type, same-character closing rule.

**Regression:** `just test tests/test_prepare_runbook_fenced.py`

---

## Cycle 6: `extract_phase_preambles()` fence awareness

**RED:**
```python
def test_extract_phase_preambles_ignores_fenced_headers():
    content = dedent("""\
        ### Phase 1: Core

        This is the preamble for phase 1.

        Example structure:

        ```
        ## Step 1.1: Example
        Some content.
        ```

        More preamble content after the fence.

        ## Step 1.1: Real step
    """)
    preambles = extract_phase_preambles(content)
    assert 1 in preambles
    assert "More preamble content after the fence." in preambles[1]
```

**Expected failure:** Fenced `## Step 1.1:` terminates preamble collection early, losing "More preamble content."

**GREEN:** Wire `_fence_tracker()` into `extract_phase_preambles()` — skip step/cycle header detection when inside fence.

**Regression:** `just test tests/test_prepare_runbook_phase_context.py`

---

## Cycle 7: `extract_phase_models()` fence awareness

**RED:**
```python
def test_extract_phase_models_ignores_fenced_annotations():
    content = dedent("""\
        ### Phase 1: Core (model: haiku)

        ## Step 1.1: Real step

        Example:

        ```
        ### Phase 2: Infrastructure (model: opus)
        ```
    """)
    models = extract_phase_models(content)
    assert models == {1: "haiku"}
    assert 2 not in models
```

**Expected failure:** Regex matches fenced `### Phase 2:` annotation.

**GREEN:** Implement `strip_fenced_blocks(content)` using `_fence_tracker()`. Use it in `extract_phase_models()` before regex.

**Regression:** `just test tests/test_prepare_runbook_phase_context.py`

---

## Cycle 8: `extract_file_references()` — 4-backtick fence support

**RED:**
```python
def test_extract_file_references_handles_four_backtick_fences():
    content = dedent("""\
        Real reference: `src/main.py`

        ````markdown
        Example reference: `src/example.py`

        ```python
        import src.other
        ```

        Another: `src/fake.py`
        ````
    """)
    refs = extract_file_references(content)
    assert "src/main.py" in refs
    assert "src/example.py" not in refs
    assert "src/fake.py" not in refs
```

**Expected failure:** Current `re.sub(r"```.*?```", ...)` closes on the inner ``` fence, exposing `src/fake.py`.

**GREEN:** Replace naive regex in `extract_file_references()` with `strip_fenced_blocks()`.

**Regression:** `just test tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_fenced.py`

---

## Cycle 9: `assemble_phase_files()` — fenced header detection

**RED:**
```python
def test_assemble_ignores_fenced_cycle_headers(tmp_path):
    phase_file = tmp_path / "runbook-phase-1.md"
    phase_file.write_text(dedent("""\
        ### Phase 1: Core

        ## Step 1.1: Real step

        Example TDD cycle:

        ```
        ## Cycle 1.1: Example
        ### RED Phase
        test something
        ```
    """))
    # assemble_phase_files checks for Cycle/Step headers to detect type
    # Fenced cycle header should not cause TDD detection
    assembled, _ = assemble_phase_files(tmp_path)
    assert assembled is not None
    # Should detect as general (has Step), not TDD (fenced Cycle)
    assert "type: tdd" not in assembled
```

**Expected failure:** `re.search(r"^##+ Cycle\s+\d+\.\d+:", content, re.MULTILINE)` matches fenced header.

**GREEN:** Use `strip_fenced_blocks()` on content before header detection in `assemble_phase_files()`.

**Regression:** `just test`

---

## Execution notes

- All tests in `tests/test_prepare_runbook_fenced.py`
- Import: `from prepare_runbook import extract_sections, extract_cycles, extract_phase_preambles, extract_phase_models, extract_file_references, assemble_phase_files, _fence_tracker, strip_fenced_blocks, parse_frontmatter, derive_paths, validate_and_create`
- Fixtures: `setup_git_repo`, `setup_baseline_agents` from existing test files (check `tests/conftest.py`)
- Cycles 1-5 are core (the bug fix + CommonMark compliance)
- Cycles 6-9 are completeness (same pattern applied to remaining functions)
- Each GREEN is minimal — wire existing helper into one more call site

## Affected functions in prepare-runbook.py

| Function | Line | Parser type | Fix approach |
|----------|------|-------------|--------------|
| `extract_cycles()` | 104 | Line-by-line | `_fence_tracker()` skip |
| `extract_sections()` pass 1 | 356 | Line-by-line | `_fence_tracker()` skip |
| `extract_sections()` pass 2 | 416 | Line-by-line | `_fence_tracker()` skip |
| `extract_sections()` inline extraction | 366 | Line-by-line | `_fence_tracker()` skip |
| `extract_phase_models()` | 460 | Regex on content | `strip_fenced_blocks()` before regex |
| `extract_phase_preambles()` | 469 | Line-by-line | `_fence_tracker()` skip |
| `assemble_phase_files()` detection | 561 | Regex on content | `strip_fenced_blocks()` before regex |
| `extract_file_references()` | 689 | Regex strip + match | Replace naive `re.sub` with `strip_fenced_blocks()` |

## Design decisions made during planning

- **No cross-module reuse:** `markdown_parsing.py` segment parser is wrong abstraction (pydantic dependency, batch processing vs line-by-line). Helpers are local to prepare-runbook.py.
- **Closure pattern for tracker:** `_fence_tracker()` returns a callable with `nonlocal` state — same pattern used successfully in existing `save_current()` closure (extract_sections line 405).
- **Line count preservation:** `strip_fenced_blocks()` replaces fenced lines with empty strings, not removes them. Position-dependent logic (line_to_phase mapping, step_line tracking) depends on stable line numbers.
- **4+ backtick nesting:** Not built in Cycle 1 GREEN (YAGNI for minimal fix). Added in Cycle 4 after basic 3-backtick works. Avoids over-engineering the initial helper.
