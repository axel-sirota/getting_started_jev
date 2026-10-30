---
description: Build one module end to end from its approved plan by running the build-module workflow (shared changes, exercises, solutions, diagrams, live check, review, commit)
---

Build module: $ARGUMENTS

(Argument is a module number, 0 to 8. Required. Module 0 builds `course/module_00/start_here.ipynb`.)

## GUARD

```bash
N=$(printf %02d $ARGUMENTS)
ls plans/DECISIONS.md plans/modules/module_${N}_plan.md data/00_lab_setup.ipynb 2>/dev/null
ls course/module_${N}/*.ipynb 2>/dev/null
```

- No plan: stop, "Run `/research-module <N>` first and approve it."
- Notebooks already exist: stop and ask Axel whether to rebuild (the workflow never
  overwrites an existing notebook).
- Another module's workflow running: one module at a time (shared files in `data/`).

## Run

Calling `/build-module N` is Axel's opt-in to the workflow. Run:

```
Workflow  scriptPath=.claude/workflows/build-module.js  args={"module": <N>}
```

Report the run id and tell Axel progress is visible in `/workflows`. When the completion
notification arrives, summarize per stage (status, files, issues) and the commit hash, and
list the solution cells Axel must run in his instructor Studio space (modules 3+).

If a stage fails, report it and stop. Fix, then resume with `resumeFromRunId` so finished
stages are not rerun.
