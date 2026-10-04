"""Minimal browser intent cannot become runtime or business authority."""

import pytest
from jsonschema import Draft202012Validator, ValidationError

BASE = "https://schemas.alos.dev/v1/ara/"


@pytest.mark.parametrize("authority", ("tenant_id", "organization_id", "workspace_id", "actor_id",
    "permission_refs", "scope_refs", "classification", "allowed_tool_ids", "execution_budget", "model_policy_ref"))
@pytest.mark.parametrize("schema, body", (("ara-thread-create-request", {}),
    ("ara-message-request", {"message": "Sales"})))
def test_browser_request_rejects_authority_fields(schemas, registry, authority, schema, body):
    validator = Draft202012Validator(schemas[BASE + schema + ".schema.json"], registry=registry)
    validator.validate(body)
    with pytest.raises(ValidationError):
        validator.validate({**body, authority: "forged"})


@pytest.mark.parametrize("kind", ("ANSWER", "CONVERSATION", "NEEDS_INFO", "DENIED", "NEEDS_REVIEW", "FAILED"))
def test_response_states_are_canonical(schemas, registry, kind):
    Draft202012Validator(schemas[BASE + "ara-response-projection.schema.json"], registry=registry).validate({
        "response_type": kind, "answer": "Bounded response", "sources": [], "failed_sources": [], "limitations": []})


def test_action_proposal_can_never_claim_execution(schemas, registry):
    validator = Draft202012Validator(schemas[BASE + "ara-action-proposal-projection.schema.json"], registry=registry)
    value = {"proposal_id": "proposal_ara", "kind": "TASK", "status": "NEEDS_REVIEW", "summary": "Follow up",
        "required_permission": "task.create", "executed": False}
    validator.validate(value)
    with pytest.raises(ValidationError):
        validator.validate({**value, "executed": True})


def test_conversation_cannot_contain_business_actions(schemas, registry):
    validator = Draft202012Validator(
        schemas[BASE + "ara-response-projection.schema.json"], registry=registry)
    response = {"response_type": "CONVERSATION", "answer": "Halo.",
        "sources": [], "failed_sources": [], "limitations": []}
    validator.validate(response)
    with pytest.raises(ValidationError):
        validator.validate({**response, "action_proposal": {
            "proposal_id": "proposal_ara", "kind": "TASK", "status": "NEEDS_REVIEW",
            "summary": "Follow up", "required_permission": "task.create", "executed": False}})
    with pytest.raises(ValidationError):
        validator.validate({**response, "failed_sources": ["sales.lead.list"]})
