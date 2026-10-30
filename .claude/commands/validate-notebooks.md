---
description: Validate a module's exercises.ipynb and solutions.ipynb (format, scaffolds, pair, nothing blocks, region rule, no infra, no real names, AI tells) and the course Python code
---

Validate: $ARGUMENTS

(Argument: a module number, a notebook path, `--all`, or `--code`. Flags below.)

## Commands

```bash
.venv/bin/python3 validate_notebooks.py <N>                 # both notebooks of module N, static checks
.venv/bin/python3 validate_notebooks.py <N> --pair          # solutions == exercises - FALLBACK cells
.venv/bin/python3 validate_notebooks.py <N> --strict        # warnings fail (diagram marker without a mermaid block)
.venv/bin/python3 validate_notebooks.py course/module_00/start_here.ipynb
.venv/bin/python3 validate_notebooks.py --code              # course/harborview (source material), data
.venv/bin/python3 validate_notebooks.py --all
```

Static only. There is no mock mode and no `--selfcheck`: solutions are checked live by the
workflow's Live check stage (laptop for modules 1, 2, 5; Axel in the instructor space for 3+).

## What is checked

| Scope | Checks |
|---|---|
| Every notebook | Path `course/module_NN/{exercises,solutions}.ipynb` or `module_00/start_here.ipynb`; title cell with Learning Objectives and synthetic-data line; first code cell is a pinned `%pip install`; a config cell with `MODEL_REGION = "us-east-1"`, `AGENTCORE_REGION = "us-west-2"`, `STUDENT_NAME = "default"`; no `harborview` import; banner with a known kind (DEMO, LAB n, FALLBACK, SOLUTION: LAB n, SETUP, CONFIG, HELPER, RECAP) on every code cell except `%pip` and `%%writefile`; max 3 markdown cells in a row; syntax and cross-cell pyflakes (magics stripped); region rule (model and KB clients on `MODEL_REGION`, AgentCore, Cognito, logs, X-Ray on `AGENTCORE_REGION`); mcp 1.x API only; no hostnames, ids, account numbers, keys, passwords; denylist; no em/en dashes, Unicode multiplication, bare `---`; outputs cleared; Summary cell last |
| exercises.ipynb | Every `## Lab n` markdown has Your Task, Steps, Expected Output, Hints or Stretch, Homework Extension; each LAB cell has at least one `= None  # YOUR CODE`; `# YOUR CODE` only in LAB cells; no CHECK cells |
| solutions.ipynb | No `= None  # YOUR CODE` left; SOLUTION cells explain themselves (`# Approach:`); no FALLBACK cells |
| `--pair` | solutions cells == exercises cells minus FALLBACK cells, same order, same kinds; LAB n at the same position as SOLUTION: LAB n |
| Diagrams | Every `<!-- DIAGRAM: <slug> -->` cell holds a ```mermaid block whose first line is the brand line; the block equals `course/diagrams/module_NN/<slug>.mmd`; identical in exercises and solutions; no image links, attachments or PNG paths; a marker without a block warns |
| Course code | Syntax, pyflakes, region rule, keys, dashes, infra and denylist |

## Not checked here (judgement)

- The bread-financial cycle per concept and the concierge flavor (failure first, closers): reviewers check it
- Slots are design decisions and do not leak answers; no helper used before its visible
  definition: `learner-engineer-refute`
- Live AWS behaviour: the workflow's Live check stage

## When to run

- After every 5-cell batch in `/build-notebook`
- `--pair --strict` before every commit
