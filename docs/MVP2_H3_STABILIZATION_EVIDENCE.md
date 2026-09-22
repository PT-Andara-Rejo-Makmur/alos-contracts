# MVP2 H3 Server-Side Stabilization Evidence

## Current final heads inspected

- `alos-contracts` source baseline: `72e9f9f935ab0c531283ada0e69b5617a92cc76e`
- `alos-backend` final cleanup: `545f4f75eb25b1f442e66b2500412c51b4662395`
- `genesis-ai`: `4c61ff60cae32665f7c017a27682601fe496dc1e`

These are the exact source revisions covered by the final cleanup evidence. The Contracts evidence
commit SHA is recorded in the delivery report because a Git commit cannot embed its own final SHA
inside its content. `alos-web` and `alos-infra` were not modified.

## Contract version

- Canonical contract version remains `1.5.0`.
- No public schema, OpenAPI semantic, compatibility rule, or canonical vocabulary changed in this
  cleanup.
- Backend persistence ordering, unused internal-model removal, tests, and evidence documentation do
  not require a contract version bump.
- `required_tool_ids` remains canonical. Deprecated `tool_ids` remains compatibility-only and does
  not grant runtime authority.

## Final H3 authority chain

```text
Principal / ExecutionContext
        ↓ narrow
AgentDefinition
        ↓ narrow
SkillDefinition prerequisites
        ↓
Backend SkillRegistry exact ACTIVE version
        ↓
AgentRunAuthority
        ↓
authorized_skill_refs
        ↓
GENESIS SkillAuthorizationSnapshot
        ↓ narrow only
SkillRuntime
```

- `AgentDefinition.skill_refs` is the only Agent–Skill assignment source of truth.
- Skill permission, scope, and tool declarations are prerequisites and cannot expand Agent or
  Backend authority.
- Exact versions are required. There is no silent latest-version fallback.
- Filesystem discovery does not grant authority.

## Registry persistence and audit

- Production composition uses `SqlRegistryStore` for registry state and `SqlAuditRepository` for
  registry and Skill audit events.
- Registry mutation now follows: build immutable candidate → `RegistryStore.save()` succeeds →
  publish candidate to the in-process cache → emit success audit.
- Failure-injection tests prove failed register, approve, or activate writes leave cached state
  unchanged and emit no false success event.
- In-memory restart/hydration coverage remains green, but it is not presented as proof of the SQL
  adapter.

**REAL POSTGRESQL VERIFICATION: PENDING DEPLOYMENT/INFRA ENVIRONMENT**

Exact evidence:

- `.github/workflows/quality.yml` has no PostgreSQL service or database provisioning step.
- A direct connection attempt to `postgresql+asyncpg://alos:alos@localhost:5432/alos_test` failed
  with `ConnectionRefusedError: [WinError 1225]`.
- No Docker workaround, infrastructure change, or in-memory substitute was added.

## Cross-repo result

The dedicated cross-repo harness passed all 11 scenarios using the Backend dependency environment.
It covers:

- exact canonical GENESIS `skill.yaml` payload registration without Backend rebuild or mutation;
- canonical contracts validation;
- Backend SkillRegistry DRAFT → APPROVED → ACTIVE lifecycle;
- ACTIVE AgentDefinition with exact `skill_refs`;
- AgentRunAuthority validation and issuance of exact `authorized_skill_refs`;
- GENESIS SkillAuthorizationSnapshot and exact package selection;
- progressive `SKILL.md` loading for Technology, Property Business, Management, and Property Market;
- fail-closed injected ref, inactive Skill, wrong exact version, permission mismatch, scope mismatch,
  and required-tool mismatch cases.

The Research Skill definitions remain owned by the canonical GENESIS packages. Backend retains only
the governed identifiers and registry payloads; it does not maintain a second definition builder.

## Final test evidence

### ALOS Contracts

- JSON Schema validation: 65 schemas passed.
- Public and internal OpenAPI validation: passed.
- Examples and MVP1 compatibility fixtures: passed.
- Python generated artifacts `--check`: passed.
- TypeScript generated artifacts `--check`: passed.
- Compatibility against `origin/main`: no unapproved breaking changes.
- `pytest -q`: **89 passed**.

### ALOS Backend

- `python -m pip install -e ".[dev]"`: passed.
- `ruff check .`: passed.
- strict `mypy`: passed for 132 source files.
- focused registry/model cleanup tests: 16 passed, including four atomicity scenarios.
- `pytest -q`: **158 passed**.
- startup import assertion: passed; application title is `ALOS Backend`.

### GENESIS and cross-repo regression

- `ruff check .`: passed.
- strict `mypy`: passed for 144 source files.
- isolated `pytest -q`: **117 passed, 1 skipped**; the skip is the cross-repo harness because the
  isolated GENESIS environment does not install Backend SQLAlchemy dependencies.
- cross-repo harness under the Backend dependency environment: **11 passed**.

Pytest emitted only cache-write warnings caused by restricted `.pytest_cache` filesystem access;
the test assertions passed.

## H3 task status

- `AI-01` through `AI-06`: **DONE** — GENESIS runtime, progressive loading, authorization narrowing,
  evaluator boundaries, package safety, and ResearchEngine regressions are green.
- `BE-01` through `BE-06`: **DONE server-side** — canonical registry lifecycle, immutable assignment,
  exact run authorization, shared persistence composition, persistent production audit wiring, and
  persist-before-cache atomicity are covered.
- `XS-01`: **PARTIAL — FE wiring pending**.
- `XS-02`: **DONE server-side** — actual AgentRunAuthority-to-GENESIS scenario passed.
- `XS-03`: **DONE** — this evidence reflects current heads, behavior, and actual test counts.
- `XS-04`: **DONE server-side** — all four R&D domain package scenarios passed.

## Out of scope confirmation

- Frontend was not modified and no frontend task is marked complete.
- H4, H5, and H6 were not expanded.
- `alos-infra` was not modified.
- No new database, Docker service, provider access, direct GENESIS HTTP/DB path, or filesystem
  authority was introduced.
