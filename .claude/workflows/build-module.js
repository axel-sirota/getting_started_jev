export const meta = {
  name: 'build-module',
  description: 'Build one module notebook pair from its approved plan: exercises, solutions, diagrams, validate, run in order, review, commit (notebook-only class, 4 beats)',
  whenToUse: 'After /research-module N is approved; triggered by /build-module N',
  phases: [
    { title: 'Exercises', detail: '/build-notebook N exercises (Part 0 in Module 1, 4 beats per Part, three-tier labs)' },
    { title: 'Solutions', detail: '/build-notebook N solutions' },
    { title: 'Diagrams', detail: '/build-diagrams N: .mmd -> PNG, raw GitHub links' },
    { title: 'Validate', detail: 'validate_notebooks.py N --pair --strict' },
    { title: 'Run in order', detail: 'execute both notebooks top to bottom against real Jev and OpenAI' },
    { title: 'Review', detail: 'learner-engineer, diagram reviewer and a beat walk; fix blockers' },
    { title: 'Commit', detail: 'final validation and git commit' },
  ],
}

const N = (args && args.module !== undefined) ? args.module : 1
const NN = String(N).padStart(2, '0')
const REPO = '/Users/axelsirota/repos/getting_started_jev'
const PLAN = `plans/modules/module_${NN}_plan.md`
const DIR = `course/module_${NN}`

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
You work in ${REPO} on Module ${N} of Getting Started with Jev. The approved plan is ${PLAN};
build from it, never re-plan it. Read CLAUDE.md, plans/DECISIONS.md, plans/NOTEBOOK_STYLE.md,
plans/TEACHING_STYLE.md and .claude/skills/jev-course/SKILL.md first; load the typesafe-ai
skill before touching any Jev call. Axel gave blanket "go until the end" approval for this run:
skip every "ask the user / wait for approval" step in the repo commands, but NEVER skip
validation. Make exactly one tool call per response (no parallel tool calls, ever). Use
.venv/bin/python3 only. Never use sed, not even to filter output; edit with the Edit/Write
tools or a checked Python edit. Web research uses the built-in WebSearch / WebFetch only, never
Kryla web tools; Jev facts come only from docs.typesafe.ai, typesafe.ai or
github.com/typesafe-ai. Follow .claude/NOTEBOOK_EDIT_PROTOCOL.md for every notebook edit:
print the id map BEFORE, write the expected order, print the id map AFTER and assert it.

THE CLASS IS THE NOTEBOOK. There are no slides: every explanation and every diagram lives in
the notebook's markdown cells. The structure is Axel's 4 beats and nothing reorders it:
${N === 1 ? '"## Part 0: What is Jev" first (text and diagrams only, explains the product before anything else), then ' : ''}every
"## Part k: <concept>" has, in order, "### 1. The problem" (text + one figure, no code),
"### 2. The solution" (text + one figure, no code), "### 3. Demo" (DEMO cells: the problem
live, then the solution, then Think About It) and "### 4. Lab k: <title>" (three tiers:
# LAB k.1 (Guided) with "name = None  # YOUR CODE" slots, # LAB k.2 (Core) with a
"# YOUR CODE" function body, # LAB k.3 (Challenge, optional) that nothing later depends on).
Learners run the notebooks in Google Colab: first code cell is the pinned %pip install, then
# KEYS (TYPESAFE_API_KEY and, where needed, OPENAI_API_KEY from os.environ, else getpass;
never Colab secrets, never printed, never literal), then # CONFIG (client, pinned model ids,
a probe). Every Jev and OpenAI call is a visible cell. Diagrams: .mmd master in
course/diagrams/module_${NN}/ (brand line first), its PNG committed next to it, shown in a
figure cell ("**Figure: ...**", the DIAGRAM marker, the raw GitHub image link; RAW_BASE in
validate_notebooks.py); never a mermaid block or an attachment in a notebook. No em dashes or
en dashes anywhere you write. Return status "failed" with concrete issues if you cannot
finish; never pretend.`

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
validating after each batch with .venv/bin/python3 validate_notebooks.py ${N}. Markdown cells
are the lesson: copy them from the plan word for word. Every helper a cell uses must be
defined in a visible cell above it. Create plans/LABS.md if missing and set this module's
exercises to done.`)

  results.solutions = await stage('Solutions', `Run .claude/commands/build-notebook.md with arguments
"${N} solutions" (follow it exactly, minus approval pauses): copy exercises.ipynb to
${DIR}/solutions.ipynb, replace each "# LAB k.n" cell with the plan's "# SOLUTION: LAB k.n"
source by cell id, delete every "# FALLBACK" cell. Verify: validate_notebooks.py ${N} --pair
(must PASS). Update plans/LABS.md.`)

  results.diagrams = await stage('Diagrams', `Run .claude/commands/build-diagrams.md for module ${N}
(minus approval pauses), using .claude/skills/mermaid-diagrams/SKILL.md. For each slug in the
plan's "## Diagram Index": make sure course/diagrams/module_${NN}/<slug>.mmd exists and starts
with the brand line, render it with
cd deck && ./node_modules/.bin/mmdc -i ../course/diagrams/module_${NN}/<slug>.mmd -o ../course/diagrams/module_${NN}/<slug>.png -s 2 -b white -c tools/mermaid-config.json
(mermaid-cli 12: -s is the scale; there is no -w. Call the local binary, not npx: a hook rewrites npx)
and look at the PNG with the Read tool (legible, labels match the code, the problem and
solution figures of each Part line up). Any fix goes into the .mmd and is re-rendered. Both
notebooks show the same figure cells. Finish with validate_notebooks.py ${N} --pair --strict
(must PASS).`)

  results.validate = await stage('Validate', `Run
.venv/bin/python3 validate_notebooks.py ${N} --pair --strict
and fix every FAIL in BOTH notebooks (pair rule) with the Notebook Edit Protocol, until it
PASSES. Then read the cell maps and confirm the order matches the plan: title, Setup, %pip,
KEYS, CONFIG, DATA, ${N === 1 ? 'Part 0, ' : ''}then per Part: Part heading, 1. The problem (text,
figure), 2. The solution (text, figure), 3. Demo (DEMO cells, Think About It), 4. Lab k
(markdown, LAB k.1, optional FALLBACK in exercises only, LAB k.2, optional CHECK, LAB k.3),
then Summary. Report any order difference you fixed.`)

  results.run = await stage('Run in order', `Execute the solutions notebook top to bottom against the
REAL Jev and OpenAI APIs. The keys live in the gitignored ${REPO}/.env. Load them in the
SAME Bash command that runs the notebook, without printing anything from the file:
set -a && . ./.env && set +a && export TYPESAFE_API_KEY="\${TYPESAFE_API_KEY:-\$JEV_AI_API_KEY}" && <run command>
If either key is still missing return "failed" with issue "Axel: add TYPESAFE_API_KEY (or
JEV_AI_API_KEY) and OPENAI_API_KEY to .env and rerun from this stage" (never print, echo or
copy a key, never ask for it in chat, never write it to another file). Work on a scratch copy
of ${DIR}/solutions.ipynb in the session scratchpad (never the committed file), drop the %pip
lines (the venv has course/requirements.txt), and execute it headless with nbclient (timeout
600 per cell) so getpass is skipped because the env vars are set. Every cell must run without
error. Check each claim in the plan's "## Measured numbers" and "## Run in order" still holds
(report the numbers you saw). Then run the exercises notebook the same way with FALLBACK cells
kept: it must run top to bottom without an error (unfilled slots print a message or are filled
by FALLBACK). If a difference breaks the teaching point, fix BOTH notebooks so it holds and
re-run validate_notebooks.py ${N} --pair --strict. Never stage a fake result.`)

  // Workflow subagents have no Agent tool, so the script launches the reviewers itself.
  phase('Review')
  const BUILT = `${DIR}/exercises.ipynb, ${DIR}/solutions.ipynb and course/diagrams/module_${NN}/*.mmd
and *.png, in ${REPO}. Context: ${PLAN}, plans/TEACHING_STYLE.md, plans/NOTEBOOK_STYLE.md,
imp_files/outline_getting_started_jev.md`
  const personas = [
    ['learner-engineer-refute', 'both notebooks as a Python engineer new to Jev works through them in Colab: does each beat teach on its own (problem felt, solution understood before code, demo shows both, lab doable), lab tiers (Level 1 guided, Level 2 core, Level 3 a real optional stretch), slots and markers, FALLBACK cells, helpers used before defined, key handling, outline coverage' + (N === 1 ? ', and above all: after Part 0 can you say what Jev is, what state and questions are, what Choice / Score / Noul return and how it differs from an LLM?' : '')],
    ['deck-diagram-refute', 'every figure in both notebooks (.mmd sources and PNGs) against the beat it sits in and the code it describes'],
    ['general-purpose', `BEAT WALK. Read ${DIR}/exercises.ipynb top to bottom as a learner who has never heard of Jev, markdown first. For every Part report: is the problem concrete and felt, does the solution follow from it, does the demo show the problem live and then the solution, does the lab exercise exactly what the Part taught, is every term explained before it is used${N === 1 ? ', and does Part 0 explain Jev fully before any comparison' : ''}. Report every beat that is missing, out of order, thin, or that teaches something different from its neighbors. Do not edit files`],
  ]
  const reviews = await parallel(personas.map(([type, scope]) => () =>
    agent(`Review Module ${N} as built. Files: ${BUILT}. Focus: ${scope}. Output your ranked table of findings (BLOCKER, MAJOR, MINOR) with where, what and a one-line fix.`,
      { label: `review:${type}`, phase: 'Review', agentType: type })))
  const findings = personas.map(([type], i) => `### ${type}\n${reviews[i] || '(no output)'}`).join('\n\n')

  results.review = await stage('Review', `Apply the reviewer findings below to everything built for
module ${N}: ${BUILT}. Fix every BLOCKER and every MAJOR you agree with, in BOTH notebooks when
the cell exists in both (pair rule); list rejected ones with the reason (approved plan content
changes only to fix a real defect; reviewers never reorder the 4 beats or move Part 0). Re-render
changed diagrams. Re-run both notebooks against the real APIs if any code changed. Then:
- .venv/bin/python3 validate_notebooks.py ${N} --pair --strict   (must PASS)

REVIEWER FINDINGS:
${findings}`)

  results.commit = await stage('Commit', `Final gate and commit for module ${N}:
- .venv/bin/python3 validate_notebooks.py ${N} --pair --strict   (must PASS)
- .venv/bin/python3 -m pytest tests/unit -q                        (must PASS)
- scan this module's files for em dashes, en dashes and denylisted names (validation/denylist.txt)
- clear all outputs in both notebooks
- update plans/LABS.md (Edit, only module ${N}'s row)
- git add ONLY: ${DIR}/ course/diagrams/module_${NN}/. Never git add -A.
  git commit with message "Module ${N}: notebooks and diagrams" ending with the line
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Do not push.
Return the commit hash in the summary and remind Axel that the diagram PNGs show in Colab only
after he pushes.`)
} catch (e) {
  log(`Stopped: ${e.message}`)
  return { stoppedAt: String(e.message), completed: Object.keys(results), results }
}

return { completed: Object.keys(results), results }
