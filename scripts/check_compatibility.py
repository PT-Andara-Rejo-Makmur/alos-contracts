"""Detect common backward-incompatible JSON Schema changes against a git ref."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
from typing import Any

if __package__:
    from .validate_schemas import ROOT
else:
    from validate_schemas import ROOT


APPROVED_BREAKING_CHANGES_PATH = ROOT / "compatibility" / "approved-breaking-changes.json"


def git_command(*args: str) -> list[str]:
    """Build a git command that also works in sandboxed Windows audit users."""
    return ["git", "-c", f"safe.directory={ROOT.as_posix()}", *args]


def resolve_refs(document: dict[str, Any], schemas: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Materialize local canonical $refs before comparing schema constraints.

    A schema may evolve from an inline object to a reusable canonical schema without
    changing its consumer-facing contract. Compatibility checks must compare the
    effective schemas, not their storage form.
    """

    def resolve(value: Any, resolving: tuple[str, ...] = ()) -> Any:
        if isinstance(value, list):
            return [resolve(item, resolving) for item in value]
        if not isinstance(value, dict):
            return value
        reference = value.get("$ref")
        if isinstance(reference, str) and reference in schemas and reference not in resolving:
            target = resolve(schemas[reference], (*resolving, reference))
            siblings = {
                key: resolve(item, resolving)
                for key, item in value.items()
                if key != "$ref"
            }
            if isinstance(target, dict):
                merged = copy.deepcopy(target)
                merged.update(siblings)
                return merged
            return target
        return {key: resolve(item, resolving) for key, item in value.items() if key != "$id"}

    return resolve(document)


def breaking_changes(old: dict, new: dict, location: str = "$") -> list[str]:
    """Return conservative compatibility violations for consumer-facing constraints."""
    issues: list[str] = []
    old_types = old.get("type")
    new_types = new.get("type")
    if old_types is not None and new_types is not None and old_types != new_types:
        issues.append(f"{location}: type changed from {old_types!r} to {new_types!r}")

    old_enum = set(old.get("enum", []))
    new_enum = set(new.get("enum", []))
    if old_enum and new_enum and not old_enum.issubset(new_enum):
        issues.append(f"{location}: enum values removed: {sorted(old_enum - new_enum)}")

    old_required = set(old.get("required", []))
    new_required = set(new.get("required", []))
    if added := new_required - old_required:
        issues.append(f"{location}: required properties added: {sorted(added)}")

    old_properties = old.get("properties", {})
    new_properties = new.get("properties", {})
    if removed := set(old_properties) - set(new_properties):
        issues.append(f"{location}: properties removed: {sorted(removed)}")
    for name in set(old_properties) & set(new_properties):
        issues.extend(breaking_changes(old_properties[name], new_properties[name], f"{location}.{name}"))

    for keyword in ("minLength", "minimum", "minItems", "minProperties"):
        if keyword in new and new[keyword] > old.get(keyword, new[keyword]):
            issues.append(f"{location}: {keyword} became more restrictive")
    for keyword in ("maxLength", "maximum", "maxItems", "maxProperties"):
        if keyword in new and new[keyword] < old.get(keyword, new[keyword]):
            issues.append(f"{location}: {keyword} became more restrictive")
    return issues


def git_text(ref: str, path: str) -> str:
    result = subprocess.run(
        git_command("show", f"{ref}:{path}"),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def schema_documents(ref: str | None = None) -> dict[str, dict[str, Any]]:
    paths = (
        baseline_paths(ref) if ref is not None else {
            path.relative_to(ROOT).as_posix()
            for pattern in ("schemas/**/*.schema.json", "events/**/*.schema.json")
            for path in ROOT.glob(pattern)
        }
    )
    documents: dict[str, dict[str, Any]] = {}
    for path in paths:
        raw = git_text(ref, path) if ref is not None else (ROOT / path).read_text(encoding="utf-8")
        document = json.loads(raw)
        schema_id = document.get("$id")
        if isinstance(schema_id, str):
            documents[schema_id] = document
    return documents


def baseline_paths(ref: str) -> set[str]:
    result = subprocess.run(
        git_command("ls-tree", "-r", "--name-only", ref),
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        line for line in result.stdout.splitlines()
        if line.endswith(".schema.json") and line.startswith(("schemas/", "events/"))
    }


def compare_ref(ref: str) -> list[str]:
    violations: list[str] = []
    current = {
        path.relative_to(ROOT).as_posix(): path
        for pattern in ("schemas/**/*.schema.json", "events/**/*.schema.json")
        for path in ROOT.glob(pattern)
    }
    previous = baseline_paths(ref)
    old_documents = schema_documents(ref)
    new_documents = schema_documents()
    for removed in sorted(previous - set(current)):
        violations.append(f"{removed}: schema removed")
    for relative_path in sorted(previous & set(current)):
        old = resolve_refs(json.loads(git_text(ref, relative_path)), old_documents)
        new = resolve_refs(
            json.loads(current[relative_path].read_text(encoding="utf-8")), new_documents
        )
        violations.extend(f"{relative_path}: {item}" for item in breaking_changes(old, new))
    return violations


def approved_breaking_changes() -> set[str]:
    """Load exact, documented bootstrap cutover exceptions.

    This does not weaken detection. An exception only applies when the complete
    schema path and complete detected violation still match the reviewed record.
    """
    document = json.loads(APPROVED_BREAKING_CHANGES_PATH.read_text(encoding="utf-8"))
    return {
        f"{entry['schema']}: {entry['violation']}"
        for entry in document["approved_breaking_changes"]
    }


def split_approved(violations: list[str]) -> tuple[list[str], list[str]]:
    """Return reviewed cutover changes and any unreviewed compatibility violations."""
    approved = approved_breaking_changes()
    return (
        [violation for violation in violations if violation in approved],
        [violation for violation in violations if violation not in approved],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", required=True, help="Git commit or ref to compare against")
    args = parser.parse_args()
    approved, violations = split_approved(compare_ref(args.baseline_ref))
    if approved:
        print("Approved bootstrap breaking changes (strict schemas retained):")
        for violation in approved:
            print(f"- {violation}")
    if violations:
        print("Backward-incompatible contract changes detected:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print(f"No unapproved breaking schema changes against {args.baseline_ref}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
