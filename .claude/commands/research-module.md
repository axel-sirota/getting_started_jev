---
description: Research one module and write BOTH plans for ONE approval by Axel - the notebook plan (plans/modules/module_NN_plan.md, every exercise and solution cell drafted in full, three-tier lab, Flow table) and the slide plan (imp_files/slides/moduleNN_slides.md + moduleNN_diagrams.md). /build-module then builds everything from them
---

Research and plan module: $ARGUMENTS

(Argument is a module number, 1 to 4.)

## GUARD

```bash
ls plans/DECISIONS.md plans/TEACHING_STYLE.md plans/NOTEBOOK_STYLE.md validate_notebooks.py validate_slides.py imp_files/outline_getting_started_jev.md 2>/dev/null
```

- Missing DECISIONS / TEACHING_STYLE / NOTEBOOK_STYLE: stop, "Run `/init-course` first."

**This command creates no `.ipynb` and no deck.** Only the three plan files below. Then it
STOPS and waits for Axel.

| Part | Writes | How |
|---|---|---|
| 1. Notebooks | `plans/modules/module_NN_plan.md` (every exercise and solution cell, Flow table) | the 5 research cycles below |
| 2. Slides | `imp_files/slides/moduleNN_slides.md` + `moduleNN_diagrams.md` | after Part 1, follow `.claude/commands/plan-slides.md`, skipping its approval wait |

**Web research is MANDATORY, with the built-in WebSearch / WebFetch tools only (never Kryla
web tools).** Per cycle: hypothesis, evidence, antithesis, refinement. Evidence ranking,
strongest first:
1. **Running the code** in `.venv/bin/python3` against `course/requirements.txt`, live with
   `TYPESAFE_API_KEY` / `OPENAI_API_KEY` from the shell environment (ask Axel to export them
   if missing; never write a key to a file)
2. The official `typesafe-ai` skill and the live docs it points to (docs.typesafe.ai,
   `llms.txt`, the OpenAPI spec, the jaggedness page), the `typesafe` SDK source for the pinned
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
- Notebook plan written with every section, every cell drafted in full (exercise and solution)
- A `## Flow` table that interleaves SLIDES and NOTEBOOK steps, with matching hop labels
- Every notebook diagram drafted in full as a `.mmd` (brand line first), rendered to PNG with
  `mmdc` and looked at
- Slide plan and slide diagrams written per plan-slides, `validate_slides.py N` passing
- `learner-engineer-refute` run on the notebook plan, deck reviewers run on the slide plan,
  BLOCKERs fixed

**COMPLETE FAILURE** = any of: fewer than 5 cycles; a Jev or OpenAI API asserted from memory
where running it was possible; a number shown (accuracy, latency, cost) not measured; a lab
tier missing or a Level 3 that a later cell depends on; a Level 1 slot that is boilerplate
rather than a decision; an outline bullet not covered; stub content; a diagram left as a
placeholder or description; a slide badge without a matching notebook section.

---

## Pre-Work: MANDATORY Reading

0. `plans/NOTES_AXEL.md` if it exists: Axel's direction for this module (wins over everything)
1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/TEACHING_STYLE.md` (whole file) and `plans/NOTEBOOK_STYLE.md` (whole file)
3. `imp_files/outline_getting_started_jev.md`: this module, its objectives, its neighbours
4. The `typesafe-ai` skill (load it) and the docs pages for every primitive and pattern this
   module uses
5. `.claude/skills/jev-course/SKILL.md` and `.claude/skills/mermaid-diagrams/SKILL.md`
6. `plans/modules/module_<NN-1>_plan.md` if it exists (continuity: The Story So Far, recap cells)
7. For exercise style ideas: one notebook pair from `~/repos/finetuning-llms-hf` (numbered
   exercises, an optional harder last one) and `~/repos/nwm_foundations_agentic_ai_engineering/course/module_02/`
   (exercises/solutions anatomy)
8. `.claude/commands/build-notebook.md`, `.claude/commands/plan-slides.md` and
   `.claude/workflows/build-module.js`: the consumers of these plans

## MANDATORY CYCLE TRACKER

```
CYCLE TRACKER
[_] Cycle 1 - Outline alignment, kill line, Flow, continuity  evidence logged: NO
[_] Cycle 2 - API surface (pinned), run it                    evidence logged: NO
[_] Cycle 3 - Demo design (measured), diagrams                evidence logged: NO
[_] Cycle 4 - Lab in three tiers, FALLBACK                    evidence logged: NO
[_] Cycle 5 - Think About It, summary, run-in-order plan      evidence logged: NO
```

### Cycle 1 - Outline alignment, kill line, Flow, continuity
- Map each outline bullet to a slide group or a demo; map the outline lab to the lab; map
  each learning objective to the cell that proves it
- Write the module's `Kills:` / `Establishes:` line and the problem chain (which fix uncovers
  which next problem, including the one handed to the next module)
- Draft the `## Flow` table: step, where (SLIDES or NOTEBOOK), slide titles or cell numbers,
  minutes (module = 1 hour including the lab). Every NOTEBOOK step starts at a hop label
  (`Demo n`, `Lab n`) and ends with `Back to the slides: <next slide title>`
- **Research**: how TypeSafe's docs and cookbooks teach this topic; how practitioners
  evaluate classifiers on CLINC150 in 2026
- **Refutation**: is any outline bullet missing? Is the opening problem real or staged?

### Cycle 2 - API surface (pinned), run it
- Run every import and call the module uses: `typesafe` (client, `system_one`, Choice / Score
  / Noul, probabilities, confidence, model id), `openai` (pinned model id), `datasets`
  (`clinc_oos` config and label names), `transformers` zero-shot where module 3 needs it
- Draft the pinned `%pip install` cell, the `# KEYS` cell (env var, else `getpass`, refuse
  empty, never print) and the `# CONFIG` cell (client, pinned model ids, one probe call that
  fails loud) in full. Every notebook repeats them
- Every Jev and OpenAI call is a visible cell. Small helpers go in a `# HELPER` cell where
  first needed
- Record per call: latency and cost per request (measured), rate limits from the docs
- **Research**: breaking changes in the pinned versions; Jev model ids and limits
- **Refutation**: will 25 learners on the same key hit rate limits? Does Colab already ship a
  conflicting version of any pinned package?

### Cycle 3 - Demo design (measured), diagrams
- Per concept: `## Demo n` markdown (two-line recap + diagram), `# DEMO:` problem cells,
  `# DEMO:` fix cells, `> **Think About It**:`, `## Back to the slides: <title>`
- The problem DEMO is a contrast engineers recognize (LLM prose vs typed answer, vague vs
  atomic question, confident but wrong). Measure it on a fixed CLINC150 sample (N queries,
  rate) and record the numbers; if it does not reproduce, redesign it and say how it is seeded
- Jev answers feed a decision written in code (truth table), never a "should we..." question
- **Notebook diagrams, drafted in full now.** Every new concept gets one: write
  `course/diagrams/module_NN/<slug>.mmd` (brand line first, labels use the real identifiers),
  render with
  `cd deck && npx mmdc -i ../course/diagrams/module_NN/<slug>.mmd -o ../course/diagrams/module_NN/<slug>.png -w 1600 -b white -c tools/mermaid-config.json`
  and Read the PNG. The notebook cell is the marker plus a raw GitHub image link (mermaid skill)
- **Refutation**: could Axel narrate each cell? Are before and after both on screen? Run
  `deck-diagram-refute` on the drafted diagrams and fix every BLOCKER

### Cycle 4 - Lab in three tiers
- `## Lab n: <Title>` markdown with ### Your Task, ### Level 1: Guided, ### Level 2: Core,
  ### Level 3: Challenge (optional), ### Expected Output, ### Hints
- `# LAB n.1 (Guided)`: everything given but 1 to 3 decisions, `name = None  # YOUR CODE` slots
- `# LAB n.2 (Core)`: signature, type hints, docstring, test call given; body is `# YOUR CODE`
  then `pass`
- `# LAB n.3 (Challenge, optional)`: spec comment, expected output and a test call; nothing
  later may use a name it defines
- Each cell prints what Expected Output describes. Solutions drafted in full for all three
- `# FALLBACK` only when a later section needs a Level 1 or 2 result
- **Refutation**: run `learner-engineer-refute` on the lab drafts. Fix every BLOCKER. Can a
  learner finish Level 1 in 5 minutes, Level 2 in 10, and is Level 3 really harder?

### Cycle 5 - Think About It, summary, run-in-order plan
- Think About It questions, Summary (Key Takeaways, Looking Ahead, Homework)
- Run-in-order plan: the solutions notebook must run top to bottom headless with the two keys
  in the environment (getpass skipped). List any cell that cannot (none expected)
- **Refutation**: what if Jev or OpenAI throttles mid-class? What if a learner's slot is
  still `None` when they reach the next section?

## Output Contract, Part 1 (NON-NEGOTIABLE)

One file: `plans/modules/module_NN_plan.md`. Sections, all required:

- `# Module <N>: <Title>, Plan`
- `## What it teaches` (outline text + objectives)
- `## Kill line and problem chain`
- `## Story So Far`
- `## Flow` (table: step, SLIDES/NOTEBOOK, slide titles or cell numbers, hop label, minutes)
- `## Sections` (one row per concept: diagram slug, problem DEMO, fix DEMO, Think About It)
- `## Measured numbers` (each number shown in class: how measured, N, value, date)
- `# EXERCISES: course/module_NN/exercises.ipynb (Target: <K> cells)`
  - Each cell: `## Cell K - Markdown/Code [KIND]: Description` with full source in a fenced
    block. Diagram cells are `[DIAGRAM]` markdown cells (marker + raw GitHub image link)
- `# SOLUTIONS: course/module_NN/solutions.ipynb`
  - Only the cells that differ: `## Cell K - SOLUTION: LAB n.k` full source; list of
    FALLBACK cells removed
- `## Diagram Index` (slug, exercises cell K, what it shows, shape, renders with mmdc YES/NO)
- `## Slide hooks` (what each slide group must carry so slides and notebook tell one story)
- `## Run in order` (expected result of a headless run of solutions.ipynb)
- `# VERIFICATION CHECKLIST`
- `# RESEARCH VALIDATED (Month Year)` (URL + fact per line)

Write the header first, then append in ~50-line chunks with Edit.

## HARD GATE: Pre-Write Self-Check

```
PRE-WRITE SELF-CHECK
--------------------
Cycle tracker all 5 [x] with evidence:                   YES / NO
Every outline bullet covered:                            YES / NO
Flow table interleaves slides and notebook, labels exact: YES / NO
Every Demo/Lab section ends with "Back to the slides":   YES / NO
Every shown number measured and recorded:                YES / NO
Every new concept has a .mmd + rendered PNG (looked at): YES / NO
Diagram labels match identifiers in the code cells:      YES / NO
Lab markdown has the 6 headings:                          YES / NO
LAB n.1 / n.2 / n.3 present, titled, markers right:      YES / NO
Nothing later depends on Level 3:                        YES / NO
FALLBACK only where a later section needs the result:    YES / NO
%pip pinned, KEYS via env or getpass, CONFIG pinned ids:  YES / NO
No Colab secrets, no key literal, no key printed:        YES / NO
Every helper defined in a visible cell before use:       YES / NO
Jev decides judgments, code decides actions:             YES / NO
learner-engineer-refute run, BLOCKERs fixed:             YES / NO
deck-diagram-refute run, BLOCKERs fixed:                 YES / NO
RESEARCH VALIDATED block has URLs (official sources):    YES / NO
AI-tells scan passed:                                    YES / NO
```

## Part 2: Slides (after the notebook plan is written)

Follow `.claude/commands/plan-slides.md` for this module end to end: its research (every
factual claim sourced, every number from `## Measured numbers`), its format, its slide order,
and its review loop (deck-sales, deck-marketing, deck-diagram, deck-designer and
learner-engineer refute agents, one at a time, then the `-build` counterparts). Skip only its
"wait for approval" step: approval happens once, below, for both parts.

Slides explain well and diagram first: every concept slide carries one Mermaid diagram that
carries the idea, at most 2 short sentences. The slide order follows the `## Flow` table. A
slide that sends the room to the notebook ends with `Badge: "Switch to the notebook: Demo n"`
(or `Lab n`), and the slide right after it has exactly the title the notebook's
`## Back to the slides:` cell names. The slides must match the notebook plan (same queries,
same numbers, same lab levels).

Finish with `.venv/bin/python3 validate_slides.py <N>` passing.

## Approval (one checkpoint for the whole module, STOP here)

Show Axel, in chat:
1. The Flow table
2. The notebook summary: sections, demos, lab tiers with their slots, measured numbers
3. The slide table: slide, title, layout, diagram type, badge
4. Review findings fixed and any rejected, with the reason

**Wait for approval.** Silence is not approval. If Axel asks for changes, edit the plan files
and show the diff.

## Handoff

> Module <N> planned: `plans/modules/module_NN_plan.md`,
> `imp_files/slides/moduleNN_slides.md` and `moduleNN_diagrams.md`.
>
> Next: `/build-module <N>` runs the workflow that builds exercises, solutions, diagrams and
> the deck from these approved files, validates them in order, reviews and commits.
