"""Validate OpenAPI documents after resolving contract references offline."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from urllib.parse import urldefrag

import yaml
from openapi_spec_validator import validate

if __package__:
    from .validate_schemas import ROOT, load_schemas
else:
    from validate_schemas import ROOT, load_schemas


def json_pointer(document: object, fragment: str) -> object:
    current = document
    if not fragment:
        return current
    if not fragment.startswith("/"):
        raise ValueError(f"Unsupported JSON pointer fragment: #{fragment}")
    for raw_part in fragment[1:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current


def bundle_contract_refs(value: object, schemas: dict[str, dict], current_schema: dict | None = None) -> object:
    if isinstance(value, list):
        return [bundle_contract_refs(item, schemas, current_schema) for item in value]
    if not isinstance(value, dict):
        return value

    reference = value.get("$ref")
    if isinstance(reference, str) and reference.startswith("https://schemas.alos.dev/"):
        schema_id, fragment = urldefrag(reference)
        target_schema = schemas[schema_id]
        target = copy.deepcopy(json_pointer(target_schema, fragment))
        resolved = bundle_contract_refs(target, schemas, target_schema)
        siblings = {key: item for key, item in value.items() if key != "$ref"}
        if siblings:
            return {"allOf": [resolved, bundle_contract_refs(siblings, schemas, current_schema)]}
        return resolved
    if isinstance(reference, str) and reference.startswith("#") and current_schema is not None:
        target = copy.deepcopy(json_pointer(current_schema, reference[1:]))
        return bundle_contract_refs(target, schemas, current_schema)
    return {
        key: bundle_contract_refs(item, schemas, current_schema)
        for key, item in value.items()
    }


def resolve_file_refs(value: object, source_path: Path, schemas: dict[str, dict]) -> object:
    if isinstance(value, list):
        return [resolve_file_refs(item, source_path, schemas) for item in value]
    if not isinstance(value, dict):
        return value
    reference = value.get("$ref")
    if isinstance(reference, str) and not reference.startswith(("#", "http://", "https://")):
        file_part, fragment = urldefrag(reference)
        target_path = (source_path.parent / file_part).resolve()
        target = json.loads(target_path.read_text(encoding="utf-8"))
        selected = copy.deepcopy(json_pointer(target, fragment))
        return bundle_contract_refs(selected, schemas, target)
    return {
        key: resolve_file_refs(item, source_path, schemas)
        for key, item in value.items()
    }


def validate_file(path: Path) -> None:
    specification = yaml.safe_load(path.read_text(encoding="utf-8"))
    bundled = resolve_file_refs(specification, path, load_schemas())
    validate(bundled)


def main() -> int:
    paths = sorted(ROOT.glob("openapi/**/*.yaml"))
    if not paths:
        raise ValueError("No OpenAPI documents found")
    for path in paths:
        validate_file(path)
        print(f"Validated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
