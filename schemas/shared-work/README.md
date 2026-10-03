# Shared Work contract boundary

`shared-work.schema.json` defines six entity projections, creation inputs, status vocabulary, and distinct permission references. These definitions grant no permissions and publish no endpoint. The Backend must derive tenant, organization, workspace access, actors, lifecycle transitions, and audit data from authenticated authority. Creation inputs deliberately exclude these fields.

`WorkspaceMemberProjection.project_assignable` reports whether an active member of the authenticated workspace has `project.read` or `work.read` for Project owner replacement. The Backend always emits this boolean. It is optional in the schema to remain compatible with older projections; consumers must require `true` before offering a replacement. Task/finding flags and role names do not establish Project owner eligibility.

Project creation without an owner override assigns the authenticated creator. Existing Backend validation also accepts `project.create` or `work.write` for that creator alone; this does not make other members with those permissions eligible replacements. Clients displaying an explicit creator selection should send that canonical `owner_actor_id`. Unchanged owner assignments should be omitted from update requests, including legacy assignments.

| Entity | Canonical status | Permission actions |
| --- | --- | --- |
| Project | `PLANNED`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`, `ARCHIVED` | read, create, update, archive |
| Task | `OPEN`, `IN_PROGRESS`, `BLOCKED`, `UNDER_REVIEW`, `COMPLETED`, `CANCELLED` | read, create, update, assign, complete |
| Approval | `PENDING`, `APPROVED`, `RETURNED`, `REJECTED`, `HELD` | read, request, review, approve, return, reject, hold |
| Document | `DRAFT`, `IN_REVIEW`, `APPROVED`, `REJECTED`, `RETIRED` | read, create, version, review, approve, retire |
| Report | `DRAFT`, `IN_REVIEW`, `APPROVED`, `PUBLISHED`, `ARCHIVED` | read, create, review, publish, archive |
| Finding | `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `PENDING_VERIFICATION`, `VERIFIED`, `CLOSED` | read, create, update, assign, verify, close |

The initial status values follow database defaults and existing Web workflow requirements; they are a vocabulary, not implemented transition rules. Approval decisions are `APPROVED`, `RETURNED`, `REJECTED`, or `HOLD`. The Backend currently denies every generic Approval write, including creation and deletion, until a dedicated API can enforce the distinct permissions and record audit history.

The projections contain only columns in `core.projects`, `core.tasks`, `core.work_approvals`, `core.work_reports`, `core.work_findings`, `core.documents`, `core.document_versions`, and the workspace link tables. They do not promise progress, risk, dependency, comment, evidence, or relationship counts. A future dedicated API must implement and validate transitions before using lifecycle permissions. Existing generic `work.read` and `work.write` remain legacy runtime permissions; the new references are vocabulary only until Backend policy grants and enforces them.

`core.documents` and `core.document_versions` are the PostgreSQL authority for document metadata and immutable versions. Backend `DocumentRegistry` currently stores data in memory and must be replaced or adapted to these tables before a public Documents API is added. No duplicate document table is needed.

The Web Reports definitions view has no authoritative table. `ReportProjection` covers stored report results only. Definition persistence, periods, publication timestamps, and recipients require separate requirements and a dedicated API before they can become canonical.

The Finding UI contained two conflicting local status sets. The canonical sequence is `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `PENDING_VERIFICATION`, `VERIFIED`, `CLOSED`. Other presentation-only values are outside this contract; future persisted transitions must be implemented and guarded by the Backend before they are accepted. Generated TypeScript and Python types come from this schema.
