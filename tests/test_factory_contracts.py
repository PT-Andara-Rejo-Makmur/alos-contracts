import copy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from scripts.generate_typescript import OUTPUT as TYPESCRIPT_OUTPUT
from scripts.generate_typescript import render as render_typescript

SCHEMA_BASE = "https://schemas.alos.dev/v1"
ROOT = Path(__file__).resolve().parents[1]


def validate(schema_id, payload, schemas, registry):
    Draft202012Validator(
        schemas[schema_id], registry=registry, format_checker=FormatChecker()
    ).validate(payload)


def without_schema(document):
    return {key: value for key, value in document.items() if key != "$schema"}


def test_public_factory_create_and_reuse_examples_are_canonical(load_json, schemas, registry):
    schema_id = f"{SCHEMA_BASE}/factory/factory-analyze-response.schema.json"
    for path in (
        "examples/factory/factory-analyze-response.create.json",
        "examples/factory/factory-analyze-response.reuse.json",
    ):
        validate(schema_id, without_schema(load_json(path)), schemas, registry)


def test_public_factory_request_cannot_supply_authority_context(load_json, schemas, registry):
    request = without_schema(load_json("examples/factory/factory-analyze-request.json"))
    request["permission_refs"] = ["admin.all"]

    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/factory/factory-analyze-request.schema.json",
            request,
            schemas,
            registry,
        )


def test_reuse_forbids_new_draft_and_registry_write(load_json, schemas, registry):
    reuse = without_schema(load_json("examples/factory/factory-analyze-response.reuse.json"))
    create = without_schema(load_json("examples/factory/factory-analyze-response.create.json"))
    reuse["capability_draft"] = create["capability_draft"]
    reuse["registry_result"] = create["registry_result"]

    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/factory/factory-analyze-response.schema.json",
            reuse,
            schemas,
            registry,
        )


def test_internal_reuse_has_reference_without_draft_or_create_handoff(
    load_json, schemas, registry
):
    reuse = without_schema(load_json("examples/factory/factory-analysis-result.reuse.json"))
    validate(
        f"{SCHEMA_BASE}/factory/factory-analysis-result.schema.json",
        reuse,
        schemas,
        registry,
    )
    assert reuse["existing_capability_refs"]
    assert reuse["capability_draft"] is None
    assert reuse["agent_draft"] is None
    assert reuse["handoff"]["requested_operations"] == []


def test_create_requires_backend_registry_draft_result(load_json, schemas, registry):
    create = without_schema(load_json("examples/factory/factory-analyze-response.create.json"))
    create["registry_result"] = None

    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/factory/factory-analyze-response.schema.json",
            create,
            schemas,
            registry,
        )


def test_factory_contract_forbids_approved_or_active_create_result(load_json, schemas, registry):
    schema_id = f"{SCHEMA_BASE}/factory/factory-analyze-response.schema.json"
    create = without_schema(load_json("examples/factory/factory-analyze-response.create.json"))

    approved = copy.deepcopy(create)
    approved["capability_draft"]["output_state"] = "APPROVED"
    with pytest.raises(ValidationError):
        validate(schema_id, approved, schemas, registry)

    active = copy.deepcopy(create)
    active["registry_result"]["state"] = "ACTIVE"
    active["registry_result"]["registered_refs"][0]["state"] = "ACTIVE"
    with pytest.raises(ValidationError):
        validate(schema_id, active, schemas, registry)


def test_internal_create_is_non_authoritative_and_draft_only(load_json, schemas, registry):
    result = without_schema(load_json("examples/factory/factory-analysis-result.create.json"))
    assert result["capability_draft"]["output_state"] == "DRAFT"
    assert result["capability_draft"]["lifecycle_state"] == "DRAFT"
    assert result["handoff"]["authoritative_state_changed"] is False

    invalid = copy.deepcopy(result)
    invalid["handoff"]["authoritative_state_changed"] = True
    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/factory/factory-analysis-result.schema.json",
            invalid,
            schemas,
            registry,
        )


def test_actor_permission_context_is_not_capability_permission_proposal(load_json):
    request = without_schema(load_json("examples/factory/factory-analysis-request.json"))
    result = without_schema(load_json("examples/factory/factory-analysis-result.create.json"))

    assert "admin.all" in request["requirement"]["execution_context"]["permission_refs"]
    assert "admin.all" not in result["resolution"]["required_permission_refs"]
    assert "admin.all" not in result["capability_draft"]["permission_refs"]


def test_factory_examples_preserve_correlation_id(load_json):
    request = without_schema(load_json("examples/factory/factory-analysis-request.json"))
    result = without_schema(load_json("examples/factory/factory-analysis-result.create.json"))
    response = without_schema(load_json("examples/factory/factory-analyze-response.create.json"))

    correlation_id = request["requirement"]["execution_context"]["correlation_id"]
    assert result["correlation_id"] == correlation_id
    assert result["capability_draft"]["correlation_id"] == correlation_id
    assert response["correlation_id"] == correlation_id


def test_factory_openapi_boundaries_are_frozen():
    public = yaml.safe_load(
        (ROOT / "openapi/public/alos-public-api.yaml").read_text(encoding="utf-8")
    )
    internal = yaml.safe_load(
        (ROOT / "openapi/internal/genesis-internal-api.yaml").read_text(encoding="utf-8")
    )

    assert public["paths"]["/api/v1/genesis/factory/analyze"]["post"]["operationId"] == (
        "analyzeFactoryRequirement"
    )
    assert internal["paths"]["/internal/v1/factory/analyze"]["post"]["operationId"] == (
        "analyzeInternalFactoryRequirement"
    )


def test_generated_typescript_is_current():
    assert TYPESCRIPT_OUTPUT.read_text(encoding="utf-8") == render_typescript()
