import copy

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from jsonschema.validators import validator_for


SCHEMA_BASE = "https://schemas.alos.dev/v1"

REQUIRED_CONTRACT_IDS = {
    f"{SCHEMA_BASE}/identity/authorization-vocabulary.schema.json",
    f"{SCHEMA_BASE}/identity/actor-projection.schema.json",
    f"{SCHEMA_BASE}/identity/workspace-projection.schema.json",
    f"{SCHEMA_BASE}/identity/workspace-access-projection.schema.json",
    f"{SCHEMA_BASE}/identity/authenticated-principal-projection.schema.json",
    f"{SCHEMA_BASE}/identity/active-workspace-projection.schema.json",
    f"{SCHEMA_BASE}/identity/provision-account-request.schema.json",
    f"{SCHEMA_BASE}/identity/membership-mutation-request.schema.json",
    f"{SCHEMA_BASE}/identity/account-access-projection.schema.json",
    f"{SCHEMA_BASE}/identity/account-state-projection.schema.json",
    f"{SCHEMA_BASE}/common/execution-context.schema.json",
    f"{SCHEMA_BASE}/common/data-classification.schema.json",
    f"{SCHEMA_BASE}/common/source-semantics.schema.json",
    f"{SCHEMA_BASE}/runtime/execution-budget.schema.json",
    f"{SCHEMA_BASE}/runtime/runtime-authorization.schema.json",
    f"{SCHEMA_BASE}/runtime/agent-runtime-invocation.schema.json",
    f"{SCHEMA_BASE}/context/context-bundle.schema.json",
    f"{SCHEMA_BASE}/capability/capability-draft.schema.json",
    f"{SCHEMA_BASE}/capability/capability-definition.schema.json",
    f"{SCHEMA_BASE}/agent/agent-draft.schema.json",
    f"{SCHEMA_BASE}/agent/agent-definition.schema.json",
    f"{SCHEMA_BASE}/agent/agent-run-request.schema.json",
    f"{SCHEMA_BASE}/agent/agent-run-result.schema.json",
    f"{SCHEMA_BASE}/skill/skill-definition.schema.json",
    f"{SCHEMA_BASE}/skill/skill-ref.schema.json",
    f"{SCHEMA_BASE}/skill/skill-list-response.schema.json",
    f"{SCHEMA_BASE}/skill/skill-detail.schema.json",
    f"{SCHEMA_BASE}/skill/skill-version-list.schema.json",
    f"{SCHEMA_BASE}/skill/agent-skill-assignment-request.schema.json",
    f"{SCHEMA_BASE}/skill/agent-skill-assignment-receipt.schema.json",
    f"{SCHEMA_BASE}/skill/agent-skill-projection.schema.json",
    f"{SCHEMA_BASE}/skill/skill-execution-request.schema.json",
    f"{SCHEMA_BASE}/skill/skill-execution-result.schema.json",
    f"{SCHEMA_BASE}/tool/tool-request.schema.json",
    f"{SCHEMA_BASE}/tool/tool-result.schema.json",
    f"{SCHEMA_BASE}/delegation/delegation-request.schema.json",
    f"{SCHEMA_BASE}/delegation/delegation-result.schema.json",
    f"{SCHEMA_BASE}/evidence/evidence-ref.schema.json",
    f"{SCHEMA_BASE}/evidence/evidence-bundle.schema.json",
    f"{SCHEMA_BASE}/research/research-request.schema.json",
    f"{SCHEMA_BASE}/research/research-result.schema.json",
    f"{SCHEMA_BASE}/research/research-decision.schema.json",
    f"{SCHEMA_BASE}/research/research-finding.schema.json",
    f"{SCHEMA_BASE}/research/recommendation.schema.json",
    f"{SCHEMA_BASE}/review/ai-review-result.schema.json",
    f"{SCHEMA_BASE}/review/review-package.schema.json",
    f"{SCHEMA_BASE}/review/review-invocation.schema.json",
    f"{SCHEMA_BASE}/decision/decision-ref.schema.json",
    f"{SCHEMA_BASE}/release/release-state.schema.json",
    f"{SCHEMA_BASE}/runtime/run-status.schema.json",
    f"{SCHEMA_BASE}/factory/capability-catalog-item.schema.json",
    f"{SCHEMA_BASE}/factory/requirement.schema.json",
    f"{SCHEMA_BASE}/factory/requirement-understanding.schema.json",
    f"{SCHEMA_BASE}/factory/capability-decision.schema.json",
    f"{SCHEMA_BASE}/capability/capability-detail.schema.json",
    f"{SCHEMA_BASE}/factory/factory-resolution.schema.json",
    f"{SCHEMA_BASE}/factory/registry-handoff.schema.json",
    f"{SCHEMA_BASE}/factory/factory-analyze-request.schema.json",
    f"{SCHEMA_BASE}/factory/factory-analysis-request.schema.json",
    f"{SCHEMA_BASE}/factory/factory-analysis-result.schema.json",
    f"{SCHEMA_BASE}/factory/factory-analyze-response.schema.json",
    f"{SCHEMA_BASE}/events/run/run-event.schema.json",
}

CANONICAL_IDENTIFIERS = {
    "tenant_id",
    "organization_id",
    "workspace_id",
    "actor_id",
    "capability_id",
    "agent_id",
    "agent_version",
    "skill_id",
    "skill_version",
    "run_id",
    "root_run_id",
    "parent_run_id",
    "tool_call_id",
    "source_id",
    "evidence_id",
    "review_id",
    "decision_id",
    "release_id",
    "correlation_id",
    "requirement_id",
}

MVP1_COMPATIBILITY_FIXTURES = [
    "compatibility/fixtures/mvp1/agent-definition.adapted.json",
    "compatibility/fixtures/mvp1/agent-run-request.adapted.json",
    "compatibility/fixtures/mvp1/agent-run-result.adapted.json",
    "compatibility/fixtures/mvp1/ai-review-result.adapted.json",
    "compatibility/fixtures/mvp1/capability-definition.adapted.json",
    "compatibility/fixtures/mvp1/decision-ref.adapted.json",
    "compatibility/fixtures/mvp1/evidence-bundle.adapted.json",
    "compatibility/fixtures/mvp1/evidence-ref.adapted.json",
    "compatibility/fixtures/mvp1/execution-context.adapted.json",
    "compatibility/fixtures/mvp1/context-bundle.adapted.json",
    "compatibility/fixtures/mvp1/research-request.adapted.json",
    "compatibility/fixtures/mvp1/research-result.adapted.json",
    "compatibility/fixtures/mvp1/run-event.adapted.json",
    "compatibility/fixtures/mvp1/tool-request.adapted.json",
    "compatibility/fixtures/mvp1/tool-result.adapted.json",
]


def validator(schema_id, schemas, registry):
    return Draft202012Validator(
        schemas[schema_id], registry=registry, format_checker=FormatChecker()
    )


def without_schema(document):
    return {key: value for key, value in document.items() if key != "$schema"}


def test_provision_account_request_cannot_select_tenant_or_organization(schemas, registry):
    schema_id = f"{SCHEMA_BASE}/identity/provision-account-request.schema.json"
    validate = validator(schema_id, schemas, registry)
    payload = {
        "email": "new-account@andara.local",
        "password": "StrongPass!123",
        "display_name": "New Account",
        "workspace_id": "workspace_existing",
        "role_refs": ["WORKSPACE_MEMBER"],
    }
    validate.validate(payload)

    with pytest.raises(ValidationError):
        validate.validate({**payload, "tenant_id": "tenant_browser_selected"})
    with pytest.raises(ValidationError):
        validate.validate({**payload, "organization_id": "org_browser_selected"})
    with pytest.raises(ValidationError):
        validate.validate({**payload, "role_refs": ["IT_LEAD"]})


def test_all_schemas_load_and_pass_meta_schema(schemas):
    assert len(schemas) >= 20
    for schema in schemas.values():
        validator_for(schema).check_schema(schema)


def test_runtime_invocation_preserves_backend_authority(schemas, registry, load_json):
    schema_id = f"{SCHEMA_BASE}/runtime/agent-runtime-invocation.schema.json"
    payload = without_schema(load_json("examples/runtime/agent-runtime-invocation.json"))
    validator(schema_id, schemas, registry).validate(payload)
    assert payload["runtime_authorization"]["run_id"] == payload["run_request"]["run_id"]
    assert payload["run_request"]["authorized_skill_refs"] == payload["agent_definition"]["skill_refs"]


def test_runtime_authorization_rejects_injected_authority(schemas, registry, load_json):
    schema_id = f"{SCHEMA_BASE}/runtime/agent-runtime-invocation.schema.json"
    payload = without_schema(load_json("examples/runtime/agent-runtime-invocation.json"))
    payload["runtime_authorization"]["permission_refs"] = ["admin"]
    with pytest.raises(ValidationError):
        validator(schema_id, schemas, registry).validate(payload)


def test_all_baseline_contracts_are_present(schemas):
    assert REQUIRED_CONTRACT_IDS <= schemas.keys()


def test_canonical_identifier_definitions_and_references_are_consistent(schemas):
    identifiers_id = f"{SCHEMA_BASE}/common/identifiers.schema.json"
    definitions = schemas[identifiers_id]["$defs"]
    assert CANONICAL_IDENTIFIERS <= definitions.keys()

    def inspect(node):
        if isinstance(node, dict):
            properties = node.get("properties", {})
            for field_name in CANONICAL_IDENTIFIERS & properties.keys():
                expected = f"{identifiers_id}#/$defs/{field_name}"
                assert properties[field_name].get("$ref") == expected
            for value in node.values():
                inspect(value)
        elif isinstance(node, list):
            for value in node:
                inspect(value)

    for schema_id, schema in schemas.items():
        if schema_id != identifiers_id:
            inspect(schema)


def test_capability_definition_example_is_valid(load_json, schemas, registry):
    payload = load_json("examples/capability/capability-definition.json")
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


def test_agent_run_request_example_is_valid(load_json, schemas, registry):
    payload = load_json("examples/agent/agent-run-request.json")
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


def test_agent_run_result_example_is_valid(load_json, schemas, registry):
    payload = load_json("examples/agent/agent-run-result.json")
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


def test_invalid_agent_run_request_is_rejected(load_json, schemas, registry):
    payload = without_schema(load_json("examples/agent/agent-run-request.json"))
    del payload["execution_context"]["tenant_id"]
    with pytest.raises(ValidationError):
        validator("https://schemas.alos.dev/v1/agent/agent-run-request.schema.json", schemas, registry).validate(payload)


def test_invalid_canonical_identifier_is_rejected(load_json, schemas, registry):
    payload = without_schema(load_json("examples/agent/agent-run-request.json"))
    payload["run_id"] = "contains spaces"
    with pytest.raises(ValidationError):
        validator("https://schemas.alos.dev/v1/agent/agent-run-request.schema.json", schemas, registry).validate(payload)


def test_review_package_example_is_valid(load_json, schemas, registry):
    payload = load_json("examples/review/review-package.json")
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


def test_ai_recommendation_cannot_be_used_as_decision(load_json, schemas, registry):
    payload = without_schema(load_json("examples/review/review-package.json"))
    payload["it_decision"] = copy.deepcopy(payload["ai_recommendation"])
    with pytest.raises(ValidationError):
        validator("https://schemas.alos.dev/v1/review/review-package.schema.json", schemas, registry).validate(payload)


def test_event_example_is_valid(load_json, schemas, registry):
    payload = load_json("events/run/run.started.example.json")
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


@pytest.mark.parametrize("fixture_path", MVP1_COMPATIBILITY_FIXTURES)
def test_adapted_mvp1_fixture_is_valid(fixture_path, load_json, schemas, registry):
    payload = load_json(fixture_path)
    validator(payload["$schema"], schemas, registry).validate(without_schema(payload))


def test_capability_draft_accepts_canonical_or_deprecated_type_field(schemas, registry):
    schema_id = f"{SCHEMA_BASE}/capability/capability-draft.schema.json"
    base = {
        "capability_id": "capability_mvp1_test",
        "name": "MVP-1 test capability",
        "purpose": "Exercise compatibility behavior.",
        "owner": "platform",
        "output_state": "DRAFT",
    }

    validator(schema_id, schemas, registry).validate({**base, "capability_type": "VALIDATOR"})
    validator(schema_id, schemas, registry).validate({**base, "delivery_mode": "TOOL"})
    with pytest.raises(ValidationError):
        validator(schema_id, schemas, registry).validate(base)


def test_legacy_identifier_aliases_are_not_accepted(load_json, schemas, registry):
    payload = without_schema(load_json(MVP1_COMPATIBILITY_FIXTURES[0]))
    payload["agent_key"] = payload.pop("agent_id")

    with pytest.raises(ValidationError):
        validator(f"{SCHEMA_BASE}/agent/agent-definition.schema.json", schemas, registry).validate(payload)


def test_ambiguous_legacy_release_states_require_explicit_mapping(schemas, registry):
    release_validator = validator(
        f"{SCHEMA_BASE}/release/release-state.schema.json", schemas, registry
    )
    for compatible_state in ("DRAFT", "RETURNED", "REJECTED", "RELEASED", "ACTIVE", "SUSPENDED", "ROLLED_BACK"):
        release_validator.validate(compatible_state)
    for ambiguous_state in ("TESTED", "IN_REVIEW", "APPROVED"):
        with pytest.raises(ValidationError):
            release_validator.validate(ambiguous_state)


def test_rejected_tool_result_requires_structured_error(load_json, schemas, registry):
    payload = without_schema(load_json("compatibility/fixtures/mvp1/tool-result.adapted.json"))
    payload["status"] = "REJECTED"
    payload.pop("output")

    with pytest.raises(ValidationError):
        validator(f"{SCHEMA_BASE}/tool/tool-result.schema.json", schemas, registry).validate(payload)


@pytest.mark.parametrize("status", ["FAILED", "TIMEOUT", "DENIED", "REJECTED"])
def test_non_success_tool_result_requires_structured_error(
    status, load_json, schemas, registry
):
    payload = without_schema(load_json("compatibility/fixtures/mvp1/tool-result.adapted.json"))
    payload["status"] = status
    payload.pop("output")
    payload.pop("error", None)

    with pytest.raises(ValidationError):
        validator(f"{SCHEMA_BASE}/tool/tool-result.schema.json", schemas, registry).validate(payload)


def test_failed_agent_run_requires_structured_error(load_json, schemas, registry):
    payload = without_schema(load_json("examples/agent/agent-run-result.json"))
    payload["status"] = "FAILED"
    payload["output_state"] = "BLOCKED"
    payload.pop("output")
    payload.pop("error", None)

    with pytest.raises(ValidationError):
        validator(f"{SCHEMA_BASE}/agent/agent-run-result.schema.json", schemas, registry).validate(payload)


def test_ai_review_cannot_claim_authoritative_approval(load_json, schemas, registry):
    payload = without_schema(load_json("compatibility/fixtures/mvp1/ai-review-result.adapted.json"))
    payload["status"] = "APPROVED_BY_AI"

    with pytest.raises(ValidationError):
        validator(f"{SCHEMA_BASE}/review/ai-review-result.schema.json", schemas, registry).validate(payload)


def test_authorized_skill_refs_are_exact_and_cannot_embed_grants(load_json, schemas, registry):
    payload = without_schema(load_json("examples/agent/agent-run-request.json"))
    payload["authorized_skill_refs"] = [{"skill_id": "skill.research.core", "skill_version": "1.0.0"}]
    run_validator = validator(f"{SCHEMA_BASE}/agent/agent-run-request.schema.json", schemas, registry)
    run_validator.validate(payload)
    payload["authorized_skill_refs"][0]["permission_refs"] = ["permission.expanded"]
    with pytest.raises(ValidationError):
        run_validator.validate(payload)


def test_assignment_receipt_is_draft_only(schemas, registry):
    payload = {
        "agent_id": "agent.research", "base_agent_version": "1.0.0",
        "draft_agent_version": "1.1.0",
        "skill_ref": {"skill_id": "skill.research.core", "skill_version": "1.0.0"},
        "lifecycle_state": "DRAFT", "correlation_id": "corr_assignment_001",
    }
    receipt_validator = validator(f"{SCHEMA_BASE}/skill/agent-skill-assignment-receipt.schema.json", schemas, registry)
    receipt_validator.validate(payload)
    payload["lifecycle_state"] = "ACTIVE"
    with pytest.raises(ValidationError):
        receipt_validator.validate(payload)
