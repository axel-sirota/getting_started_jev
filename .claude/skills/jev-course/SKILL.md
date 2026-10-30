---
name: jev-course
description: Course vocabulary, the CLINC150 triage running case, the module arc, the slide/notebook rhythm and the three-tier lab rules for Getting Started with Jev (Colab notebooks calling TypeSafe's Jev decision model and OpenAI). Use when planning, writing or reviewing any notebook cell, lab, slide, diagram or plan in this repo.
---

# Getting Started with Jev: course context

Read first: `plans/DECISIONS.md` (what we build), `plans/TEACHING_STYLE.md` (voice, moves),
`plans/NOTEBOOK_STYLE.md` (cell anatomy), `imp_files/outline_getting_started_jev.md` (as sold).
For any Jev API detail load the official `typesafe-ai` skill and read the live docs it points
to (start at https://docs.typesafe.ai/llms.txt). Use built-in WebSearch/WebFetch, never Kryla.

## Vocabulary

| Term | Meaning in this course |
|---|---|
| Jev | TypeSafe's first System One model. Answers typed questions about a state; does not generate text |
| System One model | A decision model: fast, structured, calibrated answers your code branches on |
| State | What Jev reads: a string or structured object (the CLINC150 query plus context) |
| Question / primitive | Choice (pick one option), Score (rate on described levels), Noul (probability a statement is true) |
| Probabilities | Per-option distribution Jev returns |
| Confidence | How sure Jev is; a second axis next to the answer, used to gate actions |
| Judgments in Jev, decisions in code | Jev supplies inputs to a truth table written in Python; never ask Jev "should we escalate?" |
| Atomic question | One literal, gut-check judgment; decompose anything that needs reasoning or several factors |
| Out-of-scope (OOS) | CLINC150 queries that belong to no intent; Jev must say "none of these" |
| Confidence-gated routing | Act when confident, send to a human or a fallback when not |
| Router / guardrail | Jev in front of an LLM (who handles this?) and behind it (may this reply go out?) |

## Running case

CLINC150 (`clinc_oos`, `plus`): 10 domains, 150 intents, plus out-of-scope queries. Each
module grows one triage layer: domain + urgency + escalation (M1), domain then intent (M2),
measured and thresholded against a zero-shot baseline (M3), routed to an LLM with a Jev
guardrail on every reply (M4). Fixed seed, small samples, measured numbers only.

## Module arc and kill lines

| # | Kills / Establishes |
|---|---|
| 1 | Kills "an LLM with a JSON prompt is the same thing". Establishes state + questions -> typed answers |
| 2 | Kills "one big question is fine". Establishes atomic questions, structured state, logic and dates in code |
| 3 | Kills "a confident answer is a correct answer". Establishes calibration, OOS detection, a review threshold |
| 4 | Kills "the LLM can police itself". Establishes code / Jev / LLM / human: who decides what |

## Rhythm (slides <-> notebook)

Slide badge `Switch to the notebook: Demo n` -> notebook `## Demo n` -> notebook
`## Back to the slides: <next slide title>` -> ... -> badge `Switch to the notebook: Lab n`
-> `## Lab n` with `# LAB n.1 (Guided)`, `# LAB n.2 (Core)`, `# LAB n.3 (Challenge,
optional)` -> `## Back to the slides: Debrief`. Labels match exactly; both validators check.

## Hard rules

- Keys via getpass (env var first); never Colab secrets, never printed, never literal
- Every Jev and OpenAI call is a visible cell; pinned model ids in CONFIG
- Diagrams: `.mmd` master with the brand line, committed PNG linked by raw GitHub URL
- No em dashes, en dashes or banned words anywhere learners read
