from pathlib import Path

import yaml

from scripts.validate_openapi import validate_file

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
