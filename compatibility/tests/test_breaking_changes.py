import json
from pathlib import Path

from scripts.check_compatibility import breaking_changes

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_compatible_additions_are_allowed():
    assert breaking_changes(load("baseline.schema.json"), load("compatible.schema.json")) == []


def test_required_and_enum_narrowing_are_breaking():
    issues = breaking_changes(load("baseline.schema.json"), load("breaking.schema.json"))
    assert any("required properties added" in issue for issue in issues)
    assert any("enum values removed" in issue for issue in issues)
