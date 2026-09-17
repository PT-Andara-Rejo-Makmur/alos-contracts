"""Detect common backward-incompatible JSON Schema changes against a git ref."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.validate_schemas import ROOT


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
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout


def baseline_paths(ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        line for line in result.stdout.splitlines()
        if line.endswith(".schema.json") and (line.startswith("schemas/") or line.startswith("events/"))
    }


def compare_ref(ref: str) -> list[str]:
    violations: list[str] = []
    current = {
        path.relative_to(ROOT).as_posix(): path
        for pattern in ("schemas/**/*.schema.json", "events/**/*.schema.json")
        for path in ROOT.glob(pattern)
    }
    previous = baseline_paths(ref)
    for removed in sorted(previous - set(current)):
        violations.append(f"{removed}: schema removed")
    for relative_path in sorted(previous & set(current)):
        old = json.loads(git_text(ref, relative_path))
        new = json.loads(current[relative_path].read_text(encoding="utf-8"))
        violations.extend(f"{relative_path}: {item}" for item in breaking_changes(old, new))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", required=True, help="Git commit or ref to compare against")
    args = parser.parse_args()
    violations = compare_ref(args.baseline_ref)
    if violations:
        print("Backward-incompatible contract changes detected:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print(f"No detected breaking schema changes against {args.baseline_ref}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
