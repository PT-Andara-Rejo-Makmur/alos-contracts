# Catatan Perubahan

Semua perubahan penting mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) dan Semantic Versioning.

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
