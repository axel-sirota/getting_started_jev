---
description: Build one module's notebook pair end to end from its approved plan by running the build-module workflow (exercises, solutions, diagrams, validate, run in order against the real APIs, review, commit). Notebook-only class, 4 beats per Part
---

Build module: $ARGUMENTS

(Argument is a module number, 1 to 4. Required.)

## GUARD

```bash
N=$(printf %02d $ARGUMENTS)
ls plans/DECISIONS.md plans/modules/module_${N}_plan.md 2>/dev/null
ls course/module_${N}/*.ipynb 2>/dev/null
grep -qE '^(export )?(TYPESAFE_API_KEY|JEV_AI_API_KEY)=' .env && grep -qE '^(export )?OPENAI_API_KEY=' .env && echo "keys in .env" || echo "keys MISSING in .env"
```

- No plan: stop, "Run `/research-module <N>` first and approve it."
- Notebooks already exist: stop and ask Axel whether to rebuild (the workflow never
  overwrites an existing notebook).
- Keys missing in `.env`: the "Run in order" stage will stop. Ask Axel to add them to the
  gitignored `.env` (never paste them in chat).
- One module at a time.

## Run

Calling `/build-module N` is Axel's opt-in to the workflow. Commit or tag a restore point
first, then run:

```
Workflow  scriptPath=.claude/workflows/build-module.js  args={"module": <N>}
```

Stages, in order: Exercises, Solutions, Diagrams, Validate, Run in order, Review
(learner-engineer, diagram reviewer, a beat walk), Commit.

Report the run id and tell Axel progress is visible in `/workflows`. When the completion
notification arrives, summarize per stage (status, files, issues) and the commit hash, and
remind Axel to push so the diagram PNGs show in Colab.

If a stage fails, report it and stop. Fix, then resume with `resumeFromRunId` so finished
stages are not rerun.
