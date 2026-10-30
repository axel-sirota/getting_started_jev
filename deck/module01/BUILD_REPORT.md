# Module 1 deck build report

Source: `imp_files/slides/module01_slides.md` + `module01_diagrams.md` (extract `--check`: 11 diagrams, 0 mismatches).
Rebuilt 2026-10-30 after the review round (learner, designer, marketing, diagram, flow walk).
12 planned slides, 12 deck pages, no split pages.

| Slide | Title | Template | Diagram rendered | Points | Notes | Min diagram text at 1920 |
|---|---|---|---|---|---|---|
| 1 | Getting Started with Jev | title | n/a | 0 | yes (+ playbook) | n/a |
| 2 | The reply that breaks your parser | full + strip | yes | 0 | yes | 33.6 px |
| 3 | A schema fixes the format, not the doubt | split | yes | 3 | yes | 45.1 px |
| 4 | Jev answers questions. It never writes text. | split, badge Demo 1 | yes | 3 | yes (+ playbook) | 37.5 px |
| 5 | Accuracy within noise, 3 to 4x faster, 12x cheaper | full + strip | yes | 0 | yes | 52.4 px |
| 6 | One request, three kinds of question | full, badge Demo 2 | yes | 0 | yes (+ playbook) | 38.4 px |
| 7 | Read the distribution, not only the top answer | full + strip | yes (xychart) | 0 | yes | 24.6 px |
| 8 | Rules in Python, not in the prompt | full + strip | yes | 0 | yes | 27.3 px |
| 9 | Lab 1: Build triage() in one call | lab, badge Lab 1 | yes | 0 | yes (+ playbook) | 37.2 px |
| 10 | Urgent is not risky: the declined card | full + strip | yes | 0 | yes (+ playbook) | 45.1 px |
| 11 | Jev always picks a team, even when none fits | full + strip | yes | 0 | yes | 42.1 px |
| 12 | Jev judges, your code decides | full + strip | yes | 0 | yes | 36.1 px |

## Changes from the plan, and why

| Slide | Change | Why |
|---|---|---|
| 1 | Module line "Module 1 · Meet Jev: Typed Decisions Instead of Text" under the subtitle | Title template shows course and module; no double colon |
| 2, 5, 7, 8, 10, 11, 12 | `class="has-caption"` + `<div class="caption-strip">` from the plan's "Strip under the diagram" clause; CSS in the deck style block | Diagram-first slides with one line of takeaway instead of 3 bullets |
| all | `mermaid-overrides.json` emptied | Slide 5 has no clusters any more; slide 8 is LR in the source |
| theme | `.source` footer 18 px, grey links, no underline; deck `.points li` override removed (theme already sets 34 px) | Footer competed with content |
