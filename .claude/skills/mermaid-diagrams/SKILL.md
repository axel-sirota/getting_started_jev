---
name: mermaid-diagrams
description: Design rules, brand palette and render commands for every Mermaid diagram in Getting Started with Jev (notebook PNGs linked by raw GitHub URL, slide SVGs). Use whenever a diagram is drafted, reviewed, rendered or embedded.
---

# Mermaid diagrams for Getting Started with Jev

Diagrams carry the teaching: every concept is explained with a diagram first, text second.
Audience: Python developers and data professionals new to Jev. Merged from the platform
engineering webinar deck (rendering, brand, readability), the nerdearla workshop (one concept
per diagram, teaching placement) and the nwm Foundations and Engineering courses.

## Design rules

- One idea per diagram. Max ~8 nodes on a slide, ~10 in a notebook; split if more
- Shape follows the idea:
  - request flow: `flowchart LR` (state + questions -> Jev -> typed answers -> code decides)
  - who calls whom over time: `sequenceDiagram` (notebook, Jev, LLM, human reviewer)
  - decision logic in code: `flowchart LR` with one diamond per rule, outcomes as words
    (the "truth table": Jev supplies judgments, code decides)
  - routing: `flowchart LR` fan-out to CODE, LLM, HUMAN with the confidence gate as a diamond
  - comparison: two subgraphs side by side (LLM vs Jev, zero-shot vs Jev)
  - two-stage pipelines: `flowchart LR` (domain, then intent)
- Labels: short, plain ASCII, no em dashes. Code names are fine when they are the names in
  the notebook (`system_one`, `Choice`, `Noul`, `confidence`)
- Outcomes and statuses carry a word, never colour alone (ROUTE, ESCALATE, PASS, BLOCK)
- Human checkpoints visually distinct and labeled with the role ("Agent reviews")
- Running case: CLINC150 query triage (domain, intent, out-of-scope)
- Readable on a 1280x720 shared screen: diagram text at least 22 px at 1920x1080
- No false implications: draw only what the code in that notebook or slide does

## Brand

`deck/tools/mermaid-config.json` holds the Data Trainers palette and Inter at fontSize 24:
navy `#1A3D4D`, teal `#40B8A6`, light teal fill `#ECF8F6`, body `#4B5563`, borders
`#E5E7EB`. Always render with it. Do not hard-code colours in `.mmd` files unless a single
node must stand out (the human checkpoint or the failure).

Every notebook diagram `.mmd` starts with this brand line (validate_notebooks.py checks it,
character for character):

```
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Inter, sans-serif", "primaryColor": "#ECF8F6", "primaryBorderColor": "#40B8A6", "primaryTextColor": "#111827", "lineColor": "#1A3D4D", "secondaryColor": "#F9FAFB", "tertiaryColor": "#FFFFFF", "clusterBkg": "#F9FAFB", "clusterBorder": "#D1D5DB", "actorBkg": "#ECF8F6", "actorBorder": "#40B8A6", "noteBkgColor": "#FFF6DA", "noteBorderColor": "#E0B84C"}}}%%
```

## Render

Needs `cd deck && npm install` once.

| Target | Command (from `deck/`) |
|---|---|
| Notebook PNG (module NN) | `./node_modules/.bin/mmdc -i ../course/diagrams/module_NN/<slug>.mmd -o ../course/diagrams/module_NN/<slug>.png -s 2 -b white -c tools/mermaid-config.json` (mermaid-cli 12: no `-w`; local binary, not npx) |
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

- Notebooks (Google Colab). Colab renders neither ```mermaid blocks nor cell attachments
  (it strips attachments, googlecolab/colabtools#3836). So the master is
  `course/diagrams/module_NN/<slug>.mmd`, its render `<slug>.png` sits next to it, both are
  committed and pushed, and the notebook links the PNG by raw GitHub URL in its own markdown
  cell (or at the end of a short theory cell):

  ```markdown
  <!-- DIAGRAM: <slug> -->
  ![<alt text that states the idea>](https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png)
  ```

  The URL prefix is `RAW_BASE` in `validate_notebooks.py`; it is the only place that names
  the repo, which must be public. A PNG shows in Colab only after it is pushed. The
  exercises and solutions notebooks hold the same diagram cells.
- Slides: `deck/moduleNN/diagrams/slide-NN.svg`, sourced from
  `imp_files/slides/moduleNN_diagrams.md`

## Review

For slide diagrams run `deck-diagram-build` and `deck-diagram-refute` before approval.
Examples that worked: `reference/diagram_examples/` (agent loop, LangGraph, MCP,
supervisor, swarm; labels in Spanish, structure reusable) and
`reference/diagrams.reference.md` (31 webinar slide diagrams).
