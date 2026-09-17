from pathlib import Path

from scripts.validate_openapi import validate_file

ROOT = Path(__file__).resolve().parents[1]


def test_openapi_files_are_valid():
    paths = sorted(ROOT.glob("openapi/**/*.yaml"))
    assert paths
    for path in paths:
        validate_file(path)
