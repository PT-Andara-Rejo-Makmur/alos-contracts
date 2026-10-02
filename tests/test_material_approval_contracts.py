"""Material actions retain work compatibility and reject client decision authority."""

import pytest
from jsonschema import Draft202012Validator


@pytest.mark.parametrize("subject,action", [
    ("SALES_BOOKING", "CONFIRM_BOOKING"), ("SALES_OPPORTUNITY", "WIN_OPPORTUNITY"),
    ("SALES_CLOSING", "COMPLETE_CLOSING"), ("SALES_PRICING", "ACTIVATE_PRICING"),
    ("PROPERTY_UNIT", "RESERVE_UNIT"), ("PROPERTY_UNIT", "SELL_UNIT"),
    ("PROPERTY_CHANGE_ORDER", "APPROVE_CHANGE_ORDER"),
    ("PROPERTY_PAYMENT_CERTIFICATE", "APPROVE_PAYMENT_CERTIFICATE"),
    ("FINANCE_BUDGET", "APPROVE_BUDGET"), ("FINANCE_BUDGET", "ACTIVATE_BUDGET"),
    ("FINANCE_BUDGET", "CLOSE_BUDGET"),
])
def test_material_action_request_is_explicit_and_server_owned(load_json, registry, subject, action):
    schema = load_json("schemas/shared-work/shared-work.schema.json")
    validator = Draft202012Validator({"$ref": schema["$id"] + "#/$defs/ApprovalRequest"}, registry=registry)
    payload = {"subject_type": subject, "subject_id": "record_1", "requested_action": action}
    assert validator.is_valid(payload)
    assert not validator.is_valid({"subject_type": subject, "subject_id": "record_1"})
    assert not validator.is_valid({**payload, "requested_action": "RELEASE_PRODUCTION"})
    for field in ["tenant_id", "workspace_id", "subject_snapshot", "consumed_at", "consumed_by", "transition_ref", "status", "approver_actor_id"]:
        assert not validator.is_valid({**payload, field: "client_authority"})
    assert validator.is_valid({"subject_type": "PROJECT", "subject_id": "project_1"})
    assert not validator.is_valid({**payload, "subject_type": "PROJECT"})
