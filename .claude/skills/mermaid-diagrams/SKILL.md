---
name: mermaid-diagrams
description: Design rules, brand palette, render command and placement for every Mermaid diagram in Getting Started with Jev, a notebook-only Colab class (diagrams are committed PNGs linked by raw GitHub URL). Use whenever a diagram is drafted, reviewed, rendered or embedded.
---

# Mermaid diagrams for Getting Started with Jev

There are no slides: the diagrams in the notebook carry the teaching. Audience: Python
developers and data professionals new to Jev.

## Where diagrams go (the 4 beats)

| Place | Diagram | What it must show |
|---|---|---|
| Part 0: What is Jev (Module 1) | one per markdown cell | the product: state + questions -> Jev -> typed answers; LLM text vs Jev answer; Choice / Score / Noul and what each returns |
| `### 1. The problem` | exactly one | the failure, drawn so the broken step is obvious (a word like FAILS or PARSE ERROR on it) |
| `### 2. The solution` | exactly one | the fix, same shapes as the problem diagram where possible, so before and after line up |
| `### 3. Demo`, `### 4. Lab` | optional | only if the code needs a map (for example the rules `triage()` applies) |

## Design rules

- One idea per diagram, max ~10 nodes; split if more
- Shape follows the idea:
  - request flow: `flowchart LR` (state + questions -> Jev -> typed answers -> code decides)
  - who calls whom over time: `sequenceDiagram` (notebook, Jev, LLM, human reviewer)
  - decision logic in code: `flowchart TD` with one diamond per rule, outcomes as words
  - routing: fan-out to CODE, LLM, HUMAN with the gate as a diamond
  - comparison: two subgraphs side by side (LLM vs Jev, vague vs literal)
  - a distribution: `xychart-beta` bar chart
- Labels: short, plain ASCII, no em dashes. Code names are fine when they are the names in
  the notebook (`system_one`, `Choice`, `Noul`, `confidence`)
- Outcomes and statuses carry a word, never colour alone (ROUTE, ESCALATE, PASS, BLOCK)
- Human checkpoints visually distinct and labeled with the role ("Agent reviews")
- Running case: CLINC150 message triage (team, intent, out-of-scope)
- Readable in a Colab cell on a shared screen: no tiny text, prefer TD for anything wider than
  five nodes
- No false implications: draw only what the code in that notebook does; numbers only if measured

## Brand

`deck/tools/mermaid-config.json` holds the Data Trainers palette and Inter at fontSize 24:
navy `#1A3D4D`, teal `#40B8A6`, light teal fill `#ECF8F6`, body `#4B5563`, borders
`#E5E7EB`. Always render with it. Do not hard-code colours in `.mmd` files unless a single
node must stand out (the failure or the human checkpoint).

Every `.mmd` starts with this brand line (validate_notebooks.py checks it, character for
character):

```
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Inter, sans-serif", "primaryColor": "#ECF8F6", "primaryBorderColor": "#40B8A6", "primaryTextColor": "#111827", "lineColor": "#1A3D4D", "secondaryColor": "#F9FAFB", "tertiaryColor": "#FFFFFF", "clusterBkg": "#F9FAFB", "clusterBorder": "#D1D5DB", "actorBkg": "#ECF8F6", "actorBorder": "#40B8A6", "noteBkgColor": "#FFF6DA", "noteBorderColor": "#E0B84C"}}}%%
```

## Render

`deck/` is the diagram toolchain (mermaid-cli and the brand config). Install once with
`cd deck && PUPPETEER_SKIP_DOWNLOAD=1 npm ci` (it reuses the Chrome in ~/.cache/puppeteer).

```bash
cd deck && ./node_modules/.bin/mmdc -i ../course/diagrams/module_NN/<slug>.mmd \
  -o ../course/diagrams/module_NN/<slug>.png -s 2 -b white -c tools/mermaid-config.json
```

mermaid-cli 12 has no `-w`; call the local binary, not `npx` (a hook rewrites npx). Read the
PNG with the Read tool after every render: legible, labels match the code.

## Placement in the notebook

Colab renders neither ```mermaid blocks nor cell attachments (it strips attachments,
googlecolab/colabtools#3836). The master is `course/diagrams/module_NN/<slug>.mmd`, its render
`<slug>.png` sits next to it, both are committed and pushed, and the notebook links the PNG by
raw GitHub URL inside the beat's markdown cell:

```markdown
<!-- DIAGRAM: <slug> -->
![<alt text that states the idea>](https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png)
```

The URL prefix is `RAW_BASE` in `validate_notebooks.py`; it is the only place that names the
repo (public). A PNG shows in Colab only after it is pushed. Exercises and solutions hold the
same diagram cells.

## Review

Run `deck-diagram-build` and `deck-diagram-refute` on every new diagram before approval.
Examples of shapes that worked: `reference/diagram_examples/` and
`reference/diagrams.reference.md`.
