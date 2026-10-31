#!/usr/bin/env python3
"""
Notebook validator for Getting Started with Jev.

Learners run every notebook in Google Colab. Notebooks import frameworks only (typesafe,
openai, datasets, transformers, sklearn, pandas, matplotlib); every Jev and LLM call is a
visible cell. Keys are typed in with getpass (never Colab secrets, never a literal). Rules:
plans/DECISIONS.md, plans/NOTEBOOK_STYLE.md, the mermaid-diagrams skill.

Notebooks:
    course/module_NN/exercises.ipynb     demo cells, three-tier LAB cells with `# YOUR CODE`
    course/module_NN/solutions.ipynb     same cells, labs solved, FALLBACK cells removed

Every notebook (the whole class runs in it, there are no slides):
    title cell with "## What you will be able to do"; first code cell is a pinned `%pip
    install`; a key cell reading TYPESAFE_API_KEY from the environment or getpass; no Colab
    secrets; a 77-char banner with a known kind on every code cell (except %pip and
    %%writefile cells); at most 6 markdown cells in a row; syntax and cross-cell pyflakes;
    diagrams as committed PNGs linked by raw GitHub URL (.mmd master with the brand line); no
    keys or real names; no AI tells; the 4 beats per Part; Summary cell last; outputs cleared.
Anatomy (the 4 beats): Module 1 opens with "## Part 0: What is Jev" (markdown and diagrams
only). Every "## Part k: <concept>" then has, in order:
    ### 1. The problem      markdown, at least one diagram, no code
    ### 2. The solution     markdown, at least one diagram, no code
    ### 3. Demo             at least one DEMO code cell
    ### 4. Lab k: <title>   markdown (#### Your Task, Expected Output, Hints, one #### Level
                            section per tier), then three LAB cells in order:
        # LAB k.1 (Guided)              `= None  # YOUR CODE` slots
        # LAB k.2 (Core)                `# YOUR CODE` in a function body
        # LAB k.3 (Challenge, optional) `# YOUR CODE`; no later cell may use a name it defines
optional FALLBACK cell after Level 1 where Level 2 or a later Part needs its result.
exercises.ipynb: slots in LAB cells only.
solutions.ipynb: no slots left, SOLUTION cells explain themselves, no FALLBACK cells.
--pair: solutions == exercises minus FALLBACK cells (count, order, kinds, source).

Usage:
    .venv/bin/python3 validate_notebooks.py 2                # both notebooks of module 2
    .venv/bin/python3 validate_notebooks.py 2 --pair --strict
    .venv/bin/python3 validate_notebooks.py course/module_02/exercises.ipynb
    .venv/bin/python3 validate_notebooks.py --all --pair

Exit code 1 on any FAIL.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURSE = ROOT / "course"
DIAGRAMS = COURSE / "diagrams"
DENYLIST_FILE = ROOT / "validation" / "denylist.txt"
MERMAID_SKILL = ROOT / ".claude" / "skills" / "mermaid-diagrams" / "SKILL.md"

# Copied verbatim from the mermaid-diagrams skill. check_brand_line_in_skill keeps them equal.
BRAND_LINE = (
    '%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Inter, sans-serif", '
    '"primaryColor": "#ECF8F6", "primaryBorderColor": "#40B8A6", "primaryTextColor": "#111827", '
    '"lineColor": "#1A3D4D", "secondaryColor": "#F9FAFB", "tertiaryColor": "#FFFFFF", '
    '"clusterBkg": "#F9FAFB", "clusterBorder": "#D1D5DB", "actorBkg": "#ECF8F6", '
    '"actorBorder": "#40B8A6", "noteBkgColor": "#FFF6DA", "noteBorderColor": "#E0B84C"}}}%%'
)

# Code cell banner: 77 characters, then "# <KIND>...", then the banner again.
BANNER = "# " + "=" * 75
# Kinds: DEMO / BONUS DEMO, LAB n.k, FALLBACK, SOLUTION: LAB n.k. Any other banner title
# (INSTALL, IMPORTS, CONFIG, KEYS, DATA, HELPER...) is a free-form setup cell.
KIND_RE = re.compile(r"^# (BONUS DEMO|DEMO|LAB \d+\.[123]|FALLBACK|SOLUTION: LAB \d+\.[123])\b")
TITLE_RE = re.compile(r"^# [A-Z0-9]")

TITLE_OBJECTIVES_RE = re.compile(r"^##\s+What you will be able to do", re.MULTILINE)
SUMMARY_RE = re.compile(r"^#\s+Summary", re.MULTILINE)
KEY_CELL_RES = [
    re.compile(r"\bTYPESAFE_API_KEY\b"),
    re.compile(r"\bgetpass\b"),
    re.compile(r"\bos\.environ\b"),
]
COLAB_SECRETS_RE = re.compile(r"\buserdata\.get\b|google\.colab\s+import\s+userdata")

# Labs: one per Part (beat 4), three tiers, in this order, with these banner titles.
LAB_HEADING_RE = re.compile(r"^###\s+4\.\s+Lab\s+(\d+)\b", re.MULTILINE)
LAB_SECTIONS = ["Your Task", "Expected Output", "Hints"]
TIERS = {1: "(Guided)", 2: "(Core)", 3: "(Challenge, optional)"}
TIER_SECTIONS = {1: r"Level 1: Guided", 2: r"Level 2: Core", 3: r"Level 3: Challenge \(optional\)"}
SLOT_RE = re.compile(r"=\s*None\s*#\s*YOUR CODE")
YOUR_CODE_RE = re.compile(r"#\s*YOUR CODE")

# The 4 beats (plans/NOTEBOOK_STYLE.md): every "## Part k: <concept>" has, in order,
# "### 1. The problem", "### 2. The solution", "### 3. Demo", "### 4. Lab k: <title>".
# Module 1 opens with "## Part 0: What is Jev" (markdown and diagrams only).
PART_RE = re.compile(r"^##\s+Part\s+(\d+):\s*(.+?)\s*$", re.MULTILINE)
BEAT_RE = re.compile(r"^###\s+([1-4])\.\s+(The problem|The solution|Demo|Lab\s+\d+)\b", re.MULTILINE)
BEAT_NAMES = {1: "The problem", 2: "The solution", 3: "Demo", 4: "Lab"}
PART0_TITLE = "What is Jev"
PART0_MODULES = {"module_01"}
SUMMARY_LAST_RE = re.compile(r"^#\s+Summary\b", re.MULTILINE)
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)

# Diagrams. Colab renders neither ```mermaid blocks nor cell attachments (it strips them,
# googlecolab/colabtools#3836). A DIAGRAM cell links the PNG rendered from
# course/diagrams/module_NN/<slug>.mmd, committed and pushed, by its raw GitHub URL:
#     <!-- DIAGRAM: <slug> -->
#     ![<alt text>](RAW_BASE + course/diagrams/module_NN/<slug>.png)
# RAW_BASE is the one place that names the GitHub repo and branch (the repo must be public).
RAW_BASE = "https://raw.githubusercontent.com/axel-sirota/getting_started_jev/main/"
MARKER_RE = re.compile(r"<!--\s*DIAGRAM:\s*([\w-]+)\s*-->")
MERMAID_RE = re.compile(r"```mermaid[ \t]*\n(.*?)\n?```", re.DOTALL)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)|<img\b[^>]*>", re.IGNORECASE)

# Keys. Values that are ALL_CAPS identifiers are placeholders (KEY = "TYPESAFE_API_KEY").
TOKEN_RE = re.compile(r"\bsk-(proj-|ant-)?[A-Za-z0-9_-]{16,}|\bts[_-][A-Za-z0-9_-]{20,}")
KEY_ASSIGN_RE = re.compile(
    r"""(api_key|secret|token|password)\s*=\s*["']([A-Za-z0-9_\-/+]{12,})["']""",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")
PRINT_KEY_RE = re.compile(
    r"print\s*\(.*(api_key|apikey|password|secret|access_token|TYPESAFE_API_KEY|OPENAI_API_KEY)",
    re.IGNORECASE,
)

# AI tells (global CLAUDE.md).
AI_TELL_CHARS = [(chr(0x2014), "em dash"), (chr(0x2013), "en dash"), (chr(0xD7), "Unicode multiplication")]
BANNED_PHRASES = [
    "delve", "leverage", "robust", "seamless", "unlock", "elevate", "empower", "harness",
    "game-changer", "game changer", "cutting-edge", "cutting edge", "revolutionize",
    "transformative", "in today's fast-paced", "navigate the landscape", "it's not just",
    "isn't just", "arguably", "it's worth noting", "it's important to remember",
]
BANNED_RE = re.compile(r"\b(" + "|".join(re.escape(p) for p in BANNED_PHRASES) + r")", re.IGNORECASE)

PYFLAKES_IGNORED = ("imported but unused", "redefinition of unused")

# A check result: (check name, errors, warnings).
Check = tuple[str, list[str], list[str]]


# --------------------------------------------------------------------------
# Cell helpers
# --------------------------------------------------------------------------
def cell_src(cell: dict) -> str:
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def load_cells(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)["cells"]


def code_cells(cells: list[dict]) -> list[tuple[int, dict]]:
    return [(i, c) for i, c in enumerate(cells) if c["cell_type"] == "code"]


def is_pip_cell(src: str) -> bool:
    """True when the first real line (not blank, not a comment) is a %pip command."""
    for line in src.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            return s.startswith("%pip")
    return False


def is_writefile_cell(src: str) -> bool:
    return src.lstrip().startswith("%%writefile")


def cell_kind(cell: dict) -> str | None:
    """The banner kind of a code cell: "DEMO", "BONUS DEMO", "LAB 2.1", "FALLBACK",
    "SOLUTION: LAB 2.1", "SETUP" for any other titled banner (install, imports, keys,
    data, helper), else None (no banner)."""
    if cell["cell_type"] != "code":
        return None
    lines = [l.rstrip() for l in cell_src(cell).splitlines()]
    if len(lines) < 3 or lines[0] != BANNER or lines[2] != BANNER:
        return None
    m = KIND_RE.match(lines[1])
    if m:
        return m.group(1)
    return "SETUP" if TITLE_RE.match(lines[1]) else None


def banner_title(cell: dict) -> str:
    lines = cell_src(cell).splitlines()
    return lines[1].rstrip() if len(lines) > 1 else ""


def lab_tier(kind: str | None) -> tuple[int, int] | None:
    """(lab, tier) for "LAB 2.3" or "SOLUTION: LAB 2.3", else None."""
    m = re.search(r"LAB (\d+)\.([123])", kind or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def strip_magics(src: str) -> str:
    """Blank out IPython magics and shell lines (and continuations) so ast can parse the cell.
    Lines are blanked, not removed, so line numbers stay put."""
    out, continued = [], False
    for line in src.splitlines():
        drop = continued or line.lstrip().startswith(("!", "%", "?"))
        continued = drop and line.rstrip().endswith("\\")
        out.append("" if drop else line)
    return "\n".join(out)


def comment_lines(src: str) -> str:
    """Whole-line comments of a code cell, the part learners read as prose."""
    return "\n".join(l for l in src.splitlines() if l.lstrip().startswith("#"))


def load_denylist() -> list[str]:
    if not DENYLIST_FILE.exists():
        return []
    return [l.strip() for l in DENYLIST_FILE.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")]


def parse(src: str, filename: str) -> ast.AST:
    """ast.parse that also accepts top-level await (allowed in notebook cells)."""
    return compile(src, filename, "exec", ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)


def pyflakes_messages(src: str, filename: str) -> list[tuple[int, str]]:
    """(line, message) from pyflakes, unused imports and redefinitions ignored."""
    from pyflakes.checker import Checker

    found = []
    for m in Checker(parse(src, filename), filename=filename).messages:
        text = m.message % m.message_args
        if not any(skip in text for skip in PYFLAKES_IGNORED):
            found.append((m.lineno, text))
    return sorted(found)


def top_level_names(src: str) -> tuple[set[str], set[str]]:
    """(names a cell defines at top level, names it reads anywhere). Empty on SyntaxError."""
    try:
        tree = parse(strip_magics(src), "cell")
    except SyntaxError:
        return set(), set()
    defined = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.With)):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                    defined.add(sub.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            defined.update((a.asname or a.name).split(".")[0] for a in node.names)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return defined, used


# --------------------------------------------------------------------------
# Source rules
# --------------------------------------------------------------------------
def key_errors(label: str, src: str) -> list[str]:
    errs = []
    if TOKEN_RE.search(src):
        errs.append(f"{label}: looks like a hard-coded API key")
    for m in KEY_ASSIGN_RE.finditer(src):
        if not PLACEHOLDER_RE.match(m.group(2)):
            errs.append(f"{label}: looks like a hard-coded secret: {m.group(1)} = ...")
    for line in src.splitlines():
        if not line.lstrip().startswith("#") and PRINT_KEY_RE.search(line):
            errs.append(f"{label}: prints a key: {line.strip()[:70]}")
    if COLAB_SECRETS_RE.search(src):
        errs.append(f"{label}: uses Colab secrets; keys are typed in with getpass")
    return errs


def denylist_errors(label: str, src: str, names: list[str]) -> list[str]:
    return [f"{label}: real name '{n}'"
            for n in names if re.search(r"\b" + re.escape(n) + r"\b", src, re.IGNORECASE)]


def dash_errors(label: str, src: str) -> list[str]:
    errs = []
    for ch, name in AI_TELL_CHARS:
        if ch in src:
            line = next(l for l in src.splitlines() if ch in l)
            errs.append(f"{label}: {name}: {line.strip()[:70]}")
    return errs


# --------------------------------------------------------------------------
# Every notebook. Each check returns (errors, warnings).
# --------------------------------------------------------------------------
def check_title(cells: list[dict]) -> tuple[list[str], list[str]]:
    if not cells or cells[0]["cell_type"] != "markdown":
        return ["cell 0 must be a markdown title cell"], []
    text = cell_src(cells[0]).lstrip()
    errs = []
    if not text.startswith("# "):
        errs.append(f"cell 0 must start with '# Title' (got {text[:50]!r})")
    if not TITLE_OBJECTIVES_RE.search(text):
        errs.append("cell 0 has no '## Learning Objectives'")
    return errs, []


def pip_packages(src: str) -> list[str]:
    packages = []
    for line in src.replace("\\\n", " ").splitlines():
        words = line.split()
        if words[:2] != ["%pip", "install"]:
            continue
        for word in words[2:]:
            if word.startswith("#"):
                break
            word = word.strip("'\"")
            if word and not word.startswith("-"):
                packages.append(word)
    return packages


def check_pip_cell(cells: list[dict]) -> tuple[list[str], list[str]]:
    cc = code_cells(cells)
    if not cc or not is_pip_cell(cell_src(cc[0][1])):
        return ["the first code cell must be a pinned %pip install"], []
    i, cell = cc[0]
    packages = pip_packages(cell_src(cell))
    if not packages:
        return [f"cell {i}: %pip install lists no packages"], []
    return [f"cell {i}: package {p!r} is not pinned with ==" for p in packages if "==" not in p], []


def check_key_cell(cells: list[dict]) -> tuple[list[str], list[str]]:
    for _, c in code_cells(cells):
        if all(rx.search(cell_src(c)) for rx in KEY_CELL_RES):
            return [], []
    return ["no key cell reading TYPESAFE_API_KEY from os.environ with a getpass fallback"], []


def check_banners(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs = []
    for i, c in code_cells(cells):
        src = cell_src(c)
        if is_pip_cell(src) or is_writefile_cell(src):
            continue
        lines = src.splitlines()
        if not lines or lines[0].rstrip() != BANNER:
            errs.append(f"cell {i}: must open with the 77-char '# ====' banner")
        elif cell_kind(c) is None:
            kind_line = lines[1] if len(lines) > 1 else ""
            errs.append(f"cell {i}: unknown or malformed banner kind: {kind_line[:60]!r}")
    return errs, []


def check_markdown_runs(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs, run = [], 0
    for i, c in enumerate(cells):
        run = run + 1 if c["cell_type"] == "markdown" else 0
        if run == 7:
            errs.append(f"cell {i}: more than 6 markdown cells in a row")
    return errs, []


def check_syntax(cells: list[dict]) -> tuple[list[str], list[str]]:
    """Every cell parses. A %%writefile cell is its own file: syntax and pyflakes alone."""
    errs = []
    for i, c in code_cells(cells):
        src = cell_src(c)
        if is_writefile_cell(src):
            first, _, body = src.lstrip().partition("\n")
            name = first.split()[-1]
            if not name.endswith(".py"):
                continue
            label = f"cell {i} ({name})"
            try:
                parse(body, name)
            except SyntaxError as e:
                errs.append(f"{label}: SyntaxError line {e.lineno}: {e.msg}")
                continue
            errs += [f"{label}:{ln}: pyflakes: {msg}" for ln, msg in pyflakes_messages(body, name)]
            continue
        try:
            parse(strip_magics(src), f"cell {i}")
        except SyntaxError as e:
            errs.append(f"cell {i}: SyntaxError line {e.lineno}: {e.msg}")
    return errs, []


def check_pyflakes(cells: list[dict]) -> tuple[list[str], list[str]]:
    """pyflakes over all code cells in order (magics blanked, %%writefile cells left out)."""
    parts, starts, line = [], [], 1
    for i, c in code_cells(cells):
        src = cell_src(c)
        if is_writefile_cell(src):
            continue
        src = strip_magics(src)
        try:
            parse(src, "cell")
        except SyntaxError:
            continue   # reported by check_syntax
        starts.append((line, i))
        parts.append(src)
        line += src.count("\n") + 2
    errs = []
    for ln, text in pyflakes_messages("\n\n".join(parts), "notebook"):
        cell = next((ci for start, ci in reversed(starts) if start <= ln), "?")
        errs.append(f"cell {cell}: pyflakes: {text}")
    return errs, []


def diagram_blocks(cells: list[dict]) -> dict[str, str]:
    """{slug: image URL} for every marker cell holding exactly one image."""
    found = {}
    for c in cells:
        if c["cell_type"] != "markdown":
            continue
        markers, images = MARKER_RE.findall(cell_src(c)), list(IMAGE_RE.finditer(cell_src(c)))
        if len(markers) == 1 and len(images) == 1:
            found[markers[0]] = images[0].group(0)
    return found


def check_diagrams(cells: list[dict], strict: bool, module: str = "") -> tuple[list[str], list[str]]:
    """Diagram cells link the committed PNG by raw GitHub URL. The master of each diagram is
    course/diagrams/<module folder>/<slug>.mmd (brand line first); <slug>.png is its render."""
    errs, warns = [], []
    folder = DIAGRAMS / module if module else DIAGRAMS
    shown = f"course/diagrams/{module + '/' if module else ''}"
    for i, c in enumerate(cells):
        if c["cell_type"] != "markdown":
            continue
        src = cell_src(c)
        if c.get("attachments"):
            errs.append(f"cell {i}: has attachments; Colab strips them. Link the PNG by raw GitHub URL")
        if MERMAID_RE.search(src):
            errs.append(f"cell {i}: ```mermaid block; Colab does not render it. Link the rendered PNG")
        images = list(IMAGE_RE.finditer(src))
        markers = MARKER_RE.findall(src)
        if images and not markers:
            errs.append(f"cell {i}: image without a <!-- DIAGRAM: slug --> marker")
        if not markers:
            continue
        if len(markers) > 1 or len(images) != 1:
            errs.append(f"cell {i}: a DIAGRAM cell holds exactly one marker and one image "
                        f"(found {len(markers)} and {len(images)})")
            continue
        slug, img = markers[0], images[0]
        want = f"{RAW_BASE}{shown}{slug}.png"
        if img.group(0).lower().startswith("<img"):
            errs.append(f"cell {i}: use markdown ![alt]({want}), not an <img> tag")
        else:
            if not img.group(1).strip():
                errs.append(f"cell {i}: diagram {slug} has no alt text")
            if img.group(2) != want:
                errs.append(f"cell {i}: diagram URL {img.group(2)!r}; expected {want!r}")
        mmd, png = folder / f"{slug}.mmd", folder / f"{slug}.png"
        for path in (mmd, png):
            if not path.exists():
                (errs if strict else warns).append(f"cell {i}: {shown}{path.name} is missing")
        if mmd.exists() and mmd.read_text(encoding="utf-8").strip().splitlines()[:1] != [BRAND_LINE]:
            errs.append(f"cell {i}: {shown}{slug}.mmd must start with the brand line from the mermaid skill")
    return errs, warns


def check_content(cells: list[dict], names: list[str]) -> tuple[list[str], list[str]]:
    """No keys, no Colab secrets, no real names."""
    errs = []
    for i, c in enumerate(cells):
        src, label = cell_src(c), f"cell {i}"
        if c["cell_type"] == "code":
            errs += key_errors(label, src)
        errs += denylist_errors(label, src, names)
    return errs, []


def check_ai_tells(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs = []
    for i, c in enumerate(cells):
        src = cell_src(c)
        errs += dash_errors(f"cell {i}", src)
        if c["cell_type"] == "markdown":
            prose = src
            # `---` inside a fenced block is YAML frontmatter, not a separator
            fence = ""   # the open fence ("```" or "````"), "" when outside
            for line in src.splitlines():
                m = re.match(r"^\s*(`{3,}|~{3,})", line)
                if m and not fence:
                    fence = m.group(1)
                elif m and fence and line.strip() == fence:
                    fence = ""
                elif line.strip() == "---" and not fence:
                    errs.append(f"cell {i}: bare --- separator")
        else:
            prose = comment_lines(src)
        errs += [f"cell {i}: banned phrase '{m.group(0)}'" for m in BANNED_RE.finditer(prose)]
    return errs, []


def notebook_beats(cells: list[dict]) -> list[tuple[int, int, int]]:
    """(cell index, part, beat) for every Part heading (beat 0) and beat heading, in order.
    A top-level "# " heading (Setup, Summary) closes the current Part: beat -1."""
    found, part = [], None
    for i, c in enumerate(cells):
        if c["cell_type"] != "markdown":
            continue
        src = cell_src(c)
        marks = [(m.start(), "part", int(m.group(1))) for m in PART_RE.finditer(src)]
        marks += [(m.start(), "beat", int(m.group(1))) for m in BEAT_RE.finditer(src)]
        marks += [(m.start(), "end", 0) for m in H1_RE.finditer(src)]
        for _, kind, n in sorted(marks):
            if kind == "part":
                part = n
                found.append((i, n, 0))
            elif kind == "end":
                if part is not None:
                    found.append((i, part, -1))
                part = None
            elif part is not None:
                found.append((i, part, n))
    return found


def check_beats(cells: list[dict], module: str = "") -> tuple[list[str], list[str]]:
    """Parts numbered in order (Part 0 "What is Jev" first in Module 1); every Part k >= 1 has
    the 4 beats in order; beats 1 and 2 have no code and at least one diagram; beat 3 has a
    DEMO cell; beat 4 is "### 4. Lab k" with k equal to the Part number."""
    errs = []
    beats = notebook_beats(cells)
    parts = [p for _, p, b in beats if b == 0]
    if not [p for p in parts if p >= 1]:
        return ["no '## Part k: <concept>' section; the notebook has no 4-beat Parts"], []
    want_part0 = module in PART0_MODULES
    first = 0 if want_part0 else 1
    if parts != list(range(first, first + len(parts))):
        errs.append(f"Parts {parts}; expected {list(range(first, first + len(parts)))}"
                    + (" (Module 1 starts with Part 0)" if want_part0 else ""))
    if want_part0:
        part0 = [i for i, p, b in beats if p == 0 and b == 0]
        if part0 and PART0_TITLE not in PART_RE.search(cell_src(cells[part0[0]])).group(2):
            errs.append(f"cell {part0[0]}: Part 0 must be '## Part 0: {PART0_TITLE}'")
    elif 0 in parts:
        errs.append("Part 0 is only for Module 1 ('What is Jev')")

    # Cell ranges: each heading owns the cells up to the next heading or the Summary.
    ends = [i for i, c in enumerate(cells) if c["cell_type"] == "markdown"
            and SUMMARY_LAST_RE.search(cell_src(c))]
    stop = ends[-1] if ends else len(cells)
    bounds = [i for i, _, _ in beats] + [stop]
    spans = {}
    for (start, p, b), end in zip(beats, bounds[1:]):
        spans.setdefault((p, b), []).append(range(start, max(end, start + 1)))

    for p in sorted(set(parts)):
        span0 = spans.get((p, 0), [range(0)])[0]
        if p == 0:
            code = [i for i in span0 if cells[i]["cell_type"] == "code"]
            if code:
                errs.append(f"Part 0: code cells {code}; Part 0 is text and diagrams only")
            if not any(MARKER_RE.search(cell_src(cells[i])) for i in span0):
                errs.append("Part 0: no diagram")
            continue
        order = [b for _, pp, b in beats if pp == p and b > 0]
        if order != [1, 2, 3, 4]:
            names = [BEAT_NAMES.get(b, b) for b in order]
            errs.append(f"Part {p}: beats {names}; expected The problem, The solution, Demo, Lab {p}")
            continue
        for b in (1, 2):
            span = spans[(p, b)][0]
            code = [i for i in span if cells[i]["cell_type"] == "code"]
            if code:
                errs.append(f"Part {p}, '{BEAT_NAMES[b]}': code cells {code}; beats 1 and 2 are text and a figure")
            n = sum(len(MARKER_RE.findall(cell_src(cells[i]))) for i in span
                    if cells[i]["cell_type"] == "markdown")
            if n < 1:
                errs.append(f"Part {p}, '{BEAT_NAMES[b]}': no diagram; expected at least one figure")
        if not any(cell_kind(cells[i]) in ("DEMO", "BONUS DEMO") for i in spans[(p, 3)][0]):
            errs.append(f"Part {p}, 'Demo': no '# DEMO:' code cell")
        lab_head = cell_src(cells[spans[(p, 4)][0].start])
        m = LAB_HEADING_RE.search(lab_head)
        if not m or int(m.group(1)) != p:
            errs.append(f"Part {p}: beat 4 must be '### 4. Lab {p}: <title>'")
        tiers = [lab_tier(cell_kind(cells[i])) for i in spans[(p, 4)][0]]
        tiers = [t for t in tiers if t]
        if [t[1] for t in tiers] != [1, 2, 3] or any(t[0] != p for t in tiers):
            errs.append(f"Part {p}: lab cells {tiers}; expected LAB {p}.1, {p}.2, {p}.3 inside '### 4. Lab {p}'")
    return errs, []


def check_summary_last(cells: list[dict]) -> tuple[list[str], list[str]]:
    if cells and cells[-1]["cell_type"] == "markdown" and SUMMARY_RE.search(cell_src(cells[-1])):
        return [], []
    return ["the last cell must be the markdown '# Summary' cell"], []


def check_outputs_cleared(cells: list[dict]) -> tuple[list[str], list[str]]:
    return [f"cell {i}: outputs not cleared" for i, c in code_cells(cells)
            if c.get("outputs") or c.get("execution_count") is not None], []


# --------------------------------------------------------------------------
# exercises.ipynb and solutions.ipynb
# --------------------------------------------------------------------------
def check_lab_markdown(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs = []
    headed = set()
    for i, c in enumerate(cells):
        if c["cell_type"] != "markdown":
            continue
        src = cell_src(c)
        for m in LAB_HEADING_RE.finditer(src):
            headed.add(int(m.group(1)))
            for section in LAB_SECTIONS:
                if not re.search(r"^####\s+" + section, src, re.MULTILINE):
                    errs.append(f"cell {i}: Lab {m.group(1)} markdown has no '#### {section}'")
            for tier, section in TIER_SECTIONS.items():
                if not re.search(r"^####\s+" + section, src, re.MULTILINE):
                    errs.append(f"cell {i}: Lab {m.group(1)} markdown has no '#### {section.replace(chr(92), '')}'")
    for i, c in code_cells(cells):
        lt = lab_tier(cell_kind(c))
        if lt and lt[0] not in headed:
            errs.append(f"cell {i}: LAB {lt[0]}.{lt[1]} has no '### 4. Lab {lt[0]}' markdown cell")
    return errs, []


def check_tiers(cells: list[dict]) -> tuple[list[str], list[str]]:
    """Each lab has LAB n.1, n.2, n.3 (or SOLUTION: LAB n.k) in order, with the tier titles;
    no later cell reads a name only a Level 3 cell defines."""
    errs = []
    order: dict[int, list[tuple[int, int, dict]]] = {}
    for i, c in code_cells(cells):
        lt = lab_tier(cell_kind(c))
        if lt:
            order.setdefault(lt[0], []).append((lt[1], i, c))
    for lab, tiers in sorted(order.items()):
        if [t for t, _, _ in tiers] != [1, 2, 3]:
            errs.append(f"Lab {lab}: tiers {[t for t, _, _ in tiers]}; expected exactly [1, 2, 3] in order")
        for tier, i, c in tiers:
            if not banner_title(c).endswith(TIERS[tier]):
                errs.append(f"cell {i}: LAB {lab}.{tier} banner must end with '{TIERS[tier]}'")
    # Level 3 is optional: nothing after it may depend on it.
    elsewhere: set[str] = set()
    challenge: dict[str, int] = {}
    for i, c in code_cells(cells):
        defined, _ = top_level_names(cell_src(c))
        lt = lab_tier(cell_kind(c))
        if lt and lt[1] == 3:
            for name in defined:
                challenge.setdefault(name, i)
        else:
            elsewhere |= defined
    only_l3 = {n: i for n, i in challenge.items() if n not in elsewhere}
    for i, c in code_cells(cells):
        lt = lab_tier(cell_kind(c))
        if lt and lt[1] == 3:
            continue
        _, used = top_level_names(cell_src(c))
        for name in sorted(used & set(only_l3)):
            if i > only_l3[name]:
                errs.append(f"cell {i}: uses '{name}', defined only in the optional Level 3 cell {only_l3[name]}")
    return errs, []


def check_lab_slots(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs = []
    for i, c in code_cells(cells):
        kind, src = cell_kind(c) or "", cell_src(c)
        lt = lab_tier(kind)
        if lt and kind.startswith("LAB "):
            if lt[1] == 1 and not SLOT_RE.search(src):
                errs.append(f"cell {i}: {kind} (Guided) has no '= None  # YOUR CODE' slot")
            elif not YOUR_CODE_RE.search(src):
                errs.append(f"cell {i}: {kind} has no '# YOUR CODE' marker")
        elif YOUR_CODE_RE.search(src):
            errs.append(f"cell {i}: '# YOUR CODE' outside a LAB cell ({kind or 'no kind'})")
    return errs, []


def check_solutions(cells: list[dict]) -> tuple[list[str], list[str]]:
    errs = []
    for i, c in code_cells(cells):
        kind, src = cell_kind(c) or "", cell_src(c)
        if YOUR_CODE_RE.search(src):
            errs.append(f"cell {i}: '# YOUR CODE' left in solutions")
        if kind == "FALLBACK":
            errs.append(f"cell {i}: FALLBACK cell in solutions; remove it")
        if kind.startswith("SOLUTION"):
            for tag in ("# Approach:", "# Explanation:"):
                if tag not in src:
                    errs.append(f"cell {i}: {kind} has no '{tag}'")
        if kind.startswith("LAB "):
            errs.append(f"cell {i}: {kind} in solutions; it should be 'SOLUTION: {kind}'")
    return errs, []


def check_pair(exercises: list[dict], solutions: list[dict]) -> tuple[list[str], list[str]]:
    """solutions == exercises minus FALLBACK cells: same count, order, kinds and source
    (LAB cells become SOLUTION cells)."""
    kept = [(i, c) for i, c in enumerate(exercises) if cell_kind(c) != "FALLBACK"]
    errs = []
    if len(kept) != len(solutions):
        errs.append(f"solutions has {len(solutions)} cells; exercises minus FALLBACK cells has {len(kept)}")
    for (ei, e), (si, s) in zip(kept, enumerate(solutions)):
        where = f"exercises cell {ei} / solutions cell {si}"
        if e["cell_type"] != s["cell_type"]:
            errs.append(f"{where}: {e['cell_type']} vs {s['cell_type']}")
            break
        ek, sk = cell_kind(e), cell_kind(s)
        expected = f"SOLUTION: {ek}" if (ek or "").startswith("LAB ") else ek
        if sk != expected:
            errs.append(f"{where}: kind {sk} should be {expected}")
            break
        if (ek or "").startswith("LAB "):
            continue
        if cell_src(e) != cell_src(s):
            errs.append(f"{where}: source differs")
    return errs[:10], []


def check_diagram_pair(exercises: list[dict], solutions: list[dict]) -> tuple[list[str], list[str]]:
    ex, sol = diagram_blocks(exercises), diagram_blocks(solutions)
    errs = [f"diagram {slug}: only in {'exercises' if slug in ex else 'solutions'}"
            for slug in sorted(set(ex) ^ set(sol))]
    errs += [f"diagram {slug}: block differs between exercises and solutions"
             for slug in sorted(set(ex) & set(sol)) if ex[slug] != sol[slug]]
    return errs, []


def check_beats_pair(exercises: list[dict], solutions: list[dict]) -> tuple[list[str], list[str]]:
    ex = [(p, b) for _, p, b in notebook_beats(exercises)]
    sol = [(p, b) for _, p, b in notebook_beats(solutions)]
    return ([] if ex == sol else [f"Parts and beats differ: exercises {ex} vs solutions {sol}"]), []


# --------------------------------------------------------------------------
# Runners
# --------------------------------------------------------------------------
def notebook_checks(path: Path, strict: bool = False, names: list[str] | None = None) -> list[Check]:
    cells = load_cells(path)
    names = load_denylist() if names is None else names
    checks = [
        ("title cell", check_title(cells)),
        ("pinned %pip cell", check_pip_cell(cells)),
        ("key cell (env or getpass)", check_key_cell(cells)),
        ("banners", check_banners(cells)),
        ("markdown runs", check_markdown_runs(cells)),
        ("syntax", check_syntax(cells)),
        ("cross-cell pyflakes", check_pyflakes(cells)),
        ("diagrams", check_diagrams(cells, strict, path.parent.name)),
        ("no keys, Colab secrets, real names", check_content(cells, names)),
        ("AI tells", check_ai_tells(cells)),
        ("4 beats per Part", check_beats(cells, path.parent.name)),
        ("summary cell last", check_summary_last(cells)),
        ("outputs cleared", check_outputs_cleared(cells)),
        ("lab markdown", check_lab_markdown(cells)),
        ("lab tiers", check_tiers(cells)),
    ]
    if path.name == "exercises.ipynb":
        checks.append(("lab slots", check_lab_slots(cells)))
    if path.name == "solutions.ipynb":
        checks.append(("solutions", check_solutions(cells)))
    return [(name, errs, warns) for name, (errs, warns) in checks]


def module_checks(exercises: Path, solutions: Path, pair: bool) -> list[Check]:
    ex, sol = load_cells(exercises), load_cells(solutions)
    checks = [("diagrams identical", check_diagram_pair(ex, sol)),
              ("Parts and beats identical", check_beats_pair(ex, sol))]
    if pair:
        checks.append(("pair", check_pair(ex, sol)))
    return [(name, errs, warns) for name, (errs, warns) in checks]


def check_brand_line_in_skill() -> list[Check]:
    if MERMAID_SKILL.exists() and BRAND_LINE in MERMAID_SKILL.read_text(encoding="utf-8"):
        return [("brand line matches the mermaid skill", [], [])]
    return [("brand line matches the mermaid skill",
             [f"BRAND_LINE is not in {show(MERMAID_SKILL)}; copy it again"], [])]


def show(path: Path) -> str:
    p = path.resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def module_notebooks(n: int) -> list[Path]:
    folder = COURSE / f"module_{n:02d}"
    return [folder / "exercises.ipynb", folder / "solutions.ipynb"]


def all_notebooks() -> list[Path]:
    found = []
    for folder in sorted(COURSE.glob("module_[0-9][0-9]")):
        found += [p for p in module_notebooks(int(folder.name[-2:])) if p.exists()]
    return found


def print_group(title: str, checks: list[Check]) -> tuple[int, int, int]:
    """Print one line per check; return (passed, warnings, failures)."""
    print(f"\n{title}")
    passed = warned = failed = 0
    for name, errs, warns in checks:
        if not errs and not warns:
            print(f"  PASS  {name}")
            passed += 1
        for e in errs:
            print(f"  FAIL  {name}: {e}")
        for w in warns:
            print(f"  WARN  {name}: {w}")
        warned += len(warns)
        failed += bool(errs)
    return passed, warned, failed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Getting Started with Jev notebooks.")
    ap.add_argument("target", nargs="?", help="module number or notebook path")
    ap.add_argument("--all", action="store_true", help="every module notebook")
    ap.add_argument("--pair", action="store_true", help="solutions == exercises minus FALLBACK cells")
    ap.add_argument("--strict", action="store_true", help="a missing course/diagrams/<slug>.mmd fails")
    args = ap.parse_args(argv)

    if args.all or args.target is None:
        notebooks = all_notebooks()
    elif args.target.isdigit():
        notebooks = module_notebooks(int(args.target))
    else:
        notebooks = [Path(args.target)]
        sibling = {"exercises.ipynb": "solutions.ipynb", "solutions.ipynb": "exercises.ipynb"}
        if args.pair and notebooks[0].name in sibling:
            notebooks.append(notebooks[0].parent / sibling[notebooks[0].name])

    names = load_denylist()
    groups: list[tuple[str, list[Check]]] = [("repo", check_brand_line_in_skill())]
    for path in notebooks:
        if not path.exists():
            groups.append((show(path), [("file exists", [f"missing: {show(path)}"], [])]))
            continue
        groups.append((show(path), notebook_checks(path, args.strict, names)))
    folders = {p.parent for p in notebooks if p.exists()}
    for folder in sorted(folders):
        ex, sol = folder / "exercises.ipynb", folder / "solutions.ipynb"
        if ex in notebooks and sol in notebooks and ex.exists() and sol.exists():
            groups.append((f"{show(folder)} (exercises vs solutions)", module_checks(ex, sol, args.pair)))

    passed = warned = failed = 0
    for title, checks in groups:
        p, w, f = print_group(title, checks)
        passed, warned, failed = passed + p, warned + w, failed + f
    print(f"\nSummary: {passed} passed, {warned} warnings, {failed} failed checks. "
          f"{'FAIL' if failed else 'PASS'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
