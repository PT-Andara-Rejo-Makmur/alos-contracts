# Indeks Dokumentasi alos-contracts

Mulai dari [README repository](../README.md). Panduan runtime mengikuti source
dan contracts terkini; requirements/compatibility bukan klaim seluruh fitur siap.
Bukti tes bertanggal hanya berlaku untuk source dan environment yang dicatat.
Status lintas repository dipusatkan pada [readiness produksi](https://github.com/PT-Andara-Rejo-Makmur/alos-infra/blob/development/docs/PRODUCTION_READINESS_2026-10-04.md).

Authority tetap Web → Backend → GENESIS, dengan Backend sebagai pemilik data,
akses dan keputusan. Secret, dump, log privat dan artifacts lokal tidak masuk Git.

## Panduan dan contracts

- [Governed ARA boundary](ara-contracts.md)
- [Kompatibilitas](COMPATIBILITY.md)
- [Context, Evidence, and Research Contracts](CONTEXT_EVIDENCE_RESEARCH_CONTRACTS.md)
- [Panduan Kontrak](CONTRACT_GUIDE.md)
- [Struktur Folder](FOLDER_STRUCTURE.md)
- [ALOS–GENESIS internal route ownership](GENESIS_INTERNAL_ROUTE_OWNERSHIP.md)
- [Instalasi](INSTALLATION.md)
- [Action-scoped business approval contracts](material-business-approvals.md)
- [Runtime dan Tool Contracts](runtime-contracts.md)
- [Skill Contracts](skill-contracts.md)
- [Validasi](VALIDATION.md)
- [Versioning](VERSIONING.md)

## Arsitektur dan ADR

- [ADR-001: Topologi multi-repository](adr/ADR-001-multi-repo-topology.md)
- [ADR-002: Otoritas ALOS Backend](adr/ADR-002-backend-authority.md)
- [ADR-003: GENESIS sebagai AI Control Plane](adr/ADR-003-genesis-control-plane.md)
- [ADR-004: Desain capability-first](adr/ADR-004-capability-first.md)
- [ADR-005: Batas Backend ToolExecutor](adr/ADR-005-tool-executor-boundary.md)
- [ADR-006: Batas ModelGateway](adr/ADR-006-model-gateway-boundary.md)
- [ADR-007: Batas multi-tenant](adr/ADR-007-multi-tenant-boundary.md)
- [ADR-008: Silsilah evidence dan keputusan](adr/ADR-008-evidence-decision-lineage.md)
- [ADR-009: AI review dan keputusan manusia](adr/ADR-009-ai-review-human-decision.md)
- [Architecture Freeze v1 — ALOS](architecture/ARCHITECTURE_FREEZE_V1.md)
- [Model Otoritas](architecture/AUTHORITY_MODEL.md)
- [Aturan Dependency](architecture/DEPENDENCY_RULES.md)
- [Topologi Repository](architecture/REPOSITORY_TOPOLOGY.md)

## Kompatibilitas legacy yang masih diuji

- [Rekonsiliasi Contract MVP-1](MVP1_CONTRACT_MIGRATION.md)

## Artefak canonical

- [Shared Work boundary](../schemas/shared-work/README.md)
- [Identity boundary](../schemas/identity/README.md)
- [Generated Python](../generated/python/README.md)
- [Generated TypeScript](../generated/typescript/README.md)

## Pemeriksaan sebelum commit

Dari sibling checkout Infra, jalankan `python scripts/verify-documentation.py`.
Pemeriksaan memvalidasi link file kelima repository serta casing Linux tanpa jaringan.
