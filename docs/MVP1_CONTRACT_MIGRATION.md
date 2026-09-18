# Rekonsiliasi Contract MVP-1

Dokumen ini mencatat hasil Migration Batch 1 terhadap source `andara-alos-ai/alos` branch `develop` pada pinned SHA `01416390287114a451a22e16ff14e493df43362f`. Source hanya dibaca dan tidak diubah.

## Sumber yang diaudit

- `definitions/contracts/agent-contract.schema.json` adalah satu-satunya JSON Schema pada `definitions/`.
- `definitions/schemas/` tidak ada pada pinned snapshot.
- Pydantic lintas service diaudit dari agent registry, capability registry, runtime, security actor context, ToolExecutor, source/evidence registry, GENESIS research/document analysis, audit, serta release governance.
- Model yang hanya merupakan database record, request UI lokal, bootstrap, repository, atau business operation tidak dipindahkan ke contract bersama.

## Hasil mapping

| Contract v1 | Sumber MVP-1 | Keputusan | Catatan adaptasi |
|---|---|---|---|
| `ExecutionContext` | `ActorContext`, `LocalTokenRequest` | ADAPT | `user_id` menjadi `actor_id`; role, permission, division/workspace scope dinormalisasi; Backend wajib menambahkan `tenant_id`, workspace aktif, classification, dan `correlation_id`. Claim token tidak disalin. |
| `ExecutionBudget` | `WorkspaceBudgetRequest`, `WorkspaceBudget`, `UsageBudget`, timeout agent | ADAPT | Batas per-run dinormalisasi. Daily workspace policy tetap milik Backend dan bukan payload execution budget. |
| `ContextBundle` | Genesis conversation context dan source attachment | ADAPT | Context menjadi item tenant-bound dengan optional evidence lineage; conversation persistence bukan memory contract. |
| `CapabilityDraft` | Proposed capability/agent design | ADAPT | Gunakan `capability_id` dan `capability_type`. `delivery_mode` dipertahankan sementara sebagai compatibility field deprecated. |
| `CapabilityDefinition` | `CapabilityRecord` | ADAPT | `capability_key` menjadi `capability_id`; version integer legacy menjadi semantic version; scope, classification, risk, access, availability, configuration, tool binding, dan metadata dipertahankan sebagai contract data. |
| `AgentDefinition` | JSON Schema `ALOS Agent Contract`, `AgentContract`, `ProposedAgentDesign` | ADAPT | `agent_key` menjadi `agent_id`; `semantic_version` menjadi `agent_version`; field tool/permission/evidence/restriction/budget dipertahankan. Registry record dan persistence tidak ikut. |
| `AgentRunRequest` | `AgentRunRequest` legacy | ADAPT | Backend/GENESIS menambahkan `run_id`, `root_run_id`, `agent_id`, version, capability, serta `ExecutionContext`; `requested_tool_keys` menjadi `requested_tool_ids`. Embedded `tool_calls` tidak memberi authority. |
| `AgentRunResult` | `AgentRunResult`, `AgentRunSummary` | ADAPT | `agent_run_id` menjadi `run_id`; provider usage dikelompokkan pada `usage`; evidence dan structured error menggunakan contract terpisah. |
| `SkillDefinition` | Tidak ada modul skill mandiri | Contract baru | Tidak ada legacy implementation untuk di-copy. Field procedural ditetapkan sebagai data, bukan unrestricted executable code. |
| `SkillExecutionRequest`, `SkillExecutionResult` | Tidak ada contract mandiri | Contract baru | Menggunakan lineage run, context, output state, evidence, dan structured error. |
| `DelegationRequest`, `DelegationResult` | Parent agent key dan runtime lineage parsial | ADAPT | Lineage menggunakan `root_run_id`, `parent_run_id`, depth, inherited scope/permission/tool limits, dan budget. Child tidak memperoleh authority tambahan. |
| `ToolRequest` | `StructuredToolCall`, `TypedToolRecord` | ADAPT | `tool_key` menjadi `tool_id`; `idempotency_key` dipertahankan. Permission, scope, allowlist, schema validation, execution, dan audit tetap milik Backend ToolExecutor. |
| `ToolResult` | `ToolExecutionResult`, runtime `ToolDecision` | ADAPT | Hasil diberi `tool_call_id`, `run_id`, `correlation_id`, status canonical, output atau structured error. |
| `EvidenceRef` | `EvidenceCitation`, `EvidenceRecord`, source version | ADAPT | Adapter harus menghasilkan canonical IDs, URI, timestamp, dan SHA-256. Locator/anchor, excerpt, classification, serta validation status dipertahankan. |
| `EvidenceBundle` | Kelompok citation/evidence runtime | ADAPT | Bundle menambahkan tenant/workspace/run/correlation lineage tanpa memindahkan content storage. |
| `ResearchRequest`, `ResearchResult` | Genesis external research service dan document research workflow | ADAPT | Search/provider detail tidak menjadi authority. Domain, finding, recommendation, limitation, dan evidence dinormalisasi. |
| `ResearchFinding` | External research item dan operational finding | ADAPT | `finding_type` membedakan research dan operational. Source/citation menjadi `EvidenceRef`. |
| `Recommendation` | Genesis recommendations dan operational recommendation text | ADAPT | Selalu non-authoritative; `backlog_candidate` bukan izin eksekusi. |
| `AIReviewResult` | Automated validation/test evidence | ADAPT | Mendukung READY, revision, evidence block, dan risk signals. Human review decision legacy tidak dipetakan menjadi AI approval. |
| `ReviewPackage` | Test evidence, validation matrix, review records, release detail | ADAPT | Menggabungkan assurance dan evidence; IT/Director tetap berupa `DecisionRef` terpisah. Materiality menentukan kebutuhan Director sesuai policy Backend. |
| `DecisionRef` | `ReviewRecord`, `ApprovalRecord`, readiness decision | ADAPT | Hanya human/platform authority yang dapat menghasilkan decision. `review_id`, `release_id`, subject, tenant, workspace, dan correlation menjaga lineage. |
| `ReleaseState` | `ReleaseState` legacy | ADAPT | State yang sama dipakai ulang. `TESTED`, `IN_REVIEW`, dan generic `APPROVED` tidak dibawa karena ambigu; lihat breaking changes. |
| `RunStatus` | `RunStatus` legacy | ADAPT | `SUCCEEDED` menjadi `COMPLETED`; legacy `BLOCKED` menjadi run `FAILED` dengan `output_state=BLOCKED`. |
| `RunEvent` | `AuditEvent`, `LifecycleEventRecord`, runtime run metadata | ADAPT | Event mendapat canonical event/run IDs, tenant/workspace context, payload version, correlation, dan entity reference. Audit persistence tetap Backend. |

## Reuse dan deprecation

Konsep yang direuse tanpa perubahan arti adalah risk levels, data classification, semantic version, tool idempotency, test taxonomy, source hash, correlation, serta state release yang namanya sudah canonical. Bentuk wire tetap disesuaikan ke canonical IDs.

Field berikut deprecated dan hanya dipertahankan selama lini v1:

- `CapabilityDraft.delivery_mode`; producer baru menggunakan `capability_type`.
- `ToolResult.status=COMPLETED`; producer baru menggunakan `SUCCESS` untuk tool yang berhasil.
- Bentuk `definitions/contracts/agent-contract.schema.json` sebagai wire contract; seluruh producer baru menggunakan `AgentDefinition` canonical. Schema legacy tetap menjadi evidence migrasi pada pinned source, bukan schema kedua di target.

Nama legacy berikut tidak menjadi alias schema: `agent_key`, `capability_key`, `tool_key`, `agent_run_id`, `owner_user_id`, dan `user_id`. Adapter migrasi harus mengubahnya ke nama canonical. Menambahkan kedua nama ke contract akan menciptakan dua bahasa komunikasi dan dilarang.

## Breaking changes terhadap payload MVP-1 mentah

1. `ExecutionContext` mewajibkan `tenant_id`, `organization_id`, workspace aktif, actor, authority, scope, classification, dan correlation. Actor token legacy saja tidak cukup.
2. Agent run memerlukan canonical run lineage serta agent/capability identity; Backend atau migration adapter harus membuat nilai tersebut.
3. `SUCCEEDED` dinormalisasi menjadi `COMPLETED`. `BLOCKED` menjadi `status=FAILED` dan `output_state=BLOCKED`.
4. Release `TESTED` menjadi `AUTOMATED_ASSURANCE`; `IN_REVIEW` harus dipetakan ke gate aktual; generic `APPROVED` harus dipetakan ke `IT_APPROVED` atau `DIRECTOR_APPROVED` berdasarkan authoritative decision. Mapping tiga state ini tidak boleh ditebak otomatis.
5. Evidence citation tanpa canonical IDs, capture time, URI, dan content hash harus diperkaya sebelum valid.
6. Human `ReviewRecord.decision` atau operational approval menjadi `DecisionRef`, bukan `AIReviewResult`.
7. Version integer capability dan UUID version record internal tidak menggantikan semantic version contract.

## Cutover compatibility review

Lima perubahan berikut terdeteksi oleh checker terhadap baseline MVP-1. Semuanya sengaja dipertahankan: payload lama tidak cukup untuk memenuhi batas tenant, scope, dan traceability Architecture Freeze v1. Mereka adalah cutover Bootstrap v1 sebelum consumer eksternal dirilis, bukan perubahan yang diam-diam dianggap kompatibel. Perubahan berikut setelah rilis v1 harus mengikuti semantic versioning dan migration ADR yang sesuai.

| Schema | Perilaku MVP-1 | Perilaku v1 | Perbedaan breaking | Keputusan dan perbaikan | Regression test | Hasil |
|---|---|---|---|---|---|---|
| `AgentRunResult` | Result dapat diterbitkan tanpa correlation reference. | `correlation_id` wajib. | Required field bertambah. | INTENTIONALLY_CHANGED. Backend/migration adapter menerbitkan correlation yang sama dengan request. | Fixture `agent-run-result.adapted.json`; exact-waiver checker test. | Compatible setelah adaptasi. |
| `ContextBundle` | Hanya `context_id` dan `items` wajib. | Tenant, organization, workspace, actor, correlation, scope, waktu pembuatan, dan metadata evidence item wajib. | Context legacy tidak cukup untuk otorisasi atau evidence lineage. | INTENTIONALLY_CHANGED. Backend memperkaya context dari identity/scope authoritative dan source registry; GENESIS hanya mengonsumsi context tersebut. | Fixture `context-bundle.adapted.json`; schema validation. | Compatible setelah adaptasi. |
| `EvidenceBundle` | Bundle dapat tanpa tenant/organization/workspace. | Ketiga ownership boundary wajib. | Bukti berpotensi tidak terikat tenant/workspace. | INTENTIONALLY_CHANGED. Source registry Backend menyelesaikan ownership sebelum bundle dibentuk. | Fixture `evidence-bundle.adapted.json`; schema validation. | Compatible setelah adaptasi. |
| `ResearchRequest` | Request dapat tanpa correlation reference. | `correlation_id` wajib. | Trace antar Web, Backend, dan GENESIS hilang. | INTENTIONALLY_CHANGED. Adapter meneruskan correlation dari execution context. | Fixture `research-request.adapted.json`; schema validation. | Compatible setelah adaptasi. |
| `ResearchResult` | Result dapat tanpa tenant/workspace/correlation. | Tenant, organization, workspace, dan correlation wajib. | Result tidak memiliki authority dan lineage yang cukup. | INTENTIONALLY_CHANGED. Backend resolves originating execution context sebelum canonical record/reference diterbitkan. | Fixture `research-result.adapted.json`; schema validation. | Compatible setelah adaptasi. |

`compatibility/approved-breaking-changes.json` mencatat hanya lima pelanggaran lengkap di atas. Checker tetap mendeteksi seluruh perubahan; ia hanya mengembalikan sukses ketika pelanggaran cocok persis dengan keputusan cutover terdokumentasi. Perubahan baru, atau variasi constraint pada schema yang sama, tetap gagal CI.

## Compatibility fixtures

Fixture pada `compatibility/fixtures/mvp1/` adalah payload canonical hasil adaptasi nilai dan behavior MVP-1. Fixture tersebut sengaja bukan salinan payload mentah; semuanya divalidasi dengan schema v1 pada CI. Field yang membutuhkan authority atau enrichment diberi nilai eksplisit agar adapter yang kelak dibuat memiliki acceptance target deterministik.

Business logic, SQL/repository record, token claims, provider credentials, prompt orchestration, dan database model tidak dimigrasikan ke repository ini.
