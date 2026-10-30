# CLAUDE.md: Getting Started with Jev

Course materials for a 4-hour, 4-module course: Jev (TypeSafe's System One decision model)
from Python in Google Colab, built around CLINC150 query triage. Per module: one Reveal.js
deck and one exercises/solutions notebook pair. Not an SDD repo: normal git on `main`.

## Read first

`plans/DECISIONS.md` (manifest), `plans/TEACHING_STYLE.md`, `plans/NOTEBOOK_STYLE.md`,
`imp_files/outline_getting_started_jev.md`, `.claude/skills/jev-course/SKILL.md`. For any Jev
API detail load the official `typesafe-ai` skill (plugin `typesafe@typesafe-ai`, project
scope). `plans/` is private and gitignored.

## Pipeline

| Step | Command | Writes |
|---|---|---|
| 1 | `/research-module N` | `plans/modules/module_NN_plan.md` (cells, Flow table) + `imp_files/slides/moduleNN_slides.md` + `moduleNN_diagrams.md`. ONE approval, then STOP |
| 2 | `/build-module N` | Workflow `.claude/workflows/build-module.js`: Exercises, Solutions, Notebook diagrams, Validate notebooks, Run in order (real APIs), Slides plan, Deck + PDF, Validate slides, Review (incl. flow walk), Commit |

Single steps: `/build-notebook`, `/build-diagrams`, `/plan-slides`, `/build-slides`,
`/validate-notebooks`, `/validate-slides`. Session: `/start-session`, `/save-state`, `/resume`.

## Layout

| Path | What |
|---|---|
| `course/module_NN/exercises.ipynb`, `solutions.ipynb` | Colab notebooks |
| `course/diagrams/module_NN/<slug>.mmd` + `.png` | Notebook diagrams, PNG linked by raw GitHub URL |
| `imp_files/slides/` | Slide plans (source of truth for decks) |
| `deck/moduleNN/` | Built decks; shared `deck/css`, `deck/vendor`, `deck/tools` |
| `validate_notebooks.py`, `validate_slides.py` | Validators; `tests/unit/` tests their rules |

## Hard rules

- Keys: `TYPESAFE_API_KEY`, `OPENAI_API_KEY` from env, else `getpass`. Never Colab secrets,
  never in a cell, never printed, never in chat
- Labs in three tiers: `# LAB n.1 (Guided)` slots `= None  # YOUR CODE`, `# LAB n.2 (Core)`
  function body, `# LAB n.3 (Challenge, optional)`; nothing later depends on Level 3
- Hops: slide badge `Switch to the notebook: Demo n / Lab n` <-> notebook `## Demo n` /
  `## Lab n`, closed by `## Back to the slides: <exact next slide title>`
- Slides: diagram first, one idea per slide, at most 2 short sentences, Data Trainers brand
- Notebook diagrams: never a ```mermaid block or attachment (Colab renders neither); link
  the committed PNG via `RAW_BASE` in `validate_notebooks.py`. Push so Colab can load it
- Jev makes judgments, code makes decisions; OpenAI for every text generation
- Web research: built-in WebSearch / WebFetch only, never Kryla web tools. Jev facts only from
  docs.typesafe.ai, typesafe.ai, github.com/typesafe-ai
- `.venv/bin/python3` only; packages pinned in `course/requirements.txt` and `requirements.txt`
- Notebook edits follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`
- No em dashes, en dashes or AI-tell words in anything learners read

## Verify

```bash
.venv/bin/python3 -m pytest tests/unit -q
.venv/bin/python3 validate_notebooks.py <N> --pair --strict
.venv/bin/python3 validate_slides.py <N> --render
```
