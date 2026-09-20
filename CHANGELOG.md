# Catatan Perubahan

Semua perubahan penting mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) dan Semantic Versioning.

## [1.4.0] - 2026-09-20

### Ditambahkan

- Contract publik additive untuk projection context aktif, akses empat domain riset,
  permintaan riset, dan receipt yang aman untuk frontend.
- Contract internal untuk keputusan sumber riset Backend ke GENESIS tanpa memindahkan
  authority, egress, permission, scope, atau eksekusi tool.
- Endpoint tersebut pada public dan internal OpenAPI, generated Python/TypeScript,
  canonical examples, serta regression test authority dan correlation.

### Dipertahankan

- Schema `ResearchRequest` yang telah ada tetap kompatibel. Request publik memakai
  schema terpisah agar payload lama tidak berubah.
- Public receipt hanya mengekspos state keputusan yang aman; detail retrieval dan
  authorization snapshot tetap berada pada boundary internal.

## [1.3.1] - 2026-09-19

### Diperbaiki

- Generator TypeScript kini menghasilkan regex trailing-slash yang valid pada client
  `getCapabilityDetail`, sehingga artifact dapat diparse oleh TypeScript consumer.
- Regression test mencegah double-escaping regex pada generated Factory client.

## [1.3.0] - 2026-09-19

### Ditambahkan

- Contract alignment untuk `ExecutionContext`, `ContextBundle`, evidence lineage/source semantics, dan keputusan external research yang non-authoritative.
- Vocabulary kanonis additive untuk data classification, `INTERNAL`/`EXTERNAL`, freshness, reliability, serta governed/untrusted content trust.
- `ResearchDecision` dengan state `USE_INTERNAL_SOURCE`, `USE_MEMORY`, `REQUEST_EXTERNAL_RESEARCH`, `INSUFFICIENT_EVIDENCE`, dan `NEEDS_INFORMATION`.
- Proposal external retrieval yang hanya menunjuk `BACKEND_TOOL_EXECUTOR` dan secara schema melarang instruction authority, permission expansion, dan scope expansion.
- Contoh canonical dan regression test untuk correlation lineage, old-payload compatibility, enum rejection, external-content safety, authority boundary, serta public API exposure.
- Generated TypeScript dan Python contract types yang reproducible dan diperiksa freshness-nya oleh CI.

### Diubah

- `ExecutionContext` menerima `allowed_tool_ids` opsional sebagai snapshot allowlist dari Backend; GENESIS hanya boleh mempersempitnya dan tetap tidak mengeksekusi tool secara langsung.
- `ContextBundle` menerima field opsional untuk goal, capability, allowed tools, execution budget, memory references, dan source semantics tanpa mengekspos ranking, trimming, planner state, atau reasoning trace internal GENESIS.
- `EvidenceRef` menerima lineage, scope, retrieval timestamp, source semantics, serta invariant bahwa evidence EXTERNAL selalu `UNTRUSTED` dan tidak mempunyai instruction authority.
- `EvidenceBundle` menerima `scope_refs` opsional. Semua perubahan schema bersifat additive agar payload valid versi 1.2 tetap valid.

## [1.2.0] - 2026-09-19

### Ditambahkan

- Contract Freeze MVP2 untuk alur Requirement → RequirementUnderstanding → CapabilityDecision → CapabilityDraft → CapabilityDetail.
- Schema stage canonical baru (additive, non-breaking): `factory/requirement.schema.json`, `factory/requirement-understanding.schema.json`, `factory/capability-decision.schema.json`, `capability/capability-detail.schema.json`.
- Identifier kanonis `requirement_id` dan tautan Backend→GENESIS→Backend yang diverifikasi Backend.
- Field MVP2 opsional pada `RequirementUnderstanding`: `objective`, `trigger`, `capability_need`, `data_need`, `source_semantics`, `ambiguity` (`NONE` | `NEEDS_CLARIFICATION`).
- Field MVP2 opsional pada `CapabilityDecision` dan `CapabilityDraft`: `human_gate_required` (proposal AI; Backend governance tetap wajib human gate), `dependency_refs` pada draft.
- Public endpoint `GET /api/v1/capabilities/{capability_id}` dengan proyeksi `CapabilityDetail` yang ter-autorisasi: DRAFT hanya untuk creator, konsumen lain hanya ACTIVE yang diotorisasi, state lain fail-closed 404.
- Error contract terfrozen: `REQUIREMENT_AMBIGUOUS` (422), `CAPABILITY_NOT_FOUND` (404), `CAPABILITY_NOT_AUTHORIZED` (403), `GENESIS_HUMAN_GATE_REQUIRED` (502), dan `INTERNAL_PROCESSING_FAILURE` (500, tanpa stack trace/SQL/schema).

### Diubah

- `factory-analysis-request.schema.json` kini `$ref` ke `requirement.schema.json` (format payload identik dengan 1.1.0).
- `factory-resolution.schema.json` kini `$ref` ke `capability-decision.schema.json` (format payload identik dengan 1.1.0).

## [1.1.0] - 2026-09-18

### Ditambahkan

- Contract Freeze MVP2 H1 untuk public Factory Analyze dan internal Backend–GENESIS Factory boundary.
- Semantik canonical REUSE/CREATE, authoritative catalog reference, non-authoritative Registry handoff, dan Backend Registry result berstatus DRAFT.
- `AgentDraft` serta metadata H1 additive pada `CapabilityDraft`: version, scope, tool, least-privilege permission, prohibited action, risk, evidence, dan test requirements.
- Contoh CREATE/REUSE, negative contract tests, serta correlation dan authority regression tests.
- Generated TypeScript Factory type/client yang reproducible dan diperiksa agar tidak stale.

## [1.0.0] - 2026-09-17

### Ditambahkan

- Architecture Freeze v1 dan dokumentasi otoritas lintas repository.
- JSON Schema kanonis untuk kontrak common, runtime, capability, agent, skill, context, delegation, tool, evidence, research, review, decision, dan release.
- Pemisahan `CapabilityDraft` dan `CapabilityDefinition` dengan taxonomy capability-first yang kanonis.
- Field lineage tenant/correlation untuk context, capability draft, AI review, dan decision tanpa memutus payload v1 yang sudah valid.
- Pengujian katalog baseline dan konsistensi seluruh canonical identifier lintas schema.
- Dokumen OpenAPI publik ALOS dan internal ALOS–GENESIS.
- Kontrak event per domain beserta contoh yang tervalidasi.
- Validasi schema, OpenAPI, contoh, kompatibilitas, dan pytest.
- Workflow quality GitHub Actions dan placeholder ownership.
- Rekonsiliasi contract MVP-1 dari pinned `develop` SHA, compatibility fixtures tervalidasi, serta dokumentasi rename, deprecation, dan breaking state mapping.
- Split runtime MVP-1: mandatory AgentRunResult correlation, canonical ToolResult lineage pada
  hasil run, serta structured error wajib untuk terminal failure/denial/timeout/rejection.
- Rekonsiliasi knowledge/research MVP-1: provenance wajib pada `ContextBundle`, lineage
  tenant/organisasi/workspace pada evidence dan research, serta contoh request/bundle tervalidasi.
