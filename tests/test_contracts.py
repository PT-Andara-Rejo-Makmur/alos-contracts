import copy

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from jsonschema.validators import validator_for


def validator(schema_id, schemas, registry):
    return Draft202012Validator(
        schemas[schema_id], registry=registry, format_checker=FormatChecker()
    )


def without_schema(document):
    return {key: value for key, value in document.items() if key != "$schema"}


def test_all_schemas_load_and_pass_meta_schema(schemas):
    assert len(schemas) >= 20
    for schema in schemas.values():
        validator_for(schema).check_schema(schema)


def test_agent_run_request_example_is_valid(load_json, schemas, registry):
    payload = load_json("examples/agent/agent-run-request.json")
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
