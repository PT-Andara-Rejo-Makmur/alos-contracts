# Skill Contract Freeze

The canonical skill boundary is additive as of contract version 1.5.0.

- `required_tool_ids` is the sole canonical tool prerequisite. The older `tool_ids` field remains accepted only for payload compatibility and consumers must ignore it.
- Permission, scope, and tool references declare minimum prerequisites; they never grant or expand Backend authority.
- A skill is addressed by the exact immutable pair `skill_id` and `skill_version`.
- `authorized_skill_refs` is an optional Backend-issued run snapshot. GENESIS may filter or reject it but cannot add references.
- Assignment creates a new immutable `AgentDefinition` in `DRAFT`; it never mutates an active version or approves/activates the draft.
- `AgentDefinition.skill_refs` is the only assignment source of truth.

Frontend projection remains a separate consumer handoff and is not part of this server-side freeze.
