---
description: Validate a module's exercises.ipynb and solutions.ipynb (format, 4 beats per Part from Part 1 (no Part 0), three-tier labs, pair, key handling, diagrams, no real names, AI tells)
---

Validate: $ARGUMENTS

(Argument: a module number, a notebook path, or `--all`. Flags below.)

## Commands

```bash
.venv/bin/python3 validate_notebooks.py <N>                 # both notebooks of module N, static checks
.venv/bin/python3 validate_notebooks.py <N> --pair          # solutions == exercises - FALLBACK cells
.venv/bin/python3 validate_notebooks.py <N> --strict        # a missing .mmd or .png fails
.venv/bin/python3 validate_notebooks.py --all
.venv/bin/python3 -m pytest tests/unit -q                   # the validator's own rules
```

Static only. Running solutions top to bottom against the real APIs is the workflow's
"Run in order" stage.

## What is checked

| Scope | Checks |
|---|---|
| Every notebook | Title cell with `## What you will be able to do`; first code cell is a pinned `%pip install`; a key cell reading `TYPESAFE_API_KEY` from `os.environ` with a `getpass` fallback; banner with a known kind on every code cell except `%pip` and `%%writefile`; max 6 markdown cells in a row; syntax and cross-cell pyflakes; no key literals, no printed keys, no Colab secrets; denylist; no em/en dashes, Unicode multiplication, bare `---`, banned words; outputs cleared; Summary cell last |
| 4 beats | Parts numbered in order from `## Part 1`; no `## Part 0` in any module; every `## Part k` has `### 1. The problem`, `### 2. The solution`, `### 3. Demo`, `### 4. Lab k` in order; beats 1 and 2 have no code and at least one diagram each (Module 1 Part 1's solution carries several: the "what Jev is" figures); beat 3 has a DEMO cell; LAB k.1, k.2, k.3 sit inside `### 4. Lab k` |
| Labs | Every lab markdown has #### Your Task, Level 1: Guided, Level 2: Core, Level 3: Challenge (optional), Expected Output, Hints; tier banners in order; no later cell uses a name defined only in a Level 3 cell |
| exercises.ipynb | Level 1 has `= None  # YOUR CODE` slots; Levels 2 and 3 have `# YOUR CODE`; `# YOUR CODE` only in LAB cells |
| solutions.ipynb | No `# YOUR CODE` left; SOLUTION cells have `# Approach:` and `# Explanation:`; no FALLBACK cells |
| `--pair` | solutions cells == exercises cells minus FALLBACK cells, same order, same kinds, same source outside the labs; same Parts, beats and diagrams |
| Diagrams | Every `<!-- DIAGRAM: <slug> -->` cell holds one `<img src="..." width="W" alt="...">` tag (W = 600 x png width / png height, kept to 420..750, rounded to 10; 700 for xychart-beta charts; never markdown `![]()` image syntax, which Colab stretches to full width) whose src is `RAW_BASE` + `course/diagrams/module_NN/<slug>.png`; the `.mmd` and `.png` exist; the `.mmd` starts with the brand line; no ```mermaid blocks or attachments in notebooks (Colab renders neither) |

## Not checked here (judgement)

- Whether each beat actually teaches (problem felt before the product, solution understood, in Module 1 Part 1's solution explains what Jev is):
  `learner-engineer-refute` and the workflow's beat walk
- Slots are decisions and do not leak answers; tiers really get harder: `learner-engineer-refute`
- Live Jev and OpenAI behaviour: the workflow's "Run in order" stage

## When to run

- After every 5-cell batch in `/build-notebook`
- `--pair --strict` before every commit
