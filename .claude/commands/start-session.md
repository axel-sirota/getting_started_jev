---
description: Begin a work session - load context, review core and per-module progress, identify next steps
---

Start a new work session for this course.

## GUARD

```bash
ls plans/DECISIONS.md 2>/dev/null
```

If missing: "`plans/DECISIONS.md` not found. Run `/init-course` first."

## Step 1: Load context

Run `/read` (CLAUDE.md, DECISIONS, TEACHING_STYLE, NOTEBOOK_STYLE, CONTENT_SOURCES, outline,
lab_environment, skill).

## Step 2: Load plans/LABS.md (status tracker)

If it does NOT exist, create it:

```markdown
# Course Status

## Core
| Piece | Status |
|---|---|
| Postgres schema + seed (loan_requests, reader and writer roles) | not_started |
| data/00_lab_setup.ipynb run in the instructor space (shared Memory, Cognito, deps zip, shared.json) | not_started |
| validate_notebooks.py (static checks, pair) | not_started |

## Modules
| # | Module | Plan | Exercises | Solutions | Diagrams | Live check | Committed |
|---|---|---|---|---|---|---|---|
| 0 | Start here (start_here.ipynb) | not_started | | n/a | | | |
| 1 | Agentic foundations, coding agents | not_started | | | | | |
| 2 | Single agent in LangGraph | not_started | | | | | |
| 3 | AgentCore Runtime | not_started | | | | | |
| 4 | Tools, MCP, Gateway | not_started | | | | | |
| 5 | RAG, Bedrock KB | not_started | | | | | |
| 6 | Memory and state | not_started | | | | | |
| 7 | Multi-agent, HITL | not_started | | | | | |
| 8 | Eval, guardrails, observability | not_started | | | | | |

## Open issues
- none
```

## Step 3: Cross-check the filesystem

```bash
ls -la course/module_* course/diagrams data plans/modules 2>/dev/null
git log --oneline | head -10
```

Flag anything on disk but `not_started`, `done` but missing, or a plan newer than its notebooks.

## Step 4: Report

The LABS.md tables plus mismatches and open items from `plans/lab_environment.md`.

## Step 5: Recommend next step

| State | Next |
|---|---|
| Core (schema, `data/00_lab_setup.ipynb`, validator) not done | `/build-core` |
| No module plan | `/research-module N` (0 to 8) |
| Plan approved, notebooks missing | `/build-module N` (runs the workflow) |
| Live check lists cells for the instructor space | Axel runs `solutions.ipynb` in his instructor Studio space |
| One stage failed | `/build-notebook N exercises\|solutions` or `/build-diagrams N`, then resume the workflow |
| Diagram shows as raw code | fix the ```mermaid block (brand line, syntax), re-check with mmdc |

## Step 6: Ask

"Ready to proceed with <next step>? Or something else?"
