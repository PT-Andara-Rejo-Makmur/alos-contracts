# Panduan Kontrak

## Aturan umum

Gunakan URI `$id` kanonis dan `$ref` ke definisi bersama, bukan menyalinnya. Payload transport harus tervalidasi sebelum melewati batas repository. Model internal yang disimpan boleh berbeda, tetapi adapter harus mempertahankan semantik kontrak. Setiap request harus sadar tenant, workspace, scope, dan correlation.

## ALOS Backend

Backend mengimplementasikan `openapi/public/alos-public-api.yaml`, memiliki otoritas bisnis dan data, memvalidasi request publik yang masuk, serta memetakan run request yang valid ke API internal ALOS–GENESIS. Backend mengimplementasikan ToolExecutor dan memvalidasi ulang setiap ToolRequest terhadap permission serta scope terbaru. Backend juga mencatat keputusan IT dan Director yang authoritative.

Untuk runtime, Backend membuat authoritative run record sebelum GENESIS bekerja, lalu
memvalidasi AgentRunResult sebelum melakukan terminal transition. ToolResult yang muncul pada
AgentRunResult harus berasal dari Backend ToolExecutor.

Untuk tool execution, GENESIS mengirim `ToolRequest` ke internal Backend ToolExecutor. Backend
mengembalikan `ToolResult` dengan `correlation_id` yang sama dan status `SUCCESS`, `DENIED`,
`REJECTED`, `FAILED`, atau `TIMEOUT`. Status `COMPLETED` dipertahankan untuk kompatibilitas consumer
lama; implementasi baseline baru menggunakan `SUCCESS`.

## GENESIS dan kapabilitas AI

GENESIS menggunakan API internal serta schema agent, skill, runtime, delegation, context, tool, evidence, research, dan review. Semua akses model dikirim melalui ModelGateway. Agent tidak pernah menggunakan credential database bisnis dan hanya dapat meminta aksi bisnis dengan menghasilkan ToolRequest. Turunan agent mempertahankan `root_run_id` dan `parent_run_id`.

AgentRuntimeEngine mengonsumsi AgentRunRequest, ExecutionContext, dan ExecutionBudget,
mengirim ToolRequest melalui internal HTTP boundary, lalu menghasilkan AgentRunResult.
GENESIS tidak menyimpan lifecycle authority atau menjalankan adapter business tool.

`CapabilityDraft` adalah usulan yang belum aktif, sedangkan `CapabilityDefinition` adalah definisi berversi yang telah masuk registry dan lifecycle governance. Produsen baru wajib menggunakan `capability_type` sesuai taxonomy capability-first. Field `delivery_mode` tetap diterima pada lini v1 hanya untuk backward compatibility dan akan memerlukan perubahan mayor bila dihapus.

### Factory MVP2 H1

Factory memiliki dua boundary yang berbeda:

1. Web mengirim `FactoryAnalyzeRequest` ke public ALOS Backend tanpa tenant, scope, permission,
   catalog, atau authority buatan client.
2. Backend membentuk canonical `ExecutionContext`, mengambil authoritative capability catalog,
   lalu mengirim `FactoryAnalysisRequest` ke internal GENESIS.

`FactoryAnalysisResult` dari GENESIS selalu non-authoritative. REUSE wajib membawa existing
capability reference dan tidak boleh membawa draft atau registry-create handoff. CREATE wajib
membawa canonical `CapabilityDraft`, optional `AgentDraft` bila capability-first memang
memerlukan Agent, dan handoff yang menyatakan `authoritative_state_changed: false`.

Backend memvalidasi proposal, lalu untuk CREATE mendaftarkan version ke authoritative Registry
sebagai `DRAFT`. Hanya setelah itu Backend mengembalikan public `FactoryAnalyzeResponse` dengan
`registry_result.state: DRAFT`. Contract ini tidak menyediakan operasi self-approve,
self-activate, atau release.

Permission actor pada `ExecutionContext.permission_refs` adalah konteks otorisasi, bukan
permission yang otomatis dibutuhkan capability. `required_permission_refs` dan draft
`permission_refs` hanya berisi least-privilege permission yang berasal dari capability/tool.

Artifact baru sebaiknya selalu membawa field tenant/workspace dan correlation yang tersedia pada schema, walaupun beberapa field tambahan tetap optional pada lini v1 untuk menjaga backward compatibility. Backend tetap wajib menegakkan tenant, scope, permission, dan authority dari `ExecutionContext`.

Field AI review merupakan rekomendasi dan sinyal assurance. Field tersebut tidak boleh mengisi atau menyamar sebagai `it_decision` maupun `director_decision`.

### Factory MVP2 stage contract (M2-H01-BE-02)

Alur requirement-to-capability dibekukan menjadi lima stage contract:

| Stage | Canonical schema | Produsen | Otoritas |
|---|---|---|---|
| Requirement | `factory/requirement.schema.json` | Backend (dari input client + authority context) | Backend |
| RequirementUnderstanding | `factory/requirement-understanding.schema.json` | GENESIS (proposal) | Backend |
| CapabilityDecision | `factory/capability-decision.schema.json` (alias v1: `factory-resolution`) | GENESIS (proposal) | Backend |
| CapabilityDraft | `capability/capability-draft.schema.json` | GENESIS (proposal), didaftarkan Backend | Backend registry (`DRAFT`) |
| CapabilityDetail | `capability/capability-detail.schema.json` | Backend (proyeksi authoritative) | Backend |

Aturan stage:

- `requirement_id` diturunkan Backend (`req_<correlation_id>`), di-echo GENESIS pada
  `RequirementUnderstanding`, dan diverifikasi Backend. GENESIS tidak boleh mengarang identitas.
- `ambiguity: NEEDS_CLARIFICATION` membuat Backend fail-closed dengan error
  `REQUIREMENT_AMBIGUOUS` (422): tidak ada draft, tidak ada registry state, tidak ada authority.
- `human_gate_required` pada proposal adalah sinyal AI. Backend governance mewajibkan human
  gate; proposal `false` ditolak `GENESIS_HUMAN_GATE_REQUIRED` (502) dan metadata definisi
  selalu dicatat `true` oleh Backend.
- `implementation_type` dipetakan dari `understanding.recommended_type`, `rationale` dari
  `reason`, `risk` dari `understanding.risk_level`, `tool_requirements` dari
  `required_tool_ids`, `permission_requirements` dari `required_permission_refs`, dan
  status proposal dari `activation_readiness`. Tidak ada field duplikat.
- `DRAFT != APPROVE != RELEASE != ACTIVE`: hanya Backend yang melakukan transisi registry.
  Konsumen tidak dapat mengubah lifecycle lewat payload apa pun.

### Error contract terfrozen (Factory & capability)

Semua error memakai `common/error.schema.json` (ProblemDetail: `code`, `message`,
`correlation_id`, `retryable`, `details`). Code untuk boundary ini:

| Code | HTTP | Arti |
|---|---|---|
| `REQUEST_VALIDATION_FAILED` | 422 | Body tidak memenuhi API input contract |
| `FACTORY_REQUEST_INVALID` | 422 | Requirement tidak lengkap/invalid (termasuk requirement kosong, tipe capability tidak valid, context injection) |
| `REQUIREMENT_AMBIGUOUS` | 422 | AI menandai `NEEDS_CLARIFICATION`; needs-info, tidak ada state dibuat |
| `MISSING_TOKEN` | 401 | Unauthorized |
| `INACTIVE_PRINCIPAL` | 403 | Principal tidak aktif |
| `FACTORY_SCOPE_REQUIRED` | 403 | Invalid/missing scope |
| `FACTORY_PROPOSAL_NOT_AUTHORIZED` | 403 | Proposal menuntut permission/scope di luar otoritas actor |
| `FACTORY_REGISTRY_CONFLICT` | 409 | Versi registry immutable bentrok / transisi lifecycle tidak valid |
| `CAPABILITY_NOT_FOUND` | 404 | Detail tidak tersedia bagi peminta (termasuk state tersembunyi fail-closed) |
| `CAPABILITY_NOT_AUTHORIZED` | 403 | Principal tidak memenuhi otoritas registry |
| `GENESIS_FACTORY_RESPONSE_INVALID` | 502 | Proposal GENESIS tidak valid (termasuk lifecycle dibuat palsu) |
| `GENESIS_CORRELATION_MISMATCH` | 502 | Correlation_id Backend tidak dipertahankan |
| `GENESIS_AUTHORITY_CONTEXT_MISMATCH` | 502 | GENESIS mengubah authority context Backend |
| `GENESIS_OWNER_MISMATCH` | 502 | GENESIS menetapkan owner di luar otoritas Backend |
| `GENESIS_HUMAN_GATE_REQUIRED` | 502 | Proposal mencoba menghapus human gate |
| `GENESIS_UNAVAILABLE` / `GENESIS_TIMEOUT` | 503 | Dependency AI tidak tersedia |
| `GENESIS_INVALID_RESPONSE` | 502 | Respons GENESIS melanggar contract |
| `INTERNAL_PROCESSING_FAILURE` | 500 | Kegagalan internal; tanpa SQL, stack trace, schema, credential, atau secret |

Error tidak pernah membocorkan SQL, stack trace internal, database schema, credential, atau
secret. Detail bersifat minimal dan typed.

## Frontend, ARA, dan GIIVEPRO

Client frontend menghasilkan atau menulis client hanya dari OpenAPI publik. Client tidak pernah memanggil GENESIS atau endpoint internal. ARA merupakan workspace manusia, sedangkan GIIVEPRO merupakan lapisan bisnis/produk di atas ALOS. Keduanya tidak menjadi otoritas terpisah.

## Menambahkan kontrak

Pilih domain pemilik yang paling sempit, gunakan kembali identifier kanonis, tetapkan `$id` unik pada `/v1/`, tolak field yang tidak dikenal kecuali extensibility memang disengaja, tambahkan contoh valid dan pengujian negatif, serta perbarui kontrak OpenAPI atau event ketika schema melintasi boundary tersebut.
