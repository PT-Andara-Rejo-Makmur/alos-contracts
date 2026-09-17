"""Validate every JSON Schema and its local references."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urldefrag

from jsonschema.validators import validator_for

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_GLOBS = ("schemas/**/*.schema.json", "events/**/*.schema.json")


def schema_paths() -> list[Path]:
    return sorted({path for pattern in SCHEMA_GLOBS for path in ROOT.glob(pattern)})


def load_schemas() -> dict[str, dict]:
    schemas: dict[str, dict] = {}
    for path in schema_paths():
        document = json.loads(path.read_text(encoding="utf-8"))
        schema_id = document.get("$id")
        if not schema_id:
            raise ValueError(f"{path.relative_to(ROOT)} has no $id")
        if schema_id in schemas:
            raise ValueError(f"Duplicate $id: {schema_id}")
        validator_for(document).check_schema(document)
        schemas[schema_id] = document
    return schemas


def iter_refs(value: object):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "$ref" and isinstance(item, str):
                yield item
            else:
                yield from iter_refs(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_refs(item)


def main() -> int:
    schemas = load_schemas()
    for schema_id, schema in schemas.items():
        for reference in iter_refs(schema):
            target, _ = urldefrag(reference)
            if target and target.startswith("https://schemas.alos.dev/") and target not in schemas:
                raise ValueError(f"{schema_id} references missing schema {target}")
    print(f"Validated {len(schemas)} JSON Schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
