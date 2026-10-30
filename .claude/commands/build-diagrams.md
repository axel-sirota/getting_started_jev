---
description: Build Mermaid diagrams one by one, for module notebooks (committed PNG linked by raw GitHub URL) or slides (SVG)
---

Build diagrams: $ARGUMENTS

(Argument: a module number to build its notebook diagrams, or `slides <N>` to build module
N's slide diagrams from `imp_files/slides/moduleNN_diagrams.md`.
With no argument, list every unbuilt diagram and ask which set.)

## GUARD

```bash
ls plans/DECISIONS.md 2>/dev/null
```

If missing: "Run `/init-course` first."

Follow `.claude/skills/mermaid-diagrams/SKILL.md` for design rules, palette and rendering.

---

## Two kinds of diagram

| Kind | Source | Output | Rendered with |
|---|---|---|---|
| Notebook | module plan's `## Diagram Index` | `course/diagrams/module_NN/<slug>.mmd` (brand line first) + `.png`, both committed | mermaid-cli + `deck/tools/mermaid-config.json` |
| Slide | `imp_files/slides/moduleNN_diagrams.md` (from `/plan-slides N`) | `deck/moduleNN/diagrams/slide-NN.mmd` + `.svg` | `DECK_MODULE=N` + `extract-mmd.mjs` + `render-diagrams.mjs` |

---

## Step 1: Read context

1. The source above for the requested set
2. The notebook cell or slide that embeds each diagram, to see what it must serve
3. `reference/diagram_examples/` and `reference/diagrams.reference.md` for shape and style
   that already worked

## Step 2: List and ask

```
Diagrams to build:
1. <slug>.mmd - <what it shows> - used in <cell / slide>
...
I'll build them one at a time and ask for approval before each file.
```

Ask: "Ready to start with diagram 1?"

## Step 3: One at a time, approval between each

### 3a. Show the Mermaid source in chat first

```
Diagram <K>: <slug>
Shows: <one line>
Used in: <cell / slide>

<mermaid source>

Does this look right? I'll write the file once you approve.
```

**Wait for approval.** For a diagram that carries a slide, optionally run the
`deck-diagram-build` and `deck-diagram-refute` agents on it first and show their verdict.

### 3b. Write the `.mmd`

Raw Mermaid only, no fences.

### 3c. Render

Notebook diagram:
```bash
cd deck && npx mmdc -i ../course/diagrams/module_NN/<slug>.mmd -o ../course/diagrams/module_NN/<slug>.png -w 1600 -b white -c tools/mermaid-config.json
```
Read the PNG with the Read tool: legible, labels match the code.

Slide diagram (needs `cd deck && npm install` once):
```bash
cd deck && DECK_MODULE=<module> node tools/extract-mmd.mjs <slide> && DECK_MODULE=<module> node tools/render-diagrams.mjs <slide>
```

If `npx` or `node` is unavailable, say so and stop; do not install global packages
without asking.

### 3d. Link (notebook diagrams)

Colab renders neither ```mermaid blocks nor cell attachments (it strips attachments), so the
notebook links the committed PNG by raw GitHub URL. The diagram cell in BOTH notebooks is:

```markdown
<!-- DIAGRAM: <slug> -->
![<alt text that states the idea>](https://raw.githubusercontent.com/axelsirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png)
```

The prefix is `RAW_BASE` in `validate_notebooks.py`. The PNG shows in Colab only after Axel
pushes. Follow the Notebook Edit Protocol (targeted edit, read back and assert).

### 3e. Ask before the next

"`<slug>` written and rendered. Ready for `<next-slug>`?"

---

## Step 4: Summary

| Slug | Kind | .mmd | Rendered | Embedded / used in |
|---|---|---|---|---|

Next step: `/validate-notebooks` for labs, `/build-slides` for slides.

---

## Notebook Edit Protocol (MANDATORY when embedding)

Follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`. Blind bulk index-based rewrites are forbidden.
