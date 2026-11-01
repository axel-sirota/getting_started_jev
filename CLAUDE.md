# CLAUDE.md: Getting Started with Jev

Course materials for a 4-hour, 4-module course: Jev (TypeSafe's System One decision model)
from Python in Google Colab, built around CLINC150 message triage. **The class is the
notebook: there are no slides.** Per module: one exercises/solutions notebook pair that holds
every explanation, every diagram, the demos and the labs. Not an SDD repo: normal git on `main`.

## Read first

`plans/DECISIONS.md` (manifest), `plans/TEACHING_STYLE.md`, `plans/NOTEBOOK_STYLE.md`,
`imp_files/outline_getting_started_jev.md`, `.claude/skills/jev-course/SKILL.md`. For any Jev
API detail load the official `typesafe-ai` skill (plugin `typesafe@typesafe-ai`, project
scope). `plans/` is private and gitignored. Reference notebooks for style:
`~/repos/ml_and_nlp/Solutions/2-Build-It/5-Word2Vec_and_Sentence_Embeddings.ipynb` and
`~/repos/finetuning-llms-hf/`.

## The 4 beats (Axel's structure, never reordered)

No Part 0 (Axel, 2026-11-01). Every module starts at `## Part 1`, and every
`## Part k: <concept>` has, in order:

1. `### 1. The problem`: the failure in plain words + one figure, no code
2. `### 2. The solution`: the idea + one figure, no code
3. `### 3. Demo`: DEMO cells, the problem live then the solution, Think About It
4. `### 4. Lab k: <title>`: `# LAB k.1 (Guided)`, `# LAB k.2 (Core)`, `# LAB k.3 (Challenge, optional)`

Never explain the product before showing the problem it solves. In Module 1, Jev is
introduced inside Part 1's `### 2. The solution`, as the answer to the problem just shown (an
LLM gives a bare text label with no probability). Its sub-sections explain what Jev is: System
One, state + questions -> typed answers, Choice / Score / Noul, score and confidence, LLM vs Jev.

## Pipeline

| Step | Command | Writes |
|---|---|---|
| 1 | `/research-module N` | `plans/modules/module_NN_plan.md` (every cell, Flow table) and the module's diagrams. ONE approval, then STOP |
| 2 | `/build-module N` | Workflow `.claude/workflows/build-module.js`: Exercises, Solutions, Diagrams, Validate, Run in order (real APIs), Review (learner, diagrams, beat walk), Commit |

Single steps: `/build-notebook`, `/build-diagrams`, `/validate-notebooks`. Session:
`/start-session`, `/save-state`, `/resume`.

## Layout

| Path | What |
|---|---|
| `course/module_NN/exercises.ipynb`, `solutions.ipynb` | The class, in Colab |
| `course/diagrams/module_NN/<slug>.mmd` + `.png` | Diagrams, PNG embedded by raw GitHub URL in an `<img width="W">` tag |
| `deck/` | Diagram toolchain only (mermaid-cli + brand config); no decks |
| `validate_notebooks.py` | Validator; `tests/unit/` tests its rules |

## Hard rules

- Keys: `TYPESAFE_API_KEY`, `OPENAI_API_KEY` from env, else `getpass`. Never Colab secrets,
  never in a cell, never printed, never in chat. Locally they live in the gitignored `.env`
- Labs in three tiers per Part; nothing later depends on Level 3
- Diagrams: never a ```mermaid block or attachment in a notebook (Colab renders neither); embed
  the committed PNG (via `RAW_BASE` in `validate_notebooks.py`) with an HTML tag, never
  markdown image syntax, so Colab does not stretch it to full cell width:
  `<img src="https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png" width="W" alt="<alt text>">` (W = 600 x png width / png height, kept to 420..750, rounded to 10; 700 for xychart-beta charts), under its `<!-- DIAGRAM: <slug> -->` marker. Push so Colab can load it
- Jev makes judgments, code makes decisions; OpenAI for every text generation
- Web research: built-in WebSearch / WebFetch only, never Kryla web tools. Jev facts only from
  docs.typesafe.ai, typesafe.ai, github.com/typesafe-ai
- `.venv/bin/python3` only; packages pinned in `course/requirements.txt` and `requirements.txt`
  (`typesafe-sdk`, never the unrelated `typesafe` package)
- Notebook edits follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`
- No em dashes, en dashes or AI-tell words in anything learners read

## Verify

```bash
.venv/bin/python3 -m pytest tests/unit -q
.venv/bin/python3 validate_notebooks.py <N> --pair --strict
```
