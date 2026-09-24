import copy
import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, ValidationError

from scripts.validate_openapi import resolve_file_refs, validate_file
from scripts.validate_schemas import load_schemas

ROOT = Path(__file__).resolve().parents[1]


def test_openapi_files_are_valid():
    paths = sorted(ROOT.glob("openapi/**/*.yaml"))
    assert paths
    for path in paths:
        validate_file(path)


def test_internal_routes_name_the_actual_service_owner():
    document = yaml.safe_load(
        (ROOT / "openapi/internal/genesis-internal-api.yaml").read_text(encoding="utf-8")
    )
    paths = document["paths"]
    genesis_paths = {
        "/internal/v1/agent-runs",
        "/internal/v1/reviews",
        "/internal/v1/factory/analyze",
        "/internal/v1/research",
        "/internal/v1/research/run",
        "/internal/v1/system/integration",
        "/internal/v1/system/info",
    }
    backend_paths = {
        "/internal/v1/tool-requests",
        "/internal/v1/agent-runs/{run_id}/cancellation",
    }

    assert genesis_paths | backend_paths == set(paths)
    assert all(
        next(iter(paths[path].values()))["x-service-owner"] == "genesis-ai"
        for path in genesis_paths
    )
    assert all(
        next(key for key in paths[path].values() if isinstance(key, dict))["x-service-owner"]
        == "alos-backend"
        for path in backend_paths
    )


def test_review_endpoint_responses_exclude_authoritative_decisions():
    documents_and_paths = (
        ("openapi/internal/genesis-internal-api.yaml", "/internal/v1/reviews"),
        ("openapi/public/alos-public-api.yaml", "/api/v1/reviews"),
    )
    authority_exclusion = {
        "not": {
            "anyOf": [
                {"required": ["it_decision"]},
                {"required": ["director_decision"]},
            ]
        }
    }
    advisory_package = json.loads(
        (ROOT / "examples/review/review-package.json").read_text(encoding="utf-8")
    )
    advisory_package.pop("$schema")

    for document_path, endpoint_path in documents_and_paths:
        path = ROOT / document_path
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        declared_schema = document["paths"][endpoint_path]["post"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]

        assert declared_schema["allOf"][1] == authority_exclusion

        bundled = resolve_file_refs(document, path, load_schemas())
        response_schema = bundled["paths"][endpoint_path]["post"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        validator = Draft202012Validator(response_schema)
        validator.validate(advisory_package)
        for decision_field in ("it_decision", "director_decision"):
            authority_violation = copy.deepcopy(advisory_package)
            authority_violation[decision_field] = {}
            with pytest.raises(ValidationError):
                validator.validate(authority_violation)
