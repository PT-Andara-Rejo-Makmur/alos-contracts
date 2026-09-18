# Catatan Perubahan

Semua perubahan penting mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) dan Semantic Versioning.

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
