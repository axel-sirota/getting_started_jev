#!/usr/bin/env python3
"""
Slide and diagram validator for Getting Started with Jev.

Validates the webinar-style slide pipeline, one deck per module: for module N,
imp_files/slides/moduleNN_slides.md and moduleNN_diagrams.md (written by /plan-slides N)
and the built deck in deck/moduleNN/ (written by /build-slides N); plus every notebook and
starter Mermaid source in course/.

Slide plan (imp_files/slides/moduleNN_slides.md):
     1. Headings are "### Slide N · Title" (middle dot), numbered 1..N with no gaps or repeats.
     2. Each slide has a Layout line with a known template.
     3. At most 4 points per slide, each one line.
     4. Every slide except the title slide has exactly one mermaid block.
     5. Every slide has a "Say:" line (speaker notes).
     6. Slides with points have a "Source:" line (warning only). A Source line that names
        an internal repo path (plans/, course/, harborview/, *.py) is a warning too.
     7. Run of show table present.

Slide diagrams (imp_files/slides/moduleNN_diagrams.md):
     8. Every slide with a diagram in the plan has the same block in the diagrams file,
        byte-identical (the extractor builds deck/moduleNN/diagrams from it).

Mermaid sources (course/diagrams/*.mmd, deck/moduleNN/diagrams/*.mmd,
course/labs/starter/*.mmd, and the blocks in both module slide files):
     9. Starts with a known diagram type.
    10. ASCII only (non-ASCII breaks labels and fonts).
    11. Node count at most 10 (lab) / 8 (slide); warning above.
    12. Lab diagrams have a rendered .png next to them (warning).
    13. Starter files contain at least one TODO node for learners to replace.

Copy (all of the above):
    14. AI tells: em dash, en dash, Unicode multiplication, banned phrases.
    15. Denylist names (validation/denylist.txt) only on Module 1, slide 1.
    16. No timings anywhere (plan, playbook, diagrams, deck, notes): no slot or beat
        minutes, no Minutes columns, no lab timers or wait estimates. Axel paces live.
        Policy facts and measured metrics are allowlisted (TIMING_ALLOW_RE).

Deck (deck/moduleNN/index.html, if built):
    17. No CDN: every script and stylesheet is local.
    18. Every section has speaker notes.
    19. Plan vs deck: every plan line `Badge: "TEXT"` has <div class="switch-badge">TEXT</div>
        as the last child of that slide's section, and every deck badge has a plan line; no
        deck overrides .switch-badge; big-diagram split pages (Nb), `Columns: A/B` and
        `Strip under the diagram: "TEXT"` clauses in the plan's Layout line match the deck.

Slides vs notebook (course/module_NN/exercises.ipynb, if built):
    20. Every badge "Switch to the notebook: X" has a "## X" section in the notebook, in the
        same order, and every notebook "## Demo n" / "## Lab n" section has a badge.
    21. Each notebook "## Back to the slides: T" names the title of the slide right after
        the badge slide that sent the room to that section.

Optional:
    --render  parse every .mmd with mermaid-cli (needs `cd deck && npm install`)

Usage:
    .venv/bin/python3 validate_slides.py            # every planned module
    .venv/bin/python3 validate_slides.py 1          # module 1 only
    .venv/bin/python3 validate_slides.py 1 --render

Exit codes: 0 all passed, 1 one or more failures.
"""
from __future__ import annotations

import argparse
import html as html_lib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DECK = ROOT / "deck"                       # shared tools, css, vendor, node_modules
SLIDES_DIR = ROOT / "imp_files" / "slides"

# One deck per module; use_module() points these at the module being checked.
MODULE = 1
PLAN = SLIDES_DIR / "module01_slides.md"
DIAGRAM_DOC = SLIDES_DIR / "module01_diagrams.md"
MODULE_DECK = DECK / "module01"


def use_module(n: int) -> None:
    """Point the checks at module n's slides file, diagrams file and deck folder."""
    global MODULE, PLAN, DIAGRAM_DOC, MODULE_DECK
    MODULE = n
    PLAN = SLIDES_DIR / f"module{n:02d}_slides.md"
    DIAGRAM_DOC = SLIDES_DIR / f"module{n:02d}_diagrams.md"
    MODULE_DECK = DECK / f"module{n:02d}"


def planned_modules() -> list[int]:
    """Modules that have a slides file."""
    return sorted(int(m.group(1)) for p in SLIDES_DIR.glob("module*_slides.md")
                  if (m := re.match(r"module(\d+)_slides\.md$", p.name)))
DENYLIST_FILE = ROOT / "validation" / "denylist.txt"

SLIDE_HEAD_RE = re.compile(r"^### Slide (\d+)([a-z]?) · (.+)$", re.MULTILINE)
BAD_HEAD_RE = re.compile(r"^###\s+Slide\s+\d+\S*\s+(?!· ).+$", re.MULTILINE)
MERMAID_RE = re.compile(r"```mermaid\n([\s\S]*?)```")
# A projected Source footer must not name repo files (plans/ is private, code paths mean
# nothing to the room). Link targets are stripped before this check.
INTERNAL_PATH_RE = re.compile(r"plans/|\.py\b|course/|DECISIONS\.md")
LAYOUTS = {
    "points left, diagram right": "split",
    "split": "split",
    "full diagram": "full",
    "full": "full",
    "title slide": "title",
    "title": "title",
    "lab holding slide": "lab",
    "holding slide": "lab",
    "lab": "lab",
    "points only": "points",
    "points": "points",
}
DIAGRAM_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "erDiagram",
    "journey", "gantt", "pie", "mindmap", "timeline", "quadrantChart", "xychart-beta",
    "block-beta", "sankey-beta", "kanban",
)
NODE_RE = re.compile(r"(?:^|-->|---|-\.->|==>|-\.-|&)\s*([A-Za-z][\w]*)\s*[\[\(\{>]", re.MULTILINE)
ACTOR_RE = re.compile(r"^\s*(participant|actor)\s+(\w+)", re.MULTILINE)

AI_TELL_CHARS = [("—", "em dash"), ("–", "en dash"), ("×", "Unicode multiplication")]
BANNED_PHRASES = [
    "delve", "leverage", "robust", "seamless", "unlock", "elevate", "empower", "harness",
    "game-changer", "game changer", "cutting-edge", "cutting edge", "revolutionize",
    "transformative", "in today's fast-paced", "navigate the landscape", "it's not just",
    "isn't just", "arguably", "it's worth noting", "it's important to remember",
]
BANNED_RE = re.compile(r"\b(" + "|".join(re.escape(p) for p in BANNED_PHRASES) + r")", re.IGNORECASE)

# No timings in any content (same rule as validate_notebooks.py): Axel paces the day live.
_NUMWORD = (r"(?:a|an|one|two|three|four|five|six|seven|eight|nine|ten|twelve|fifteen|"
            r"twenty|thirty|forty|fifty|sixty|a\s+few|a\s+couple\s+of|several)")
TIMING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:(?:-|to|or)\s*\d+(?:\.\d+)?\s*)?-?\s*"
               r"(?:min|mins|minutes?|secs?|seconds?)\b", re.IGNORECASE),
    re.compile(r"\b(?:about|around|roughly|under|over|up\s+to|takes?|another|in|for|wait|after|than)\s+"
               r"(?:about\s+)?" + _NUMWORD + r"(?:\s+(?:to|or)\s+" + _NUMWORD + r")?\s+"
               r"(?:more\s+)?(?:minutes?|seconds?)\b", re.IGNORECASE),
    re.compile(r"\b" + _NUMWORD + r"\s+(?:to|or)\s+" + _NUMWORD + r"\s+(?:minutes?|seconds?)\b",
               re.IGNORECASE),
    re.compile(r"\|\s*Min(?:utes)?\s*\|", re.IGNORECASE),
]
URL_RE = re.compile(r"https?://\S+")
TIMING_ALLOW_RE = re.compile(
    r"grace|business\s+days?|\bhours?\b|slowest|latency|\bMETR\b|model_ms|time\s+taken",
    re.IGNORECASE)


def timing_errors(label: str, text: str) -> list[str]:
    """Lines that state a duration, a beat or slot length, a lab timer or a wait estimate."""
    errs = []
    for line in text.splitlines():
        if TIMING_ALLOW_RE.search(line):
            continue
        bare = URL_RE.sub("", line)  # web addresses like .../5-sec-core/ are not timings
        if any(p.search(bare) for p in TIMING_PATTERNS):
            errs.append(f"{label}: timing in content (Axel paces live): {line.strip()[:80]}")
    return errs


class Report:
    """Collects failures and warnings per section."""

    def __init__(self) -> None:
        self.sections: list[tuple[str, list[str], list[str]]] = []
        self.prefix = ""

    def add(self, name: str, errs: list[str], warns: list[str] | None = None) -> None:
        self.sections.append((self.prefix + name, errs, warns or []))

    def print(self) -> bool:
        failed = False
        for name, errs, warns in self.sections:
            status = "PASS" if not errs else "FAIL"
            failed |= bool(errs)
            print(f"\n[{name}] status={status}")
            for e in errs:
                print(f"  FAIL  {e}")
            for w in warns:
                print(f"  WARN  {w}")
        return failed


def load_denylist() -> list[str]:
    if not DENYLIST_FILE.exists():
        return []
    return [l.strip() for l in DENYLIST_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def split_slides(text: str) -> list[tuple[str, str, str]]:
    """Return (number, title, body) per '### Slide N · Title' section."""
    heads = list(SLIDE_HEAD_RE.finditer(text))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[h.end():end]
        # A slide section stops at the next '## ' heading (module header, playbook).
        nxt = re.search(r"^## ", body, re.MULTILINE)
        if nxt:
            body = body[:nxt.start()]
        out.append((h.group(1) + h.group(2), h.group(3).strip(), body))
    return out


def copy_errors(label: str, text: str) -> list[str]:
    errs = []
    for ch, name in AI_TELL_CHARS:
        if ch in text:
            line = next((l for l in text.splitlines() if ch in l), "")
            errs.append(f"{label}: {name}: {line.strip()[:70]}")
    for m in BANNED_RE.finditer(text):
        errs.append(f"{label}: banned phrase '{m.group(0)}'")
    return errs


def denylist_errors(label: str, text: str, names: list[str]) -> list[str]:
    return [f"{label}: real name '{n}' (allowed on slide 1 only)"
            for n in names if re.search(r"\b" + re.escape(n) + r"\b", text, re.IGNORECASE)]


# --------------------------------------------------------------------------
# Slide plan
# --------------------------------------------------------------------------
def check_plan(report: Report, names: list[str]) -> dict[int, str]:
    """Validate the slide plan. Returns {slide number: mermaid block} for parity."""
    if not PLAN.exists():
        report.add("slide plan", [], [f"{PLAN.relative_to(ROOT)} not written yet (/plan-slides)"])
        return {}
    text = PLAN.read_text(encoding="utf-8")
    errs, warns = [], []
    if "Run of show" not in text:
        errs.append("no 'Run of show' table")
    for m in BAD_HEAD_RE.finditer(text):
        errs.append(f"heading not in '### Slide N · Title' form: {m.group(0)[:70]}")

    slides = split_slides(text)
    if not slides:
        errs.append("no '### Slide N · Title' sections")
    numbers = [int(re.match(r"\d+", n).group(0)) for n, _, _ in slides if n.isdigit()]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        errs.append(f"slide numbers must run 1..{len(numbers)} in order (got {numbers[:12]}...)")

    blocks: dict[int, str] = {}
    for num, title, body in slides:
        label = f"slide {num}"
        layout_m = re.search(r"^Layout:\s*(.+)$", body, re.MULTILINE)
        layout = None
        if not layout_m:
            errs.append(f"{label}: no Layout line")
        else:
            raw = layout_m.group(1).strip().lower()
            layout = next((v for k, v in LAYOUTS.items() if raw.startswith(k)), None)
            if layout is None:
                errs.append(f"{label}: unknown layout '{layout_m.group(1)[:40]}'")
        points = [l for l in body.splitlines() if re.match(r"^[-*] ", l)]
        if len(points) > 4:
            errs.append(f"{label}: {len(points)} points (max 4)")
        mermaid = MERMAID_RE.findall(body)
        if layout == "title":
            if mermaid:
                errs.append(f"{label}: title slide must not have a diagram")
        elif len(mermaid) != 1:
            errs.append(f"{label}: needs exactly one mermaid block (got {len(mermaid)})")
        else:
            if num.isdigit():
                blocks[int(num)] = mermaid[0]
            errs += [f"{label}: {e}" for e in check_mermaid_text(mermaid[0], limit=8)[0]]
        if not re.search(r"^Say:\s*\S", body, re.MULTILINE):
            errs.append(f"{label}: no 'Say:' speaker notes")
        if points and not re.search(r"^Source:", body, re.MULTILINE):
            warns.append(f"{label}: points without a Source line")
        for src in re.findall(r"^Source:(.*)$", body, re.MULTILINE):
            if INTERNAL_PATH_RE.search(re.sub(r"\]\([^)]*\)", "]", src)):
                warns.append(f"{label}: Source footer names an internal repo path (projected "
                             f"and shipped in the deck zip; keep paths in the notes)")
        errs += copy_errors(label, f"{title}\n{body}")
        if not (MODULE == 1 and num == "1"):   # client name only on the day's title slide
            errs += denylist_errors(label, f"{title}\n{body}", names)
    errs += timing_errors("slides.md", text)
    report.add(f"slide plan ({len(slides)} slides)", errs, warns)
    return blocks


def check_diagram_doc(report: Report, plan_blocks: dict[int, str]) -> None:
    if not DIAGRAM_DOC.exists():
        if plan_blocks:
            report.add("slide diagrams doc", [f"{DIAGRAM_DOC.relative_to(ROOT)} missing"])
        return
    text = DIAGRAM_DOC.read_text(encoding="utf-8")
    doc_blocks: dict[int, str] = {}
    for num, _, body in split_slides(text):
        m = MERMAID_RE.search(body)
        if m and num.isdigit():
            doc_blocks[int(num)] = m.group(1)
    errs = []
    for n, block in plan_blocks.items():
        if n not in doc_blocks:
            errs.append(f"slide {n}: diagram missing from diagrams.md")
        elif doc_blocks[n] != block:
            errs.append(f"slide {n}: diagrams.md block differs from the slide plan")
    for n in doc_blocks:
        if n not in plan_blocks:
            errs.append(f"slide {n}: in diagrams.md but not in the slide plan")
    errs += copy_errors("diagrams.md", text)
    errs += timing_errors("diagrams.md", text)
    report.add(f"slide diagrams doc ({len(doc_blocks)} blocks)", errs)


# --------------------------------------------------------------------------
# Mermaid files
# --------------------------------------------------------------------------
def count_nodes(src: str) -> int:
    nodes = set(NODE_RE.findall(src)) | {m[1] for m in ACTOR_RE.findall(src)}
    return len(nodes)


def check_mermaid_text(src: str, limit: int) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    body = "\n".join(l for l in src.splitlines() if not l.strip().startswith("%%"))
    first = next((l.strip() for l in body.splitlines() if l.strip()), "")
    if not first.startswith(DIAGRAM_TYPES):
        errs.append(f"unknown diagram type '{first[:30]}'")
    bad = sorted({ch for ch in src if ord(ch) > 127})
    if bad:
        errs.append(f"non-ASCII characters: {' '.join(bad)}")
    n = count_nodes(src)
    if n > limit:
        warns.append(f"{n} nodes (aim for at most {limit}; split it)")
    return errs, warns


def check_mmd_files(report: Report, names: list[str], scope: str) -> list[Path]:
    """scope "shared": notebook and starter diagrams; scope "module": this module's slides."""
    if scope == "shared":
        groups = [
            ("lab diagrams", sorted((ROOT / "course" / "diagrams").rglob("*.mmd")), 10),
            ("starter diagrams", sorted((ROOT / "course" / "labs" / "starter").glob("*.mmd")), 12),
        ]
    else:
        groups = [("slide diagrams", sorted((MODULE_DECK / "diagrams").glob("*.mmd")), 8)]
    all_files: list[Path] = []
    for name, files, limit in groups:
        if not files:
            continue
        all_files += files
        errs, warns = [], []
        for f in files:
            if f.name.endswith(".original.mmd"):
                continue
            src = f.read_text(encoding="utf-8")
            label = str(f.relative_to(ROOT))
            e, w = check_mermaid_text(src, limit)
            errs += [f"{label}: {x}" for x in e]
            warns += [f"{label}: {x}" for x in w]
            errs += copy_errors(label, src)
            errs += timing_errors(label, src)
            errs += denylist_errors(label, src, names)
            if name == "lab diagrams" and not f.with_suffix(".png").exists():
                warns.append(f"{label}: no rendered .png (/build-diagrams)")
            if name == "starter diagrams" and "TODO" not in src:
                errs.append(f"{label}: starter file has no TODO node for learners")
        report.add(f"{name} ({len(files)})", errs, warns)
    return all_files


def render_check(report: Report, files: list[Path]) -> None:
    """Parse every .mmd with mermaid-cli into a throwaway SVG."""
    mmdc = DECK / "node_modules" / ".bin" / "mmdc"
    if not mmdc.exists():
        report.add("render", ["deck/node_modules missing: run `cd deck && npm install`"])
        return
    errs = []
    config = DECK / "tools" / "mermaid-config.json"
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            out = Path(tmp) / (f.stem + ".svg")
            r = subprocess.run([str(mmdc), "-i", str(f), "-o", str(out), "-c", str(config), "-q"],
                               capture_output=True, text=True, timeout=120)
            if r.returncode != 0:
                lines = (r.stderr or r.stdout).strip().splitlines()
                msg = next((l.strip() for l in lines if "rror" in l and not l.strip().startswith("at ")),
                           lines[0].strip() if lines else "unknown")
                errs.append(f"{f.relative_to(ROOT)}: render failed: {msg[:140]}")
    report.add(f"render ({len(files)} files)", errs)


# --------------------------------------------------------------------------
# Built deck
# --------------------------------------------------------------------------
def check_deck(report: Report) -> None:
    index = MODULE_DECK / "index.html"
    if not index.exists():
        return
    html = index.read_text(encoding="utf-8")
    errs, warns = [], []
    for m in re.finditer(r"""<(?:script|link)[^>]+(?:src|href)=["'](https?:)?//[^"']+["']""", html):
        errs.append(f"external asset (no CDN allowed): {m.group(0)[:90]}")
    sections = re.findall(r"<section\b[\s\S]*?</section>", html)
    for i, s in enumerate(sections, 1):
        if 'class="notes"' not in s:
            errs.append(f"section {i}: no speaker notes")
    errs += copy_errors(str(index.relative_to(ROOT)), re.sub(r"<[^>]+>", " ", html))
    errs += timing_errors(str(index.relative_to(ROOT)), re.sub(r"<[^>]+>", " ", html))
    notes = MODULE_DECK / "notes.md"
    if notes.exists():
        errs += timing_errors(str(notes.relative_to(ROOT)), notes.read_text(encoding="utf-8"))
    # Plan vs projected: a split page (Nb, big-diagram rule) makes the deck drift from the plan
    planned = len(SLIDE_HEAD_RE.findall(PLAN.read_text(encoding="utf-8"))) if PLAN.exists() else 0
    split_pages = re.findall(r'data-slide="(\d+[a-z])"', html)
    if planned and len(sections) != planned:
        warns.append(f"deck has {len(sections)} pages but the plan has {planned} slides"
                     + (f" (split pages: {', '.join(split_pages)})" if split_pages else ""))
    report.add(f"deck ({len(sections)} sections)", errs, warns)


BADGE_LINE_RE = re.compile(r'^Badge: "([^"\n]+)"$', re.MULTILINE)
ANY_BADGE_LINE_RE = re.compile(r"^.*\bBadge\b.*$", re.MULTILINE)
SPLIT_PAGE_RE = re.compile(r"^Layout:\s*points only \(big-diagram rule\), then slide (\d+b)\b",
                           re.MULTILINE)
COLUMNS_RE = re.compile(r"^Layout:.*\bColumns: (\d+)/(\d+)\b", re.MULTILINE)
SECTION_RE = re.compile(r'<section\b[^>]*\bdata-slide="([^"]+)"[^>]*>([\s\S]*?)</section>')
DECK_BADGE_RE = re.compile(r'<div class="switch-badge">([^<]+)</div>')
CAPTION_RE = re.compile(r'^Layout:.*\bStrip under the diagram: "([^"\n]+)"', re.MULTILINE)
DECK_CAPTION_RE = re.compile(r'<div class="caption-strip">([^<]+)</div>')


def check_plan_vs_deck(report: Report) -> None:
    """The slide plan is the source of truth for what /build-slides adds by hand.

    Badges: every plan line `Badge: "TEXT"` (own line, inside a slide section) needs
    `<div class="switch-badge">TEXT</div>` as the last child of that slide's <section>,
    and every switch-badge in the deck needs a matching plan line. Also: a big-diagram
    split recorded in the plan has its Nb page, and a `Columns: A/B` clause has its CSS.
    """
    index = MODULE_DECK / "index.html"
    if not PLAN.exists() or not index.exists():
        return
    text = PLAN.read_text(encoding="utf-8")
    html = index.read_text(encoding="utf-8")
    errs: list[str] = []
    plan_badges: dict[str, str] = {}
    plan_splits: set[str] = set()
    plan_cols: dict[str, tuple[str, str]] = {}
    plan_caps: dict[str, str] = {}
    for num, _, body in split_slides(text):
        for line in ANY_BADGE_LINE_RE.findall(body):
            if line.lstrip().startswith("Badge") and not BADGE_LINE_RE.fullmatch(line.strip()):
                errs.append(f'slide {num}: badge line not in the form Badge: "TEXT": {line.strip()[:70]}')
        found = BADGE_LINE_RE.findall(body)
        if len(found) > 1:
            errs.append(f"slide {num}: {len(found)} Badge lines (one per slide)")
        if found:
            plan_badges[num] = found[0].strip()
        if (m := SPLIT_PAGE_RE.search(body)):
            plan_splits.add(m.group(1))
        if (m := COLUMNS_RE.search(body)):
            plan_cols[num] = (m.group(1), m.group(2))
        if (m := CAPTION_RE.search(body)):
            plan_caps[num] = m.group(1).strip()

    deck_badges: dict[str, str] = {}
    deck_ids: set[str] = set()
    deck_caps: dict[str, str] = {}
    for sid, inner in SECTION_RE.findall(html):
        deck_ids.add(sid)
        if (cm := DECK_CAPTION_RE.search(inner)):
            deck_caps[sid] = html_lib.unescape(cm.group(1)).strip()
        badges = DECK_BADGE_RE.findall(inner)
        if len(badges) > 1:
            errs.append(f"deck slide {sid}: {len(badges)} switch badges")
        if badges:
            deck_badges[sid] = badges[0].strip()
            if not re.search(r'<div class="switch-badge">[^<]+</div>\s*$', inner):
                errs.append(f"deck slide {sid}: switch-badge is not the last child of its <section>")
    if "switch-badge" in re.sub(r'<div class="switch-badge">', "", html):
        errs.append("deck styles or markup override .switch-badge (its position lives in deck/css/theme.css only)")

    for sid, txt in plan_badges.items():
        if sid not in deck_badges:
            errs.append(f'slide {sid}: plan Badge "{txt}" has no switch-badge in the deck')
        elif deck_badges[sid] != txt:
            errs.append(f'slide {sid}: plan Badge "{txt}" but deck badge "{deck_badges[sid]}"')
    for sid, txt in deck_badges.items():
        if sid not in plan_badges:
            errs.append(f'deck slide {sid}: switch-badge "{txt}" has no Badge line in the plan')

    for nb in sorted(plan_splits):
        if nb not in deck_ids:
            errs.append(f"slide {nb}: plan records a big-diagram split page, deck has no data-slide=\"{nb}\"")
    for nb in sorted(i for i in deck_ids if re.fullmatch(r"\d+b", i)):
        if nb not in plan_splits:
            errs.append(f"deck slide {nb}: split page not recorded in the plan's Layout line")
    for num, (a, b) in plan_cols.items():
        want = f'section[data-slide="{num}"] .body {{ grid-template-columns: {a}% {b}%; }}'
        if want not in html:
            errs.append(f"slide {num}: plan Columns {a}/{b} but the deck style block lacks `{want}`")

    for sid, txt in plan_caps.items():
        if deck_caps.get(sid) != txt:
            errs.append(f'slide {sid}: plan strip "{txt[:50]}" but deck caption-strip '
                        f'"{(deck_caps.get(sid) or "(none)")[:50]}"')
    for sid in deck_caps:
        if sid not in plan_caps:
            errs.append(f"deck slide {sid}: caption-strip not recorded as 'Strip under the diagram' in the plan")

    report.add(f"plan vs deck ({len(plan_badges)} badges, {len(plan_splits)} split pages, "
               f"{len(plan_caps)} strips)", errs)


SWITCH_PREFIX = "Switch to the notebook: "


def check_hops_vs_notebook(report: Report) -> None:
    """Badges "Switch to the notebook: X" vs the notebook's "## X" sections (same order), and
    each "## Back to the slides: T" names the slide right after that badge slide."""
    notebook = ROOT / "course" / f"module_{MODULE:02d}" / "exercises.ipynb"
    if not PLAN.exists() or not notebook.exists():
        return
    sys.path.insert(0, str(ROOT))
    from validate_notebooks import load_cells, notebook_hops

    slides = [(num, title, body) for num, title, body in split_slides(PLAN.read_text(encoding="utf-8"))
              if num.isdigit()]
    badges = []   # (index in slides, label X)
    for idx, (num, _, body) in enumerate(slides):
        for txt in BADGE_LINE_RE.findall(body):
            if txt.startswith(SWITCH_PREFIX):
                badges.append((idx, txt[len(SWITCH_PREFIX):].strip()))
    hops = notebook_hops(load_cells(notebook))
    to_labels = [label for kind, label in hops if kind == "to"]
    errs = []
    if [label for _, label in badges] != to_labels:
        errs.append(f"badge order {[l for _, l in badges]} != notebook sections {to_labels}")
    by_label = {label: idx for idx, label in badges}
    for (kind, label), nxt in zip(hops, hops[1:] + [("", "")]):
        if kind != "to":
            continue
        if label not in by_label:
            errs.append(f'notebook "## {label}" has no slide badge "{SWITCH_PREFIX}{label}"')
            continue
        if nxt[0] != "back":
            continue   # validate_notebooks.py reports the missing Back cell
        idx = by_label[label]
        want = slides[idx + 1][1] if idx + 1 < len(slides) else "(no slide after the badge)"
        if nxt[1] != want:
            errs.append(f'"{label}" returns to "{nxt[1]}" but the slide after slide '
                        f'{slides[idx][0]} is "{want}"')
    report.add(f"slides vs notebook ({len(badges)} hops)", errs)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate slide plans, diagrams and decks (one per module).")
    ap.add_argument("module", nargs="?", type=int, help="module number (default: every planned module)")
    ap.add_argument("--render", action="store_true", help="parse every .mmd with mermaid-cli")
    args = ap.parse_args()

    names = load_denylist()
    report = Report()
    files = check_mmd_files(report, names, "shared")
    modules = [args.module] if args.module else planned_modules()
    for n in modules:
        use_module(n)
        report.prefix = f"module {n:02d} "
        blocks = check_plan(report, names)
        check_diagram_doc(report, blocks)
        files += check_mmd_files(report, names, "module")
        check_deck(report)
        check_plan_vs_deck(report)
        check_hops_vs_notebook(report)
    report.prefix = ""
    if args.render:
        render_check(report, files)
    if not report.sections:
        print("Nothing to validate yet (no imp_files/slides/moduleNN_slides.md, no diagrams).")
        return 0
    failed = report.print()
    print("\nNot checked (do these by hand): diagram text at least 22 px "
          "(`cd deck && DECK_MODULE=N node tools/shoot.mjs`), the deck at 1280x720, speaker view.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
