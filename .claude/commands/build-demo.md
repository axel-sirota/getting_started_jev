---
description: Build the top part of a module's ONE notebook (setup, beat 1 problem, back to the slides, beat 3 fix, takeaways) from its plan, 5 cells at a time with cell_id checks
---

Build the demo part of module: $ARGUMENTS

(Argument is a module number, 1 to 10. Required.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module$(printf %02d $ARGUMENTS)_plan.md course/harborview/__init__.py 2>/dev/null
```

- No manifest: "Run `/init-course` first."
- No plan: "Run `/research-module <N>` first."
- No harborview: "Run `/build-core` first."

## ONE NOTEBOOK PER MODULE (firm rule)

Output: `course/notebooks/module<NN>_<slug>.ipynb` (slug from the Module Map in
`research-module.md`). This command builds its TOP part; `/build-lab <N>` then appends the
"Lab:" section at the BOTTOM of the same file. Never create a separate demo or lab notebook.
The whole room runs this top part together while Axel explains; learners run the Lab
section on their own afterwards.

---

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/modules/module<NN>_plan.md`: the `# DEMO NOTEBOOK` section is the cell source
3. `.claude/skills/agentic-foundations/SKILL.md`
4. `course/harborview/` public API: confirm every name the plan uses exists. Never
   redefine a harborview function inside a notebook; import it

### Show Plan Summary Before Building

In chat: module, the cell list (number, type, one line each),
where "Back to the slides" sits, harborview names used, anything that differs from the plan.

**DO NOT PROCEED until the user approves this summary** (skipped only under a blanket
"go until the end", e.g. inside the finalize-module workflow).

---

## Shape of the top part

```
Cell 0   Markdown: "# Module N: <title>", what we will see and do (demo together, then your
         own lab at the bottom), "click Run All only when the instructor says so",
         synthetic-data line
Cell 1   Code: course/setup_cell.py, copied VERBATIM (downloads the toolkit, installs)
Cell 2   Code: imports from harborview (no sys.path lines: cell 1 already did that)
## Part A: The problem              (beat 1)
  markdown: the request and what we expect
  code: run it the naive way
  markdown: "What went wrong?" in plain words
Markdown: "Back to the slides"     (beat 2 happens in the deck)
## Part B: The fix                  (beat 3)
  markdown: what changes
  code: the change, shown on screen (instructions, a tool, a table, a guardrail)
  code: the same request again
  markdown: before vs after, side by side
Markdown: "Key takeaways" and "Next: the Lab below"
```

The plan's demo title cell becomes the module title cell; keep its "gray boxes are code,
you never change them" line.

## Core Rules

1. **The problem is real.** Part A runs and visibly fails in a way a business person
   recognizes. Designed failures are verified live, seeded or cached so they happen on cue.
2. **The fix is the concept.** Part B changes exactly the thing the module teaches, and
   that change is visible on screen. Plumbing lives in `harborview`.
3. **Projector code.** A plain-English comment on the first line of every code cell.
   Comments say why, in words a business reader follows. Short cells, no clever one-liners.
4. **Nothing blocks.** Every cell runs top to bottom in a fresh SageMaker space and with
   `AGENT_MODE=mock` locally.
5. **AWS rules.** Every Bedrock or AgentCore client is created by harborview with
   `region_name="us-east-1"`. No hostnames, ids or passwords in any cell.
6. **Traces.** Agent runs go through harborview so they land in the `traces` table.
7. **Tone.** US English, first person plural ("Let's send the same request"). Harborview
   Life only. Emojis welcome in headers, not bullets. No AI tells.

---

## CRITICAL: 5-Cell Approval Checkpoints - MANDATORY

1. Add up to 5 cells, then STOP
2. Validate: `.venv/bin/python3 validate_notebooks.py <N>` (before the Lab section exists it
   reports "no Lab section": expected until `/build-lab <N>`)
3. **Unconditional /save-state** at every 10-cell boundary and when the part is done
4. Ask: "I have added cells X-Y. How does it look? Should I continue?" Under blanket "go
   until end" skip the question, never validation or save-state

Write any cell over ~30 lines in its own tool call.

## Cell Order: ALWAYS Verify cell_id (Axel's rule: never mess up the order)

Before EVERY NotebookEdit print the cell map:

```bash
.venv/bin/python3 -c "
import json, sys
nb = json.load(open(sys.argv[1]))
for i, c in enumerate(nb['cells']):
    print(i, c.get('id','?'), c['cell_type'], repr(''.join(c['source'])[:60]))
" course/notebooks/module<NN>_<slug>.ipynb
```

Create the notebook with Write (skeleton below, never overwrite an existing one), insert
Cell 0 without `cell_id`, then chain `cell_id`: every insert goes after the id of the cell
you just verified is last. Read back after each insert and assert the new cell's position
and content.

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

## Checklist

- [ ] One notebook: `course/notebooks/module<NN>_<slug>.ipynb`; no demo/lab split files
- [ ] Part A fails visibly; Part B fixes it with the module's concept on screen
- [ ] "Back to the slides" marker between them
- [ ] Every code cell starts with a plain-English comment
- [ ] Only harborview imports for plumbing; nothing redefined
- [ ] Runs with `AGENT_MODE=mock`
- [ ] No infra details; region handled by harborview
- [ ] Diagram placeholders match the plan's Diagram Index
- [ ] AI-tells clean, outputs cleared

Update `plans/LABS.md` (Edit): demo `in_progress` then `done`. Hand off: "Demo part done.
Next: `/build-lab <N>` appends the Lab section to the same notebook."

## Notebook Edit Protocol (MANDATORY)

Follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`. Blind bulk index-based rewrites are forbidden.
