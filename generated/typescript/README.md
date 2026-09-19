# Artefak TypeScript hasil generate

`factory.ts` menyediakan type dan client untuk public Factory API.
`context-research.ts` menyediakan shared contract types untuk context, evidence, dan
research. Source of truth tetap JSON Schema dan OpenAPI; file TypeScript tidak boleh
diedit manual.

Generate ulang:

```bash
python scripts/generate_typescript.py
```

Verifikasi tidak stale:

```bash
python scripts/generate_typescript.py --check
```

Frontend hanya boleh mengonsumsi public projection yang diterbitkan Backend. Raw
`ExecutionContext`, internal Factory request, catalog snapshot, dan Registry handoff
tidak boleh dijadikan payload Web hanya karena type internal tersedia di package ini.
