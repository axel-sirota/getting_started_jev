---
description: Build one module end to end from its approved plans by running the build-module workflow (exercises, solutions, notebook diagrams, validate notebooks, run in order, slides plan, deck, validate slides, review, commit)
---

Build module: $ARGUMENTS

(Argument is a module number, 1 to 4. Required.)

## GUARD

```bash
N=$(printf %02d $ARGUMENTS)
ls plans/DECISIONS.md plans/modules/module_${N}_plan.md imp_files/slides/module${N}_slides.md imp_files/slides/module${N}_diagrams.md 2>/dev/null
ls course/module_${N}/*.ipynb deck/module${N}/index.html 2>/dev/null
test -n "$TYPESAFE_API_KEY" && echo "jev key set" || echo "jev key MISSING"
test -n "$OPENAI_API_KEY" && echo "openai key set" || echo "openai key MISSING"
```

- No plan or no slide plan: stop, "Run `/research-module <N>` first and approve it."
- Notebooks or deck already exist: stop and ask Axel whether to rebuild (the workflow never
  overwrites an existing notebook).
- A key missing: the "Run in order" stage will stop. Ask Axel to export it in the shell that
  runs Claude Code (never paste it in chat).
- One module at a time.

## Run

Calling `/build-module N` is Axel's opt-in to the workflow. Run:

```
Workflow  scriptPath=.claude/workflows/build-module.js  args={"module": <N>}
```

Stages, in order: Exercises, Solutions, Notebook diagrams, Validate notebooks, Run in order,
Slides plan, Deck, Validate slides, Review (learner-engineer, deck designer, marketing,
diagram reviewers and a flow walk), Commit.

Report the run id and tell Axel progress is visible in `/workflows`. When the completion
notification arrives, summarize per stage (status, files, issues), the PDF path and the
commit hash, and remind Axel to push so the notebook diagram PNGs show in Colab.

If a stage fails, report it and stop. Fix, then resume with `resumeFromRunId` so finished
stages are not rerun.
