"""Project owner eligibility is an explicit Backend-owned directory projection."""

import pytest
from jsonschema import Draft202012Validator

from scripts.shared_work_codegen import render_python, render_typescript


@pytest.mark.parametrize("assignable", [True, False])
def test_workspace_member_project_assignability_is_boolean(
    load_json, registry, assignable: bool,
) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    validator = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/WorkspaceMemberProjection"}, registry=registry,
    )
    member = {
        "actor_id": "actor_member", "display_name": "Anggota Proyek",
        "workspace_id": "workspace_property", "role_refs": [], "active": True,
        "task_assignable": False, "finding_assignable": False,
    }
    assert validator.is_valid({**member, "project_assignable": assignable})
    # Older directories remain readable; omission never grants replacement eligibility.
    assert validator.is_valid(member)
    for invalid in ("true", 1, None):
        assert not validator.is_valid({**member, "project_assignable": invalid})
    assert not validator.is_valid({**member, "project_assignable": assignable, "active": False})


def test_project_assignability_is_available_in_canonical_generated_types() -> None:
    assert "readonly project_assignable?: boolean;" in render_typescript()
    assert "project_assignable: bool" in render_python()
