---
description: Research one module and write its plan (plans/modules/module_NN_plan.md) for ONE approval by Axel - the whole class is the Colab notebook, taught in 4 beats per Part (problem, solution, demo, lab), every cell drafted in full, diagrams rendered. /build-module then builds both notebooks from it
---

Research and plan module: $ARGUMENTS

(Argument is a module number, 1 to 4.)

## GUARD

```bash
ls plans/DECISIONS.md plans/TEACHING_STYLE.md plans/NOTEBOOK_STYLE.md validate_notebooks.py imp_files/outline_getting_started_jev.md 2>/dev/null
```

- Missing DECISIONS / TEACHING_STYLE / NOTEBOOK_STYLE: stop, "Run `/init-course` first."

**This command creates no `.ipynb`.** It writes `plans/modules/module_NN_plan.md` and the
module's diagrams (`course/diagrams/module_NN/<slug>.mmd` + `.png`). Then it STOPS and waits
for Axel.

**There are no slides.** The class is the notebook: every explanation and every diagram the
learner sees is in it. Plan the text as carefully as the code.

**The 4 beats are the structure, per Part, in this order:**

| Beat | Heading | What it holds |
|---|---|---|
| 1 | `### 1. The problem` | a concrete failure in plain words, one diagram, no code |
| 2 | `### 2. The solution` | the idea that fixes it, one diagram, the one rule to remember, no code |
| 3 | `### 3. Demo` | `# DEMO:` cells: the problem live, then the solution, measured numbers, Think About It |
| 4 | `### 4. Lab k: <title>` | three-tier lab: Guided, Core, Challenge (optional) |

Module 1 starts with `## Part 0: What is Jev` (text and diagrams only) before any Part.
No hook, comparison or benchmark comes before the product is explained.

**Web research is MANDATORY, with the built-in WebSearch / WebFetch tools only (never Kryla
web tools).** Per cycle: hypothesis, evidence, antithesis, refinement. Evidence ranking,
strongest first:
1. **Running the code** in `.venv/bin/python3` against `course/requirements.txt`, live. The
   keys are in the gitignored `.env`; load them in the same Bash command, never print them:
   `set -a && . ./.env && set +a && export TYPESAFE_API_KEY="${TYPESAFE_API_KEY:-$JEV_AI_API_KEY}"`
2. The official `typesafe-ai` skill and the live docs it points to (docs.typesafe.ai,
   `llms.txt`, the OpenAPI spec, the jaggedness page), the `typesafe-sdk` source for the pinned
   version, OpenAI and Hugging Face official docs. Look-alike Jev sites rank high in search:
   cite only docs.typesafe.ai, typesafe.ai, github.com/typesafe-ai for Jev claims
3. Current third-party writing, a lead to verify
4. Recall. **Never sufficient on its own.**

## Module Map (from plans/DECISIONS.md)

| N | Folder | Module |
|---|---|---|
| 1 | module_01 | Meet Jev: Typed Decisions Instead of Text |
| 2 | module_02 | Designing Good Questions |
| 3 | module_03 | Measuring and Trusting Jev |
| 4 | module_04 | Jev and LLMs Together |

## FAILURE DEFINITION

**COMPLETE SUCCESS** = all true:
- 5 cycles visible in chat, each with hypothesis, logged evidence, antithesis, refinement
- PRE-WRITE SELF-CHECK printed, all YES
- Plan written with every section, every cell drafted in full (exercise and solution)
- Every Part has the 4 beats in order; Module 1 has Part 0 first
- Every problem and solution beat (and every Part 0 cell) has a `.mmd` drafted in full (brand
  line first), rendered to PNG with mmdc and looked at
- The solution cells were run end to end against the real APIs before approval
- `learner-engineer-refute` and `deck-diagram-refute` run, BLOCKERs fixed

**COMPLETE FAILURE** = any of: fewer than 5 cycles; a Jev or OpenAI API asserted from memory
where running it was possible; a number shown not measured; a Part missing a beat or with
beats out of order; Module 1 without Part 0, or with a comparison before Jev is explained; a
lab tier missing or a Level 3 that a later cell depends on; a Level 1 slot that is
boilerplate; an outline bullet not covered; stub content; a diagram left as a placeholder.

---

## Pre-Work: MANDATORY Reading

0. `plans/NOTES_AXEL.md` if it exists: Axel's direction for this module (wins over everything)
1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/TEACHING_STYLE.md` (whole file) and `plans/NOTEBOOK_STYLE.md` (whole file)
3. `imp_files/outline_getting_started_jev.md`: this module, its objectives, its neighbours
4. The `typesafe-ai` skill (load it) and the docs pages for every primitive and pattern this
   module uses
5. `.claude/skills/jev-course/SKILL.md` and `.claude/skills/mermaid-diagrams/SKILL.md`
6. The previous module's plan and its built `solutions.ipynb` (continuity: The Story So Far)
7. `.claude/commands/build-notebook.md` and `.claude/workflows/build-module.js`: the consumers
   of this plan

## MANDATORY CYCLE TRACKER

```
CYCLE TRACKER
[_] Cycle 1 - Outline -> Parts, beats, kill line, Flow        evidence logged: NO
[_] Cycle 2 - API surface (pinned), run it                    evidence logged: NO
[_] Cycle 3 - Problem, solution, demo per Part (measured), diagrams  evidence logged: NO
[_] Cycle 4 - Lab per Part in three tiers, FALLBACK           evidence logged: NO
[_] Cycle 5 - Text pass, summary, run solutions end to end    evidence logged: NO
```

### Cycle 1 - Outline -> Parts, beats, kill line, Flow
- Turn the outline's bullets, demo and lab into Parts. Each Part is one concept with one
  problem and one solution. Map every outline bullet and objective to a Part and a cell
- Module 1: draft Part 0 "What is Jev" first (what a System One model is, state, questions,
  Choice / Score / Noul, typed answers with probabilities, how it differs from an LLM)
- Write the module's `Kills:` / `Establishes:` line and the problem chain (which solution
  uncovers which next problem, including the one handed to the next module)
- Draft the `## Flow` table: Part, beat, cells, minutes (module = 1 hour)
- **Research**: how TypeSafe's docs and cookbooks explain this topic
- **Refutation**: is any outline bullet missing? Is each problem real, not staged?

### Cycle 2 - API surface (pinned), run it
- Run every import and call the module uses: `typesafe_sdk` (client, `system_one`, Choice /
  Score / Noul, criteria, probabilities, confidence, model id), `openai` (pinned model id),
  `datasets` (`clinc/clinc_oos`, `plus`), `transformers` zero-shot where module 3 needs it
- Draft the pinned `%pip install` cell, `# KEYS` (env var, else `getpass`, refuse empty, never
  print) and `# CONFIG` (client, pinned model ids, one probe call that fails loud) in full
- Record per call: latency and cost (measured), rate limits from the docs
- **Refutation**: will 25 learners on one key hit rate limits? Does Colab ship a conflicting version?

### Cycle 3 - Problem, solution, demo per Part (measured), diagrams
- Beat 1: write the problem so a learner feels it: a concrete message, what goes wrong, why
- Beat 2: write the solution as an idea before any code: what changes, the one rule
- Beat 3: `# DEMO:` cells: the problem live (measured on a fixed CLINC150 sample, N and rate
  recorded), then the solution working, then `> **Think About It**:`
- Jev answers feed decisions written in code, never a "should we..." question
- **Diagrams, drafted in full now**: one for each problem beat, one for each solution beat
  (shaped so before and after line up), one per Part 0 cell. Write
  `course/diagrams/module_NN/<slug>.mmd` (brand line first, labels = code identifiers), render
  `cd deck && ./node_modules/.bin/mmdc -i ../course/diagrams/module_NN/<slug>.mmd -o ../course/diagrams/module_NN/<slug>.png -s 2 -b white -c tools/mermaid-config.json`
  and Read the PNG. The notebook cell holds the marker and the raw GitHub image link
- **Refutation**: run `deck-diagram-refute` on the diagrams and fix every BLOCKER

### Cycle 4 - Lab per Part in three tiers
- `### 4. Lab k: <Title>` markdown with #### Your Task, #### Level 1: Guided, #### Level 2:
  Core, #### Level 3: Challenge (optional), #### Expected Output, #### Hints
- `# LAB k.1 (Guided)`: everything given but 1 to 3 decisions, `name = None  # YOUR CODE`
- `# LAB k.2 (Core)`: signature, type hints, docstring, test call given; body `# YOUR CODE`, `pass`
- `# LAB k.3 (Challenge, optional)`: spec, expected output, test call; nothing later uses it
- `# FALLBACK` after Level 1 when Level 2 or a later Part needs its result
- Solutions drafted in full for all three levels
- **Refutation**: run `learner-engineer-refute` on the plan. Fix every BLOCKER

### Cycle 5 - Text pass, summary, run solutions end to end
- Read every markdown cell in order as a learner: does each beat teach on its own, is every
  term explained before use, is Part 0 enough to say what Jev is?
- Summary (Key Takeaways, Looking Ahead, Homework)
- Extract the plan's solution cells into a scratch script and run them top to bottom against
  the real APIs. Every cell must run; record the numbers it prints in `## Measured numbers`
- **Refutation**: what if Jev or OpenAI throttles mid-class? What if a slot is still `None`?

## Output Contract (NON-NEGOTIABLE)

One file: `plans/modules/module_NN_plan.md`. Sections, all required:

- `# Module <N>: <Title>, Plan`
- `## What it teaches` (outline text + objectives, each mapped to a Part and cell)
- `## Kill line and problem chain`
- `## Story So Far`
- `## Flow` (table: Part, beat, cells, minutes)
- `## Parts` (one row per Part: problem in one line, solution in one line, demo cells, lab, diagram slugs)
- `## Measured numbers` (each number shown in class: how measured, N, value, date)
- `# EXERCISES: course/module_NN/exercises.ipynb (Target: <K> cells)`
  - Each cell: `## Cell K - Markdown/Code [KIND]: Description` with full source in a fenced block
- `# SOLUTIONS: course/module_NN/solutions.ipynb`
  - Only the cells that differ: `## Cell K - SOLUTION: LAB k.n` full source; FALLBACK cells removed
- `## Diagram Index` (slug, cell K, beat, what it shows, renders with mmdc YES/NO)
- `## Run in order` (what the end-to-end run printed)
- `# VERIFICATION CHECKLIST`
- `# RESEARCH VALIDATED (Month Year)` (URL + fact per line)

Write the header first, then append in ~50-line chunks with Edit.

## HARD GATE: Pre-Write Self-Check

```
PRE-WRITE SELF-CHECK
--------------------
Cycle tracker all 5 [x] with evidence:                   YES / NO
Module 1 only: Part 0 explains Jev before anything else: YES / NO / N/A
Every Part has the 4 beats in order:                     YES / NO
Problem and solution beats: text + one diagram, no code: YES / NO
Every demo shows the problem live before the solution:   YES / NO
Every outline bullet covered:                            YES / NO
Every shown number measured and recorded:                YES / NO
Every diagram rendered and looked at:                    YES / NO
Diagram labels match identifiers in the code cells:      YES / NO
Lab markdown has the 6 headings, one lab per Part:       YES / NO
LAB k.1 / k.2 / k.3 present, titled, markers right:      YES / NO
Nothing later depends on Level 3:                        YES / NO
%pip pinned, KEYS via env or getpass, CONFIG pinned ids:  YES / NO
No Colab secrets, no key literal, no key printed:        YES / NO
Jev decides judgments, code decides actions:             YES / NO
Solution cells ran end to end against the real APIs:     YES / NO
learner-engineer-refute run, BLOCKERs fixed:             YES / NO
deck-diagram-refute run, BLOCKERs fixed:                 YES / NO
RESEARCH VALIDATED block has URLs (official sources):    YES / NO
AI-tells scan passed:                                    YES / NO
```

## Approval (STOP here)

Show Axel, in chat:
1. Part 0 (Module 1) in a few lines, then per Part: the problem, the solution, the demo, the lab
2. The Flow table
3. Lab tiers per Part with their slots, and the measured numbers
4. Diagram list (slug, beat)
5. Review findings fixed and any rejected, with the reason

**Wait for approval.** Silence is not approval. If Axel asks for changes, edit the plan and
show the diff.

## Handoff

> Module <N> planned: `plans/modules/module_NN_plan.md` and its diagrams.
>
> Next: `/build-module <N>` builds exercises and solutions from the approved plan, validates
> them, runs them against the real APIs, reviews and commits.
