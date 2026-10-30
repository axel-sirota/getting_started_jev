---
description: Write one module's slide plan and slide diagrams (imp_files/slides/moduleNN_slides.md and moduleNN_diagrams.md) in the format /build-slides parses. One deck per module
---

Plan slides for module: $ARGUMENTS

(Argument: a module number, 1 to 4. Required.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module_0<N>_plan.md 2>/dev/null
```

- No manifest: "Run `/init-course` first."
- No module plan: "Run `/research-module <N>` first." The slides follow the module's Flow
  table, demos and lab, so they are planned after them.

---

This is how the webinar deck was made: a slide plan and a diagram doc first, approved by
Axel, then a mechanical build. This command writes the plan for ONE module's deck. It never
touches `deck/`.

**Normally you do not run this directly:** `/research-module N` runs it as Part 2, so the
notebook plan and the slide plan are approved together. Run it alone only to revise an
already approved module's slides.

**One deck per module.** Slides are numbered from 1 inside each module. Module 1's deck also
opens the course (title, agenda, meet CLINC150 triage) before its own content. Every other
deck starts with a module title slide.

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md` (module map, brand)
2. `imp_files/outline_getting_started_jev.md`
3. `plans/modules/module_<NN>_plan.md`: `## Flow`, `## Slide hooks`, `## Measured numbers`,
   `## Diagram Index`, and the demo and lab cells, so the slides match what Axel will
   actually show and every hop label matches the notebook
4. The previous module's slides file, if it exists, for continuity
5. `reference/slide_plan.reference.md` and `reference/diagrams.reference.md`: the format
   and density that worked. Copy the format exactly
6. `.claude/skills/jev-course/SKILL.md`, `.claude/skills/mermaid-diagrams/SKILL.md` and the
   `typesafe-ai` skill

## Research (MANDATORY)

Run `/research` (3 cycles minimum, built-in WebSearch / WebFetch only, never Kryla web
tools) on the module's concepts for a developer audience: every slide with a factual claim
gets a `Source:` line. Jev claims cite only docs.typesafe.ai, typesafe.ai or
github.com/typesafe-ai; every number comes from the plan's `## Measured numbers`. Log sources
in a `## Sources` section at the end of the slides file.

## Output: two files (parsed by deck/tools/extract-mmd.mjs, do not change the format)

`imp_files/slides/module<NN>_slides.md`:

```markdown
# Module <N>: <Title>, Slides

## Run of show

| Step | Slides | What happens |
| --- | --- | --- |

## Slides

### Slide 1 · <Title>

Layout: title slide | points left, diagram right | full diagram | lab holding slide

Badge: "Switch to the notebook: Demo 1"

- Point 1 (max 4 points, each one line)

```mermaid
<diagram>
```

Say: <speaker notes, 2 to 4 sentences, what the instructor says>

Source: [Link title](url)

## Module <N> playbook

## Sources
```

The heading separator is ` · ` (space, middle dot, space). The extractor matches
`### Slide N · Title` exactly.

### Badges and layout tweaks live in the plan (source of truth)

`/build-slides` rebuilds `deck/module<NN>/index.html` from this file, so anything the deck
shows must be written here, never hand-edited into the deck only.

- **Switch badge.** A slide where Axel sends the room to the notebook gets ONE line of its
  own, right after the Layout line, in exactly this form (straight double quotes, nothing
  after the closing quote):

  `Badge: "Switch to the notebook: Demo 1"`

  Labels are `Demo n` and `Lab n`, numbered in order, exactly the `## Demo n` / `## Lab n`
  sections of `course/module_NN/exercises.ipynb`. The slide right after a badge slide is
  where the room comes back: its title is exactly what the notebook's
  `## Back to the slides: <title>` cell names (validate_slides.py cross-checks both). No
  color or position in the line: the badge style and position live in `deck/css/theme.css`.
- **Big-diagram split** (points slide N plus a full-diagram page Nb): write the Layout line as
  `Layout: points only (big-diagram rule), then slide Nb with the diagram as full.`
- **Custom split columns**: append `Columns: A/B` to a split Layout line, e.g.
  `Layout: points left, diagram right. Columns: 32/68 (reason).`
- **Caption strip** under a full or split diagram: `Strip under the diagram: "TEXT"` in the
  Layout line. Lab holding slides use `Strip: "TEXT"`.

`validate_slides.py <N>` fails when a Badge line, a split page or a Columns clause in the plan
has no match in the deck, or the deck has a badge or split page the plan does not record.

`imp_files/slides/module<NN>_diagrams.md`: an index table (slide, title, layout, Mermaid
type), then every slide's diagram under the same `### Slide N · Title` heading,
byte-identical to the block in the slides file.

## Slide rules

- Explain well, diagram first: every slide except the title has one diagram that carries the
  idea; the points only label it. At most 2 short sentences of body text per slide
- Max 4 points per slide, one line each, no paragraphs
- Slide order follows the plan's `## Flow` table. Per concept:
  1. Concept slides (split or full): the why, the mental model, the diagram
  2. The last concept slide before a demo carries `Badge: "Switch to the notebook: Demo n"`
     and its Say line cues the notebook section
  3. The next slide is the one the notebook returns to (often "what we just saw" with the
     measured result)
- Lab: a lab setup slide (what you will build, the three levels: Guided, Core, Challenge
  optional) carrying `Badge: "Switch to the notebook: Lab n"`, then the debrief slide the
  notebook returns to, then a lesson slide (the one takeaway)
- `## Module N playbook` after the slides: step by step, what to say, backup if Jev or
  OpenAI is slow or rate-limited. It feeds speaker notes; it is not slides
- No timings in any content: no minutes columns, no "takes about N minutes", no lab timers.
  Axel paces live. Measured latencies (model_ms, p50) are numbers, not timings
- Developer audience: code names are fine (`system_one`, `Choice`, `confidence`); define a
  Jev term on the slide where it first appears
- Running case on every example: CLINC150 query triage
- No AI tells: no em dashes, en dashes, "not just X, it's Y", banned words in CLAUDE.md

## Review loop

After drafting, run `deck-sales-refute` (arc), `deck-marketing-refute` (copy),
`deck-diagram-refute` (diagrams), `deck-designer-refute` (visual load) and
`learner-engineer-refute` (does the explanation land, are the hops clear) on the files, then
the `-build` counterparts to strengthen. Fix what they find, run
`.venv/bin/python3 validate_slides.py <N>`, then show Axel a table: slide, title, layout,
diagram type, badge.

**Wait for approval before writing the final files.**

## Handoff

> Slides for Module <N> written to `imp_files/slides/module<NN>_slides.md` and
> `module<NN>_diagrams.md`.
>
> Next: `/build-diagrams slides <N>`, then `/build-slides <N>`.
