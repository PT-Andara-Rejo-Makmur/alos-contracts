import json
from pathlib import Path

import pytest
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def schemas() -> dict[str, dict]:
    documents = {}
    paths = [*ROOT.glob("schemas/**/*.schema.json"), *ROOT.glob("events/**/*.schema.json")]
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        documents[document["$id"]] = document
    return documents


@pytest.fixture(scope="session")
def registry(schemas) -> Registry:
    return Registry().with_resources(
        (schema_id, Resource.from_contents(schema)) for schema_id, schema in schemas.items()
    )


@pytest.fixture()
def load_json():
    def _load(relative_path: str) -> dict:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    return _load
