---
description: Build one module's local Reveal.js deck in deck/moduleNN/ from imp_files/slides/moduleNN_slides.md and moduleNN_diagrams.md, the same way the platform engineering webinar deck was built
---

Build slides for module: $ARGUMENTS

(Argument: a module number, optionally with a slide range, e.g. `1` or `1 5-9`.)

## GUARD

```bash
ls plans/DECISIONS.md imp_files/slides/module$(printf %02d ${ARGUMENTS%% *})_slides.md imp_files/slides/module$(printf %02d ${ARGUMENTS%% *})_diagrams.md 2>/dev/null
```

- No slides file: stop, "Run `/plan-slides <N>` first."
- `deck/node_modules` missing: ask before running `cd deck && npm install`.

Every deck tool needs `DECK_MODULE=<N>` (they refuse to run without it).

## Pre-Work: MANDATORY Reading

1. `CLAUDE.md`, `plans/DECISIONS.md` (brand, audience)
2. `imp_files/slides/module<NN>_slides.md` and `module<NN>_diagrams.md`
3. `reference/deck_index.reference.html`: the working webinar deck. Reuse its section
   markup for each template, its Reveal config and its notes handling
4. `deck/css/theme.css`: shared Data Trainers brand (Inter, navy #1A3D4D, teal #40B8A6)
5. An already built `deck/moduleXX/index.html`, if any, so every module deck looks the same

## Scope

- Build only `### Slide N · Title` sections. The playbook feeds speaker notes only.
- The diagrams file is the diagram source. If a block differs from the slides file,
  `DECK_MODULE=<N> node tools/extract-mmd.mjs --check` reports it: stop and ask.

## Output (all inside `deck/module<NN>/`)

- `index.html`, linking the SHARED assets with `../`: `../vendor/reveal/reset.css`,
  `../vendor/reveal/reveal.css`, `../css/theme.css`, `../vendor/reveal/reveal.js`,
  `../vendor/reveal/plugin/notes/notes.js`. No CDN
- `diagrams/slide-NN.mmd` and `.svg`
- `notes.md`: every speaker note in slide order
- `BUILD_REPORT.md`
- `mermaid-overrides.json` only if a slide needs layout tuning

## Templates

| Layout line | Template | Body |
|---|---|---|
| points left, diagram right | split | points left 40%, diagram right 60%, both vertically centred |
| full diagram | full | diagram fills the body |
| title slide | title | course or module title, subtitle, no diagram |
| lab holding slide | lab | diagram as holding visual, bottom strip with the demo or lab instruction |
| points only (big-diagram rule) | points | points full width, then slide Nb with the diagram as full |

## Plan clauses the build must carry (the plan is the source of truth)

Never hand-edit these into `index.html` only: a rebuild would drop them. Read them from the
slide plan (syntax in `/plan-slides`) and emit them every build. `validate_slides.py <N>`
("plan vs deck") fails if plan and deck disagree.

| Plan line | Emit in `index.html` |
|---|---|
| `Badge: "TEXT"` (own line under the Layout line) | `<div class="switch-badge">TEXT</div>` as the LAST child of that slide's `<section>`, after `<aside class="notes">`. Exact text, no inline style. Position and look come from `deck/css/theme.css` only (top 6px, right 40px); never override `.switch-badge` in a deck |
| `Layout: points only (big-diagram rule), then slide Nb with the diagram as full.` | `<section data-slide="N" data-template="points">` then `<section data-slide="Nb" data-template="full">` with the diagram |
| `Layout: points left, diagram right. Columns: A/B` | split section plus, in the deck `<style>` block, `.reveal section[data-slide="N"] .body { grid-template-columns: A% B%; }` |
| `Layout: full diagram. Strip under the diagram: "TEXT"` | `class="has-caption"` on the section and `<div class="caption-strip">TEXT</div>` after the body, plus the `has-caption` / `.caption-strip` rules in the deck `<style>` block (pattern in `reference/deck_index.reference.html`) |
| `Layout: lab holding slide. Strip: "TEXT"` | `<div class="demo-strip"><span class="strip-label">TEXT</span></div>` |

Keep each deck's existing `<style>` block (lab row heights, split alignment, caption strip,
footer links) when rebuilding.

## Rules

- No timings in any content: no slot or beat minutes, no Minutes columns, no 'takes about N minutes/seconds', no lab timers. Axel paces live. Policy facts (grace periods, business days) are not timings. The validators fail on duration patterns. Applies to titles, subtitles, strips, diagram
  labels and speaker notes; validate_slides.py fails on them.

- Text verbatim from the plan: titles, points, sources. Don't rewrite, don't add points.
  More than 4 points: stop and ask.
- Diagrams: `cd deck && DECK_MODULE=<N> node tools/extract-mmd.mjs --all && DECK_MODULE=<N> node tools/render-diagrams.mjs`.
  Config `deck/tools/mermaid-config.json`; per-slide layout tweaks go in
  `deck/module<NN>/mermaid-overrides.json`, never in the `.mmd`.
- A diagram that fails to render: keep the slide, show the source in a monospace box, list
  it in the report.
- Readability: diagram text at least 22 px at 1920x1080. If a split diagram is under that,
  use the big-diagram rule (points slide N, then Nb full) and log it.
- Speaker notes from each `Say:` line; badge slides and lab holding slides append the
  matching step from the `## Module N playbook` (which notebook section, what to run).
- `Source:` lines become a small footer with link titles.
- 16:9 at 1920x1080, titles at least 44 px, points at least 28 px. Check at 1280x720 too.
- Slide number bottom right, showing the plan number (4, 4b, 5). No animations.

## Verify

1. `cd deck && DECK_MODULE=<N> node tools/shoot.mjs <slides...>`: screenshots at 1920 and
   1280 into `deck/module<NN>/checks/`, with the smallest diagram text per slide. Read the PNGs.
2. `.venv/bin/python3 validate_slides.py <N>`
3. Optionally `deck-designer-refute` and `deck-diagram-refute` on the screenshots.
4. ALWAYS package at the end (Axel distributes the PDF and presents from anywhere):
   `cd deck && DECK_MODULE=<N> node tools/package-deck.mjs`. It writes
   `deck/module<NN>/Getting-Started-with-Jev-Module-<NN>.pdf` (committed),
   `deck/dist/module<NN>/` (self-contained: index.html + css + vendor + diagrams + PDF +
   speaker-notes.md; open index.html anywhere, S for speaker view) and
   `deck/dist/Getting-Started-with-Jev-Module-<NN>.zip` (dist/ is gitignored, regenerable).
   It uses a complete Chrome from the puppeteer cache because decktape's bundled one can be a
   half-finished download. Read 2 or 3 PDF pages to confirm they render.
5. `cd deck && DECK_MODULE=<N> node tools/check-pdf.mjs`: page count, links per page against
   the deck, embedded fonts, no raster images.

Build in batches of at most 5 slides, show screenshots, ask before the next batch.

## Build report

Table of every slide: number, title, template, diagram rendered, points count, notes
present, min diagram text at 1920. Then "Changes from the plan, and why".

## Done when

All planned slides render offline from `deck/module<NN>/index.html`, every diagram
renders, no notes missing, speaker view (S key) shows notes.
