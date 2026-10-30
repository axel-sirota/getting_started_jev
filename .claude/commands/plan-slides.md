---
description: Write one module's slide plan and slide diagrams (imp_files/slides/moduleNN_slides.md and moduleNN_diagrams.md) in the format /build-slides parses. One deck per module
---

Plan slides for module: $ARGUMENTS

(Argument: a module number, 1 to 10. Required.)

## GUARD

```bash
ls plans/DECISIONS.md plans/modules/module$(printf %02d $ARGUMENTS)_plan.md 2>/dev/null
```

- No manifest: "Run `/init-course` first."
- No module plan: "Run `/research-module <N>` first." The slides follow the module's demo
  and lab, so they are planned after them.

---

This is how the webinar deck was made: a slide plan and a diagram doc first, approved by
Axel, then a mechanical build. This command writes the plan for ONE module's deck. It never
touches `deck/`.

**Normally you do not run this directly:** `/research-module N` runs it as Part 2, so the
notebook plan and the slide plan are approved together. Run it alone only to revise an
already approved module's slides.

**One deck per module.** Slides are numbered from 1 inside each module. Module 1's deck also
opens the day (title, agenda, meet Harborview Life) before its own beats. Every other deck
starts with a module title slide.

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md` (module map, brand)
2. `imp_files/outline_foundations.md`
3. `plans/modules/module<NN>_plan.md`: `## The 5 beats`, `## Slide hooks`,
   `## Diagram Index`, `## Debrief questions`, and the demo and lab cells, so the slides
   match what Axel will actually show
4. The previous module's slides file, if it exists, for continuity
5. `reference/slide_plan.reference.md` and `reference/diagrams.reference.md`: the format
   and density that worked. Copy the format exactly
6. `.claude/skills/agentic-foundations/SKILL.md` and `.claude/skills/mermaid-diagrams/SKILL.md`

## Research (MANDATORY)

Run `/research` (3 cycles minimum) on the module's concepts for a business audience in
insurance: every slide with a factual claim gets a `Source:` line. Log sources in a
`## Sources` section at the end of the slides file.

## Output: two files (parsed by deck/tools/extract-mmd.mjs, do not change the format)

`imp_files/slides/module<NN>_slides.md`:

```markdown
# Module <N>: <Title>, Slides

## Run of show

| Beat | Slides | What happens |
| --- | --- | --- |

## Slides

### Slide 1 · <Title>

Layout: title slide | points left, diagram right | full diagram | lab holding slide

Badge: "Switch to the notebook: Part A"

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

- **Switch badge.** A slide where Axel moves to the notebook or the live demo gets ONE line of
  its own, right after the Layout line, in exactly this form (straight double quotes, nothing
  after the closing quote):

  `Badge: "Switch to the notebook: Part A"`

  Texts in use: `Switch to the notebook: Part A`, `Switch to the notebook: Part B`,
  `Switch to the notebook: Lab`, and for Module 7 `Switch to the live demo`,
  `Back from the demo`. No color or position in the line: the badge style and position live
  in `deck/css/theme.css` only.
- **Big-diagram split** (points slide N plus a full-diagram page Nb): write the Layout line as
  `Layout: points only (big-diagram rule), then slide Nb with the diagram as full.`
- **Custom split columns**: append `Columns: A/B` to a split Layout line, e.g.
  `Layout: points left, diagram right. Columns: 32/68 (reason).`
- **Caption strip** under a full or split diagram: `Strip under the diagram: "TEXT"` in the
  Layout line (as in Modules 4 and 8). Lab holding slides use `Strip: "TEXT"`.

`validate_slides.py <N>` fails when a Badge line, a split page or a Columns clause in the plan
has no match in the deck, or the deck has a badge or split page the plan does not record.

`imp_files/slides/module<NN>_diagrams.md`: an index table (slide, title, layout, Mermaid
type), then every slide's diagram under the same `### Slide N · Title` heading,
byte-identical to the block in the slides file.

## Slide rules

- Diagram-first: every slide except the title has a diagram that carries the idea
- Max 4 points per slide, one line each, no paragraphs
- The 5 beats, in slide order:
  1. A demo holding slide for the problem (layout `lab holding slide`, strip: "Demo:
     <what fails>"), Say line cues Part A of `moduleNN_<slug>.ipynb` (one notebook per
     module, which everyone uploads at the start of the module and runs together)
  2. Theory slides (split or full), the bulk of the deck
  3. A demo holding slide for the fix (strip: "Demo: <what now works>"), cues Part B
  4. A lab setup slide (what you will do) and a lab holding slide (strip: "Scroll to
     Lab: <name> at the bottom of your notebook, run its cells, click the link").
     Module 7 has none
  5. A lesson slide (split): the one takeaway and who owns it in their organization
- `## Module N playbook` after the slides: step by step per beat, what to say, backup if
  Bedrock or the proxy fails. It feeds speaker notes; it is not slides
- No timings in any content: no slot or beat minutes, no Minutes columns, no 'takes about N minutes/seconds', no lab timers. Axel paces live. Policy facts (grace periods, business days) are not timings. The validators fail on duration patterns. Titles, subtitles, strips, diagram labels, Say lines and the playbook
  included
- Plain words for non-coders. Define a term on the slide where it first appears
- Running case on every example: the Harborview Life Policyholder Service Agent
- Northwestern Mutual only on Module 1's title slide
- No AI tells: no em dashes, en dashes, "not just X, it's Y", banned words in CLAUDE.md

## Review loop

After drafting, run `deck-sales-refute` (arc), `deck-marketing-refute` (copy),
`deck-diagram-refute` (diagrams), `deck-designer-refute` (visual load) and
`learner-noncoder-refute` (jargon) on the files. Fix what they find, run
`.venv/bin/python3 validate_slides.py <N>`, then show Axel a table: slide, title, layout,
diagram type, points count.

**Wait for approval before writing the final files.**

## Handoff

> Slides for Module <N> written to `imp_files/slides/module<NN>_slides.md` and
> `module<NN>_diagrams.md`.
>
> Next: `/build-diagrams slides <N>`, then `/build-slides <N>`.
