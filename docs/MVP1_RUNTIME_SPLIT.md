# Contract Runtime MVP-1

Contract runtime direkonsiliasi dari pinned MVP-1 SHA
`01416390287114a451a22e16ff14e493df43362f`. Contract tetap memiliki data lintas repository;
business logic, persistence, reasoning, dan authority tidak dipindahkan ke repository ini.

## Contract canonical

- `AgentRunRequest`: identity/lineage run, Agent version, capability, ExecutionContext, input,
  requested tool intent, execution mode, dan optional ContextBundle.
- `AgentRunResult`: lineage, mandatory correlation ID, RunStatus, OutputState, output/structured
  error, usage, evidence, dan ToolResult yang diterima dari Backend.
- `ExecutionContext`: tenant, organization, workspace, actor, authority reference,
  permission/scope, classification, correlation, dan optional ExecutionBudget; tanpa secret.
- `ExecutionBudget`: token, cost, steps, tool calls, children/depth, timeout, dan concurrency.
- `RunStatus` dan `RunEvent`: lifecycle komunikasi lintas service, bukan release lifecycle.
- `ToolRequest` dan `ToolResult`: satu-satunya boundary execution tool authoritative.

`ToolResult` dengan status FAILED, TIMEOUT, DENIED, atau REJECTED wajib membawa structured
error. AgentRunResult terminal gagal juga wajib membawa structured error. OutputState tetap
berbeda dari ReleaseState.

Legacy `BLOCKED` dipetakan ke `status=FAILED` dan `output_state=BLOCKED`, sehingga transport
lifecycle tetap sederhana tanpa kehilangan alasan assurance/policy block.
