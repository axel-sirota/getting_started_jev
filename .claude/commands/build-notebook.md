---
description: Cell-by-cell builder run by the build-module workflow (also usable alone) - builds course/module_NN/exercises.ipynb or solutions.ipynb from the approved plan, 5 cells at a time with cell_id checks
---

Build notebook: $ARGUMENTS

(Arguments: module number 0 to 8, then `exercises` or `solutions`. Example: `2 exercises`.
`exercises` runs Step 1 only; `solutions` runs Step 2 only and needs exercises.ipynb.
Module 0 is one notebook, `course/module_00/start_here.ipynb`: build it with Step 1 only.
Normally you run `/build-module N`, which triggers the workflow that calls this for both.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module_$(printf %02d $ARGUMENTS)_plan.md data/00_lab_setup.ipynb 2>/dev/null
```

- No plan: "Run `/research-module <N>` first."
- No `data/00_lab_setup.ipynb`: "Run `/build-core` first."

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/NOTEBOOK_STYLE.md` (the bread-financial anatomy, copied exactly) and
   `plans/TEACHING_STYLE.md` (voice)
3. `plans/modules/module_NN_plan.md`: the `# EXERCISES` and `# SOLUTIONS` sections are the
   cell source. Build from them; never re-plan
4. Every helper the plan uses is defined in a visible `# HELPER` cell before its first use.
   Never `import harborview`
5. `.claude/NOTEBOOK_EDIT_PROTOCOL.md`

### Show Plan Summary Before Building

In chat: cell list (number, kind, one line), labs and slots, FALLBACK cells, HELPER cells,
anything that differs from the plan. **Wait for approval** (skipped only under a blanket
"go until the end", e.g. inside the finalize-module workflow).

---

## Step 1: exercises.ipynb

Create `course/module_NN/exercises.ipynb` with Write (skeleton below; never overwrite an
existing notebook), then insert cells from the plan in order.

```json
{
 "nbformat": 4,
 "nbformat_minor": 5,
 "metadata": {
  "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.12"}
 },
 "cells": []
}
```

Rules:
1. First code cell: the pinned `%pip install` (same pins as `course/requirements.txt`). Then
   the `# CONFIG` cell: `MODEL_REGION = "us-east-1"`, `AGENTCORE_REGION = "us-west-2"`,
   `MODEL_ID`, `STUDENT_NAME = "default"` with the visible refusal check, the `shared.json`
   read. Frameworks only; no `harborview` import
2. Every code cell (except `%pip` and `%%writefile`) starts with the 77-char banner, kind and
   delivery tag (NOTEBOOK_STYLE)
3. Per concept: `# Section N` markdown with the diagram, `# DEMO:` problem cells, `# DEMO:`
   solution cells, `> **Think About It**:`, `## Lab N: <Title> (15 minutes)` markdown, ONE
   `# LAB N: <TITLE IN CAPS>` cell. Slots exactly as the plan: `name = None  # YOUR CODE`,
   answer never leaked
4. `# FALLBACK: Ensures Section N+1 works even if you didn't complete Lab N` only where the
   plan has one. No CHECK cells, no SAFETY-NET cells, no mini exercises
5. Diagrams: copy each `[DIAGRAM]` cell from the plan verbatim: the `<!-- DIAGRAM: <slug> -->`
   marker, the "Where to look" line and the full ```mermaid block with the brand line.
   JupyterLab renders it inline. Never a PNG, image link or attachment. `/build-diagrams <N>`
   then checks each block renders and syncs it with `course/diagrams/module_NN/<slug>.mmd`
6. Every AWS call, SQL query, deploy, Gateway, Cognito token, Cedar, Memory, Guardrail, trace
   lookup and Gradio launch is a visible cell; deployed files use `%%writefile`
7. No infra details (ids come from `shared.json`); every client passes `region_name=MODEL_REGION`
   or `AGENTCORE_REGION`

## Step 2: solutions.ipynb

1. `cp course/module_NN/exercises.ipynb course/module_NN/solutions.ipynb`
2. Replace each `# LAB N` cell with the plan's `# SOLUTION: LAB N` source, slots filled
   (Edit by cell_id)
3. Delete every `# FALLBACK` cell
4. Pair check: `.venv/bin/python3 validate_notebooks.py <N> --pair`

## CRITICAL: 5-Cell Approval Checkpoints

1. Add up to 5 cells, then STOP
2. Validate: `.venv/bin/python3 validate_notebooks.py <N>`
3. **Unconditional /save-state** at every 10-cell boundary and when each notebook is done
4. Ask: "I have added cells X-Y. Should I continue?" Under blanket "go until end" skip the
   question, never validation or save-state

Write any cell over ~30 lines in its own tool call.

## Cell Order: ALWAYS verify cell_id

Before EVERY NotebookEdit print the cell map:

```bash
.venv/bin/python3 -c "
import json, sys
nb = json.load(open(sys.argv[1]))
for i, c in enumerate(nb['cells']):
    print(i, c.get('id','?'), c['cell_type'], repr(''.join(c['source'])[:60]))
" course/module_NN/exercises.ipynb
```

Insert Cell 0 without `cell_id`, then chain: every insert goes after the id of the cell you
just verified is last. **Before AND after every edit** print the id map and assert the AFTER
order equals the expected order (NOTEBOOK_EDIT_PROTOCOL Steps 0.5 and 4b). Inserts can land
out of order silently; this check is the only thing that catches it. Mismatch: stop, restore
order by id, re-verify.

## Final checks

- `.venv/bin/python3 validate_notebooks.py <N> --pair --strict` (static checks; there is no
  mock and no `--selfcheck`)
- AI-tells clean, outputs cleared
- Live check is the workflow's job: solutions run live (modules 1, 2, 5 from the laptop;
  modules 3+ by Axel in his instructor Studio space)

Update `plans/LABS.md` (Edit): this notebook `done`. Hand off: after `exercises`, "Next:
`/build-notebook <N> solutions`"; after `solutions`, "Next: `/build-diagrams <N>`" (the
workflow does both automatically).

## Notebook Edit Protocol (MANDATORY)

Follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`. Blind bulk index-based rewrites are forbidden.
