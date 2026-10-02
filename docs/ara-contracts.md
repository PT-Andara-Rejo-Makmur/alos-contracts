# Governed ARA boundary

Browser requests contain only a message, a thread title, and an optional explicit business reference.
Backend derives every identity, permission, scope, classification, tool and budget field from the authenticated Principal.
The `/api/v1/ara` OpenAPI surface defines authority, conversation history, messages, runs and cancellation.

The response distinguishes ANSWER, NEEDS_INFO, DENIED, NEEDS_REVIEW and FAILED. AraEvidenceProjection reuses
the canonical EvidenceRef. Sources contain actual ToolExecutor lineage; proposals always have executed=false.
ReviewPackage, FactoryAnalysisResult, ResearchResult and delegated AgentRunResult reuse existing contracts.
Factory proposals remain DRAFT and advisory; they grant no registration, release or activation rights.

Internal ExecutionContext additions preserve Backend data_scope, division and project boundaries through tool callbacks.
ContextBundle additions expose Backend permission, capability and classification bounds. ToolResult may carry canonical
source/evidence references. These additions are optional to preserve foundation payload compatibility.

Generated Python and TypeScript are emitted by the existing generators. Existing canonical schema URLs are unchanged.
