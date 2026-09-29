import json
from pathlib import Path

from scripts.check_compatibility import breaking_changes, split_approved

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_compatible_additions_are_allowed():
    assert breaking_changes(load("baseline.schema.json"), load("compatible.schema.json")) == []


def test_required_and_enum_narrowing_are_breaking():
    issues = breaking_changes(load("baseline.schema.json"), load("breaking.schema.json"))
    assert any("required properties added" in issue for issue in issues)
    assert any("enum values removed" in issue for issue in issues)


def test_nested_definition_enum_removal_and_new_array_cap_are_breaking():
    old = {
        "$defs": {"role": {"type": "string", "enum": ["LEAD", "MEMBER"]}},
        "properties": {"roles": {"type": "array", "items": {"$ref": "role"}}},
    }
    new = {
        "$defs": {"role": {"type": "string", "enum": ["LEAD"]}},
        "properties": {
            "roles": {"type": "array", "maxItems": 1, "items": {"$ref": "role"}}
        },
    }

    issues = breaking_changes(old, new)
    assert any("enum values removed" in issue for issue in issues)
    assert any("maxItems became more restrictive" in issue for issue in issues)


def test_only_exact_documented_cutover_violation_is_approved():
    approved, unapproved = split_approved(
        [
            "schemas/agent/agent-run-result.schema.json: $: required properties added: ['correlation_id']",
            "schemas/agent/agent-run-result.schema.json: $: required properties added: ['tenant_id']",
        ]
    )

    assert approved == [
        "schemas/agent/agent-run-result.schema.json: $: required properties added: ['correlation_id']"
    ]
    assert unapproved == [
        "schemas/agent/agent-run-result.schema.json: $: required properties added: ['tenant_id']"
    ]
