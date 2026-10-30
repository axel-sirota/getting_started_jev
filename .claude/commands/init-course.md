---
description: Create or update plans/DECISIONS.md (the course manifest) and its companions TEACHING_STYLE.md and NOTEBOOK_STYLE.md
---

Initialize or update the course manifest: $ARGUMENTS

`plans/DECISIONS.md` (rewritten 2026-10-06 for the Engineering Track) is the source of truth,
with `plans/TEACHING_STYLE.md` and `plans/NOTEBOOK_STYLE.md`. Read them, `CLAUDE.md`,
`plans/lab_environment.md` and `imp_files/outline_engineering.md` first.

## If DECISIONS.md exists (the normal case)

Show its sections as a table and ask: "Which sections do you want to change?" Re-ask only
those, one question at a time, confirm each answer, then show the changed lines and ask
for approval before editing. Use Edit, not Write. Update "Last updated".

## If it does not exist

Interview one question at a time, only for what CLAUDE.md, the outline and
`plans/lab_environment.md` leave open. **Never ask** about minutes, timing, headcount,
dates or deadlines. Axel cares about material.

Open topics, in order, each with a recommended default:

1. How material reaches learners (uploaded .ipynb, toolkit zip, inline mermaid diagrams)
2. Model and region rules
3. Agent framework, deploy target, tools transport, identity, memory, RAG store
4. Lab surface (Gradio over the learner's agent) and backup (mock mode)
5. Fictional company and synthetic data
6. Spelling and brand
7. Module map: demo and labs per module, from the outline

Show the full draft, get approval, write `plans/DECISIONS.md`.

## After writing or updating

If the change affects stack, layout or rules, update `CLAUDE.md`, TEACHING_STYLE,
NOTEBOOK_STYLE and any command, skill or validator that hard-codes the old choice, and say
which files changed.
