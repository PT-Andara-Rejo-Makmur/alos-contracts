"""Validate example JSON payloads against their declared canonical schemas."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

if __package__:
    from .validate_schemas import ROOT, load_schemas
else:
    from validate_schemas import ROOT, load_schemas


def build_registry(schemas: dict[str, dict]) -> Registry:
    return Registry().with_resources(
        (schema_id, Resource.from_contents(schema)) for schema_id, schema in schemas.items()
    )


def example_paths() -> list[Path]:
    return sorted([
        *ROOT.glob("examples/**/*.json"),
        *ROOT.glob("events/**/*.example.json"),
        *ROOT.glob("compatibility/fixtures/mvp1/**/*.json"),
    ])


def validate_example(path: Path, schemas: dict[str, dict], registry: Registry) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema_id = payload.get("$schema")
    if schema_id not in schemas:
        raise ValueError(f"{path.relative_to(ROOT)} declares unknown $schema {schema_id!r}")
    instance = {key: value for key, value in payload.items() if key != "$schema"}
    Draft202012Validator(
        schemas[schema_id], registry=registry, format_checker=FormatChecker()
    ).validate(instance)


def main() -> int:
    schemas = load_schemas()
    registry = build_registry(schemas)
    paths = example_paths()
    if not paths:
        raise ValueError("No examples found")
    for path in paths:
        validate_example(path, schemas, registry)
        print(f"Validated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
