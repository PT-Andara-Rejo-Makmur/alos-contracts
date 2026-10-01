# Executive read contracts

ExecutiveOverviewProjection is a governed read projection of Strategy, Shared Work,
and business sources once those sources are canonical. It owns no operational
entity, database, KPI, or business mutation. GET /api/v1/executive/overview returns
this public projection with authoritative Strategy data. Shared Work remains an
authoritative ALOS source with UNAVAILABLE status until its aggregation is implemented.

ExecutiveConnectionStatus distinguishes a connected source with data (CONNECTED),
a connected source with no matching data (CONNECTED_EMPTY), an inaccessible or
unconnected source (UNAVAILABLE), and a failed source read (ERROR).
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
