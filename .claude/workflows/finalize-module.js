export const meta = {
  name: 'finalize-module',
  description: 'Run the full module pipeline in order: core changes, demo, lab, diagrams, slides plan, deck, live check, review, commit',
  whenToUse: 'After /research-module N is approved, to build everything for module N end to end',
  phases: [
    { title: 'Shared changes', detail: 'only the shared-code tweaks this module plan lists (skipped if none)' },
    { title: 'Demo', detail: '/build-demo N' },
    { title: 'Lab', detail: '/build-lab N' },
    { title: 'Notebook diagrams', detail: '/build-diagrams N' },
    { title: 'Slides plan', detail: 'validate the approved slide plan (plans it only if missing)' },
    { title: 'Deck', detail: '/build-diagrams slides N + /build-slides N' },
    { title: 'Live check', detail: 'run demo and lab against real AWS via the tunnel' },
    { title: 'Review', detail: 'non-coder + deck reviewers, fix blockers' },
    { title: 'Commit', detail: 'final validation and git commit' },
  ],
}

const N = (args && args.module) ? args.module : 1
const NN = String(N).padStart(2, '0')
const PLAN = `plans/modules/module${NN}_plan.md`
// Slides-only module (Module 7: Axel demos a coding agent live, no notebook, no lab).
// Skips the Demo, Lab, Notebook diagrams and Live check stages.
const SLIDES_ONLY = !!(args && args.slidesOnly)

const RESULT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'failed'] },
    summary: { type: 'string' },
    files: { type: 'array', items: { type: 'string' } },
    issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['status', 'summary', 'files', 'issues'],
}

const COMMON = `
You work in /Users/axelsirota/repos/nwm_foundations_agentic_ai on Module ${N}. The approved
module plan is ${PLAN}. Axel gave blanket "go until the end" approval for this whole run: skip
every "ask the user / wait for approval" step in the repo commands, but NEVER skip validation.
Make exactly one tool call per response (no parallel tool calls). Use .venv/bin/python3 only.
Never use sed to edit files; use the Edit/Write tools. Follow .claude/NOTEBOOK_EDIT_PROTOCOL.md
for notebook edits. Learners upload only .ipynb files; the first code cell of every notebook is
course/setup_cell.py verbatim. Any AWS call uses AWS_PROFILE=datacouch (never the default
profile). Never delete AWS resources. No em dashes or en dashes anywhere you write.
Another module's workflow may run in parallel in this same working tree: before editing a
shared file (course/harborview/*, course/setup_cell.py, plans/LABS.md) read it fresh, change only
what this module needs, and never revert or overwrite another module's changes.
Return status "failed" with concrete issues if you cannot finish; do not pretend.`

async function stage(title, prompt) {
  phase(title)
  const r = await agent(`${COMMON}\n\nTASK:\n${prompt}`, { label: title, phase: title, schema: RESULT })
  if (!r) throw new Error(`${title}: agent returned nothing`)
  log(`${title}: ${r.status}. ${r.summary}`)
  if (r.status !== 'done') throw new Error(`${title} failed: ${r.issues.join('; ')}`)
  return r
}

const results = {}
try {
  results.core = await stage('Shared changes', `This is NOT /build-core (the shared toolkit already exists).
If the "## Core changes needed" section of ${PLAN} says "none" or every item is marked done,
return status "done" with summary "no shared changes" immediately. Otherwise apply every item
in that section that is not marked done (mock.py realignment with live behavior and canned answers for this module's exact
request texts, agent mock intents, setup_cell.py "Setup complete" print, etc). Then:
- .venv/bin/python3 -m pyflakes course/harborview data
- .venv/bin/python3 validate_notebooks.py --code
- .venv/bin/python3 validate_notebooks.py course/notebooks/00_start_here.ipynb --selfcheck
  (if setup_cell.py changed, first update the first code cell of 00_start_here.ipynb to match it exactly)
- mock smoke: in course/ with AGENT_MODE=mock, run every request text in the plan through
  build_chat() and build_agent(kb=True) and confirm the answers tell the plan's story
- re-upload the toolkit: AWS_PROFILE=datacouch .venv/bin/python3 data/setup_lab.py --package
Mark the applied items "(done)" in the plan's Core changes section.`)

  if (SLIDES_ONLY) log('Slides-only module: skipping Demo, Lab, Notebook diagrams and Live check')
  if (!SLIDES_ONLY) results.demo = await stage('Demo', `ONE NOTEBOOK PER MODULE (Axel's firm rule): the module has a single
notebook course/notebooks/module${NN}_<slug>.ipynb; demo on top, "## Lab: <name>" section at
the bottom. Never create separate demo/lab notebooks. If the plan's headings say "DEMO NOTEBOOK"
or name demo${NN}/lab${NN} files, still build ONE module notebook.
Run the repo command .claude/commands/build-demo.md for module ${N} (read it and follow it
exactly, minus the approval pauses): build the TOP part of course/notebooks/module${NN}_<slug>.ipynb
cell by cell from the plan's demo section, printing the cell map and verifying cell_id before
every insert, validating after every 5 cells (before the Lab section exists the validator
reports "no Lab section": expected). Create plans/LABS.md from .claude/commands/start-session.md
if missing and set this module's demo to done.`)

  if (!SLIDES_ONLY) results.lab = await stage('Lab', `Run the repo command .claude/commands/build-lab.md for module ${N}
(follow it exactly, minus approval pauses). If the plan says the module has no lab, return done
with summary "no lab". Otherwise build course/apps/lab${NN}_<slug_with_underscores>.py and APPEND
the "## Lab: <name>" section at the BOTTOM of course/notebooks/module${NN}_<slug>.ipynb (the same
notebook the Demo stage built): drop the plan's lab title and setup cells, print the cell map,
verify the last cell is the demo's key takeaways, insert after its cell_id, chain cell_ids, read
back and assert the demo cells are unchanged and in order. Verify: pyflakes on the app, mock
import smoke (build_app()), call every event handler directly in mock mode with the plan's inputs
and check outputs match the plan's mock story, validate_notebooks.py ${N} --selfcheck (must PASS,
diagram placeholders may warn), validate_notebooks.py --code. Then re-upload the toolkit:
AWS_PROFILE=datacouch .venv/bin/python3 data/setup_lab.py --package. Update plans/LABS.md.`)

  if (!SLIDES_ONLY) results.ndiagrams = await stage('Notebook diagrams', `Run .claude/commands/build-diagrams.md for module ${N}
(notebook diagrams only, minus approval pauses), using .claude/skills/mermaid-diagrams/SKILL.md.
For each slug in the plan's "## Diagram Index" that a notebook cell references: write
course/diagrams/<slug>.mmd, render the PNG with
cd deck && npx mmdc -i ../course/diagrams/<slug>.mmd -o ../course/diagrams/<slug>.png -w 1600 -b white -c tools/mermaid-config.json,
look at the PNG with the Read tool to check it is legible, then embed it in the notebook cell(s)
as a cell attachment (![title](attachment:<slug>.png), base64 PNG in the cell's attachments),
keeping the <!-- DIAGRAM: --> comment. If the plan's demo cells have no placeholder for a diagram,
add the image to the markdown cell the Diagram Index names. Finish with
validate_notebooks.py <N> --selfcheck --strict (must PASS) and validate_slides.py --render.`)

  results.slidesplan = await stage('Slides plan', `FIRST check whether imp_files/slides/module${NN}_slides.md
and imp_files/slides/module${NN}_diagrams.md already exist. If they do, Axel already approved
them through /research-module: DO NOT rewrite or re-plan them. Only run
.venv/bin/python3 validate_slides.py ${N}; if it fails, make the smallest fix that keeps the
approved content (format only), and return done with summary "approved slide plan validated".
ONLY if they do not exist: run .claude/commands/plan-slides.md for module ${N}
(follow it exactly, minus the approval wait). Research every factual claim with web search and
cite it; verify any study figure against the primary source before using it. Use the plan's
"## Slide hooks", "## Debrief questions", the demo and lab cells as built, and
reference/slide_plan.reference.md for format and density. Write
imp_files/slides/module${NN}_slides.md and imp_files/slides/module${NN}_diagrams.md (create
imp_files/slides/ if needed). ${N === 1 ? 'Module 1 deck also opens the day: title slide (Northwestern Mutual may appear only there), agenda, meet Harborview Life.' : ''}
Then run the review agents deck-sales-refute, deck-marketing-refute, deck-diagram-refute,
deck-designer-refute and learner-noncoder-refute on the files (via the Agent tool, one at a time),
fix every BLOCKER and MAJOR, and run .venv/bin/python3 validate_slides.py ${N} until it PASSES.`)

  results.deck = await stage('Deck', `Run .claude/commands/build-diagrams.md "slides ${N}" and then
.claude/commands/build-slides.md for module ${N} (follow both exactly, minus approval pauses; build
all slides, batches of 5 with screenshots between). Output deck/module${NN}/index.html linking the
shared ../css and ../vendor assets, deck/module${NN}/diagrams/*.svg, notes.md, BUILD_REPORT.md.
Every deck tool needs DECK_MODULE=${N}. Check screenshots with
cd deck && DECK_MODULE=${N} node tools/shoot.mjs <slides> and read the PNGs; diagram text must be
at least 22 px at 1920x1080 (use the big-diagram rule otherwise). Then
.venv/bin/python3 validate_slides.py ${N} --render (must PASS). Then PACKAGE the deck (Axel needs
a PDF to distribute and a deck he can present from anywhere):
cd deck && DECK_MODULE=${N} node tools/package-deck.mjs
It writes deck/module${NN}/Agentic-AI-Foundations-Module-${NN}.pdf, the self-contained folder
deck/dist/module${NN}/ and deck/dist/Agentic-AI-Foundations-Module-${NN}.zip. Read 2 or 3 PDF pages
with the Read tool to confirm they render (brand colors, diagrams, slide numbers). Return the
PDF and zip paths in the summary.`)

  if (!SLIDES_ONLY) results.live = await stage('Live check', `Verify the module against REAL AWS (read plans/lab_environment.md).
1. Open the SSM port-forward tunnel to RDS on THIS module's own local port ${15430 + N} (other
   modules may run in parallel on other ports) in the background with AWS_PROFILE=datacouch
   (command in plans/lab_environment.md, with localPortNumber ${15430 + N}), wait for the port.
2. In course/ with AWS_PROFILE=datacouch HARBORVIEW_DB_HOST=127.0.0.1 HARBORVIEW_DB_PORT=${15430 + N}
   HARBORVIEW_PARTICIPANT=instructor-check AGENT_MODE=live, execute the module notebook
   course/notebooks/module${NN}_*.ipynb headless (nbclient, %pip lines removed, cwd
   course/notebooks) and check every cell runs, the demo part shows the plan's live story
   (each plan claim: present or not) and the Lab section's launch cell starts the app; then
   call the lab app's handlers directly with the plan's inputs in live mode.
3. Close ONLY this module's tunnel: kill the background shell you started (or pkill -f with
   "${15430 + N}" in the pattern), never all port-forward sessions; confirm port ${15430 + N} is closed.
Report any place where live behavior differs from the plan; if a difference breaks the teaching
point, fix the notebook/app (and mock) so it holds, re-validate with --selfcheck, and re-upload the
toolkit with --package. Never stage a fake result.`)

  // Workflow subagents have no Agent tool, so the script launches the reviewer personas itself.
  phase('Review')
  const BUILT = SLIDES_ONLY
    ? `imp_files/slides/module${NN}_slides.md, imp_files/slides/module${NN}_diagrams.md, deck/module${NN}/notes.md
and the screenshots in deck/module${NN}/checks/*.png (read the PNGs) in
/Users/axelsirota/repos/nwm_foundations_agentic_ai. This module is SLIDES ONLY (Axel demos a coding agent
live in his editor): there is no notebook and no lab app, which is correct, not a finding`
    : `course/notebooks/module${NN}_*.ipynb (ONE notebook: demo on top, Lab section at the bottom),
course/apps/lab${NN}_*.py, imp_files/slides/module${NN}_slides.md, imp_files/slides/module${NN}_diagrams.md
and the screenshots in deck/module${NN}/checks/*.png (read the PNGs) in
/Users/axelsirota/repos/nwm_foundations_agentic_ai`
  const NB_CHECK = SLIDES_ONLY
    ? '(slides-only module: skip validate_notebooks.py for this module; there is no notebook)'
    : `validate_notebooks.py ${N} --selfcheck --strict,`
  const personas = [
    ['learner-noncoder-refute', 'the notebooks (as the instructor shows them and as a learner runs the lab), the lab app labels and flow, and the slides'],
    ['deck-designer-refute', 'the deck screenshots and the slide plan'],
    ['deck-diagram-refute', 'every slide diagram (screenshots and mermaid in the diagrams file) and the notebook diagrams in course/diagrams'],
  ]
  const reviews = await parallel(personas.map(([type, scope]) => () =>
    agent(`Review Module ${N} as built. Files: ${BUILT}. Focus: ${scope}. Output your ranked table of findings (BLOCKER, MAJOR, MINOR) with where, what and a one-line fix.`,
      { label: `review:${type}`, phase: 'Review', agentType: type })))
  const findings = personas.map(([type], i) => `### ${type}\n${reviews[i] || '(no output)'}`).join('\n\n')

  results.review = await stage('Review', `Apply the reviewer findings below to everything built for module ${N}:
${BUILT}.
Fix every BLOCKER and every MAJOR you agree with; list the ones you reject and why (approved plan
content may only change to fix a real defect). Re-run
${NB_CHECK} validate_slides.py ${N} --render, and rebuild any
changed slides (and re-upload the toolkit if course/harborview, course/apps or course/kb_docs
changed). Every check must PASS.

REVIEWER FINDINGS:
${findings}`)

  results.commit = await stage('Commit', `Final gate and commit for module ${N}:
Other modules may be building in parallel in the same working tree: validate and commit ONLY
this module's files plus shared files this run changed.
- ${SLIDES_ONLY ? '(slides-only module: no module notebook to validate; LABS.md demo/lab/diagrams = "n/a, live demo")' : `.venv/bin/python3 validate_notebooks.py ${N} --selfcheck --strict    (must PASS)`}
- .venv/bin/python3 validate_notebooks.py course/notebooks/00_start_here.ipynb --selfcheck (must PASS)
- .venv/bin/python3 validate_notebooks.py --code                       (must PASS)
- .venv/bin/python3 validate_slides.py ${N} --render                   (must PASS)
- scan this module's files for em dashes, en dashes and denylisted names (validation/denylist.txt)
- update plans/LABS.md (Edit, only module ${N}'s row): demo, lab, diagrams, slides planned,
  slides built = done
- git add ONLY: course/notebooks/module${NN}_* course/apps/lab${NN}_*
  course/diagrams/ imp_files/slides/module${NN}_* deck/module${NN}/ plans/modules/module${NN}_plan.md
  plans/LABS.md (never plans/lab_environment.md; deck/module${NN}/checks/ is ignored) and any shared file this
  run changed (course/harborview/, course/setup_cell.py, course/notebooks/00_start_here.ipynb,
  course/kb_docs/, course/requirements.txt, validate_*.py, data/). Never git add -A. Never stage
  another module's files. git commit with message "Module ${N}: demo, lab, diagrams and deck"
  ending with the line "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Do not push.
  If git reports a lock (index.lock) because another module is committing, wait 30 s and retry.
Return the commit hash in the summary.`)
} catch (e) {
  log(`Stopped: ${e.message}`)
  return { stoppedAt: String(e.message), completed: Object.keys(results), results }
}

return { completed: Object.keys(results), results }
