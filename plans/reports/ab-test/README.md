# A/B Test: How Verb Form Effects on Agent Recognition

Tests whether `/how to <verb>` vs `/how <verb>` affects agent recognition of relevant index entries.

## Pipeline

```bash
D=plans/reports/ab-test
```

### Automated (done)

```bash
./plans/prototypes/ab-variant-generator.py agents/memory-index.md -o "$D"
./plans/prototypes/ab-task-selector.py /path/to/project -o "$D/task-contexts.json"
./plans/prototypes/ab-ground-truth.py generate \
  --tasks-json "$D/task-contexts.json" --variant-a "$D/memory-index-variant-a.md" \
  -o "$D/ground-truth.md"
```

### Human required

- [ ] **Curate task contexts** — review `task-contexts.json`, remove low-quality tasks (task-003 has system content in description, several others are too meta). Edit JSON directly.
- [ ] **Annotate ground truth** — open `ground-truth.md`, mark 3-5 relevant `/how` entries per task with `[x]`. Then parse:
  ```bash
  ./plans/prototypes/ab-ground-truth.py parse "$D/ground-truth.md" -o "$D/ground-truth.json"
  ```

### Automated (after human steps)

```bash
./plans/prototypes/ab-harness.py \
  --tasks-json "$D/task-contexts.json" --variant-a "$D/memory-index-variant-a.md" \
  --variant-b "$D/memory-index-variant-b.md" -o "$D/results.json"

./plans/prototypes/ab-analysis.py "$D/results.json" -o "$D/analysis.json"
```

Harness supports `--dry-run`, `--max-tasks N`, `--resume`.

## Data files

| File | Contents |
|------|----------|
| `memory-index-variant-a.md` | Control: `/how <bare imperative>` (current format) |
| `memory-index-variant-b.md` | Treatment: `/how to <bare imperative>` |
| `task-contexts.json` | 20 task descriptions from session history |
| `ground-truth.md` | Annotation template (human marks relevant entries) |
| `ground-truth.json` | Parsed annotations (after human step) |
| `results.json` | Raw experiment results (after harness run) |
| `analysis.json` | McNemar's test + per-entry sensitivity (after analysis) |

## Methodology

Forced selection design (TREC/Cranfield). 62 entries × 20 tasks × 2 variants. McNemar's test on paired binary outcomes. Per-entry sensitivity analysis (ProSA-inspired).

Full methodology: `plans/reports/how-verb-form-ab-methodology.md`
