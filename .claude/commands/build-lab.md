---
description: Build one module's lab (beat 4) - the Gradio app in course/apps/ and the "Lab:" section appended at the BOTTOM of the module's ONE notebook, cell_id verified before every insert
---

Build lab for module: $ARGUMENTS

(Argument is a module number, 1 to 10, except 7 which has no lab.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module$(printf %02d $ARGUMENTS)_plan.md course/harborview/__init__.py course/notebooks/module$(printf %02d $ARGUMENTS)_*.ipynb 2>/dev/null
```

- No plan: "Run `/research-module <N>` first."
- No harborview: "Run `/build-core` first."
- No module notebook: "Run `/build-demo <N>` first. The Lab section goes at its bottom."

## ONE NOTEBOOK PER MODULE (firm rule)

Outputs:
- `course/apps/lab<NN>_<slug_>.py`: the Gradio app. `<slug_>` is the slug with underscores
  instead of hyphens (e.g. `lab01_ai_literacy.py`) so the notebook can import it
- The **"Lab: <name>" section appended at the bottom** of
  `course/notebooks/module<NN>_<slug>.ipynb`. Never a separate lab notebook.

---

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md`
2. `plans/modules/module<NN>_plan.md`: the `# LAB` section (learner actions, app layout,
   behaviour, mock responses, lab notebook cells)
3. `course/harborview/` public API, especially `harborview.theme` (shared header, CSS,
   Gradio theme) and `harborview.launch` (shared-link launcher with the class login, `for_learner`)
4. The module notebook as built so far (print its cell map)
5. `reference/ai_for_pms/`: the app that inspired this lab, if the plan names one. Reuse
   its interaction ideas, not its code style or keys handling

### Show Plan Summary Before Building

In chat: the screens/tabs, every learner action in order, what is per-session, what goes
to Postgres (traces only), the mock story, and the Lab cells to append. **Wait for
approval** (skipped only under a blanket "go until the end", e.g. in the workflow).

---

## The app: `course/apps/lab<NN>_<slug_>.py`

- `build_app() -> gr.Blocks` plus `if __name__ == "__main__":` that calls
  `harborview.launch.launch(build_app(), lab_port(N))`. The notebook imports `build_app`
- Look: `harborview.theme` header and CSS on every app. Data Trainers brand (teal, navy,
  Inter, no rounded corners). Status colors always come with a word (APPROVED, ESCALATE,
  PASS, FAIL). Red practice-mode banner when `is_mock()`
- All agent, data, KB and memory calls go through `harborview`. No boto3, SQL or region
  strings in the app
- **Per-session state** (`gr.State`) for everything the learner edits: decision table,
  instructions, guardrails, toggles. Never write learner edits to shared tables
- **Shared links: one app serves the whole room.** Axel launches it and pastes the public
  link and class password in the chat. The FIRST control is a "Your name" textbox with the
  instruction "Type your first name so your results show as yours". Every handler that
  writes or reads per-learner data (traces, approvals, ratings, evals, "Just me" views,
  checkpoint thread ids) is wired as `for_learner(handler)` with the name box as its first
  input; inside it `participant_id()` returns the typed name (blank: `guest-<4 chars>`).
  Room views count distinct names
- Every agent run logs to `traces` with the participant id from `harborview.identity`
- **Change, rerun, compare**: every lab shows before and after side by side
- Plain-language labels and help text on every control; terms defined in the UI; free text
  boxes say "made-up details only"
- Works with `AGENT_MODE=mock`: the mock responses from the plan tell the same story
- Readable at 1280x720; short functions, docstrings, a comment atop each section

## The Lab section: appended to `course/notebooks/module<NN>_<slug>.ipynb`

Take the plan's "Lab notebook cells", DROP the lab's own title cell and setup cell (the
notebook already has them at the top), and append the rest after the demo's last cell:

```
## Lab: <name>                     markdown heading (exactly "## Lab: ..."; the validator
                                   looks for it), what you will do (no minutes), "from here you
                                   work on your own", Axel shares the link and password in the
                                   chat, type your first name, what to do if it fails. Learners
                                   never upload or run anything
Code: # Start the <name> app (Axel runs it)       from apps.lab<NN>_<slug_> import build_app;
                                   launch(build_app(), lab_port(N), title=...)
## Try it                          numbered steps from the plan's Learner actions
### What did you notice?           questions
## Key takeaways (lab)             one or two lines, then "Next module: ..."
```

Learners never edit a cell. If a step needs input, it is a widget in the app.

### Appending: ALWAYS verify cell_id first (Axel's rule)

1. Print the cell map (snippet in `build-demo.md`). Note the id of the LAST cell and assert
   its content is the demo's "Key takeaways" cell
2. Insert the first Lab cell AFTER that id; print the map again; assert it is now last
3. Chain: each next insert goes after the id you just verified is last
4. After the last insert: read the file back, assert the order (demo cells unchanged and in
   place, Lab heading after the demo takeaways), run `nbformat.validate`
5. Never rewrite cells by index; never touch the demo cells while appending

## Build order and checks

1. Write the app with Write (one file). Run
   `.venv/bin/python3 -m pyflakes course/apps/lab<NN>_<slug_>.py`
2. Import smoke in mock mode, no launch:
   `cd course && AGENT_MODE=mock ../.venv/bin/python3 -c "from apps.lab<NN>_<slug_> import build_app; build_app()"`
3. Handler smoke: call each event handler function directly with the plan's sample
   inputs in mock mode and assert the outputs match the mock story
4. Append the Lab section (5-cell rule, cell_id chaining above, Notebook Edit Protocol)
5. `.venv/bin/python3 validate_notebooks.py <N> --selfcheck` (checks the demo part above the
   Lab heading and the lab part below it)
6. Run `learner-noncoder-refute` on the app's labels and the Lab section. Fix BLOCKERs
7. Optional local click-through on request: `AGENT_MODE=mock`, open http://127.0.0.1:<port>
8. The app is part of the toolkit zip: run (or tell Axel to run)
   `AWS_PROFILE=datacouch .venv/bin/python3 data/setup_lab.py --package`

Update `plans/LABS.md` (Edit): lab `in_progress` then `done`. Hand off: "Lab done. Next:
`/build-diagrams <N>`."

## Not checked locally (Axel checks in a real space)

- The gradio.live link opens with the class login on a phone and a second browser, two names
- Live Bedrock behaviour matches the mock story
- 25 learners at once (Bedrock throttling)
