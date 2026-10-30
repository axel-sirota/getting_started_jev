---
name: mermaid-diagrams
description: Design rules, brand palette and render commands for every Mermaid diagram in this course (module notebook PNGs, slide SVGs, learner starter files). Use whenever a diagram is drafted, reviewed, rendered or embedded.
---

# Mermaid diagrams for the Agentic AI Foundations course

Diagrams carry the teaching. Audience: business and operations people, no coders.
Merged from the platform engineering webinar deck (rendering, brand, readability) and the
nerdearla workshop (one concept per diagram, teaching placement).

## Design rules

- One idea per diagram. Max ~8 nodes on a slide, ~10 in a notebook; split if more
- Shape follows the idea:
  - process or loop: `flowchart LR` (plan, act, evaluate; request to resolution)
  - hierarchy or spectrum: `flowchart TD` or LR with ordered nodes (autonomy levels)
  - who talks to whom over time: `sequenceDiagram` (agent, tool, policy system, human)
  - decision table logic: `flowchart LR` with one diamond per rule, outcomes as words
  - BPMN-style process: `flowchart LR` with subgraphs as swimlanes (customer, agent,
    human reviewer, system of record)
  - comparison: two subgraphs side by side (chat model vs agent)
- Labels: short plain English, plain ASCII, no em dashes, no jargon a business reader
  cannot parse in 3 seconds. Define acronyms on the slide, not in the node
- Outcomes and statuses carry a word, never colour alone (APPROVED, ESCALATE, PASS, FAIL)
- Human checkpoints are always visually distinct: a node labelled with the human role
  ("Underwriter approves"), never an unlabeled gate
- Running case in every diagram: the Policyholder Service Agent, fictional company
- Readable on a 1280x720 shared screen: diagram text at least 22 px at 1920x1080
- No false implications: draw only what the lab agent actually does

## Brand

`deck/tools/mermaid-config.json` holds the Data Trainers palette and Inter at fontSize 24:
navy `#1A3D4D`, teal `#40B8A6`, light teal fill `#ECF8F6`, body `#4B5563`, borders
`#E5E7EB`. Always render with it. Do not hard-code colours in `.mmd` files unless a single
node must stand out (the human checkpoint or the failure).

## Render

Needs `cd deck && npm install` once.

| Target | Command (from `deck/`) |
|---|---|
| Notebook PNG | `npx mmdc -i ../course/diagrams/<slug>.mmd -o ../course/diagrams/<slug>.png -w 1600 -b white -c tools/mermaid-config.json` |
| Slide SVG (module M) | `DECK_MODULE=M node tools/extract-mmd.mjs --all && DECK_MODULE=M node tools/render-diagrams.mjs` |
| Check slide sources match | `DECK_MODULE=M node tools/extract-mmd.mjs --check` |
| Screenshot + min text size | `DECK_MODULE=M node tools/shoot.mjs <slide>` |

One deck per module: every deck tool requires `DECK_MODULE`. `render-diagrams.mjs`
deep-merges `deck/moduleNN/mermaid-overrides.json` (or `tools/mermaid-overrides.json`) per
slide (keys are the unpadded slide number, like `"7": {...}`) over the base config, fixes
dotted links, can keep clusters in source order
(`"_clusterOrder": "source"`), and tight-fits the SVG. Layout tweaks go there, never in
the `.mmd`.

## Placement

- Notebooks (SageMaker JupyterLab): learners upload only the `.ipynb`, so embed the PNG as
  a cell attachment: `![<title>](attachment:<slug>.png)` with the base64 PNG in the cell's
  `attachments`. Never link a file path. Sources and PNGs live in `course/diagrams/`.
  Placeholder until built: `<!-- DIAGRAM: ... -->`
- Slides: `deck/moduleNN/diagrams/slide-NN.svg`, sourced from
  `imp_files/slides/moduleNN_diagrams.md`
- Learner starter files (Module 4): `course/labs/starter/<slug>.mmd`, valid Mermaid with
  clearly marked `TODO` nodes for learners to replace in their JupyterLab. Learners edit
  Mermaid text, the one place they type structured text; keep it to node labels and
  arrows. Whether their JupyterLab renders Mermaid is an open item in
  `plans/lab_environment.md`

## Review

For slide diagrams run `deck-diagram-build` and `deck-diagram-refute` before approval.
Examples that worked: `reference/diagram_examples/` (agent loop, LangGraph, MCP,
supervisor, swarm; labels in Spanish, structure reusable) and
`reference/diagrams.reference.md` (31 webinar slide diagrams).
