# MVP2 H3 Server-Side Stabilization Evidence

## Inspected source heads

- `alos-contracts`: `18bee12648f0f5f3720bef8db0b156fb6c55867f`
- `alos-backend`: `87f0d5f05a2a637fef7fbc9313c10f415ae7226b`
- `genesis-ai`: `7203c0840bff50323cfea19b7eb6e1a518cf3c7a`

The working branches were created from these exact `main` heads. `alos-web` and `alos-infra` were not modified.

## Contract freeze

- Contract version: `1.5.0` (additive minor release).
- `required_tool_ids` is canonical; `tool_ids` is deprecated compatibility input and is ignored by consumers.
- Permission, scope, and tool declarations are prerequisites, never grants.
- Exact `authorized_skill_refs` are issued by Backend and cannot be expanded by GENESIS.
- `AgentDefinition.skill_refs` is the only Agent–Skill assignment source of truth.

## Server-side scenario results

- Contracts: schema (65), examples, OpenAPI, compatibility against `main`, generated-artifact freshness, and `pytest` (89 passed): PASS.
- Backend: `ruff`, strict `mypy`, registry lifecycle, immutable assignment draft, audit, persistence hydration, and full `pytest` (134 passed): PASS.
- GENESIS: `ruff`, strict `mypy`, authorization filtering, progressive loading, evaluator, package safety, research profiles, and full `pytest` (112 passed; cross-repo harness skipped in the isolated GENESIS environment): PASS.
- Dedicated cross-repo harness using Backend dependencies: 5 passed.
- Cross-repo manifest → contract → Backend registry → AgentDefinition → authorization snapshot → GENESIS runtime roundtrip: PASS for Technology, Property Business, Management, and Property Market.
- Internal-evidence and Backend-governed external-research decision scenarios: PASS; correlation is preserved and no direct HTTP is introduced.

## Remaining handoff and risk

- `M2-H03-XS-01`: **PARTIAL — contracts/backend/genesis complete; FE shared-state wiring pending**.
- Production PostgreSQL persistence uses `core.registry_definitions`; the automated restart regression uses the same registry port with an in-memory store. Environment database migration/connectivity remains deployment verification.
- Branch protection and frontend work are outside this package.

## Changed areas

- Contracts: skill schemas/examples, AgentDefinition/AgentRunRequest references, public/internal OpenAPI, generated Python/TypeScript, version/changelog, and freeze tests.
- Backend: registry public query/persistence port, SQL adapter, application wiring, canonical skill API, immutable AgentDefinition assignment, R&D identifiers, audit/error behavior, and tests.
- GENESIS: immutable skill authorization snapshot, prerequisite filtering, deprecated-field handling, safe package data loading, cross-repo harness, and tests.

## Commands run

- Contracts: schema/OpenAPI/example validators, compatibility against `main`, both generators with `--check`, and `pytest -q`.
- Backend: `ruff check src tests`, `mypy src`, and `pytest -q`.
- GENESIS: `ruff check src tests`, `mypy src`, `pytest -q`, plus the cross-repo test under the Backend virtual environment with both source roots on `PYTHONPATH`.

## Rollback grouping

1. Revert GENESIS runtime alignment and cross-repo harness.
2. Revert Backend assignment/persistence/API wiring.
3. Revert contract `1.5.0` schemas, OpenAPI, and generated artifacts last.

No H4, H5, or H6 capability was added. Existing later-horizon regressions were only kept green.
