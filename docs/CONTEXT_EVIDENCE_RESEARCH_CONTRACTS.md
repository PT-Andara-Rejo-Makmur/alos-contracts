# Context, Evidence, and Research Contracts

Versi 1.3.0 menetapkan vocabulary data lintas boundary untuk context, evidence,
dan research. Kontrak membawa snapshot atau proposal; kontrak tidak memberikan
authority.

## Boundary canonical

- Backend menerbitkan `ExecutionContext`, termasuk tenant, organization, workspace,
  actor, authority context, scope, permission references, classification, correlation,
  execution budget, dan optional tool allowlist.
- GENESIS memvalidasi snapshot tersebut dan hanya boleh mempersempit scope, permission,
  tool, budget, serta classification.
- `ContextBundle` adalah proyeksi bounded yang dapat memuat goal, capability, memory,
  evidence, dan source semantics. Ranking score, trimming algorithm, planner state,
  prompt internal, dan reasoning trace bukan bagian contract canonical.
- `ResearchDecision` adalah hasil non-authoritative. Keputusan external hanya dapat
  mengusulkan tool melalui `BACKEND_TOOL_EXECUTOR`; Backend tetap melakukan policy,
  permission, scope, cost, egress, dan audit enforcement.
- Evidence `EXTERNAL` wajib `UNTRUSTED` dan `instruction_authority=false`.

## Proyeksi dan exposure

Schema Context, Evidence, dan Research Decision adalah shared/internal contract.
OpenAPI publik tidak mengekspos raw `ExecutionContext`, source locator, snapshot
authorization, maupun state internal GENESIS. Frontend hanya boleh menerima proyeksi
yang diterbitkan Backend melalui public API.

## Consumer mapping

- Backend harus mengisi `allowed_tool_ids` dari authority yang telah diverifikasi,
  bukan dari input Web atau proposal GENESIS.
- GENESIS harus memproyeksikan hasil decision internal ke `ResearchDecision`; full
  domain profile dan salinan authorization internal tidak dikirim lintas boundary.
- Correlation lineage dari `ExecutionContext` harus dipertahankan pada `ContextBundle`,
  `EvidenceRef`/`EvidenceBundle`, `ResearchDecision`, dan structured error.
