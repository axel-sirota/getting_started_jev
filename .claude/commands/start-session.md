---
description: Begin a work session - load context, review per-module progress, identify next steps
---

Start a new work session for this course.

## GUARD

```bash
ls plans/DECISIONS.md 2>/dev/null
```

If missing: "`plans/DECISIONS.md` not found. Run `/init-course` first."

## Step 1: Load context

Run `/read` (CLAUDE.md, DECISIONS, TEACHING_STYLE, NOTEBOOK_STYLE, outline, jev-course skill).

## Step 2: Load plans/LABS.md (status tracker)

If it does NOT exist, create it:

```markdown
# Course Status

## Modules
| # | Module | Plan | Exercises | Solutions | Diagrams | Run in order | Committed |
|---|---|---|---|---|---|---|---|
| 1 | Meet Jev | not_started | | | | | |
| 2 | Designing Good Questions | not_started | | | | | |
| 3 | Measuring and Trusting Jev | not_started | | | | | |
| 4 | Jev and LLMs Together | not_started | | | | | |

## Open issues
- none
```

## Step 3: Cross-check the filesystem

```bash
ls -la course/module_* course/diagrams plans/modules 2>/dev/null
git log --oneline | head -10
```

Flag anything on disk but `not_started`, `done` but missing, or a plan newer than its notebooks.

## Step 4: Report

The LABS.md table plus mismatches and open issues.

## Step 5: Recommend next step

| State | Next |
|---|---|
| No module plan | `/research-module N` (1 to 4) |
| Plan approved, notebooks or deck missing | `/build-module N` (runs the workflow) |
| One stage failed | fix with `/build-notebook` or `/build-diagrams`, then resume the workflow |
| Diagram missing in Colab | push the repo (PNGs are linked by raw GitHub URL) |

## Step 6: Ask

"Ready to proceed with <next step>? Or something else?"
