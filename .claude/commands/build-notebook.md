---
description: Cell-by-cell builder run by the build-module workflow (also usable alone) - builds course/module_NN/exercises.ipynb or solutions.ipynb from the approved plan, 5 cells at a time with cell_id checks
---

Build notebook: $ARGUMENTS

(Arguments: module number 1 to 4, then `exercises` or `solutions`. Example: `2 exercises`.
`exercises` runs Step 1 only; `solutions` runs Step 2 only and needs exercises.ipynb.
Normally you run `/build-module N`, which triggers the workflow that calls this for both.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module_0<N>_plan.md 2>/dev/null
```

- No plan: "Run `/research-module <N>` first."

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/NOTEBOOK_STYLE.md` (cell anatomy, 4 beats per Part from Part 1, three-tier labs) and
   `plans/TEACHING_STYLE.md` (voice)
3. `plans/modules/module_NN_plan.md`: the `# EXERCISES` and `# SOLUTIONS` sections are the
   cell source. Build from them; never re-plan
4. The `typesafe-ai` skill when a cell calls Jev
5. Every helper the plan uses is defined in a visible `# HELPER` cell before its first use
6. `.claude/NOTEBOOK_EDIT_PROTOCOL.md`

### Show Plan Summary Before Building

In chat: cell list (number, kind, one line), Parts with their 4 beats (problem, solution,
demo, lab), lab tiers and their markers, FALLBACK cells, HELPER cells, anything that differs
from the plan.
**Wait for approval** (skipped only under a blanket "go until the end", e.g. inside the
build-module workflow).

---

## Step 1: exercises.ipynb

Create `course/module_NN/exercises.ipynb` with Write (skeleton below; never overwrite an
existing notebook), then insert cells from the plan in order.

```json
{
 "nbformat": 4,
 "nbformat_minor": 5,
 "metadata": {
  "colab": {"provenance": []},
  "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.12"}
 },
 "cells": []
}
```

Rules:
1. First code cell: the pinned `%pip install -q` (only what Colab lacks; same pins as
   `course/requirements.txt`). Then `# KEYS`: each key from `os.environ`, else
   `getpass.getpass(...)`, refused if empty, never printed. Never Colab secrets. Then
   `# CONFIG`: client, pinned model ids, a one-call probe
2. Every code cell (except `%pip` and `%%writefile`) starts with the 77-char banner, kind and
   delivery tag (NOTEBOOK_STYLE)
3. No Part 0: the first Part is `## Part 1`. Never explain the product before the problem it
   solves. Module 1 only: Jev is introduced inside Part 1's `### 2. The solution`, as the
   answer to the bare LLM label just shown; its "what Jev is" sub-sections (markdown, each
   with its diagram, no code) come from the plan
4. Per Part k, the 4 beats in order, exactly as the plan:
   - `## Part k: <concept>` markdown (one sentence)
   - `### 1. The problem` markdown with its diagram, no code
   - `### 2. The solution` markdown with its diagram, no code
   - `### 3. Demo` markdown, then `# DEMO:` cells (the problem live, then the solution), then
     `> **Think About It**:`
   - `### 4. Lab k: <Title>` markdown (#### Your Task, Level 1: Guided, Level 2: Core,
     Level 3: Challenge (optional), Expected Output, Hints), then in order:
     - `# LAB k.1 (Guided)` with `name = None  # YOUR CODE` slots, answer never leaked
     - optional `# FALLBACK` when Level 2 or a later Part needs Level 1's result
     - `# LAB k.2 (Core)` with signature, docstring, test call and a `# YOUR CODE` body
     - `# LAB k.3 (Challenge, optional)` with spec, test call and `# YOUR CODE`; nothing later
       uses a name it defines
5. `# FALLBACK: ...` only where the plan has one. No CHECK cells, no mini exercises
6. Diagrams: copy each `[DIAGRAM]` cell from the plan verbatim: `<!-- DIAGRAM: <slug> -->` and
   `<img src="https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png" width="W" alt="...">`
   (W = 600 x png width / png height, kept to 420..750, rounded to 10; 700 for xychart-beta charts). Never markdown image syntax (Colab draws it at
   full cell width). Never a ```mermaid
   block or an attachment (Colab renders neither). `/build-diagrams <N>` renders the PNGs
7. Every Jev and OpenAI call is a visible cell

## Step 2: solutions.ipynb

1. `cp course/module_NN/exercises.ipynb course/module_NN/solutions.ipynb`
2. Replace each `# LAB n.k` cell with the plan's `# SOLUTION: LAB n.k` source (Edit by
   cell_id); each has `# Approach:` and `# Explanation:`
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

- `.venv/bin/python3 validate_notebooks.py <N> --pair --strict`
- AI-tells clean, outputs cleared
- Running solutions top to bottom is the workflow's "Run in order" stage

Update `plans/LABS.md` (Edit): this notebook `done`. Hand off: after `exercises`, "Next:
`/build-notebook <N> solutions`"; after `solutions`, "Next: `/build-diagrams <N>`" (the
workflow does both automatically).

## Notebook Edit Protocol (MANDATORY)

Follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`. Blind bulk index-based rewrites are forbidden.
