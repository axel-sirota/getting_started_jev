export const meta = {
  name: 'build-module',
  description: 'Build one module from its approved plan: shared changes, exercises, solutions, diagrams, live check, review, commit',
  whenToUse: 'After /research-module N is approved; triggered by /build-module N',
  phases: [
    { title: 'Shared changes', detail: 'only the data/ schema or data/00_lab_setup.ipynb changes the plan lists (skipped if none)' },
    { title: 'Exercises', detail: '/build-notebook N exercises' },
    { title: 'Solutions', detail: '/build-notebook N solutions' },
    { title: 'Diagrams', detail: '/build-diagrams N' },
    { title: 'Live check', detail: 'run solutions against real AWS where the laptop can; the rest is listed for Axel' },
    { title: 'Review', detail: 'learner-engineer and diagram reviewers, fix blockers' },
    { title: 'Commit', detail: 'final validation and git commit' },
  ],
}

const N = (args && args.module !== undefined) ? args.module : 1
const NN = String(N).padStart(2, '0')
const REPO = '/Users/axelsirota/repos/nwm_foundations_agentic_ai_engineering'
const PLAN = `plans/modules/module_${NN}_plan.md`
const DIR = `course/module_${NN}`
// Modules whose solutions run fully from the laptop. Modules 3+ create AgentCore, Cognito or
// Guardrail resources the laptop identity cannot create: Axel runs those in his instructor space.
const LAPTOP_MODULES = [1, 2, 5]
const LAPTOP_FULL = LAPTOP_MODULES.includes(N)

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
You work in ${REPO} on Module ${N}. The approved module plan is ${PLAN}; build from it, never
re-plan it. Read CLAUDE.md, plans/DECISIONS.md, plans/NOTEBOOK_STYLE.md and
plans/TEACHING_STYLE.md first. Axel gave blanket "go until the end" approval for this run: skip
every "ask the user / wait for approval" step in the repo commands, but NEVER skip validation.
Make exactly one tool call per response (no parallel tool calls). Use .venv/bin/python3 only.
Never use sed; edit with the Edit/Write tools. Follow .claude/NOTEBOOK_EDIT_PROTOCOL.md for
every notebook edit: print the id map BEFORE, write the expected order, print the id map AFTER
and assert it (cells can land out of order silently). Learners upload only .ipynb files.
Notebooks import frameworks only (no harborview package, no toolkit zip, no mock mode): the
first code cell is the pinned %pip install, then the CONFIG cell (MODEL_REGION="us-east-1",
AGENTCORE_REGION="us-west-2", MODEL_ID, STUDENT_NAME="default" refused by a visible check,
shared.json read). Every AWS call, SQL query, deploy and Gradio launch is a visible cell; helpers
live in visible HELPER cells; deployed files use %%writefile. course/harborview/ is source
material only, never imported. Anatomy (bread-financial): per concept a Section markdown with
the diagram, DEMO problem cells, DEMO solution cells, a Think About It, a "## Lab N: <Title>
(15 minutes)" markdown and ONE "# LAB N" cell with "name = None  # YOUR CODE" slots; a
"# FALLBACK" cell only where a later section needs the lab's result. No CHECK cells, no
SAFETY-NET cells, no mini exercises. Any local AWS call uses AWS_PROFILE=datacouch (never the
default profile). Never delete AWS resources other than ones this run created with the
instructor-check learner id. No em dashes or en dashes anywhere you write. Before editing a
shared file (data/schema.sql, data/00_lab_setup.ipynb, plans/LABS.md) read it fresh and change
only what this module needs. Return status "failed" with concrete issues if you cannot finish;
never pretend.`

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
  results.core = await stage('Shared changes', `If the "## Shared changes needed" section of ${PLAN} says
"none" or every item is marked done, return done with summary "no shared changes". Otherwise
apply every open item. Shared changes are ONLY data/ schema or seed changes (data/schema.sql,
data/setup_lab.py) or data/00_lab_setup.ipynb (shared resources, shared.json keys). Then:
- .venv/bin/python3 validate_notebooks.py --code
- for schema changes: apply them through the SSM tunnel with AWS_PROFILE=datacouch and run
  data/check_db_roles.py
- for data/00_lab_setup.ipynb changes: list under issues "Axel reruns data/00_lab_setup.ipynb in
  the instructor space" (the laptop identity cannot create those resources)
Mark applied items "(done)" in the plan's Shared changes section.`)

  results.exercises = await stage('Exercises', `Run the repo command .claude/commands/build-notebook.md
with arguments "${N} exercises" (read it and follow it exactly, minus approval pauses). Build
${N === 0 ? `${DIR}/start_here.ipynb` : `${DIR}/exercises.ipynb`} cell by cell from the plan's "# EXERCISES" section, 5 cells per batch,
validating after each batch with .venv/bin/python3 validate_notebooks.py ${N}. Every helper a
cell uses must be defined in a visible cell above it. Create plans/LABS.md if missing and set
this module's exercises to done.`)

  // Module 0 is one notebook (start_here.ipynb, no labs): build-notebook builds it in the
  // Exercises stage and there is no solutions copy.
  results.solutions = N === 0 ? { status: 'done', summary: 'module 0 has no solutions notebook', files: [], issues: [] }
    : await stage('Solutions', `Run .claude/commands/build-notebook.md with arguments
"${N} solutions" (follow it exactly, minus approval pauses): copy exercises.ipynb to
${DIR}/solutions.ipynb, replace each "# LAB N" cell with the plan's "# SOLUTION: LAB N" source by
cell id, delete every "# FALLBACK" cell. Verify: validate_notebooks.py ${N} --pair (must PASS).
Update plans/LABS.md.`)

  results.diagrams = await stage('Diagrams', `Run .claude/commands/build-diagrams.md for module ${N}
(minus approval pauses), using .claude/skills/mermaid-diagrams/SKILL.md. Diagrams are inline
\`\`\`mermaid blocks in markdown cells (JupyterLab renders them); the notebooks already hold them,
copied from the plan. For each slug in the plan's "## Diagram Index": check the block starts
with the brand line from the skill, write it to course/diagrams/module_${NN}/<slug>.mmd (no fences), render a
scratch PNG to prove it parses
cd deck && npx mmdc -i ../course/diagrams/module_${NN}/<slug>.mmd -o ../course/diagrams/module_${NN}/<slug>.png -s 2 -b white -c tools/mermaid-config.json
and look at it with the Read tool (legible, labels match the code). Any fix goes into the .mmd
AND the block in BOTH notebooks (Notebook Edit Protocol, id maps BEFORE and AFTER); the three
must be identical. PNGs are gitignored review artifacts, never referenced by a notebook. Finish
with validate_notebooks.py ${N} --pair (must PASS).`)

  results.live = await stage('Live check', `Verify the module against REAL AWS (read plans/lab_environment.md).
There is no mock mode. ${LAPTOP_FULL
    ? `Module ${N} runs fully from the laptop.`
    : `Module ${N} creates resources the laptop identity cannot (AgentCore, Cognito, Guardrails):
run only the cells the laptop can (config, model calls, SQL, KB, reads) and stop before the
first cell that creates one of those resources.`}
1. If the module touches Postgres, open the SSM port-forward tunnel on local port ${15430 + N} in
   the background with AWS_PROFILE=datacouch (command in plans/lab_environment.md, localPortNumber
   ${15430 + N}) and wait for the port.
2. Work on a scratch copy of ${N === 0 ? 'start_here.ipynb' : 'solutions.ipynb'} (never the committed file): set STUDENT_NAME to
   "instructorcheck", point the DB connection at 127.0.0.1:${15430 + N} if needed, drop %pip lines,
   and execute it headless (nbclient) in ${DIR} with AWS_PROFILE=datacouch. Check every cell you
   run works and each claim in the plan's "## Measured failures" and labs holds (with counts).
3. Every cell not run from the laptop goes under issues as one line per cell:
   "Axel runs solutions.ipynb in the instructor space: cell K (<what it creates>)". These are
   not failures.
4. Close ONLY this module's tunnel (port ${15430 + N}) and confirm it is closed.
Report where live differs from the plan; if a difference breaks the teaching point, fix BOTH
notebooks so it holds and re-run --pair. Never stage a fake result.`)

  // Workflow subagents have no Agent tool, so the script launches the reviewers itself.
  phase('Review')
  const BUILT = `${DIR}/exercises.ipynb, ${DIR}/solutions.ipynb, this module's course/diagrams/module_${NN}/<slug>.mmd
sources and their scratch PNG renders, and any data/ changes, in ${REPO}. Context: plans/TEACHING_STYLE.md,
plans/NOTEBOOK_STYLE.md, imp_files/outline_engineering.md`
  const personas = [
    ['learner-engineer-refute', 'both notebooks as a learner works through them: LAB cells and slots, FALLBACK cells, helpers used before they are defined, AWS calls hidden in helpers, lab instructions, outline coverage, teaching flow'],
    ['deck-diagram-refute', 'every inline mermaid block this module has (read the .mmd sources and their scratch PNG renders) against the code in the notebook'],
  ]
  const reviews = await parallel(personas.map(([type, scope]) => () =>
    agent(`Review Module ${N} as built. Files: ${BUILT}. Focus: ${scope}. Output your ranked table of findings (BLOCKER, MAJOR, MINOR) with where, what and a one-line fix.`,
      { label: `review:${type}`, phase: 'Review', agentType: type })))
  const findings = personas.map(([type], i) => `### ${type}\n${reviews[i] || '(no output)'}`).join('\n\n')

  results.review = await stage('Review', `Apply the reviewer findings below to everything built for
module ${N}: ${BUILT}. Fix every BLOCKER and every MAJOR you agree with, in BOTH notebooks when
the cell exists in both (pair rule); list rejected ones with the reason (approved plan content
changes only to fix a real defect). Re-run validate_notebooks.py ${N} --pair --strict and
re-render changed diagrams with mmdc, keeping each .mmd identical to its notebook blocks.
Every check must PASS.

REVIEWER FINDINGS:
${findings}`)

  results.commit = await stage('Commit', `Final gate and commit for module ${N}:
- .venv/bin/python3 validate_notebooks.py ${N} --pair --strict   (must PASS)
- .venv/bin/python3 validate_notebooks.py --code                 (must PASS)
- scan this module's files for em dashes, en dashes and denylisted names (validation/denylist.txt)
- clear all outputs in both notebooks
- update plans/LABS.md (Edit, only module ${N}'s row)
- git add ONLY: ${DIR}/ course/diagrams/module_${NN}/ and any data/ file this run changed. Never git add -A.
  git commit with message "Module ${N}: exercises, solutions and diagrams" ending with the line
  "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>". Do not push.
Return the commit hash in the summary, and repeat the Live check list of cells Axel runs in the
instructor space.`)
} catch (e) {
  log(`Stopped: ${e.message}`)
  return { stoppedAt: String(e.message), completed: Object.keys(results), results }
}

return { completed: Object.keys(results), results }
