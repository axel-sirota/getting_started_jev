"""Unit tests for the 4-beat, tier, key, diagram and pair rules in validate_notebooks.py."""
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
URL = vn.RAW_BASE + "course/diagrams/module_02/{}.png"


def md(src: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code(title: str, body: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": f"{B}\n# {title}\n{B}\n{body}"}


def figure(slug: str) -> dict:
    return md(f"**Figure: {slug}.**\n\n<!-- DIAGRAM: {slug} -->\n![{slug}]({URL.format(slug)})")


LAB_MD = md(
    "### 4. Lab 1: Classify by team\n\nWhy it matters.\n\n#### Your Task\nx\n"
    "#### Level 1: Guided\nx\n#### Level 2: Core\nx\n#### Level 3: Challenge (optional)\nx\n"
    "#### Expected Output\nx\n#### Hints\nx\n"
)


def exercises() -> list[dict]:
    return [
        md("# Module 2\n\n## The story\nx\n\n## What you will be able to do\n- one"),
        {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
         "source": "%pip install -q typesafe-sdk==0.7.5"},
        code("KEYS", 'import os, getpass\nif not os.environ.get("TYPESAFE_API_KEY"):\n'
                     '    os.environ["TYPESAFE_API_KEY"] = getpass.getpass("Jev key: ")'),
        md("## Part 1: Literal questions\n\nOne sentence."),
        md("### 1. The problem\n\nA vague question hides two judgments."),
        figure("vague-question"),
        md("### 2. The solution\n\nSplit it.\n\n**Ask what is true.**"),
        figure("literal-questions"),
        md("### 3. Demo\n\nRun along."),
        code("DEMO", "answer = 1\nprint(answer)"),
        md("> **Think About It**: why?"),
        LAB_MD,
        code("LAB 1.1 (Guided)", "domain = None  # YOUR CODE\nprint(domain)"),
        code("LAB 1.2 (Core)", "def triage(q):\n    # YOUR CODE\n    pass"),
        code("LAB 1.3 (Challenge, optional)", "# YOUR CODE\nextra = 3"),
        md("# Summary\n- done"),
    ]


def solutions() -> list[dict]:
    cells = copy.deepcopy(exercises())
    cells[12] = code("SOLUTION: LAB 1.1 (Guided)", "# Approach: a\n# Explanation: b\ndomain = 'x'\nprint(domain)")
    cells[13] = code("SOLUTION: LAB 1.2 (Core)", "# Approach: a\n# Explanation: b\ndef triage(q):\n    return q")
    cells[14] = code("SOLUTION: LAB 1.3 (Challenge, optional)", "# Approach: a\n# Explanation: b\nextra = 3")
    return cells


def errs(check, *args) -> list[str]:
    return check(*args)[0]


# --- happy path -----------------------------------------------------------------
def test_validate_notebooks_good_exercises_pass_every_rule():
    cells = exercises()
    for check in (vn.check_title, vn.check_pip_cell, vn.check_key_cell, vn.check_banners,
                  vn.check_lab_markdown, vn.check_tiers, vn.check_lab_slots,
                  vn.check_summary_last, vn.check_outputs_cleared, vn.check_syntax,
                  vn.check_markdown_runs):
        assert errs(check, cells) == [], check.__name__
    assert errs(vn.check_beats, cells, "module_02") == []


def test_validate_notebooks_good_pair_passes():
    assert errs(vn.check_solutions, solutions()) == []
    assert errs(vn.check_tiers, solutions()) == []
    assert errs(vn.check_pair, exercises(), solutions()) == []
    assert errs(vn.check_beats_pair, exercises(), solutions()) == []


# --- the 4 beats ----------------------------------------------------------------
def test_validate_notebooks_beats_out_of_order_fail():
    cells = exercises()
    cells[4], cells[6] = cells[6], cells[4]
    assert any("expected The problem, The solution, Demo" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_missing_beat_fails():
    cells = exercises()
    del cells[8]
    assert any("beats" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_problem_without_figure_fails():
    cells = exercises()
    del cells[5]
    assert any("The problem': 0 diagrams" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_code_in_solution_beat_fails():
    cells = exercises()
    cells.insert(7, code("DEMO", "print(1)"))
    assert any("beats 1 and 2 are text" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_demo_without_demo_cell_fails():
    cells = exercises()
    cells[9] = code("HELPER", "answer = 1")
    assert any("no '# DEMO:' code cell" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_lab_number_must_match_part():
    cells = exercises()
    cells[11] = md(LAB_MD["source"].replace("### 4. Lab 1:", "### 4. Lab 2:"))
    assert any("beat 4 must be '### 4. Lab 1" in e for e in errs(vn.check_beats, cells, "module_02"))


def test_validate_notebooks_module1_needs_part0():
    assert any("starts with Part 0" in e for e in errs(vn.check_beats, exercises(), "module_01"))


def test_validate_notebooks_module1_part0_text_only_passes_and_code_fails():
    cells = exercises()
    cells[3:3] = [md("## Part 0: What is Jev\n\nJev is a System One model."), figure("what-is-jev")]
    assert errs(vn.check_beats, cells, "module_01") == []
    cells.insert(5, code("DEMO", "print(1)"))
    assert any("Part 0: code cells" in e for e in errs(vn.check_beats, cells, "module_01"))


def test_validate_notebooks_module1_setup_between_part0_and_part1_passes():
    cells = exercises()
    setup = cells[1:3]
    del cells[1:3]
    cells[1:1] = [md("## Part 0: What is Jev\n\nJev is a System One model."), figure("what-is-jev"),
                  md("# Setup\n\nRun the next cells in order."), *setup]
    assert errs(vn.check_beats, cells, "module_01") == []
    assert errs(vn.check_pip_cell, cells) == []


def test_validate_notebooks_no_parts_fails():
    cells = [c for c in exercises() if "Part 1" not in vn.cell_src(c)]
    assert errs(vn.check_beats, cells, "module_02")


# --- tiers ----------------------------------------------------------------------
def test_validate_notebooks_missing_tier_fails():
    cells = exercises()
    del cells[14]
    assert any("expected exactly [1, 2, 3]" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_tier_title_wrong_fails():
    cells = exercises()
    cells[14] = code("LAB 1.3 (Challenge)", "# YOUR CODE\nextra = 3")
    assert any("(Challenge, optional)" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_later_cell_using_level3_name_fails():
    cells = exercises()
    cells.insert(15, code("DEMO", "print(extra)"))
    assert any("optional Level 3" in e for e in errs(vn.check_tiers, cells))


def test_validate_notebooks_guided_without_slot_fails():
    cells = exercises()
    cells[12] = code("LAB 1.1 (Guided)", "# YOUR CODE\ndomain = 1")
    assert any("Guided" in e for e in errs(vn.check_lab_slots, cells))


def test_validate_notebooks_lab_markdown_without_level_section_fails():
    cells = exercises()
    cells[11] = md(LAB_MD["source"].replace("#### Level 2: Core\nx\n", ""))
    assert any("Level 2: Core" in e for e in errs(vn.check_lab_markdown, cells))


def test_validate_notebooks_your_code_left_in_solutions_fails():
    cells = solutions()
    cells[13] = code("SOLUTION: LAB 1.2 (Core)", "# Approach: a\n# Explanation: b\n# YOUR CODE")
    assert errs(vn.check_solutions, cells)


def test_validate_notebooks_seven_markdown_cells_in_a_row_fail():
    cells = exercises()
    cells[4:4] = [md("text") for _ in range(4)]
    assert errs(vn.check_markdown_runs, cells)


# --- diagrams -------------------------------------------------------------------
def write_diagram(folder: Path, brand: bool = True) -> None:
    folder.mkdir(parents=True)
    first = vn.BRAND_LINE if brand else "%%{init: {}}%%"
    (folder / "jev-call.mmd").write_text(f"{first}\nflowchart LR\n  A --> B\n", encoding="utf-8")
    (folder / "jev-call.png").write_bytes(b"png")


def diagram_cell(url: str, alt: str = "Jev call") -> dict:
    return md(f"<!-- DIAGRAM: jev-call -->\n![{alt}]({url})")


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
    cells[9] = code("DEMO", 'api_key = "sk-proj-abcdefghijklmnopqrstuvwx"')
    assert errs(vn.check_content, cells, [])
