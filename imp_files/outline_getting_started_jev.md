# Getting Started with Jev

## Course Overview

Jev doesn't write text: it makes typed decisions your code can use directly. In this four-hour
course you build a triage layer on the CLINC150 dataset, from one question to a
confidence-gated workflow, compare Jev with a Hugging Face zero-shot model, and put it in
front of and behind an LLM.

## Duration

4 hours

## Learning Objectives

- Call Jev from Python with Choice, Score and Noul questions and read probabilities and
  confidence.
- Design atomic questions and structured state, keeping logic, maths and dates in code.
- Measure Jev's accuracy and calibration against a zero-shot baseline and set confidence
  thresholds.
- Combine Jev with an LLM as a router and a guardrail.

## Target Audience

Python developers and data professionals getting acquainted with Jev.

## Prerequisites

- Python in notebooks and basic classification metrics (Pluralsight: Python 3 Fundamentals)

## Technical Requirements

- Google account for Colab; Jev and LLM API keys provided in class

## Outline

### Meet Jev: Typed Decisions Instead of Text

Make your first Jev calls from Colab and see how they differ from an LLM.

- System One models vs LLMs
- State and questions
- Choice, Score and Noul
- Probabilities, confidence and pinned versions

Labs/Demos:

- Demo: The same triage question asked of an LLM and of Jev, comparing output, speed
  and cost.
- Lab: Classify CLINC150 queries by domain, adding urgency and escalation in one call.

### Designing Good Questions

Turn fuzzy judgements into atomic questions and keep the logic in code.

- Instructions and criteria
- Structured state
- Composing answers in code
- Known failure modes

Labs/Demos:

- Demo: Fix a vague question by splitting it into literal ones and moving a date check into
  code.
- Lab: Build a two-stage domain-then-intent classifier over CLINC150's 150 intents.

### Measuring and Trusting Jev

Check Jev's accuracy and calibration on labelled data and compare it with a zero-shot model.

- Accuracy and calibration
- Out-of-scope detection
- Confidence-gated routing
- Speed and cost

Labs/Demos:

- Demo: Plot Jev's confidence against real accuracy on CLINC150.
- Lab: Compare Jev with a zero-shot classifier and set a human-review threshold.

### Jev and LLMs Together

Put Jev in front of an LLM as a router and behind it as a guardrail.

- Code, Jev or LLM: who decides what
- Routing to code, an LLM or a human
- Guardrails on LLM replies

Labs/Demos:

- Demo: Jev catching an LLM reply that breaks the assistant's policy.
- Lab: Route triaged queries to an LLM and check every reply with Jev before it goes out.
