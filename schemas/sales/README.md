# Sales canonical records

Persistence from existing migrations; mutation authority is Backend-derived.
Amounts use exact decimal strings. Public create/update/transition schemas forbid
unknown and authority fields. Legacy stored statuses are retained in read projections;
unknown lifecycle states fail closed for mutations. Material outcomes without a
canonical authority remain read-only.
