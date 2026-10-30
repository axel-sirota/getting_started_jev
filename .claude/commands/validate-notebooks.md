---
description: Validate a module's exercises.ipynb and solutions.ipynb (format, three-tier labs, slide hops, pair, key handling, diagrams, no real names, AI tells)
---

Validate: $ARGUMENTS

(Argument: a module number, a notebook path, or `--all`. Flags below.)

## Commands

```bash
.venv/bin/python3 validate_notebooks.py <N>                 # both notebooks of module N, static checks
.venv/bin/python3 validate_notebooks.py <N> --pair          # solutions == exercises - FALLBACK cells
.venv/bin/python3 validate_notebooks.py <N> --strict        # a missing .mmd or .png fails
.venv/bin/python3 validate_notebooks.py --all
.venv/bin/python3 -m pytest tests/unit -q                   # the validators' own rules
```

Static only. Running solutions top to bottom against the real APIs is the workflow's
"Run in order" stage. The slide side of each hop is checked by `validate_slides.py <N>`.

## What is checked

| Scope | Checks |
|---|---|
| Every notebook | Title cell with Learning Objectives; first code cell is a pinned `%pip install`; a key cell reading `TYPESAFE_API_KEY` from `os.environ` with a `getpass` fallback; banner with a known kind (DEMO, BONUS DEMO, LAB n.k, FALLBACK, SOLUTION: LAB n.k, or a free setup title) on every code cell except `%pip` and `%%writefile`; max 3 markdown cells in a row; syntax and cross-cell pyflakes (magics stripped); no key literals, no printed keys, no Colab secrets; denylist; no em/en dashes, Unicode multiplication, bare `---`, banned words; outputs cleared; Summary cell last |
| Slide hops | `## Demo n` / `## Lab n` numbered in order; each closed by exactly one `## Back to the slides: <title>` before the next hop or the Summary |
| Labs | Every `## Lab n` markdown has Your Task, Level 1: Guided, Level 2: Core, Level 3: Challenge (optional), Expected Output, Hints; cells `LAB n.1 (Guided)`, `LAB n.2 (Core)`, `LAB n.3 (Challenge, optional)` in order; no later cell uses a name defined only in a Level 3 cell |
| exercises.ipynb | Level 1 has `= None  # YOUR CODE` slots; Levels 2 and 3 have `# YOUR CODE`; `# YOUR CODE` only in LAB cells |
| solutions.ipynb | No `# YOUR CODE` left; SOLUTION cells have `# Approach:` and `# Explanation:`; no FALLBACK cells |
| `--pair` | solutions cells == exercises cells minus FALLBACK cells, same order, same kinds, same source outside the labs; same hops and diagrams |
| Diagrams | Every `<!-- DIAGRAM: <slug> -->` cell holds one markdown image with alt text whose URL is `RAW_BASE` + `course/diagrams/module_NN/<slug>.png`; the `.mmd` and `.png` exist; the `.mmd` starts with the brand line; no ```mermaid blocks or attachments in notebooks (Colab renders neither) |

## Not checked here (judgement)

- Demo flavor (failure first, closers): reviewers check it
- Slots are decisions and do not leak answers; tiers really get harder; no helper used
  before its visible definition: `learner-engineer-refute`
- Live Jev and OpenAI behaviour: the workflow's "Run in order" stage

## When to run

- After every 5-cell batch in `/build-notebook`
- `--pair --strict` before every commit
