"""Unit tests for the slides-vs-notebook hop cross-check in validate_slides.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_slides as vs  # noqa: E402
from test_validate_notebooks_rules import exercises  # noqa: E402

pytestmark = pytest.mark.unit

PLAN = """## Module 1

### Slide 1 · Meet Jev
Layout: title slide
Say: hi

### Slide 2 · State and questions
Layout: full diagram
Badge: "Switch to the notebook: Demo 1"
Say: go

### Slide 3 · Probabilities
Layout: full diagram
Badge: "Switch to the notebook: Lab 1"
Say: go

### Slide 4 · Debrief
Layout: points only
Say: done
"""


def run(tmp_path: Path, monkeypatch, plan: str, cells: list[dict]) -> list[str]:
    folder = tmp_path / "course" / "module_01"
    folder.mkdir(parents=True)
    (folder / "exercises.ipynb").write_text(json.dumps({"cells": cells}), encoding="utf-8")
    plan_file = tmp_path / "module01_slides.md"
    plan_file.write_text(plan, encoding="utf-8")
    monkeypatch.setattr(vs, "ROOT", tmp_path)
    monkeypatch.setattr(vs, "PLAN", plan_file)
    monkeypatch.setattr(vs, "MODULE", 1)
    report = vs.Report()
    vs.check_hops_vs_notebook(report)
    return report.sections[0][1]


def test_validate_slides_matching_hops_pass(tmp_path, monkeypatch):
    assert run(tmp_path, monkeypatch, PLAN, exercises()) == []


def test_validate_slides_missing_badge_fails(tmp_path, monkeypatch):
    plan = PLAN.replace('Badge: "Switch to the notebook: Lab 1"\n', "")
    found = run(tmp_path, monkeypatch, plan, exercises())
    assert any("no slide badge" in e for e in found)


def test_validate_slides_back_to_wrong_slide_fails(tmp_path, monkeypatch):
    plan = PLAN.replace("### Slide 4 · Debrief", "### Slide 4 · Wrap up")
    found = run(tmp_path, monkeypatch, plan, exercises())
    assert any('returns to "Debrief"' in e for e in found)


def test_validate_slides_badge_order_mismatch_fails(tmp_path, monkeypatch):
    plan = PLAN.replace("notebook: Demo 1", "notebook: TMP").replace("notebook: Lab 1", "notebook: Demo 1") \
               .replace("notebook: TMP", "notebook: Lab 1")
    found = run(tmp_path, monkeypatch, plan, exercises())
    assert any("badge order" in e for e in found)
