export const meta = {
  name: 'build-module',
  description: 'Build one module from its approved plans: exercises, solutions, diagrams, validate, run in order, slides, deck, validate, review, commit',
  whenToUse: 'After /research-module N is approved; triggered by /build-module N',
  phases: [
    { title: 'Exercises', detail: '/build-notebook N exercises (three-tier labs, slide hops)' },
    { title: 'Solutions', detail: '/build-notebook N solutions' },
    { title: 'Notebook diagrams', detail: '/build-diagrams N: .mmd -> PNG, raw GitHub links' },
    { title: 'Validate notebooks', detail: 'validate_notebooks.py N --pair --strict' },
    { title: 'Run in order', detail: 'execute solutions.ipynb top to bottom against real Jev and OpenAI' },
    { title: 'Slides plan', detail: 'validate the approved slide plan (plans it only if missing)' },
    { title: 'Deck', detail: '/build-diagrams slides N + /build-slides N + PDF' },
    { title: 'Validate slides', detail: 'validate_slides.py N --render, incl. slides vs notebook hops' },
    { title: 'Review', detail: 'learner-engineer, deck reviewers and a flow walk; fix blockers' },
    { title: 'Commit', detail: 'final validation and git commit' },
  ],
}

const N = (args && args.module !== undefined) ? args.module : 1
const NN = String(N).padStart(2, '0')
const REPO = '/Users/axelsirota/repos/getting_started_jev'
const PLAN = `plans/modules/module_${NN}_plan.md`
const DIR = `course/module_${NN}`
const SLIDES = `imp_files/slides/module${NN}_slides.md`
const SLIDE_DIAGRAMS = `imp_files/slides/module${NN}_diagrams.md`

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
You work in ${REPO} on Module ${N} of Getting Started with Jev. The approved plans are
${PLAN} (notebooks, Flow table) and ${SLIDES} + ${SLIDE_DIAGRAMS} (slides); build from them,
never re-plan them. Read CLAUDE.md, plans/DECISIONS.md, plans/NOTEBOOK_STYLE.md,
plans/TEACHING_STYLE.md and .claude/skills/jev-course/SKILL.md first; load the typesafe-ai
skill before touching any Jev call. Axel gave blanket "go until the end" approval for this run:
skip every "ask the user / wait for approval" step in the repo commands, but NEVER skip
validation. Make exactly one tool call per response (no parallel tool calls). Use
.venv/bin/python3 only. Never use sed; edit with the Edit/Write tools. Web research uses the
built-in WebSearch / WebFetch only, never Kryla web tools; Jev facts come only from
docs.typesafe.ai, typesafe.ai or github.com/typesafe-ai. Follow .claude/NOTEBOOK_EDIT_PROTOCOL.md
for every notebook edit: print the id map BEFORE, write the expected order, print the id map
AFTER and assert it (cells can land out of order silently). Learners run the notebooks in
Google Colab: first code cell is the pinned %pip install, then # KEYS (TYPESAFE_API_KEY and,
where needed, OPENAI_API_KEY from os.environ, else getpass; never Colab secrets, never
printed, never literal), then # CONFIG (client, pinned model ids, a probe). Every Jev and
OpenAI call is a visible cell. Labs have three cells: # LAB n.1 (Guided) with
"name = None  # YOUR CODE" slots, # LAB n.2 (Core) with a "# YOUR CODE" function body,
# LAB n.3 (Challenge, optional) that nothing later depends on. Slide hops: "## Demo n" /
"## Lab n" sections close with "## Back to the slides: <exact next slide title>", matching the
slide badges "Switch to the notebook: Demo n / Lab n". Notebook diagrams: .mmd master in
course/diagrams/module_${NN}/ (brand line first), its PNG committed next to it, linked in the
notebook by raw GitHub URL (RAW_BASE in validate_notebooks.py); never a mermaid block or an
attachment in a notebook. No em dashes or en dashes anywhere you write. Return status
"failed" with concrete issues if you cannot finish; never pretend.`

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
  results.exercises = await stage('Exercises', `Run the repo command .claude/commands/build-notebook.md
with arguments "${N} exercises" (read it and follow it exactly, minus approval pauses). Build
${DIR}/exercises.ipynb cell by cell from the plan's "# EXERCISES" section, 5 cells per batch,
validating after each batch with .venv/bin/python3 validate_notebooks.py ${N}. Every helper a
cell uses must be defined in a visible cell above it. Create plans/LABS.md if missing and set
this module's exercises to done.`)

  results.solutions = await stage('Solutions', `Run .claude/commands/build-notebook.md with arguments
"${N} solutions" (follow it exactly, minus approval pauses): copy exercises.ipynb to
${DIR}/solutions.ipynb, replace each "# LAB n.k" cell with the plan's "# SOLUTION: LAB n.k"
source by cell id, delete every "# FALLBACK" cell. Verify: validate_notebooks.py ${N} --pair
(must PASS). Update plans/LABS.md.`)

  results.ndiagrams = await stage('Notebook diagrams', `Run .claude/commands/build-diagrams.md for module ${N}
(notebook diagrams only, minus approval pauses), using .claude/skills/mermaid-diagrams/SKILL.md.
For each slug in the plan's "## Diagram Index": make sure course/diagrams/module_${NN}/<slug>.mmd
exists and starts with the brand line, render it with
cd deck && npx mmdc -i ../course/diagrams/module_${NN}/<slug>.mmd -o ../course/diagrams/module_${NN}/<slug>.png -w 1600 -b white -c tools/mermaid-config.json
and look at the PNG with the Read tool (legible, labels match the code). Any fix goes into
the .mmd and is re-rendered. Both notebooks link the same PNG by raw GitHub URL in a
"<!-- DIAGRAM: <slug> -->" cell. Finish with validate_notebooks.py ${N} --pair --strict (must PASS).`)

  results.vnotebooks = await stage('Validate notebooks', `Run
.venv/bin/python3 validate_notebooks.py ${N} --pair --strict
and fix every FAIL in BOTH notebooks (pair rule) with the Notebook Edit Protocol, until it
PASSES. Then confirm by reading the cell maps that the order matches the plan: title, %pip,
KEYS, CONFIG, data, then per concept Demo n, its cells, Think About It, Back to the slides,
then Lab n, LAB n.1, n.2, n.3, optional FALLBACK (exercises only), Back to the slides,
Summary. Report any order difference you fixed.`)

  results.run = await stage('Run in order', `Execute the solutions notebook top to bottom against the
REAL Jev and OpenAI APIs. TYPESAFE_API_KEY and OPENAI_API_KEY must be in the environment of
your shell; if either is missing return "failed" with issue "Axel: export TYPESAFE_API_KEY and
OPENAI_API_KEY and rerun from this stage" (never ask for the key in chat, never write it to a
file). Work on a scratch copy of ${DIR}/solutions.ipynb in the session scratchpad (never the
committed file), drop the %pip lines (the venv has course/requirements.txt), and execute it
headless with nbclient (timeout 600 per cell) so getpass is skipped because the env vars are
set. Every cell must run without error. Check each claim in the plan's "## Measured numbers"
and "## Run in order" still holds (report the numbers you saw). Then run the exercises
notebook the same way with FALLBACK cells kept: it must run up to the first LAB cell without
error. If a difference breaks the teaching point, fix BOTH notebooks so it holds and re-run
validate_notebooks.py ${N} --pair --strict. Never stage a fake result.`)

  results.slidesplan = await stage('Slides plan', `FIRST check whether ${SLIDES} and ${SLIDE_DIAGRAMS}
already exist. If they do, Axel already approved them through /research-module: DO NOT rewrite
or re-plan them. Only run .venv/bin/python3 validate_slides.py ${N}; if it fails, make the
smallest fix that keeps the approved content (format, or a hop label or slide title the
notebooks as built need), and return done with summary "approved slide plan validated".
ONLY if they do not exist: run .claude/commands/plan-slides.md for module ${N} (follow it
exactly, minus the approval wait), using the plan's "## Flow", "## Slide hooks" and
"## Measured numbers" and the notebooks as built. Diagram first: every concept slide has one
Mermaid diagram that carries the idea and at most 2 short sentences. Badges
"Switch to the notebook: Demo n / Lab n" exactly where the Flow table sends the room to the
notebook. Then run the review agents deck-sales-refute, deck-marketing-refute,
deck-diagram-refute, deck-designer-refute and learner-engineer-refute on the files (via the
Agent tool, one at a time), fix every BLOCKER and MAJOR, and run
.venv/bin/python3 validate_slides.py ${N} until it PASSES.`)

  results.deck = await stage('Deck', `Run .claude/commands/build-diagrams.md "slides ${N}" and then
.claude/commands/build-slides.md for module ${N} (follow both exactly, minus approval pauses; build
all slides, batches of 5 with screenshots between). Output deck/module${NN}/index.html linking the
shared ../css and ../vendor assets, deck/module${NN}/diagrams/*.svg, notes.md, BUILD_REPORT.md.
Every deck tool needs DECK_MODULE=${N}. Check screenshots with
cd deck && DECK_MODULE=${N} node tools/shoot.mjs <slides> and read the PNGs; diagram text must be
at least 22 px at 1920x1080 (use the big-diagram rule otherwise). Then PACKAGE the deck:
cd deck && DECK_MODULE=${N} node tools/package-deck.mjs
It writes deck/module${NN}/Getting-Started-with-Jev-Module-${NN}.pdf, deck/dist/module${NN}/ and
deck/dist/Getting-Started-with-Jev-Module-${NN}.zip. Read 2 or 3 PDF pages with the Read tool to
confirm they render (brand colors, diagrams, badges, slide numbers). Return the PDF path.`)

  results.vslides = await stage('Validate slides', `Run
.venv/bin/python3 validate_slides.py ${N} --render
and fix every FAIL until it PASSES. The "slides vs notebook" group must PASS: every badge
"Switch to the notebook: X" has a "## X" section in ${DIR}/exercises.ipynb in the same order,
and every "## Back to the slides: T" names the slide right after that badge slide. Fix the
side that drifted from the approved plan (both notebooks if the notebook drifted, then
validate_notebooks.py ${N} --pair --strict again).`)

  // Workflow subagents have no Agent tool, so the script launches the reviewers itself.
  phase('Review')
  const BUILT = `${DIR}/exercises.ipynb, ${DIR}/solutions.ipynb, course/diagrams/module_${NN}/*.mmd and
*.png, ${SLIDES}, ${SLIDE_DIAGRAMS}, deck/module${NN}/index.html and its screenshots, in ${REPO}.
Context: ${PLAN} (Flow table), plans/TEACHING_STYLE.md, plans/NOTEBOOK_STYLE.md,
imp_files/outline_getting_started_jev.md`
  const personas = [
    ['learner-engineer-refute', 'both notebooks as a Python engineer new to Jev works through them in Colab: lab tiers (is Level 1 guided enough, Level 2 core, Level 3 a real stretch and optional), slots and markers, FALLBACK cells, helpers used before defined, key handling, lab instructions, outline coverage, teaching flow'],
    ['deck-designer-refute', 'the deck as built (index.html and screenshots): visual hierarchy, diagram-first discipline, clutter, brand consistency'],
    ['deck-marketing-refute', 'slide titles and copy: does each slide explain one idea clearly in at most 2 short sentences'],
    ['deck-diagram-refute', 'every slide diagram and every notebook diagram (.mmd sources and PNGs) against the code and the claim it supports'],
    ['general-purpose', `FLOW WALK. Walk the module exactly in the order of the "## Flow" table in ${PLAN}: read each slide in ${SLIDES} in order; at every slide with a Badge "Switch to the notebook: X" jump to the "## X" section of ${DIR}/exercises.ipynb, read until its "## Back to the slides: T" cell, then continue at slide T. Report every hop that is missing, mislabeled, out of order, lands on the wrong slide, or where the slide and the notebook tell a different story (different query, number or lab level). Do not edit files`],
  ]
  const reviews = await parallel(personas.map(([type, scope]) => () =>
    agent(`Review Module ${N} as built. Files: ${BUILT}. Focus: ${scope}. Output your ranked table of findings (BLOCKER, MAJOR, MINOR) with where, what and a one-line fix.`,
      { label: `review:${type}`, phase: 'Review', agentType: type })))
  const findings = personas.map(([type], i) => `### ${type}\n${reviews[i] || '(no output)'}`).join('\n\n')

  results.review = await stage('Review', `Apply the reviewer findings below to everything built for
module ${N}: ${BUILT}. Fix every BLOCKER and every MAJOR you agree with, in BOTH notebooks when
the cell exists in both (pair rule); list rejected ones with the reason (approved plan content
changes only to fix a real defect). Rebuild the deck slides you changed (build-slides) and
re-render changed diagrams. Then re-run, all must PASS:
- .venv/bin/python3 validate_notebooks.py ${N} --pair --strict
- .venv/bin/python3 validate_slides.py ${N} --render

REVIEWER FINDINGS:
${findings}`)

  results.commit = await stage('Commit', `Final gate and commit for module ${N}:
- .venv/bin/python3 validate_notebooks.py ${N} --pair --strict   (must PASS)
- .venv/bin/python3 validate_slides.py ${N} --render              (must PASS)
- .venv/bin/python3 -m pytest tests/unit -q                        (must PASS)
- scan this module's files for em dashes, en dashes and denylisted names (validation/denylist.txt)
- clear all outputs in both notebooks
- update plans/LABS.md (Edit, only module ${N}'s row)
- git add ONLY: ${DIR}/ course/diagrams/module_${NN}/ ${SLIDES} ${SLIDE_DIAGRAMS} deck/module${NN}/
  (not deck/dist, not *.zip). Never git add -A.
  git commit with message "Module ${N}: notebooks, diagrams and deck" ending with the line
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Do not push.
Return the commit hash in the summary and remind Axel that the notebook diagram PNGs show in
Colab only after he pushes.`)
} catch (e) {
  log(`Stopped: ${e.message}`)
  return { stoppedAt: String(e.message), completed: Object.keys(results), results }
}

return { completed: Object.keys(results), results }
