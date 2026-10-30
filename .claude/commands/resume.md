---
description: Reload saved course build state from progress.txt and orient the session to continue
---

# /resume

Load the saved state from `progress.txt` and orient the session so work continues
immediately. Ask at most one clarifying question.

## Step 1: Check for progress.txt

```bash
ls progress.txt 2>/dev/null
```

If missing: "`progress.txt` not found. Run `/save-state` first, or `/start-session`." Stop.

## Step 2: Read progress.txt

Extract: core status, module statuses, open issues, locked decisions, NEXT ACTION.

## Step 3: Verify against the filesystem

```bash
ls -la course/module_* course/diagrams data plans/modules 2>/dev/null
git log --oneline | head -5
```

- A file exists that progress.txt says is missing: update your understanding
- progress.txt says done but the file is missing, or a plan is newer than its notebooks: flag it

Do NOT re-run full validation.

## Step 4: Print orientation summary

```
=== RESUMED SESSION ===

Saved: <date>

CORE
  schema <s>  00_lab_setup (shared.json) <s>  validator <s>

MODULES
  1 Agentic foundations   plan <s>  exercises <s>  solutions <s>  diagrams <s>  live <s>
  ...

OPEN ISSUES
  <list or "none">

NEXT ACTION
  <command>
  Reason: <one sentence>

KEY DECISIONS (active)
  - Engineers code: exercises + solutions per module; no slides
  - Bread demo and lab structure (no CHECK cells, no mini exercises); concierge ideas only
  - Frameworks only in notebooks; no harborview package, no mock mode
  - Model and KB us-east-1; AgentCore, Gateway, Memory, Guardrails, Cognito us-west-2
  - Notebook edits: id map before and after, order asserted

=== READY ===
```

## Step 5: At most one question

- NEXT ACTION obvious: confirm ready
- progress.txt conflicts with the filesystem: describe it and ask which is right

Do not build or fix anything until the user says "go" or "continue".
