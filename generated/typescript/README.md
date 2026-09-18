# Artefak TypeScript hasil generate

`factory.ts` adalah type dan client H1 untuk public Factory API. Source of truth tetap JSON Schema
dan `openapi/public/alos-public-api.yaml`; file TypeScript tidak boleh diedit manual.

Generate ulang:

```bash
python scripts/generate_typescript.py
```

Verifikasi tidak stale:

```bash
python scripts/generate_typescript.py --check
```

Frontend mengonsumsi hanya public client/type ini. Internal Factory request, authoritative
ExecutionContext, catalog snapshot, dan Registry handoff tidak diekspos sebagai client Web.
