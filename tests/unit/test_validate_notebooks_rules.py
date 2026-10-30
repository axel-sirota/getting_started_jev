"""Unit tests for the tier, slide-hop, key and pair rules in validate_notebooks.py."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import validate_notebooks as vn  # noqa: E402

pytestmark = pytest.mark.unit

B = vn.BANNER


def md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(title: str, body: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": f"{B}\n# {title}\n{B}\n{body}"}


LAB_MD = md(
    "## Lab 1: Classify by domain\n### Your Task\nx\n### Expected Output\nx\n### Hints\nx\n"
    "### Level 1: Guided\nx\n### Level 2: Core\nx\n### Level 3: Challenge (optional)\nx\n"
)


def exercises() -> list[dict]:
    return [
        md("# Module 1\n## Learning Objectives\n- one"),
        {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
         "source": "%pip install -q typesafe-sdk==0.7.5"},
        code("KEYS", 'import os, getpass\nif not os.environ.get("TYPESAFE_API_KEY"):\n'
                     '    os.environ["TYPESAFE_API_KEY"] = getpass.getpass("Jev key: ")'),
        md("## Demo 1: First call"),
        code("DEMO", "answer = 1\nprint(answer)"),
        md("## Back to the slides: Probabilities"),
        LAB_MD,
        code("LAB 1.1 (Guided)", "domain = None  # YOUR CODE\nprint(domain)"),
        code("LAB 1.2 (Core)", "def triage(q):\n    # YOUR CODE\n    pass"),
        code("LAB 1.3 (Challenge, optional)", "# YOUR CODE\nextra = 3"),
        md("## Back to the slides: Debrief"),
        md("# Summary\n- done"),
    ]


def solutions() -> list[dict]:
    cells = copy.deepcopy(exercises())
    cells[7] = code("SOLUTION: LAB 1.1 (Guided)", "# Approach: a\n# Explanation: b\ndomain = 'x'\nprint(domain)")
    cells[8] = code("SOLUTION: LAB 1.2 (Core)", "# Approach: a\n# Explanation: b\ndef triage(q):\n    return q")
    cells[9] = code("SOLUTION: LAB 1.3 (Challenge, optional)", "# Approach: a\n# Explanation: b\nextra = 3")
    return cells


def errs(check, *args) -> list[str]:
    return check(*args)[0]


# --- happy path -----------------------------------------------------------------
def test_validate_notebooks_good_exercises_pass_every_rule():
    cells = exercises()
    for check in (vn.check_title, vn.check_pip_cell, vn.check_key_cell, vn.check_banners,
                  vn.check_hops, vn.check_lab_markdown, vn.check_tiers, vn.check_lab_slots,
                  vn.check_summary_last, vn.check_outputs_cleared, vn.check_syntax):
        assert errs(check, cells) == [], check.__name__


def test_validate_notebooks_good_pair_passes():
    assert errs(vn.check_solutions, solutions()) == []
    assert errs(vn.check_tiers, solutions()) == []
    assert errs(vn.check_pair, exercises(), solutions()) == []
    assert errs(vn.check_hops_pair, exercises(), solutions()) == []


# --- tiers ----------------------------------------------------------------------
def test_validate_notebooks_missing_tier_fails():
    cells = exercises()
    del cells[9]
    assert any("expected exactly [1, 2, 3]" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_tier_title_wrong_fails():
    cells = exercises()
    cells[9] = code("LAB 1.3 (Challenge)", "# YOUR CODE\nextra = 3")
    assert any("(Challenge, optional)" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_later_cell_using_level3_name_fails():
    cells = exercises()
    cells.insert(10, code("DEMO", "print(extra)"))
    assert any("optional Level 3" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_guided_without_slot_fails():
    cells = exercises()
    cells[7] = code("LAB 1.1 (Guided)", "# YOUR CODE\ndomain = 1")
    assert any("Guided" in e for e in errs(vn.check_lab_slots, cells))


def test_validate_notebooks_lab_markdown_without_level_section_fails():
    cells = exercises()
    cells[6] = md(LAB_MD["source"].replace("### Level 2: Core\nx\n", ""))
    assert any("Level 2: Core" in e for e in errs(vn.check_lab_markdown, cells))


def test_validate_notebooks_your_code_left_in_solutions_fails():
    cells = solutions()
    cells[8] = code("SOLUTION: LAB 1.2 (Core)", "# Approach: a\n# Explanation: b\n# YOUR CODE")
    assert errs(vn.check_solutions, cells)


# --- slide hops -----------------------------------------------------------------
def test_validate_notebooks_demo_without_back_cell_fails():
    cells = exercises()
    del cells[5]
    assert any("Back to the slides" in e for e in errs(vn.check_hops, cells))


def test_validate_notebooks_hops_out_of_order_fail():
    cells = exercises()
    cells[3] = md("## Demo 2: First call")
    assert any("out of order" in e for e in errs(vn.check_hops, cells))


def test_validate_notebooks_notebook_without_hops_fails():
    cells = [c for c in exercises() if "Demo" not in vn.cell_src(c) and "## Lab" not in vn.cell_src(c)
             and "Back to" not in vn.cell_src(c)]
    assert errs(vn.check_hops, cells)


# --- diagrams -------------------------------------------------------------------
def diagram_cell(url: str, alt: str = "Jev call") -> dict:
    return md(f"<!-- DIAGRAM: jev-call -->\n![{alt}]({url})")


def write_diagram(folder: Path, brand: bool = True) -> None:
    folder.mkdir(parents=True)
    first = vn.BRAND_LINE if brand else "%%{init: {}}%%"
    (folder / "jev-call.mmd").write_text(f"{first}\nflowchart LR\n  A --> B\n", encoding="utf-8")
    (folder / "jev-call.png").write_bytes(b"png")


def test_validate_notebooks_raw_github_diagram_passes(tmp_path, monkeypatch):
    monkeypatch.setattr(vn, "DIAGRAMS", tmp_path)
    write_diagram(tmp_path / "module_01")
    url = f"{vn.RAW_BASE}course/diagrams/module_01/jev-call.png"
    assert errs(vn.check_diagrams, [diagram_cell(url)], True, "module_01") == []


def test_validate_notebooks_mermaid_block_in_notebook_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(vn, "DIAGRAMS", tmp_path)
    cell = md("```mermaid\nflowchart LR\n  A --> B\n```")
    assert any("Colab does not render" in e for e in errs(vn.check_diagrams, [cell], True, "module_01"))


def test_validate_notebooks_wrong_diagram_url_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(vn, "DIAGRAMS", tmp_path)
    write_diagram(tmp_path / "module_01")
    cell = diagram_cell("course/diagrams/module_01/jev-call.png")
    assert any("expected" in e for e in errs(vn.check_diagrams, [cell], True, "module_01"))


def test_validate_notebooks_missing_png_and_brand_line_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(vn, "DIAGRAMS", tmp_path)
    write_diagram(tmp_path / "module_01", brand=False)
    (tmp_path / "module_01" / "jev-call.png").unlink()
    url = f"{vn.RAW_BASE}course/diagrams/module_01/jev-call.png"
    found = errs(vn.check_diagrams, [diagram_cell(url)], True, "module_01")
    assert any("jev-call.png is missing" in e for e in found)
    assert any("brand line" in e for e in found)


# --- keys -----------------------------------------------------------------------
def test_validate_notebooks_colab_secrets_fail():
    cells = exercises()
    cells[2] = code("KEYS", "from google.colab import userdata\nk = userdata.get('TYPESAFE_API_KEY')")
    assert errs(vn.check_content, cells, [])
    assert errs(vn.check_key_cell, cells)


def test_validate_notebooks_hard_coded_key_fails():
    cells = exercises()
    cells[4] = code("DEMO", 'api_key = "sk-proj-abcdefghijklmnopqrstuvwx"')
    assert errs(vn.check_content, cells, [])
