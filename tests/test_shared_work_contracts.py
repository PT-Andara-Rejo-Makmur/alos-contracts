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


def test_document_links_and_checklist_are_scoped_requests(load_json, registry) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    definitions = schema["$defs"]
    assert {"work.relation.link", "work.checklist.manage"} <= set(
        definitions["Permission"]["enum"]
    )
    for name, valid, forbidden in (
        ("DocumentLinkRequest", {"target_type": "TASK", "target_id": "task_1"},
         {"tenant_id": "tenant_other"}),
        ("ChecklistCreateRequest", {"body": "Inspect"}, {"completed": True}),
    ):
        validator = Draft202012Validator(
            {"$ref": schema["$id"] + "#/$defs/" + name}, registry=registry
        )
        assert validator.is_valid(valid)
        assert not validator.is_valid({**valid, **forbidden})
    link = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/DocumentLinkRequest"}, registry=registry
    )
    assert not link.is_valid({"target_type": "REPORT", "target_id": "report_1"})
    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    assert "/api/v1/documents/{document_id}/links" in paths
    assert "/api/v1/work/{entity_type}/{entity_id}/checklist" in paths
    assert "/api/v1/work/{entity_type}/{entity_id}/relations" in paths


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


def test_approval_workflow_is_typed_and_authority_fields_are_server_owned(
    load_json, registry
) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    definitions = schema["$defs"]
    assert definitions["ApprovalSubjectType"]["enum"] == ["PROJECT", "TASK"]
    for name, valid, forbidden in (
        ("ApprovalRequest", {"subject_type": "PROJECT", "subject_id": "project_1"}, {"status": "APPROVED"}),
        ("ApprovalDecisionRequest", {"decision_reason": "Reviewed"}, {"approver_actor_id": "actor_1"}),
    ):
        validator = Draft202012Validator(
            {"$ref": schema["$id"] + "#/$defs/" + name}, registry=registry
        )
        assert validator.is_valid(valid)
        assert not validator.is_valid({**valid, **forbidden})
    request = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/ApprovalRequest"}, registry=registry
    )
    assert not request.is_valid({"subject_type": "BUDGET", "subject_id": "budget_1"})
    assert "decision_reason" in definitions["ApprovalProjection"]["properties"]

    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    base = "../../schemas/shared-work/shared-work.schema.json#/$defs/"
    assert paths["/api/v1/approvals"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "ApprovalRequest"
    for action in ("approve", "return", "reject", "hold"):
        operation = paths[f"/api/v1/approvals/{{approval_id}}/{action}"]["post"]
        assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "ApprovalDecisionRequest"
        assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "ApprovalProjection"


def test_document_metadata_and_version_reference_have_canonical_public_contracts(
    load_json, registry
) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    request = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/DocumentVersionCreateRequest"},
        registry=registry,
    )
    valid = {"version": "1.0", "source_id": "source_123", "source_version": "1"}
    assert request.is_valid(valid)
    for field in ("storage_uri", "content_hash", "created_by", "tenant_id", "workspace_id"):
        assert not request.is_valid({**valid, field: "injected"})
    assert not request.is_valid({"version": "1.0"})

    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    base = "../../schemas/shared-work/shared-work.schema.json#/$defs/"
    assert paths["/api/v1/documents"]["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "DocumentCreateRequest"
    assert paths["/api/v1/documents"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"] == base + "DocumentProjection"
    versions = paths["/api/v1/documents/{document_id}/versions"]
    assert versions["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "DocumentVersionCreateRequest"
    assert versions["post"]["responses"]["201"]["content"]["application/json"]["schema"]["$ref"] == base + "DocumentVersionProjection"
    assert "patch" not in versions
    for action in ("review", "approve", "retire"):
        lifecycle = paths[f"/api/v1/documents/{{document_id}}/{action}"]
        assert "post" in lifecycle
        assert lifecycle["post"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "DocumentProjection"
        assert "requestBody" not in lifecycle["post"]
        assert "patch" not in lifecycle


def test_reports_and_findings_have_canonical_public_contracts(load_json, registry) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    report_req = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/ReportCreateRequest"},
        registry=registry,
    )
    valid_report = {"title": "Laporan Keuangan", "report_type": "FINANCIAL"}
    assert report_req.is_valid(valid_report)
    for field in ("status", "owner_actor_id", "tenant_id", "workspace_ids"):
        assert not report_req.is_valid({**valid_report, field: "injected"})

    finding_req = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/FindingCreateRequest"},
        registry=registry,
    )
    valid_finding = {"title": "Temuan Audit", "description": "Detail temuan", "severity": "HIGH"}
    assert finding_req.is_valid(valid_finding)
    for field in ("status", "source_type", "owner_actor_id", "tenant_id", "workspace_ids"):
        assert not finding_req.is_valid({**valid_finding, field: "injected"})

    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    base = "../../schemas/shared-work/shared-work.schema.json#/$defs/"

    # Reports
    reports = paths["/api/v1/work/reports/results"]
    assert reports["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"] == base + "ReportProjection"
    assert reports["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportCreateRequest"
    assert reports["post"]["responses"]["201"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportProjection"
    report_detail = paths["/api/v1/work/reports/results/{report_id}"]
    assert report_detail["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportProjection"
    for action in ("submit-review", "review", "publish", "archive"):
        operation = paths[f"/api/v1/work/reports/results/{{report_id}}/{action}"]["post"]
        assert "requestBody" not in operation
        assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportProjection"
    definitions = paths["/api/v1/work/reports/definitions"]
    assert definitions["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"] == base + "ReportDefinitionProjection"
    assert definitions["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportDefinitionCreateRequest"
    assert paths["/api/v1/work/reports/definitions/{definition_id}"]["patch"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "ReportDefinitionUpdateRequest"

    # Findings
    findings = paths["/api/v1/work/findings"]
    assert findings["get"]["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"] == base + "FindingProjection"
    assert findings["post"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingCreateRequest"
    assert findings["post"]["responses"]["201"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingProjection"
    finding_detail = paths["/api/v1/work/findings/{finding_id}"]
    assert finding_detail["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingProjection"


def test_finding_lifecycle_requests_reject_authority_and_use_dedicated_routes(load_json, registry) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    update_request = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/FindingUpdateRequest"}, registry=registry,
    )
    assignment_request = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/FindingAssignmentRequest"}, registry=registry,
    )
    assert update_request.is_valid({"title": "Revised finding", "severity": "HIGH"})
    assert not update_request.is_valid({})
    assert not update_request.is_valid({"title": "x" * 501})
    assert assignment_request.is_valid({"owner_actor_id": "actor_target"})
    for field in ("status", "owner_actor_id", "source_type", "tenant_id", "organization_id", "workspace_ids"):
        assert not update_request.is_valid({"title": "Revised finding", field: "injected"})
    for field in ("status", "source_type", "tenant_id", "organization_id", "workspace_ids"):
        assert not assignment_request.is_valid({"owner_actor_id": "actor_target", field: "injected"})
    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    paths = spec["paths"]
    base = "../../schemas/shared-work/shared-work.schema.json#/$defs/"
    detail = paths["/api/v1/work/findings/{finding_id}"]
    assert detail["patch"]["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingUpdateRequest"
    assignment = paths["/api/v1/work/findings/{finding_id}/assign"]["post"]
    assert assignment["requestBody"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingAssignmentRequest"
    for action in ("start", "submit-verification", "verify", "close"):
        operation = paths[f"/api/v1/work/findings/{{finding_id}}/{action}"]["post"]
        assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"] == base + "FindingProjection"
        assert "requestBody" not in operation


def test_document_source_selector_and_task_start_date_are_canonical(load_json, registry) -> None:
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    task_request = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/TaskCreateRequest"}, registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    assert task_request.is_valid({"title": "Inspect site", "start_date": "2026-10-01"})
    assert not task_request.is_valid({"title": "Inspect site", "start_date": "yesterday"})
    option = Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/DocumentSourceOptionProjection"},
        registry=registry,
    )
    valid = {
        "source_id": "source_one", "source_title": "Verified source",
        "source_version": "1", "content_hash": "sha256:abc",
    }
    assert option.is_valid(valid)
    assert not option.is_valid({**valid, "storage_uri": "secret"})
    spec = yaml.safe_load((ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8"))
    operation = spec["paths"]["/api/v1/documents/{document_id}/source-options"]["get"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["items"]["$ref"].endswith(
        "#/$defs/DocumentSourceOptionProjection"
    )

