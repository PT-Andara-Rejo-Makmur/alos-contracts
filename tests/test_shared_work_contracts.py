"""Shared Work vocabulary is generated from persisted, Backend-owned shapes."""

import pytest
import yaml
from jsonschema import Draft202012Validator

from scripts.shared_work_codegen import ROOT, definitions, render_python, render_typescript


@pytest.mark.parametrize(
    ("entity", "identifier"),
    [
        ("Project", "project_id"),
        ("Task", "task_id"),
        ("Approval", "approval_id"),
        ("Document", "document_id"),
        ("Report", "report_id"),
        ("Finding", "finding_id"),
    ],
)
def test_projection_and_request_separate_authority(entity: str, identifier: str) -> None:
    defs = definitions()
    projection = defs[f"{entity}Projection"]
    request_name = "ApprovalRequest" if entity == "Approval" else f"{entity}CreateRequest"
    request = defs[request_name]
    assert identifier in projection["required"]
    assert {"tenant_id", "organization_id"} <= set(projection["required"])
    assert not {
        identifier,
        "tenant_id",
        "organization_id",
        "workspace_id",
        "workspace_ids",
        "actor_id",
        "owner_actor_id",
        "requested_by",
        "approver_actor_id",
        "created_by",
        "status",
        "decision",
        "decided_at",
        "permission_refs",
        "scope_refs",
        "source_type",
    } & set(request["properties"])
    assert request["additionalProperties"] is False


def test_finding_status_and_approval_authority_are_unambiguous() -> None:
    defs = definitions()
    assert defs["FindingStatus"]["enum"] == [
        "OPEN",
        "ASSIGNED",
        "IN_PROGRESS",
        "PENDING_VERIFICATION",
        "VERIFIED",
        "CLOSED",
    ]
    assert "approval.approve" in defs["Permission"]["enum"]
    assert "approval.request" in defs["Permission"]["enum"]
    assert "work.write" not in defs["Permission"]["enum"]
    assert "decision" not in defs["ApprovalRequest"]["properties"]


def test_generated_artifacts_match_schema() -> None:
    assert (ROOT / "generated/typescript/shared-work.ts").read_text(encoding="utf-8") == render_typescript()
    assert (ROOT / "generated/python/shared_work_contracts.py").read_text(encoding="utf-8") == render_python()
    assert "SharedWorkFindingStatus" in render_typescript()
    assert "SharedWorkApprovalProjection" in render_python()


def test_create_request_rejects_authority_fields(load_json, registry) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    validator = Draft202012Validator({"$ref": schema["$id"] + "#/$defs/ApprovalRequest"}, registry=registry)
    assert validator.is_valid({"subject_type": "TASK", "subject_id": "task_123"})
    assert not validator.is_valid(
        {"subject_type": "TASK", "subject_id": "task_123", "status": "APPROVED"}
    )


def test_public_projects_and_tasks_use_canonical_definitions() -> None:
    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    schema_file = "../../schemas/shared-work/shared-work.schema.json#/$defs/"
    for entity, collection, identifier in (
        ("Project", "/api/v1/projects", "project_id"),
        ("Task", "/api/v1/tasks", "task_id"),
    ):
        listed = paths[collection]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        created = paths[collection]["post"]
        detail = paths[f"{collection}/{{{identifier}}}"]["get"]
        assert listed["items"]["$ref"] == schema_file + entity + "Projection"
        assert created["requestBody"]["content"]["application/json"]["schema"]["$ref"] == (
            schema_file + entity + "CreateRequest"
        )
        assert created["responses"]["201"]["content"]["application/json"]["schema"]["$ref"] == (
            schema_file + entity + "Projection"
        )
        assert detail["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == (
            schema_file + entity + "Projection"
        )
        assert "security" not in paths[collection]["get"]
        assert "security" not in created


@pytest.mark.parametrize(
    ("definition", "valid", "forbidden"),
    [
        ("ProjectUpdateRequest", {"name": "Revised"}, {"status": "ARCHIVED"}),
        ("TaskUpdateRequest", {"priority": "HIGH"}, {"owner_actor_id": "actor_1"}),
        ("TaskAssignRequest", {"owner_actor_id": "actor_1"}, {"status": "COMPLETED"}),
    ],
)
def test_lifecycle_requests_reject_authority_fields(
    load_json, registry, definition: str, valid: dict, forbidden: dict
) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    validator = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/" + definition}, registry=registry
    )
    assert validator.is_valid(valid)
    assert not validator.is_valid({**valid, **forbidden})
    assert not validator.is_valid({})


def test_public_lifecycle_operations_use_canonical_requests() -> None:
    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    base = "../../schemas/shared-work/shared-work.schema.json#/$defs/"
    for path, method, request, projection in (
        ("/api/v1/projects/{project_id}", "patch", "ProjectUpdateRequest", "ProjectProjection"),
        ("/api/v1/tasks/{task_id}", "patch", "TaskUpdateRequest", "TaskProjection"),
        ("/api/v1/tasks/{task_id}/assign", "post", "TaskAssignRequest", "TaskProjection"),
    ):
        operation = paths[path][method]
        assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + request
        assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + projection
    for path, projection in (
        ("/api/v1/projects/{project_id}/archive", "ProjectProjection"),
        ("/api/v1/tasks/{task_id}/complete", "TaskProjection"),
    ):
        operation = paths[path]["post"]
        assert "requestBody" not in operation
        assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + projection
