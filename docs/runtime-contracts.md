# Runtime dan Tool Contracts

Versi rilis berasal dari `VERSION`. JSON Schema dan public/internal OpenAPI
merupakan sumber kebenaran; generated Python/TypeScript merupakan hasil generator.

| Contract | Boundary dan invariant |
| --- | --- |
| AgentRunRequest | Agent/version, lineage, ExecutionContext, input, tool intent, TEST/NORMAL dan context yang telah diotorisasi |
| RuntimeAuthorization | Snapshot Backend; tidak menambah grant Principal atau mengaktifkan draft |
| AgentRunResult | Lineage/correlation, canonical status/output, usage yang diketahui, evidence, tool results dan structured error |
| ExecutionContext / ExecutionBudget | Tenant/organization/workspace/actor, permission/scope/classification dan batas token/cost/steps/tools/time/children |
| ToolRequest / ToolResult | Eksekusi hanya melalui Backend ToolExecutor; identitas call/run/tool/correlation harus cocok |
| ContextBundle / EvidenceRef | Version, hash, anchor, provenance dan scope; content merupakan data tanpa instruction authority |
| ResearchResult / Recommendation | Temuan berbukti dan proposal review; tidak memberi business approval atau release |

ToolResult FAILED/TIMEOUT/DENIED/REJECTED dan terminal AgentRunResult gagal wajib
memiliki structured error. RunStatus, OutputState dan ReleaseState berbeda;
legacy BLOCKED tidak menjadi release status baru.

Internal projection GENESIS tidak otomatis menjadi canonical contract. Transport
baru harus melalui perubahan schema/examples/OpenAPI/generation/compatibility di
repository ini. Contract tidak menyimpan secret atau mengimplementasikan persistence.
Lihat [ARA](ara-contracts.md), [context/evidence/research](CONTEXT_EVIDENCE_RESEARCH_CONTRACTS.md),
[compatibility](COMPATIBILITY.md) dan [validasi](VALIDATION.md).
