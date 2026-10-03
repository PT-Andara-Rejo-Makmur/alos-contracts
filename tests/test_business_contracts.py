"""Canonical business boundaries retain exact values and server-owned authority."""

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

BASE = "https://schemas.alos.dev/v1/"
DOMAINS = ("sales", "marketing", "property", "finance", "legal", "hr", "it")


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


def test_business_analytics_preserves_zero_and_decimal_amounts(registry):
    validate = Draft202012Validator(
        {"$ref": f"{BASE}business/business-contracts.schema.json#/$defs/BusinessAnalyticsProjection"},
        registry=registry,
        format_checker=FormatChecker(),
    )
    projection = {
        "domain": "sales",
        "generated_at": "2027-03-01T00:00:00Z",
        "period": {"from": "2027-02-01", "to": "2027-02-28", "granularity": "MONTH"},
        "series": [
            {
                "code": "closing_count",
                "label": "Closing selesai",
                "unit": "COUNT",
                "available": True,
                "source": "Closing yang telah selesai",
                "points": [{"period": "2027-02-01", "value": 0}],
            },
            {
                "code": "closing_value",
                "label": "Nilai Closing",
                "unit": "AMOUNT",
                "available": True,
                "source": "Closing yang telah selesai",
                "points": [{"period": "2027-02-01", "value": "0.00"}],
            },
        ],
        "breakdowns": [],
        "comparisons": [],
    }
    validate.validate(projection)
    with pytest.raises(ValidationError):
        validate.validate(
            {
                **projection,
                "series": [
                    {**projection["series"][1], "points": [{"period": "2027-02-01", "value": 0.0}]}
                ],
            }
        )


def test_business_analytics_rejects_malformed_or_fabricated_unavailable_values(registry):
    validate = Draft202012Validator(
        {"$ref": f"{BASE}business/business-contracts.schema.json#/$defs/BusinessAnalyticsProjection"},
        registry=registry,
        format_checker=FormatChecker(),
    )
    base = {
        "domain": "finance",
        "generated_at": "2027-03-01T00:00:00Z",
        "period": {"from": "2027-03-01", "to": "2027-03-31", "granularity": "MONTH"},
        "series": [],
        "breakdowns": [],
        "comparisons": [],
    }
    validate.validate(base)
    unavailable = {
        "code": "cash_balance",
        "label": "Posisi kas",
        "unit": "AMOUNT",
        "available": False,
        "source": "Saldo kas terverifikasi",
        "points": [],
    }
    validate.validate({**base, "series": [unavailable]})
    with pytest.raises(ValidationError):
        validate.validate({**base, "series": [{**unavailable, "points": [{"period": "2027-03-01", "value": "99.00"}]}]})
    with pytest.raises(ValidationError):
        validate.validate({**base, "period": {**base["period"], "granularity": "WEEK"}})
    with pytest.raises(ValidationError):
        validate.validate({**base, "series": [{**unavailable, "points": [{"period": "not-a-date", "value": "1.00"}]}]})


def test_business_analytics_comparisons_enforce_exact_values_by_unit(registry):
    validate = Draft202012Validator(
        {"$ref": f"{BASE}business/business-contracts.schema.json#/$defs/BusinessAnalyticsProjection"},
        registry=registry,
        format_checker=FormatChecker(),
    )
    base = {
        "domain": "executive",
        "generated_at": "2027-03-01T00:00:00Z",
        "period": {"from": "2027-03-01", "to": "2027-03-31", "granularity": "MONTH"},
        "series": [],
        "breakdowns": [],
        "comparisons": [],
    }
    item = {
        "code": "target_1",
        "label": "Closing perusahaan",
        "value": 0,
        "target_value": 3,
        "actual_value": 0,
        "forecast_value": None,
    }
    count_comparison = {
        "code": "closing_count",
        "label": "Target, aktual, dan perkiraan",
        "unit": "COUNT",
        "available": True,
        "source": "Observasi target yang dipilih",
        "items": [item],
    }
    validate.validate({**base, "comparisons": [count_comparison]})
    with pytest.raises(ValidationError):
        validate.validate({
            **base,
            "comparisons": [{
                **count_comparison,
                "items": [{**item, "actual_value": "0"}],
            }],
        })

    amount_comparison = {
        **count_comparison,
        "unit": "AMOUNT",
        "items": [{**item, "value": "0.00", "target_value": "98765432109876543210.05",
                   "actual_value": "0.00"}],
    }
    validate.validate({**base, "comparisons": [amount_comparison]})
    with pytest.raises(ValidationError):
        validate.validate({
            **base,
            "comparisons": [{
                **amount_comparison,
                "items": [{**amount_comparison["items"][0], "actual_value": 0}],
            }],
        })

    percent_comparison = {
        **count_comparison,
        "unit": "PERCENT",
        "items": [{**item, "value": 68.5, "target_value": 70, "actual_value": 68.5}],
    }
    validate.validate({**base, "comparisons": [percent_comparison]})
    with pytest.raises(ValidationError):
        validate.validate({
            **base,
            "comparisons": [{
                **percent_comparison,
                "items": [{**percent_comparison["items"][0], "actual_value": "68.5"}],
            }],
        })

    with pytest.raises(ValidationError):
        validate.validate({
            **base,
            "comparisons": [{
                **count_comparison,
                "available": False,
            }],
        })
