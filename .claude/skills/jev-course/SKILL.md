---
name: jev-course
description: Course vocabulary, the CLINC150 triage running case, the module arc, the 4-beat structure (problem, solution, demo, lab) and the three-tier lab rules for Getting Started with Jev, a notebook-only Colab class on TypeSafe's Jev decision model with OpenAI. Use when planning, writing or reviewing any notebook cell, lab, diagram or plan in this repo.
---

# Getting Started with Jev: course context

Read first: `plans/DECISIONS.md` (what we build), `plans/TEACHING_STYLE.md` (voice, moves),
`plans/NOTEBOOK_STYLE.md` (cell anatomy), `imp_files/outline_getting_started_jev.md` (as sold).
For any Jev API detail load the official `typesafe-ai` skill and read the live docs it points
to (start at https://docs.typesafe.ai/llms.txt). Use built-in WebSearch/WebFetch, never Kryla.

## The class is the notebook

No slides. Axel teaches from the Colab notebook: all explanation text and every diagram live
in markdown cells. One notebook pair per module (exercises + solutions).

## The 4 beats (never reordered)

| Beat | Heading | Content |
|---|---|---|
| 1 | `### 1. The problem` | the failure, a concrete example, one diagram, no code |
| 2 | `### 2. The solution` | the idea that fixes it, one diagram, one rule, no code |
| 3 | `### 3. Demo` | `# DEMO:` cells: the problem live, then the solution, measured numbers, Think About It |
| 4 | `### 4. Lab k: <title>` | `# LAB k.1 (Guided)`, `# LAB k.2 (Core)`, `# LAB k.3 (Challenge, optional)` |

Each concept is a `## Part k: <concept>` with those 4 beats. Every module starts at
`## Part 1`; there is no Part 0 (Axel, 2026-11-01). Never explain the product before showing
the problem it solves: in Module 1, Jev arrives inside Part 1's `### 2. The solution` as the
answer to the problem just shown (an LLM gives a bare text label with no probability), and
that solution's sub-sections explain what Jev is (System One, state + questions -> typed
answers, Choice / Score / Noul, score and confidence, LLM vs Jev).

## Vocabulary

| Term | Meaning in this course |
|---|---|
| Jev | TypeSafe's first System One model. Answers typed questions about a state; does not generate text |
| System One model | A decision model: fast, structured, calibrated answers your code branches on |
| State | What Jev reads: a string or structured object (the CLINC150 message plus context) |
| Question / primitive | Choice (pick one option), Score (rate on described levels), Noul (probability a statement is true) |
| Probabilities | Per-option distribution Jev returns (Choice, Score) |
| Confidence | How much of the probability sits on one option; not the same as being right |
| Judgments in Jev, decisions in code | Jev supplies inputs to rules written in Python; never ask Jev "should we escalate?" |
| Atomic question | One literal, gut-check judgment; decompose anything that needs reasoning or several factors |
| Out-of-scope (OOS) | CLINC150 messages that belong to no intent; a Choice still picks one, so pair it with a Noul |
| Confidence-gated routing | Act when the evidence is clear, send to a human or a fallback when not |
| Router / guardrail | Jev in front of an LLM (who handles this?) and behind it (may this reply go out?) |

## Running case

CLINC150 (`clinc/clinc_oos`, `plus`): 10 domains (our "teams"), 150 intents, plus
out-of-scope messages. Each module grows the same triage layer: team + urgency + risk (M1),
literal questions and team then intent (M2), measured against a zero-shot baseline with a
review threshold (M3), routed to an LLM with a Jev guardrail on every reply (M4). Fixed seed,
small samples, measured numbers only.

## Module arc

| # | Parts (each with the 4 beats) | Kills / Establishes |
|---|---|---|
| 1 | The triage question as typed answers (its solution beat introduces Jev); then judgments in Jev, decisions in code | Establishes what Jev is, as the fix for a bare LLM label; kills "an LLM with a JSON schema gives me the same thing" |
| 2 | Vague vs literal questions, dates in code; structured state and two stages | Kills "one big question is fine" |
| 3 | Accuracy and calibration; out-of-scope; confidence-gated routing | Kills "a confident answer is a correct answer" |
| 4 | Jev as router; Jev as guardrail | Kills "the LLM can police itself" |

## Hard rules

- Keys via getpass (env var first); never Colab secrets, never printed, never literal
- Every Jev and OpenAI call is a visible cell; pinned model ids in CONFIG
- Diagrams: `.mmd` master with the brand line, committed PNG embedded by raw GitHub URL in an
  `<img ... width="W">` tag (W = 600 x png width / png height, kept to 420..750, rounded to 10; 700 for xychart-beta charts), never `![]()` (Colab
  stretches markdown images to full width)
- No em dashes, en dashes or banned words anywhere learners read
