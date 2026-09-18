# Architecture Freeze v1 — ALOS

Status: **FINAL — Diterima dan dibekukan**

Mulai berlaku: **2026-09-17**

Dokumen ini menetapkan batas arsitektur lintas repository untuk ALOS, GENESIS, ARA, dan GIIVEPRO.
Implementasi wajib mengikuti keputusan ini sampai digantikan melalui ADR yang disetujui.

## Ownership repository

| Repository | Ownership |
|---|---|
| `alos-contracts` | Sumber kebenaran kontrak API, schema, event, identifier, state, dan compatibility. |
| `alos-backend` | Authoritative core platform: identity, authorization, tenant, business state, ToolExecutor, audit, decision, dan release. |
| `genesis-ai` | Governed AI Control Plane: capability factory, agent/skill runtime, orchestration, research, AI review, dan ModelGateway. |
| `alos-web` | Human/product experience untuk Business, ARA, GENESIS, Director, dan GIIVEPRO; bukan authority. |
| `alos-infra` | Deployment/runtime infrastructure, network, PostgreSQL/pgvector service, ingress, observability, backup, restore, dan runbook. |

Factory H1 mengikuti alur tunggal `alos-web → alos-backend → genesis-ai → alos-backend
Registry`. GENESIS hanya menghasilkan proposal. Backend membentuk authority context, memasok
catalog, memvalidasi handoff, dan menjadi satu-satunya service yang dapat mencatat Registry
state `DRAFT` atau menjalankan lifecycle governance berikutnya.

## Dependency dan communication direction

1. Semua repository aplikasi mengonsumsi kontrak kanonis dari `alos-contracts`; kontrak lintas service tidak boleh diduplikasi.
2. Alur pengguna adalah `Frontend -> ALOS Backend -> GENESIS`. Frontend tidak boleh memanggil GENESIS secara langsung.
3. Backend dan GENESIS tidak saling mengimpor domain implementation. Komunikasi menggunakan HTTP/internal contract dari `alos-contracts`.
4. GENESIS mengusulkan aksi melalui `ToolRequest -> Backend ToolExecutor -> ToolResult`. Backend memvalidasi schema, tenant, scope, permission, allowlist, dan audit sebelum eksekusi.
5. `alos-infra` menjalankan dan menghubungkan service, tetapi tidak memiliki application schema, business logic, atau authority decision.

## Authority dan governance

- ALOS Backend adalah satu-satunya authority untuk state bisnis, permission, approval, decision, audit, dan release.
- GENESIS adalah AI Control Plane dan reasoning system; GENESIS bukan authentication server, business database authority, atau release authority.
- Semua akses model wajib melalui `ModelGateway -> policy -> budget -> routing -> provider adapter`. Agent tidak boleh memanggil provider secara langsung.
- Setiap eksekusi wajib tenant-aware dan scope-aware. Permission bersifat deny-by-default, dan child execution tidak boleh memperluas authority parent.
- Agent, Sub-Agent, dan Sub-Sub-Agent wajib membawa `run_id`, `root_run_id`, `parent_run_id`, depth, budget, serta lineage yang dapat ditelusuri.
- Evidence, review, recommendation, decision, dan release wajib terhubung melalui identifier kanonis dan `correlation_id`.
- Jalur assurance adalah `AI Review -> IT Decision -> Director Decision` bila materialitas mensyaratkannya. AI Review hanya recommendation/assurance dan tidak pernah menjadi approval authoritative.
- `OutputState` menyatakan kualitas/status output. `ReleaseState` menyatakan lifecycle aktivasi dan operasi. Keduanya adalah kontrak terpisah dan tidak boleh digabungkan.
- GIIVEPRO berjalan di atas authority ALOS yang sama dan bukan platform authority terpisah.
- Desain bersifat capability-first: kebutuhan dapat menjadi skill, workflow, rule, validator, report, human task, connector, atau agent sesuai risiko dan kebutuhan.

## Approved technology baseline

- Contracts: JSON Schema, OpenAPI, Python 3.12 validation tooling, pytest, PyYAML, `jsonschema`, validator OpenAPI ringan, dan GitHub Actions.
- Backend: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy Async, Alembic, PostgreSQL, pytest, Ruff, mypy, OpenTelemetry, Docker, dan GitHub Actions.
- GENESIS: Python 3.12, FastAPI, Pydantic v2; PydanticAI, LangGraph, dan MCP hanya melalui adapter; PostgreSQL/pgvector sebagai target persistence AI yang terpisah dari business authority; OpenTelemetry, pytest, Ruff, mypy, Docker, dan GitHub Actions. Hermes hanya reference architecture.
- Web: Next.js, React, TypeScript, pnpm, dan Backend API sebagai satu-satunya network boundary aplikasi.
- Infra: Docker, Docker Compose, PostgreSQL/pgvector, Caddy, OpenTelemetry, dan GitHub Actions.

Teknologi di luar baseline memerlukan kebutuhan yang terdokumentasi dan ADR sebelum diadopsi.

## Forbidden architecture patterns

- Frontend memanggil GENESIS, model provider, database, atau authoritative service selain Backend.
- GENESIS atau Agent mengakses business database secara langsung.
- Agent menjalankan business tool/action tanpa Backend ToolExecutor.
- Agent atau domain GENESIS memanggil provider di luar ModelGateway.
- AI melakukan final approval, authoritative decision, release, atau self-activation.
- Child agent memperluas tenant, scope, permission, tool access, budget, atau authority parent.
- Duplikasi atau fork permanen contract lintas repository.
- Menggabungkan OutputState dengan ReleaseState.
- Menyimpan secret pada source, browser, contract payload, contoh, atau repository.
- Menambah framework runtime/orchestration, message broker, cache, database, atau infrastructure platform di luar baseline tanpa ADR.

## Perubahan setelah freeze

Perubahan besar terhadap ownership, dependency direction, authority, trust boundary, canonical contract,
atau approved technology baseline **wajib** memiliki ADR, review owner repository terkait, analisis
compatibility/security, dan rencana migrasi lintas repository. Breaking contract change wajib
menaikkan versi sesuai kebijakan versioning dan harus ditolak CI bila tidak dideklarasikan.
