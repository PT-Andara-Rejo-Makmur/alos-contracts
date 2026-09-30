"""Shared Work vocabulary is generated from persisted, Backend-owned shapes."""

import pytest
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
