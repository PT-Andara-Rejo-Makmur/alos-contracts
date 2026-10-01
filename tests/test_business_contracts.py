"""Canonical business boundaries retain exact values and server-owned authority."""

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

BASE = "https://schemas.alos.dev/v1/"
DOMAINS = ("sales", "marketing", "property", "finance")


def validator(registry, domain, definition):
    return Draft202012Validator(
        {"$ref": f"{BASE}{domain}/{domain}-contracts.schema.json#/$defs/{definition}"},
        registry=registry,
        format_checker=FormatChecker(),
    )


@pytest.mark.parametrize("domain", DOMAINS)
def test_mutations_never_accept_authority_or_lifecycle_fields(schemas, domain):
    document = schemas[f"{BASE}{domain}/{domain}-contracts.schema.json"]
    for name, definition in document["$defs"].items():
        if name.endswith(("CreateRequest", "UpdateRequest")):
            assert definition["additionalProperties"] is False
            assert not set(definition["properties"]) & {
                "tenant_id", "organization_id", "workspace_id", "actor_id",
                "status", "created_at", "updated_at", "outstanding_amount",
                "approved_by", "closed_by", "reconciled_by",
            }


@pytest.mark.parametrize("amount", [1.1, "NaN", "Infinity", "1e3", "1.001", "-10"])
def test_financial_amount_is_exact_decimal_string(registry, amount):
    validate = validator(registry, "finance", "FinanceReceivableCreateRequest")
    validate.validate({"reference": "invoice", "amount": "100.01"})
    with pytest.raises(ValidationError):
        validate.validate({"reference": "invoice", "amount": amount})


def test_signed_change_order_amount_is_explicit(registry):
    validate = validator(registry, "property", "PropertyChangeOrderCreateRequest")
    validate.validate({"project_id": "project_test", "change_number": "C1",
                       "description": "Recorded decrease", "amount_delta": "-10.25"})


def test_sales_unit_reference_preserves_unknown_project(registry):
    validate = validator(registry, "sales", "SalesUnitReferenceProjection")
    validate.validate({"property_unit_id": "unit_test", "unit_code": "U1",
                       "status": "AVAILABLE", "project_id": None})
    with pytest.raises(ValidationError):
        validate.validate({"property_unit_id": "unit_test", "unit_code": "U1",
                           "status": "AVAILABLE", "project_id": ""})


@pytest.mark.parametrize("field,value", [("tenant_id", "forged"), ("status", "APPROVED"),
                                         ("outstanding_amount", "0")])
def test_finance_forged_fields_are_rejected(registry, field, value):
    validate = validator(registry, "finance", "FinanceReceivableCreateRequest")
    with pytest.raises(ValidationError):
        validate.validate({"reference": "invoice", "amount": "100.01", field: value})


@pytest.mark.parametrize("domain", DOMAINS)
def test_overview_has_record_counts_without_synthetic_kpis(schemas, registry, domain):
    schema = schemas[f"{BASE}{domain}/{domain}-contracts.schema.json"]
    validate = Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())
    empty = {"source": {"source": domain, "status": "CONNECTED_EMPTY", "authoritative": True,
                         "last_updated_at": None},
             "counts": dict.fromkeys(schema["properties"]["counts"]["required"], 0),
             "last_updated_at": None}
    validate.validate(empty)
    with pytest.raises(ValidationError):
        validate.validate({**empty, "revenue": "0"})


@pytest.mark.parametrize("definition", ["FinanceBudgetLineUpdateRequest",
                                       "FinanceTaxObligationUpdateRequest"])
def test_recorded_financial_period_cannot_be_reassigned(registry, definition):
    with pytest.raises(ValidationError):
        validator(registry, "finance", definition).validate({"period": "2027-02"})


def test_pipeline_action_cannot_claim_final_win(registry):
    validate = validator(registry, "sales", "SalesOpportunityPipelineRequest")
    validate.validate({"stage": "Qualified"})
    with pytest.raises(ValidationError):
        validate.validate({"stage": "Won"})


def test_safety_severity_is_explicit_canonical_enum(registry):
    validate = validator(registry, "property", "PropertySafetyIncidentCreateRequest")
    data = {"project_id": "project_test", "incident_date": "2027-02-01",
            "description": "Explicit observation", "severity": "HIGH"}
    validate.validate(data)
    with pytest.raises(ValidationError):
        validate.validate({**data, "severity": "guessed"})
