---
description: Snapshot course build state to progress.txt so a new session can resume exactly where the build stopped
---

# /save-state

Snapshot the current session into `progress.txt` (repo root, gitignored) so `/resume` in a
new conversation continues with zero context loss.

## Step 1: Read state sources (one at a time, never batched)

- `plans/LABS.md`
- `plans/DECISIONS.md`

Then:

```bash
ls -la course/module_* course/diagrams imp_files/slides deck/module* plans/modules 2>/dev/null
.venv/bin/python3 validate_notebooks.py --all
.venv/bin/python3 validate_slides.py
git log --oneline | head -5
```

Cell count per notebook:

```bash
for f in course/module_*/*.ipynb; do .venv/bin/python3 -c "
import json, sys
nb = json.load(open(sys.argv[1]))
print(sys.argv[1], 'cells:', len(nb['cells']))
" "$f"; done 2>/dev/null
```

## Step 2: Status per module

| Signal | Status |
|---|---|
| No plan | `not_started` |
| Plan not approved | `planned` |
| Exercises or solutions missing or partial | `building` |
| Both validate, pair passes, diagrams rendered | `notebooks_done` |
| Deck built, slides validate (incl. hops) | `deck_done` |
| Ran in order, reviewed, committed | `done` |
| Any validation failure or open TODO | `needs_fix` |

## Step 3: Next action

The first module not `done`: `/research-module N`, `/build-module N`,
`/build-notebook N exercises|solutions`, `/build-diagrams N`, `/build-slides N`, or the fix.

## Step 4: Write progress.txt

```
COURSE: Getting Started with Jev
SAVED: <YYYY-MM-DD HH:MM>
REPO: /Users/axelsirota/repos/getting_started_jev

==============================================================================
MODULES (exercises.ipynb + solutions.ipynb + deck per module)
==============================================================================

[done]       Module 1 - Meet Jev: Typed Decisions Instead of Text
             plan: plans/modules/module_01_plan.md
             notebooks: course/module_01/exercises.ipynb (<n> cells), solutions.ipynb (<n> cells)
             deck: deck/module01/index.html (<n> slides)   diagrams: <slugs>   commit: <hash>

[building]   Module 2 - Designing Good Questions
             next: /build-module 2

==============================================================================
OPEN ISSUES AND UNVERIFIED ITEMS
==============================================================================

<entries from LABS.md, or "none">

==============================================================================
LOCKED DECISIONS (do not re-litigate without Axel)
==============================================================================

- Colab notebooks: exercises.ipynb and solutions.ipynb per module. Keys via env var or
  getpass, never Colab secrets. Cell 1 pinned %pip, then KEYS, then CONFIG.
- Labs in three tiers: LAB n.1 (Guided) slots, LAB n.2 (Core) function body,
  LAB n.3 (Challenge, optional), nothing later depends on Level 3. FALLBACK only where needed.
- Slides like the nwm Foundations decks, diagram first. Hops: badge "Switch to the notebook:
  Demo n / Lab n", notebook "## Back to the slides: <next slide title>".
- Notebook diagrams: .mmd master + committed PNG linked by raw GitHub URL (Colab renders
  neither mermaid nor attachments).
- Jev for every decision, OpenAI for every text generation. Judgments in Jev, decisions in code.
- Web research with built-in WebSearch/WebFetch only; Jev facts from official TypeSafe sources.
- Notebook edits: id map BEFORE and AFTER every edit, order asserted.

==============================================================================
NEXT ACTION
==============================================================================

<one runnable command>
Reason: <one sentence>

==============================================================================
HOW TO RESUME
==============================================================================

1. Open /Users/axelsirota/repos/getting_started_jev
2. Run /resume
3. If /resume is unavailable, read this file and run the NEXT ACTION.
```

## Step 5: Confirm

```
progress.txt written.
  modules: <n> done, <n> building, <n> not started
Next action: <command>
```

## Non-Negotiables

- Real paths only, no placeholders
- NEXT ACTION is one runnable command
- Every module listed, even `not_started`
- Plain text, no markdown, no emoji
