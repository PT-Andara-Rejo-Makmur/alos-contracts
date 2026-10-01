import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://schemas.alos.dev/v1/"


def validator(name):
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (ROOT / "schemas").rglob("*.schema.json")
    ]
    registry = Registry().with_resources(
        (item["$id"], Resource.from_contents(item)) for item in documents
    )
    return Draft202012Validator(
        {"$ref": BASE + name}, registry=registry, format_checker=FormatChecker()
    )


@pytest.mark.parametrize(
    "name",
    [
        "strategy/metric-observation-create-request.schema.json",
        "strategy/planning-assumption-create-request.schema.json",
    ],
)
@pytest.mark.parametrize("source", [None, "", "   "])
def test_source_linked_requires_explicit_nonblank_source(name, source):
    document = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    conditional = document["allOf"][-1]
    with pytest.raises(ValidationError):
        Draft202012Validator(conditional).validate(
            {"source_mode": "SOURCE_LINKED", "source_ref": source}
        )


@pytest.mark.parametrize("state", ["VERIFIED", "CONFLICT", "REJECTED"])
def test_verification_decision_requires_reason_and_rejects_forged_actor(state):
    validate = validator("strategy/strategy-verification-request.schema.json")
    valid = {"verification_state": state, "reason": "Evidence reviewed"}
    validate.validate(valid)
    with pytest.raises(ValidationError):
        validate.validate({**valid, "actor_id": "forged_actor"})
    with pytest.raises(ValidationError):
        validate.validate({**valid, "reason": " "})


def test_candidate_explicitly_represents_missing_metadata():
    validate = validator("strategy/cascade-derived-target-candidate.schema.json")
    valid = {
        "target_id": "target_candidate",
        "version": 1,
        "calculated_value": None,
        "request": None,
        "required_metadata": ["code", "name", "period", "owner_workspace_id"],
    }
    validate.validate(valid)
    with pytest.raises(ValidationError):
        validate.validate({"target_id": "target_candidate"})
    with pytest.raises(ValidationError):
        validate.validate({**valid, "revenue": 0})


def test_strategy_overview_empty_is_not_fake_business_performance():
    validate = validator("strategy/strategy-overview-projection.schema.json")
    empty = {
        "active_strategic_plans": [],
        "active_operating_plans": [],
        "plans": [],
        "objectives": [],
        "targets": [],
        "assumptions": [],
        "last_updated_at": None,
    }
    validate.validate(empty)
    for field in ("revenue", "sales", "cashflow", "kpis"):
        with pytest.raises(ValidationError):
            validate.validate({**empty, field: 0})


def test_target_update_cannot_reassign_plan_owner_or_lifecycle():
    validate = validator("strategy/business-target-update-request.schema.json")
    validate.validate({"version": 2, "name": "Reviewed revised target"})
    for field, value in (
        ("lifecycle_state", "ACTIVE"),
        ("owner_workspace_id", "foreign_workspace"),
        ("plan_ref", {"id": "forged_plan", "version": 1}),
    ):
        with pytest.raises(ValidationError):
            validate.validate({"version": 2, field: value})
    with pytest.raises(ValidationError):
        validate.validate({"version": 2})
