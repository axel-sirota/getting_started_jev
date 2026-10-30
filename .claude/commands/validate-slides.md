---
description: Validate one module's slide plan, slide diagrams and deck (or every planned module), plus notebook and starter Mermaid files
---

# Validate Slides

Validate: $ARGUMENTS

(Argument: a module number, optionally `--render`. Nothing = every planned module.)

`validate_slides.py` at the repo root. Its docstring is the authoritative check list.
Change a check in the script and in this file together. One deck per module.

## What it checks

| Area | Checks |
|---|---|
| `imp_files/slides/moduleNN_slides.md` | `### Slide N · Title` headings numbered 1..N; known Layout; max 4 points; one mermaid block per slide except title slides; `Say:` notes; `Source:` when there are points (warning); a `Source:` line naming an internal repo path such as `plans/` or a `.py` file (warning) |
| `imp_files/slides/moduleNN_diagrams.md` | Every plan diagram present and byte-identical (the deck is built from this file) |
| `deck/moduleNN/diagrams/*.mmd` | Known diagram type; ASCII only; node count (warning above 8) |
| `course/diagrams/`, `course/labs/starter/` `.mmd` | Same, limit 10; notebook `.png` rendered (warning); starter files have a `TODO` node |
| Copy | Em dash, en dash, Unicode multiplication, banned phrases from CLAUDE.md |
| Real names | `validation/denylist.txt` names only on Module 1, slide 1 (the day's title slide) |
| `deck/moduleNN/index.html` | No CDN assets; every section has speaker notes |
| `--render` | Parses every `.mmd` with mermaid-cli using `deck/tools/mermaid-config.json` |

## Usage

```bash
.venv/bin/python3 validate_slides.py 1
.venv/bin/python3 validate_slides.py 1 --render
.venv/bin/python3 validate_slides.py
```

## Not checked (do these by hand)

- Diagram text at least 22 px at 1920x1080: `cd deck && DECK_MODULE=N node tools/shoot.mjs <slide>`
- The deck at 1280x720, speaker view (S key) shows notes

## When to run

- After `/plan-slides N`, before asking Axel to approve
- After `/build-diagrams slides N` (with `--render`)
- After every `/build-slides N` batch
