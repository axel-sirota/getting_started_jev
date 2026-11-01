---
description: Build a module's notebook diagrams one by one (problem and solution figures, including Module 1's "what Jev is" figures in Part 1's solution) as committed PNGs embedded by raw GitHub URL in an img tag with a fixed width
---

Build diagrams: $ARGUMENTS

(Argument: a module number. With no argument, list every unbuilt diagram and ask which module.)

## GUARD

```bash
ls plans/DECISIONS.md 2>/dev/null
```

If missing: "Run `/init-course` first."

Follow `.claude/skills/mermaid-diagrams/SKILL.md` for design rules, palette, rendering and
which beat needs which diagram.

---

## Step 1: Read context

1. The module plan's `## Diagram Index` (slug, cell, beat, what it shows)
2. The notebook cell (beat) that embeds each diagram, to see what it must serve
3. For a solution figure, its problem figure: shape them so before and after line up
4. `reference/diagram_examples/` and `reference/diagrams.reference.md` for shapes that worked

## Step 2: List and ask

```
Diagrams to build:
1. <slug>.mmd - <what it shows> - <Part k, beat>
...
I'll build them one at a time and ask for approval before each file.
```

Ask: "Ready to start with diagram 1?"

## Step 3: One at a time, approval between each

### 3a. Show the Mermaid source in chat first

```
Diagram <K>: <slug>
Shows: <one line>
Used in: <Part k, beat>

<mermaid source>

Does this look right? I'll write the file once you approve.
```

**Wait for approval** (skipped inside the build-module workflow). Optionally run the
`deck-diagram-build` and `deck-diagram-refute` agents on it first and show their verdict.

### 3b. Write the `.mmd`

`course/diagrams/module_NN/<slug>.mmd`: raw Mermaid, no fences, the brand line first.

### 3c. Render and look

```bash
cd deck && ./node_modules/.bin/mmdc -i ../course/diagrams/module_NN/<slug>.mmd -o ../course/diagrams/module_NN/<slug>.png -s 2 -b white -c tools/mermaid-config.json -C tools/inter.css
```

Read the PNG with the Read tool: legible, labels match the code. If `node_modules` is missing,
run `cd deck && PUPPETEER_SKIP_DOWNLOAD=1 npm ci` (ask first).

### 3d. Embed it in a figure cell (both notebooks)

Colab renders neither ```mermaid blocks nor cell attachments (it strips attachments), so the
notebook embeds the committed PNG by raw GitHub URL in its own figure cell, with an HTML
`<img>` tag and a fixed width:

```markdown
**Figure: <title> - <what to look at, one line>.**

<!-- DIAGRAM: <slug> -->
<img src="https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/course/diagrams/module_NN/<slug>.png" width="W" alt="<alt text that states the idea>">
```

`W sized from the PNG shape (W = 600 x png width / png height, kept to 420..750, rounded to 10; 700 for xychart-beta charts). Never markdown image syntax (`![alt](url)`):
Colab draws markdown images at full cell width and stretches them.

The prefix is `RAW_BASE` in `validate_notebooks.py`. The PNG shows in Colab only after Axel
pushes. Follow the Notebook Edit Protocol (targeted edit, read back and assert).

### 3e. Ask before the next

"`<slug>` written and rendered. Ready for `<next-slug>`?"

---

## Step 4: Summary

| Slug | Part, beat | .mmd | Rendered | Linked in both notebooks |
|---|---|---|---|---|

Next step: `/validate-notebooks <N> --pair --strict`.

---

## Notebook Edit Protocol (MANDATORY when linking)

Follow `.claude/NOTEBOOK_EDIT_PROTOCOL.md`. Blind bulk index-based rewrites are forbidden.
