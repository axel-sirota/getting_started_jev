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

Extract: module statuses, open issues, locked decisions, NEXT ACTION.

## Step 3: Verify against the filesystem

```bash
ls -la course/module_* course/diagrams plans/modules 2>/dev/null
git log --oneline | head -5
```

- A file exists that progress.txt says is missing: update your understanding
- progress.txt says done but the file is missing, or a plan is newer than its notebooks: flag it

Do NOT re-run full validation.

## Step 4: Print orientation summary

```
=== RESUMED SESSION ===

Saved: <date>

MODULES
  1 Meet Jev   plan <s>  exercises <s>  solutions <s>  diagrams <s>  run <s>
  ...

OPEN ISSUES
  <list or "none">

NEXT ACTION
  <command>
  Reason: <one sentence>

KEY DECISIONS (active)
  - No slides: the class is the Colab notebook pair (exercises + solutions) per module
  - Module 1 opens with Part 0 "What is Jev"; every Part: problem, solution, demo, lab
  - Labs in three tiers (Guided, Core, Challenge optional)
  - Keys via env var or getpass; Jev decides judgments, code decides actions; OpenAI for text
  - Notebook diagrams: committed PNGs linked by raw GitHub URL
  - Notebook edits: id map before and after, order asserted

=== READY ===
```

## Step 5: At most one question

- NEXT ACTION obvious: confirm ready
- progress.txt conflicts with the filesystem: describe it and ask which is right

Do not build or fix anything until the user says "go" or "continue".
