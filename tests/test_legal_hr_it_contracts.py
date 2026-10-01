"""Exact claims, explicit observations and unavailable authority in owner contracts."""

import pytest
from jsonschema import ValidationError

from test_business_contracts import validator


@pytest.mark.parametrize("amount", [1.1, "NaN", "1e3", "1.001", "-1", "1000000000000000000.00"])
def test_legal_claim_amount_requires_exact_bounded_decimal(registry, amount):
    validate = validator(registry, "legal", "LegalClaimReviewCreateRequest")
    payload = {"subject_type": "CONTRACT", "subject_id": "record", "claim_amount": "123456789012345678.90"}
    validate.validate(payload)
    with pytest.raises(ValidationError):
        validate.validate({**payload, "claim_amount": amount})


@pytest.mark.parametrize("domain,definition,status", [
    ("legal", "LegalContractTransitionRequest", "SIGNED"),
    ("legal", "LegalPermitTransitionRequest", "VALID"),
    ("legal", "LegalDueDiligenceTransitionRequest", "APPROVED"),
    ("hr", "HrLeaveRequestTransitionRequest", "APPROVED"),
    ("hr", "HrCandidateTransitionRequest", "HIRED"),
    ("hr", "HrEmploymentContractTransitionRequest", "SIGNED"),
    ("it", "ItReleaseTransitionRequest", "RELEASED"),
    ("it", "ItReleaseTransitionRequest", "ROLLBACK"),
])
def test_material_authority_has_no_request_command(registry, domain, definition, status):
    with pytest.raises(ValidationError):
        validator(registry, domain, definition).validate({"status": status})


def test_monitoring_requires_explicit_observation_timestamp(registry):
    validate = validator(registry, "it", "ItServiceMonitorCreateRequest")
    payload = {"name": "Operator observation", "check_type": "RECORDED",
               "target": "https://example.test/health", "recorded_status": "DOWN"}
    with pytest.raises(ValidationError):
        validate.validate(payload)
    validate.validate({**payload, "last_checked_at": "2026-01-01T01:00:00Z"})


@pytest.mark.parametrize("domain", ["legal", "hr", "it"])
def test_no_historical_transition_or_update_contract_is_invented(schemas, domain):
    document = schemas[f"https://schemas.alos.dev/v1/{domain}/{domain}-contracts.schema.json"]
    historical = {"hr": ["HrAttendance"], "it": ["ItCiRun", "ItBackupRun", "ItRestoreTest", "ItServiceMonitor"], "legal": []}
    for name in historical[domain]:
        assert name + "CreateRequest" in document["$defs"]
        assert name + "UpdateRequest" not in document["$defs"]
        assert name + "TransitionRequest" not in document["$defs"]
    for name, definition in document["$defs"].items():
        if name.endswith(("CreateRequest", "UpdateRequest")):
            assert not set(definition["properties"]) & {"actor_id", "approved_by", "approved_at", "owner_actor_id", "reviewer_actor_id", "interviewer_actor_id", "decided_by", "verified_by", "released_at"}
