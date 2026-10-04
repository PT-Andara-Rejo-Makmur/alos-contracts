# Skill Contracts

Skill merupakan definition/prosedur berversi. Prerequisite bukan grant authority.

- `required_tool_ids` adalah prerequisite tool canonical. `tool_ids` lama hanya
  untuk compatibility payload; konsumen tidak menggunakannya untuk izin runtime.
- Permission, scope dan tool merupakan kebutuhan minimum; Backend tetap membatasi
  semuanya terhadap Principal, lifecycle dan release.
- Referensi Skill memakai pasangan immutable `skill_id` dan `skill_version`.
- `authorized_skill_refs` adalah snapshot opsional dari Backend. GENESIS dapat
  menyaring/menolaknya, tetapi tidak menambah referensi sendiri.
- Assignment menghasilkan versi AgentDefinition baru berstatus DRAFT; tidak
  mengubah versi ACTIVE atau menyetujui/mengaktifkan draft.
- `AgentDefinition.skill_refs` adalah source of truth assignment.

Schema, examples dan generated artifacts menentukan field terkini. Versi rilis
dibaca dari `VERSION`, bukan nomor milestone lama. UI projection, server assignment
dan runtime filtering perlu diuji pada consumer masing-masing.
