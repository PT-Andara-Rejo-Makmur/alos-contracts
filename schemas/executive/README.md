# Executive read contracts

ExecutiveOverviewProjection is a governed read projection of Strategy, Shared Work,
and business sources once those sources are canonical. It owns no operational
entity, database, KPI, or business mutation. GET /api/v1/executive/overview returns
this public projection with authoritative Strategy and Shared Work data. The optional
`shared_work_data` extension reuses canonical Shared Work entity projections. Counts
cover all matching entities; previews contain at most 50 records per collection.
Both sources remain authoritative regardless of retrieval success.

ExecutiveConnectionStatus distinguishes a connected source with data (CONNECTED),
a connected source with no matching data (CONNECTED_EMPTY), an unimplemented
projection capability (UNAVAILABLE), and a failed source read (ERROR).
Neither an empty collection nor an unknown source means zero business performance.

ExecutiveSourceStatus describes the source's authority, availability, and known
update time. ExecutiveDomainStatus groups actual source statuses. Timestamps are
nullable; producers must retain null when no authoritative time is known.
Verification is optional and nullable, and uses Strategy's existing verification
vocabulary only when the source actually supplies that state. Periods reuse
Strategy BusinessPeriod and may be omitted or null when unknown.

Generate Python and TypeScript with the repository generators. Web imports the
generated Executive types through its contract facade. No operational metrics are
declared until a canonical business source supports them.

The active principal needs EXECUTIVE, strategy.read and work.read. Company Strategy
visibility uses its existing authority. Shared Work retains tenant, organization and
active workspace link visibility, including company work explicitly shared there;
Executive never grants access to every company workspace. Documents retain their
existing workspace boundary. Partial retrieval failures carry null data for the failed
source; authentication, authorization and unavailable contracts fail closed.

Pending approvals count only PENDING, preserving APPROVED, RETURNED, REJECTED and
HELD separately. Active findings are OPEN, ASSIGNED, IN_PROGRESS or
PENDING_VERIFICATION; VERIFIED and CLOSED do not count as unresolved. Critical/high
counts intersect those states with canonical severity. Overdue tasks require due_at
and exclude COMPLETED/CANCELLED. Source timestamps come from entity updated_at,
or approval decided_at/requested_at. The overall timestamp is the latest known source
timestamp, and remains null if neither source provides one.
