"""Read projections describe source availability without inventing business data."""

import copy
import importlib
import json

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from scripts.projection_codegen import ROOT, render

BASE = "https://schemas.alos.dev/v1/executive/"


def overview():
    return {
        "tenant_id": "tenant_01",
        "organization_id": "org_01",
        "workspace_id": "workspace_01",
        "strategy": {
            "source": "strategy",
            "status": "CONNECTED_EMPTY",
            "authoritative": True,
            "last_updated_at": None,
        },
        "shared_work": {
            "source": "shared-work",
            "status": "UNAVAILABLE",
            "authoritative": True,
            "last_updated_at": None,
        },
        "domains": [
            {"domain": "finance", "status": "UNAVAILABLE", "sources": [], "last_verified_at": None}
        ],
        "period": None,
        "last_updated_at": None,
    }


def validator(schemas, registry):
    return Draft202012Validator(
        schemas[BASE + "executive-overview-projection.schema.json"],
        registry=registry,
        format_checker=FormatChecker(),
    )


@pytest.mark.parametrize("status", ["CONNECTED", "CONNECTED_EMPTY", "UNAVAILABLE", "ERROR"])
def test_all_source_states_allow_unknown_timestamps(schemas, registry, status):
    payload = overview()
    payload["strategy"]["status"] = status
    validator(schemas, registry).validate(payload)
    assert payload["last_updated_at"] is None


@pytest.mark.parametrize(
    "field", ["revenue", "sales", "cashflow", "kpis", "project_progress", "division_statistics"]
)
def test_operational_business_numbers_are_not_executive_contract_fields(schemas, registry, field):
    payload = overview()
    payload[field] = 0
    with pytest.raises(ValidationError):
        validator(schemas, registry).validate(payload)


def test_status_and_timestamps_are_strict_and_period_reuses_strategy(schemas, registry):
    check = validator(schemas, registry)
    for path, value in [
        ("status", "SUCCESS"),
        ("last_updated_at", 0),
        ("last_updated_at", "yesterday"),
        ("authoritative", "true"),
    ]:
        payload = overview()
        payload["strategy"][path] = value
        with pytest.raises(ValidationError):
            check.validate(payload)
    payload = overview()
    payload["period"] = {
        "granularity": "ANNUAL",
        "starts_at": "2027-01-01",
        "ends_at": "2027-12-31",
    }
    payload["strategy"]["verification_state"] = "VERIFIED"
    check.validate(payload)
    unknown = copy.deepcopy(payload)
    unknown["strategy"]["verification_state"] = None
    check.validate(unknown)


@pytest.mark.parametrize("domain", ["strategy", "executive"])
@pytest.mark.parametrize("python", [True, False])
def test_generated_projection_types_are_derived_and_consistent(domain, python):
    extension = "_contracts.py" if python else ".ts"
    language = "python" if python else "typescript"
    output = ROOT / "generated" / language / (domain + extension)
    assert output.read_text(encoding="utf-8") == render(domain, python=python)


def test_generated_python_preserves_required_nullable_fields(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "generated" / "python"))
    contracts = importlib.import_module("executive_contracts")
    assert "tenant_id" in contracts.ExecutiveOverviewProjection.__annotations__
    assert "last_updated_at" in contracts.ExecutiveSourceStatus.__annotations__
    assert "last_updated_at" in contracts.ExecutiveSourceStatus.__required_keys__
    assert "period" in contracts.ExecutiveOverviewProjection.__optional_keys__
    strategy = importlib.import_module("strategy_contracts")
    assert set(strategy.StrategyPlanCreateRequest.__annotations__) == set(
        json.loads(
            (ROOT / "schemas/strategy/strategy-plan-create-request.schema.json").read_text()
        )["properties"]
    )
