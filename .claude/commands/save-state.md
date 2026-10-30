---
description: Snapshot course build state to progress.txt so a new session can resume exactly where the build stopped
---

# /save-state

Snapshot the current session into `progress.txt` (repo root, gitignored) so `/resume` in a
new conversation continues with zero context loss.

## Step 1: Read state sources (one at a time, never batched)

- `plans/LABS.md`
- `plans/DECISIONS.md`
- `plans/lab_environment.md` (open items)

Then:

```bash
ls -la course/module_* course/diagrams data plans/modules 2>/dev/null
.venv/bin/python3 validate_notebooks.py --all
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
| Both validate, pair passes, diagrams embedded | `notebooks_done` |
| Live check passed, reviewed, committed | `done` |
| Any validation failure or open TODO | `needs_fix` |

## Step 3: Next action

Core first if not verified, then the first module not `done`: `/research-module N`,
`/build-module N`, `/build-notebook N exercises|solutions`, `/build-diagrams N`, or the fix.

## Step 4: Write progress.txt

```
COURSE: Developing in Agentic AI Systems, Engineering Track
SAVED: <YYYY-MM-DD HH:MM>
REPO: /Users/axelsirota/repos/nwm_foundations_agentic_ai_engineering

==============================================================================
CORE
==============================================================================

schema: <status>   00_lab_setup (shared.json): <status>   validator: <status>

==============================================================================
MODULES (exercises.ipynb + solutions.ipynb per module)
==============================================================================

[done]       Module 1 - Agentic foundations and coding agents
             plan: plans/modules/module_01_plan.md
             notebooks: course/module_01/exercises.ipynb (<n> cells), solutions.ipynb (<n> cells)
             diagrams: <slugs>   commit: <hash>

[building]   Module 2 - Single agent in LangGraph
             next: /build-module 2

==============================================================================
OPEN ISSUES AND UNVERIFIED ITEMS
==============================================================================

<entries from LABS.md and lab_environment.md, or "none">

==============================================================================
LOCKED DECISIONS (do not re-litigate without Axel)
==============================================================================

- Engineers code: exercises.ipynb with one # LAB N cell per lab (# YOUR CODE slots),
  FALLBACK cells only where needed, solutions.ipynb solved. No CHECK cells, no mini exercises.
- No slides. Theory in notebook markdown, Mermaid as inline ```mermaid blocks (JupyterLab renders).
- Demo and lab structure = bread weeks 16 to 19 (plans/NOTEBOOK_STYLE.md); the concierge
  workshop is ideas and voice only (plans/TEACHING_STYLE.md).
- Learners upload ONLY .ipynb files. Frameworks only, no harborview package, no toolkit zip.
  Cell 1 pinned %pip install; then a visible CONFIG cell (regions, MODEL_ID, STUDENT_NAME,
  shared.json). Every AWS call, query, deploy and launch is a visible cell.
- Bedrock Claude Haiku 4.5. MODEL_REGION us-east-1 (model, KB); AGENTCORE_REGION us-west-2
  (AgentCore, Gateway, Memory, Guardrails, Cognito, logs, X-Ray).
- LangGraph; AgentCore Runtime per learner with the lab role; Gateway + Identity; Memory;
  Postgres camula; Bedrock KB on S3 Vectors; Bedrock Guardrails; AgentCore Observability.
- Gradio over the learner's own agent; no mock mode; nothing blocks. Live check: modules 1,
  2, 5 from the laptop, modules 3+ by Axel in the instructor space.
- Notebook edits: id map BEFORE and AFTER every edit, order asserted.

==============================================================================
NEXT ACTION
==============================================================================

<one runnable command>
Reason: <one sentence>

==============================================================================
HOW TO RESUME
==============================================================================

1. Open /Users/axelsirota/repos/nwm_foundations_agentic_ai_engineering
2. Run /resume
3. If /resume is unavailable, read this file and run the NEXT ACTION.
```

## Step 5: Confirm

```
progress.txt written.
  core: <status>   modules: <n> done, <n> building, <n> not started
Next action: <command>
```

## Non-Negotiables

- Real paths only, no placeholders
- NEXT ACTION is one runnable command
- Every module listed, even `not_started`
- Plain text, no markdown, no emoji
