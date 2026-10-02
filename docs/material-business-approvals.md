# Action-scoped business approval contracts

Shared Work remains the universal Approval authority. PROJECT/TASK payloads stay compatible. Implemented business subjects require `requested_action`; request input cannot set snapshot, reviewer, decision, consumption or scope.

Business projections add optional `material_actions` using the generated SharedWorkMaterialActionProjection. Each action provides subject/action/target, approval requirement and executor authority. It is separate from ordinary `allowed_transitions`. Transition request accepts `approval_id`; the owner rejects any material transition without a matching approved reference. The frontend consumes generated types and does not own a status graph.

Approval projections expose action, content snapshot, allowed human decisions and consumption metadata. `allowed_decisions` is an authority projection; status alone never grants a reviewer decision. Decision and business execution are distinct requests. A consumed approval cannot be replayed. Snapshot binds persisted record content and relevant pricing/budget children, so changing content invalidates the request.

Implemented actions: WIN_OPPORTUNITY, CONFIRM_BOOKING, COMPLETE_CLOSING, ACTIVATE_PRICING, RESERVE_UNIT, SELL_UNIT, APPROVE_CHANGE_ORDER, APPROVE_PAYMENT_CERTIFICATE, APPROVE_BUDGET, ACTIVATE_BUDGET, CLOSE_BUDGET. No financial threshold or production release authority is introduced. Existing Governance DecisionRef retains its separate IT/DIRECTOR release role.

HR/GA adds internal FacilityRequest, InventoryItem, AssetHandover, MaintenanceRecord and ServiceAssessment. Legal adds distinct LegalReview and immutable LegalContractRevision referencing an actual Shared Work document version. Additional overview counts are optional for compatibility with older providers. Recorded assessments do not imply external validity, signature, execution or inferred readiness.

Sources are JSON Schema, generated Python/TypeScript and public OpenAPI. Generation parity, schema/reference validation, example validation, backward compatibility and contract tests are mandatory. Backend and Web coverage evidence is maintained in their canonical-business-coverage documents.
