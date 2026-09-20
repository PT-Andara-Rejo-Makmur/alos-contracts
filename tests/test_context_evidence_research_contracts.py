import copy
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from scripts.generate_python import OUTPUT as PYTHON_OUTPUT
from scripts.generate_python import render as render_python
from scripts.generate_typescript import CONTEXT_RESEARCH_OUTPUT as TYPESCRIPT_OUTPUT
from scripts.generate_typescript import render_context_research as render_typescript


SCHEMA_BASE = "https://schemas.alos.dev/v1"
ROOT = Path(__file__).resolve().parents[1]


def validate(schema_id, payload, schemas, registry):
    Draft202012Validator(
        schemas[schema_id], registry=registry, format_checker=FormatChecker()
    ).validate(payload)


def without_schema(document):
    return {key: value for key, value in document.items() if key != "$schema"}


def test_execution_context_accepts_backend_tool_allowlist(load_json, schemas, registry):
    payload = without_schema(load_json("examples/agent/agent-run-request.json"))[
        "execution_context"
    ]
    payload["allowed_tool_ids"] = ["research.external.retrieve"]
    validate(
        f"{SCHEMA_BASE}/common/execution-context.schema.json",
        payload,
        schemas,
        registry,
    )


def test_context_bundle_is_canonical_and_correlation_aware(load_json, schemas, registry):
    payload = without_schema(load_json("examples/context/context-bundle.authorized.json"))
    validate(f"{SCHEMA_BASE}/context/context-bundle.schema.json", payload, schemas, registry)
    assert payload["correlation_id"] == payload["evidence_refs"][0]["correlation_id"]
    assert payload["allowed_tool_ids"] == ["research.external.retrieve"]
    assert "selected_segments" not in payload
    assert "ranking_score" not in payload
    assert "reasoning_trace" not in payload


def test_evidence_bundle_preserves_scope_and_correlation_lineage(
    load_json, schemas, registry
):
    context = without_schema(
        load_json("examples/context/context-bundle.authorized.json")
    )
    evidence = context["evidence_refs"][0]
    bundle = {
        "bundle_id": "bundle_market_001",
        "tenant_id": context["tenant_id"],
        "organization_id": context["organization_id"],
        "workspace_id": context["workspace_id"],
        "run_id": evidence["run_id"],
        "correlation_id": context["correlation_id"],
        "scope_refs": context["scope_refs"],
        "evidence_refs": [evidence],
    }
    validate(
        f"{SCHEMA_BASE}/evidence/evidence-bundle.schema.json",
        bundle,
        schemas,
        registry,
    )
    assert bundle["correlation_id"] == evidence["correlation_id"]
    assert bundle["scope_refs"] == evidence["scope_refs"]


def test_internal_and_external_evidence_semantics_are_valid(load_json, schemas, registry):
    internal = without_schema(load_json("examples/context/context-bundle.authorized.json"))[
        "evidence_refs"
    ][0]
    external = without_schema(load_json("examples/evidence/evidence-ref.external.json"))
    schema_id = f"{SCHEMA_BASE}/evidence/evidence-ref.schema.json"
    validate(schema_id, internal, schemas, registry)
    validate(schema_id, external, schemas, registry)
    assert internal["source_type"] == "INTERNAL"
    assert external["source_type"] == "EXTERNAL"
    assert external["content_trust"] == "UNTRUSTED"
    assert external["instruction_authority"] is False


def test_external_evidence_cannot_claim_trust_or_instruction_authority(
    load_json, schemas, registry
):
    schema_id = f"{SCHEMA_BASE}/evidence/evidence-ref.schema.json"
    external = without_schema(load_json("examples/evidence/evidence-ref.external.json"))

    trusted = copy.deepcopy(external)
    trusted["content_trust"] = "GOVERNED"
    with pytest.raises(ValidationError):
        validate(schema_id, trusted, schemas, registry)

    instruction = copy.deepcopy(external)
    instruction["instruction_authority"] = True
    with pytest.raises(ValidationError):
        validate(schema_id, instruction, schemas, registry)


@pytest.mark.parametrize(
    "path",
    (
        "examples/research/research-decision.internal.json",
        "examples/research/research-decision.external.json",
    ),
)
def test_research_decision_states_are_canonical(path, load_json, schemas, registry):
    payload = without_schema(load_json(path))
    validate(f"{SCHEMA_BASE}/research/research-decision.schema.json", payload, schemas, registry)


def test_invalid_research_decision_state_is_rejected(load_json, schemas, registry):
    payload = without_schema(load_json("examples/research/research-decision.internal.json"))
    payload["decision"] = "EXECUTE_EXTERNAL_HTTP"
    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/research/research-decision.schema.json",
            payload,
            schemas,
            registry,
        )


@pytest.mark.parametrize(
    "decision",
    (
        "USE_INTERNAL_SOURCE",
        "USE_MEMORY",
        "INSUFFICIENT_EVIDENCE",
        "NEEDS_INFORMATION",
    ),
)
def test_non_external_research_states_accept_no_retrieval(
    decision, load_json, schemas, registry
):
    payload = without_schema(load_json("examples/research/research-decision.internal.json"))
    payload["decision"] = decision
    payload["retrieval"] = None
    validate(
        f"{SCHEMA_BASE}/research/research-decision.schema.json",
        payload,
        schemas,
        registry,
    )


def test_external_research_is_backend_tool_proposal_without_authority_expansion(
    load_json, schemas, registry
):
    payload = without_schema(load_json("examples/research/research-decision.external.json"))
    retrieval = payload["retrieval"]
    assert retrieval == {
        "boundary": "BACKEND_TOOL_EXECUTOR",
        "tool_id": "research.external.retrieve",
        "instruction_authority": False,
        "permission_expansion": False,
        "scope_expansion": False,
    }

    forged = copy.deepcopy(payload)
    forged["retrieval"]["permission_expansion"] = True
    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/research/research-decision.schema.json",
            forged,
            schemas,
            registry,
        )


def test_research_decision_does_not_carry_raw_authorization_snapshot(
    load_json, schemas, registry
):
    payload = without_schema(load_json("examples/research/research-decision.internal.json"))
    payload["authorized_permission_refs"] = ["admin.all"]
    with pytest.raises(ValidationError):
        validate(
            f"{SCHEMA_BASE}/research/research-decision.schema.json",
            payload,
            schemas,
            registry,
        )


def test_public_context_projection_is_explicit_and_correlation_aware(schemas, registry):
    payload = {
        "status": "ACTIVE",
        "context_id": "context_public_001",
        "tenant_id": "tenant_public",
        "organization_id": "org_public",
        "workspace_id": "workspace_public",
        "actor_id": "actor_public",
        "data_classification": "INTERNAL",
        "scope_refs": ["research.technology"],
        "evidence_refs": [],
        "items": [],
        "correlation_id": "corr_context_public_001",
    }
    validate(
        f"{SCHEMA_BASE}/context/context-projection.schema.json",
        payload,
        schemas,
        registry,
    )
    assert "permission_refs" not in payload
    assert "allowed_tool_ids" not in payload


def test_research_domain_access_cannot_claim_authorized_while_denied(schemas, registry):
    domains = [
        "TECHNOLOGY",
        "PROPERTY_BUSINESS",
        "MANAGEMENT",
        "PROPERTY_MARKET",
    ]
    payload = {
        "domains": [
            {
                "domain": domain,
                "status": "DENIED",
                "is_allowed": False,
                "reason": "Denied by Backend policy.",
                "required_scope": f"research.{domain.lower()}",
            }
            for domain in domains
        ],
        "correlation_id": "corr_domain_access_001",
    }
    schema_id = f"{SCHEMA_BASE}/research/domain-access-response.schema.json"
    validate(schema_id, payload, schemas, registry)
    payload["domains"][0]["is_allowed"] = True
    with pytest.raises(ValidationError):
        validate(schema_id, payload, schemas, registry)


def test_public_research_request_cannot_supply_authority(schemas, registry):
    payload = {
        "question": "Apa teknologi yang relevan untuk operasi?",
        "source_mode": "INTERNAL",
        "domain": "TECHNOLOGY",
    }
    schema_id = f"{SCHEMA_BASE}/research/public-research-request.schema.json"
    validate(schema_id, payload, schemas, registry)
    payload["execution_context"] = {"permission_refs": ["admin"]}
    with pytest.raises(ValidationError):
        validate(schema_id, payload, schemas, registry)


def test_public_research_receipt_exposes_safe_decision_state_only(schemas, registry):
    payload = {
        "request_id": "research_public_001",
        "state": "NEEDS_REVIEW",
        "correlation_id": "corr_research_public_001",
        "decision": "REQUEST_EXTERNAL_RESEARCH",
    }
    validate(
        f"{SCHEMA_BASE}/research/research-request-receipt.schema.json",
        payload,
        schemas,
        registry,
    )
    assert "retrieval" not in payload
    assert "authorized_permission_refs" not in payload


@pytest.mark.parametrize(
    "code",
    (
        "PERMISSION_DENIED",
        "SCOPE_DENIED",
        "CONTEXT_INVALID",
        "CONTEXT_UNAVAILABLE",
        "EVIDENCE_UNAVAILABLE",
        "BLOCKED_SOURCE",
        "EXTERNAL_RESEARCH_BLOCKED",
        "EXTERNAL_RESEARCH_UNAVAILABLE",
        "GENESIS_TIMEOUT",
        "NEEDS_INFORMATION",
    ),
)
def test_structured_errors_use_existing_correlation_aware_contract(
    code, schemas, registry
):
    payload = {
        "code": code,
        "message": "The governed operation did not complete.",
        "correlation_id": "corr_external_research_001",
        "retryable": False,
        "details": {"reason": "tool is not in the Backend allowlist"},
    }
    validate(f"{SCHEMA_BASE}/common/error.schema.json", payload, schemas, registry)
    assert not {"stack_trace", "credential", "secret"}.intersection(payload["details"])


def test_public_openapi_does_not_expose_internal_authority_or_research_state():
    public_path = ROOT / "openapi/public/alos-public-api.yaml"
    public_text = public_path.read_text(encoding="utf-8")
    public = yaml.safe_load(public_text)
    assert "research-decision.schema.json" not in public_text
    assert "execution-context.schema.json" not in public_text
    assert "evidence-ref.schema.json" not in public_text
    assert "authorized_permission_refs" not in public_text
    assert "/internal/" not in public["paths"]


def test_generated_context_research_artifacts_are_current():
    assert TYPESCRIPT_OUTPUT.read_text(encoding="utf-8") == render_typescript()
    assert PYTHON_OUTPUT.read_text(encoding="utf-8") == render_python()
