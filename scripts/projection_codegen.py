"""Generate Strategy and Executive types directly from their canonical schemas."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Renderer:
    def __init__(self, domain: str, python: bool) -> None:
        self.python = python
        self.domain = domain
        self.imports: set[str] = set()
        self.documents = {
            doc["$id"]: doc
            for path in sorted((ROOT / "schemas").glob("**/*.schema.json"))
            for doc in [json.loads(path.read_text(encoding="utf-8"))]
        }
        self.declarations: dict[str, str] = {}

    def reference(self, ref: str, document: dict) -> tuple[dict, dict]:
        uri, _, fragment = ref.partition("#")
        source = self.documents[uri] if uri else document
        value = source
        for part in fragment.strip("/").split("/") if fragment else []:
            value = value[part]
        return value, source

    def value(self, schema: dict, name: str, document: dict) -> str:
        if "$ref" in schema:
            ref = schema["$ref"]
            if "/common/identifiers.schema.json" in ref:
                return "str" if self.python else "string"
            target, source = self.reference(ref, document)
            if "#" not in ref:
                if f"/{self.domain}/" not in ref:
                    self.imports.add(source["title"])
                    return source["title"]
                return self.declare(source["title"], target, source)
            return self.value(target, name, source)
        if "const" in schema or "enum" in schema:
            values = schema.get("enum", [schema.get("const")])
            if self.python:
                return "Literal[" + ", ".join(repr(v) for v in values) + "]"
            return " | ".join(json.dumps(v) for v in values)
        options = schema.get("oneOf", schema.get("anyOf"))
        if options:
            return " | ".join(self.value(item, name, document) for item in options)
        kind = schema.get("type", "object")
        if isinstance(kind, list):
            return " | ".join(self.value({**schema, "type": item}, name, document) for item in kind)
        if kind == "array":
            item = self.value(schema["items"], name + "Item", document)
            return f"list[{item}]" if self.python else f"readonly ({item})[]"
        if kind == "object":
            if "properties" in schema:
                return self.declare(name, schema, document)
            additional = schema.get("additionalProperties", {})
            item = (
                self.value(additional, name + "Value", document)
                if additional
                else ("object" if self.python else "unknown")
            )
            return f"dict[str, {item}]" if self.python else f"Readonly<Record<string, {item}>>"
        return (
            {
                "string": "str",
                "number": "float",
                "integer": "int",
                "boolean": "bool",
                "null": "None",
            }
            if self.python
            else {
                "string": "string",
                "number": "number",
                "integer": "number",
                "boolean": "boolean",
                "null": "null",
            }
        )[kind]

    def declare(self, name: str, schema: dict, document: dict) -> str:
        if name in self.declarations:
            return name
        if "$ref" in schema:
            schema, document = self.reference(schema["$ref"], document)
        self.declarations[name] = ""
        if "properties" not in schema:
            value = self.value(schema, name + "Value", document)
            self.declarations[name] = (
                f"{name} = {value}" if self.python else f"export type {name} = {value};"
            )
            return name
        lines = [
            f"class {name}(TypedDict, total=False):"
            if self.python
            else f"export interface {name} {{"
        ]
        required = set(schema.get("required", []))
        for field, prop in schema["properties"].items():
            value = self.value(
                prop, name + "".join(part.title() for part in field.split("_")), document
            )
            if self.python:
                value = repr(value)
                if field in required:
                    value = f"Required[{value}]"
                lines.append(f"    {field}: {value}")
            else:
                optional = "" if field in required else "?"
                lines.append(f"  readonly {field}{optional}: {value};")
        if not self.python:
            lines.append("}")
        self.declarations[name] = "\n".join(lines)
        return name

    def render(self, domain: str) -> str:
        for uri, document in self.documents.items():
            if f"/{domain}/" in uri:
                self.declare(document["title"], document, document)
        prefix = "#" if self.python else "//"
        lines = [
            f"{prefix} Generated by scripts/generate_{'python' if self.python else 'typescript'}.py. DO NOT EDIT.",
            f"{prefix} Source of truth: schemas/{domain}/*.schema.json.",
            "",
        ]
        if self.python:
            lines += ["from typing import Literal, Required, TypedDict", ""]
        if self.imports:
            names = ", ".join(sorted(self.imports))
            lines.append(
                f"from strategy_contracts import {names}"
                if self.python
                else f'import type {{ {names} }} from "./strategy";'
            )
        lines.extend(self.declarations.values())
        if domain == "strategy":
            aliases = {
                "StrategyPlan": "StrategicPlan | OperatingPlan",
                "CascadePreview": "CascadePreviewResponse",
                "StrategyLifecycleState": "StrategicPlan['lifecycle_state']",
                "VerificationState": "MetricObservation['verification_state']",
                "ConstraintResultState": "ConstraintResult['result']",
                "CascadeRunStatus": "CascadeRun['status']",
                "MetricValueKind": "MetricObservation['kind']",
                "BusinessUnit": "BusinessTarget['unit']",
                "MeasurementType": "BusinessTarget['measurement_type']",
                "VersionRef": "BusinessTarget['plan_ref']",
            }
            if not self.python:
                lines.extend(f"export type {name} = {value};" for name, value in aliases.items())
        return "\n\n".join(lines) + "\n"


def render(domain: str, *, python: bool) -> str:
    return Renderer(domain, python).render(domain)
