---
description: Research one module and write BOTH plans for one human approval - the notebook plan (plans/modules/moduleNN_plan.md, demo cells and lab spec) and the slide plan (imp_files/slides/moduleNN_slides.md + _diagrams.md). The finalize-module workflow then builds from them
---

Research and plan module: $ARGUMENTS

(Argument is a module number, 1 to 10.)

## GUARD

```bash
ls plans/DECISIONS.md course/harborview/__init__.py 2>/dev/null
```

- No manifest: stop, "Run `/init-course` first."
- No `course/harborview/`: stop, "Run `/build-core` first. Every module builds on it."

---

This command plans ONE module across all 5 beats, in two parts, and Axel approves both
together. After approval the `finalize-module` workflow builds everything from these files
without further planning.

| Part | Output | How |
|---|---|---|
| 1. Notebooks | `plans/modules/module<NN>_plan.md` (demo cells, lab app spec, slide hooks) | the 5 research cycles below |
| 2. Slides | `imp_files/slides/module<NN>_slides.md` + `module<NN>_diagrams.md` (slide by slide) | after Part 1 is written, follow `.claude/commands/plan-slides.md` for this module, skipping its approval wait |

**It creates no `.ipynb`, no app, no deck.** Only the three plan files.

**Web research is MANDATORY.** Per cycle: hypothesis, evidence, antithesis, refinement.

**Evidence ranking, strongest first:**
1. **Running the code** in `.venv/bin/python3` against the pinned packages in
   `course/requirements.txt`, with `AGENT_MODE=mock` locally and, for AWS behaviour, the
   notes in `plans/lab_environment.md`
2. Official docs, changelog and source for the exact pinned version (LangGraph, boto3,
   Bedrock, AgentCore, Gradio)
3. Current third-party writing, treated as a lead to verify
4. Recall. **Never sufficient on its own.**

If the `Skill` tool is unavailable (subagent context), run the discipline directly and log
each cycle into the plan's `# RESEARCH VALIDATED` block.

## Module Map (slugs fixed; titles from plans/DECISIONS.md)

| N | Slug | Lab app |
|---|---|---|
| 1 | ai-literacy | Request Triage |
| 2 | agentic-vs-genai | Chat vs Agent, step labeler |
| 3 | autonomy-hitl | Autonomy Mapper, approval queue |
| 4 | bpmn-dmn | Starter .mmd, Decision Table Editor |
| 5 | instructions | Instruction Workbench |
| 6 | rag-tools-mcp | KB on/off, Trace Viewer |
| 7 | coding-agents | none (demo only) |
| 8 | eval-guardrails | Scenario Scorer |
| 9 | observability | Room Dashboard |
| 10 | use-case-mapping | Pilot Worksheet |

## FAILURE DEFINITION

**COMPLETE SUCCESS** = all true:
- All 5 cycles visible in chat, each with hypothesis, logged evidence, antithesis, refinement
- PRE-WRITE SELF-CHECK printed with all YES
- Plan written with every required section, every cell and app screen drafted in full
- `learner-noncoder-refute` run on the draft and its BLOCKERs fixed

**COMPLETE FAILURE** = any of: fewer than 5 cycles; an API asserted from memory where
running it was possible; a cell or app step that asks a learner to write code; a missing
beat; stub content. On failure, report what failed and restart.

---

## Output Contract (NON-NEGOTIABLE)

One file: `plans/modules/module<NN>_plan.md`. Sections, all required:

- `# Module <N>: <Title>, Plan`
- `## What it teaches` (from OUTLINE + the learning objective it serves)
- `## Slot` (what comes before and after; no minutes. No timings in any content: no slot or beat minutes, no Minutes columns, no 'takes about N minutes/seconds', no lab timers. Axel paces live. Policy facts (grace periods, business days) are not timings. The validators fail on duration patterns.)
- `## The 5 beats` (one paragraph each: Problem, Theory, Fix, Lab, Lesson)
- `## STAR Story` (Situation / Task / Action / Result at the Harborview Life service desk)
- `## Harborview pieces used` (exact `harborview` functions, tools, tables, KB, memory;
  anything missing is listed under `## Core changes needed`, never invented in the module)
ONE NOTEBOOK PER MODULE (firm rule): both sections below describe the SAME notebook,
`course/notebooks/module<NN>_<slug>.ipynb`. The demo part is its top (the whole room runs it
together while Axel explains); the Lab part is appended at its bottom under a
`## Lab: <name>` heading (learners run it on their own). Never plan separate notebooks.

- `# DEMO PART: course/notebooks/module<NN>_<slug>.ipynb, top (Target: <K> cells)`
  - Cell 0 is the module title cell: what we see together, then "your own Lab at the bottom"
  - `## Part A: The problem` then `## Part B: The fix`, separated by a markdown cell
    "Back to the slides" so Axel knows where beat 2 goes; ends with "Key takeaways" and
    "Next: the Lab below"
  - Each cell: `## Cell K - Markdown/Code: Description` with full source in a fenced block
- `# LAB PART: course/apps/lab<NN>_<slug_>.py + the "## Lab: <name>" section at the bottom
  of the same notebook` (`<slug_>` = slug with underscores, so the app is importable)
  (skip for Module 7, say why)
  - `## Learner actions` (every click, edit and toggle in order, and what to notice after)
  - `## App layout` (tabs, components, defaults, what each button does)
  - `## App behaviour` (which harborview calls, per-session state, what is logged to traces)
  - `## Mock responses` (canned outputs per action so `AGENT_MODE=mock` tells the same story)
  - `## Lab section cells` (full source, appended after the demo's takeaways: the
    `## Lab: <name>` heading with instructions, where the link appears and what to do if
    something fails, the launch cell, Try it, "What did you notice?", lab takeaways; no
    second title or setup cell)
- `## Diagram Index` (slug, `course/diagrams/<slug>.mmd`, what it shows, used where)
- `## Slide hooks` (beat 2 theory slides and the beat 5 lesson slide, one line each)
- `## Debrief questions`
- `## Core changes needed` ("none" if none)
- `# VERIFICATION CHECKLIST`
- `# RESEARCH VALIDATED (Month Year)`

Write the header first, then append in ~50-line chunks with Edit.

---

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md`, `plans/lab_environment.md`
2. `imp_files/outline_foundations.md`: this module and its neighbours
3. `.claude/skills/agentic-foundations/SKILL.md`
4. `course/harborview/` (the public functions and their docstrings) and `data/` (tables,
   seed rows, KB docs)
5. `.claude/commands/build-demo.md` and `build-lab.md`: the consumers of this plan
6. `plans/modules/module<NN-1>_plan.md` if it exists
7. For lab ideas: `reference/ai_for_pms/README.md` (catalog) and the matching
   `reference/ai_for_pms/apps/<name>.py`

---

## MANDATORY CYCLE TRACKER

```
CYCLE TRACKER
[_] Cycle 1 - OUTLINE alignment, the 5 beats, continuity   evidence logged: NO
[_] Cycle 2 - API surface (pinned, us-east-1)              evidence logged: NO
[_] Cycle 3 - Problem and fix demo design                  evidence logged: NO
[_] Cycle 4 - Lab app for non-coders                       evidence logged: NO
[_] Cycle 5 - Failure modes, clock, slides, take-homes     evidence logged: NO
```

### Cycle 1 - OUTLINE alignment, the 5 beats, continuity
- Map each OUTLINE lab bullet to a beat. Map the learning objective to the beat that proves it.
- **Invoke `/research`**: how this concept is taught to business audiences in 2026, with
  realistic life insurance servicing examples.
- **Refutation**: is any beat missing or weak? Is the problem demo genuinely broken, or
  staged? Does the fix use only harborview pieces that exist?

### Cycle 2 - API surface (pinned, us-east-1)
- Verify by running every import and signature the module uses: LangGraph, the AgentCore
  Memory checkpointer, Bedrock Converse via LangChain, Knowledge Base retrieve, MCP,
  Gradio. Every Bedrock or AgentCore client has `region_name="us-east-1"`.
- **Invoke `/research`**: breaking changes in the pinned versions.
- **Refutation**: deprecated path? Something that needs internet the space may not have?

### Cycle 3 - Problem and fix demo design
- Part A runs and visibly fails in a way a business person recognizes. Part B is the same
  request, now succeeding, with the change that made the difference shown on screen.
- Demo code is short and heavily commented; plumbing stays in harborview.
- **Refutation**: could Axel narrate each cell? Is the "before" and "after" side by side?

### Cycle 4 - Lab app for non-coders
- Every learner change is a widget. Change, rerun, compare side by side.
- Instructions in plain language before every action; "What did you notice?" after.
- **Invoke `/research`**: Gradio usability gotchas behind the SageMaker Studio proxy.
- **Refutation**: run `learner-noncoder-refute` on the lab section. Fix every BLOCKER.

### Cycle 5 - Failure modes, slides, take-homes
- Every beat is narrated and clicked, not silently executed. No minute splits: Axel paces live.
- LLM variance: seed or cache the designed failure. Define the mock responses.
- Draft slide hooks, diagram index, debrief questions, verification checklist, research
  block (URL + fact).
- **Refutation**: what if Bedrock throttles with 25 learners? If the proxy fails?

## HARD GATE: Pre-Write Self-Check

```
PRE-WRITE SELF-CHECK
--------------------
Cycle tracker all 5 [x] with evidence:             YES / NO
All 5 beats planned (lab N/A only for Module 7):   YES / NO
Problem demo fails visibly; fix demo succeeds:     YES / NO
Only existing harborview pieces used:              YES / NO
No step asks a learner to write code:              YES / NO
Nothing blocks; Run all works with defaults:       YES / NO
Mock responses defined for every lab action:       YES / NO
Every Bedrock/AgentCore client us-east-1:          YES / NO
No infra details (hosts, ids, passwords):          YES / NO
No timings anywhere (minutes, waits, lab timers): YES / NO
learner-noncoder-refute run, BLOCKERs fixed:       YES / NO
Harborview Life only, no real names:               YES / NO
RESEARCH VALIDATED block has URLs:                 YES / NO
AI-tells scan passed:                              YES / NO
```

## Part 2: Slides (after the notebook plan is written)

Follow `.claude/commands/plan-slides.md` for this module end to end: its research (every
factual claim sourced, study figures checked against the primary source), its format, its
5-beat slide order, and its review loop (deck-sales, deck-marketing, deck-diagram,
deck-designer and learner-noncoder refute agents, one at a time). Skip only its "wait for
approval" step: approval happens once, below, for both parts. The slides must match the
demo and lab cells in the notebook plan (same requests, same numbers, same lab steps).
Finish with `.venv/bin/python3 validate_slides.py <N>` passing.

## Approval (one checkpoint for the whole module)

Show Axel, in chat:
1. The notebook plan summary: the 5 beats, demo cells, lab actions, core changes
2. The slide table: slide, title, layout, diagram type, points count
3. Review findings fixed and any rejected, with the reason

**Wait for approval.** If Axel asks for changes, edit the plan files and show the diff.

## Handoff

> Module <N> planned: `plans/modules/module<NN>_plan.md`,
> `imp_files/slides/module<NN>_slides.md` and `module<NN>_diagrams.md`.
>
> Next: run the `finalize-module` workflow with `{"module": <N>}`. It builds the demo, lab,
> diagrams and deck from these approved files and never re-plans them.
