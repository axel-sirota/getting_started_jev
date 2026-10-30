---
description: Create or update plans/DECISIONS.md (the course manifest) and its companions TEACHING_STYLE.md and NOTEBOOK_STYLE.md
---

Initialize or update the course manifest: $ARGUMENTS

`plans/DECISIONS.md` (written 2026-10-30 for Getting Started with Jev) is the source of truth,
with `plans/TEACHING_STYLE.md` and `plans/NOTEBOOK_STYLE.md`. Read them, `CLAUDE.md` and
`imp_files/outline_getting_started_jev.md` first.

## If DECISIONS.md exists (the normal case)

Show its sections as a table and ask: "Which sections do you want to change?" Re-ask only
those, one question at a time, confirm each answer, then show the changed lines and ask
for approval before editing. Use Edit, not Write. Add a row to the decisions log.

## If it does not exist

Interview one question at a time, only for what CLAUDE.md and the outline leave open.
**Never ask** about minutes, timing, headcount, dates or deadlines. Axel cares about material.

Open topics, in order, each with a recommended default:

1. How material reaches learners (Colab from GitHub, keys via getpass, diagrams as raw
   GitHub PNG links)
2. Jev model id and OpenAI model id
3. Running case and data (CLINC150 config, sample size, seed)
4. Lab tiers (Guided, Core, Challenge optional)
5. Spelling and brand
6. Module map: demo and lab per module, from the outline

Show the full draft, get approval, write `plans/DECISIONS.md`.

## After writing or updating

If the change affects stack, layout or rules, update `CLAUDE.md`, TEACHING_STYLE,
NOTEBOOK_STYLE and any command, skill or validator that hard-codes the old choice, and say
which files changed.
