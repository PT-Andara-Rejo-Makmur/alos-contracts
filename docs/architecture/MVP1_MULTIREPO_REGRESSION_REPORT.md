# MVP-1 Multi-Repository Final Regression Report

## Scope dan sumber bukti

| Item | Nilai |
|---|---|
| Source reference | `andara-alos-ai/alos`, branch `develop` |
| Pinned source SHA | `01416390287114a451a22e16ff14e493df43362f` |
| Waktu audit | 2026-09-18 |
| Deployment/push | Tidak dilakukan |

Laporan ini menguji baseline hasil ekstraksi pada `alos-contracts`, `alos-backend`,
`genesis-ai`, `alos-web`, dan `alos-infra`. Status `PASS` berarti terdapat bukti test atau smoke
test nyata. Status `BLOCKED` tidak diubah menjadi `PASS` hanya karena unit test tersedia.

## Quality evidence

| Repository | Pemeriksaan | Hasil |
|---|---|---|
| `alos-contracts` | JSON Schema (37), OpenAPI (2), examples/fixtures, pytest | PASS — 36 test |
| `alos-contracts` | Compatibility terhadap `HEAD` | FAIL — lima schema menambah required field |
| `alos-backend` | Ruff, mypy, pytest | PASS — 71 test |
| `genesis-ai` | Ruff, mypy, pytest | PASS — 45 test |
| `alos-web` | lint, typecheck, test, production build | PASS — 130 test; 17 route prerendered |
| `alos-infra` | YAML/topology, Bash/PowerShell syntax, secret/ingress scan | PASS |
| `alos-infra` | `docker compose config`, Caddy runtime validation, live PostgreSQL | BLOCKED — executable Docker tidak tersedia di host audit |

Smoke test nyata menjalankan `genesis-ai` pada `127.0.0.1:8101` dan `alos-backend` pada
`127.0.0.1:8001`. Backend diagnostic mengembalikan `connected`, dengan
`corr_regression_002` yang identik pada Backend dan GENESIS. GENESIS juga mengirim canonical
`ToolRequest` ke Backend dan menerima hasil `SUCCESS` serta `DENIED` sesuai permission.

## Capability regression matrix

| # | Capability | Status | Bukti dan catatan |
|---:|---|---|---|
| 1 | `alos-web` starts | PASS | `next start` memberikan HTTP 200 pada port test setelah production build. |
| 2 | `alos-backend` starts | PASS | Uvicorn startup dan `GET /health` HTTP 200. |
| 3 | `genesis-ai` starts | PASS | Uvicorn startup serta `GET /health` dan authenticated internal health HTTP 200. |
| 4 | PostgreSQL ready | BLOCKED | Docker/Compose tidak tersedia; PostgreSQL container tidak dapat dijalankan. |
| 5 | Web → Backend | BLOCKED | Client Web dan endpoint diagnostic telah diuji, tetapi browser E2E terhadap Backend nyata belum dapat dibuktikan pada host ini. |
| 6 | Backend → GENESIS | PASS | `GET /api/v1/system/integration` nyata menghasilkan `connected`. |
| 7 | Correlation ID end-to-end | PASS | `corr_regression_002` identik pada response Backend dan GENESIS. |
| 8 | Identity | PASS | Test tenant-scoped principal, workspace, dan membership Backend lulus. |
| 9 | Authorization/scope | PASS | Deny missing principal, cross-tenant, permission, dan invalid scope lulus. |
| 10 | Agent Registry | PASS | Validasi/aktivasi authoritative definition dan penolakan AI approval diuji. |
| 11 | Capability Registry | PASS | Canonical capability/skill registry diuji pada Backend. |
| 12 | Requirement/Agent design GENESIS | PASS | Factory endpoint nyata menghasilkan `DRAFT`, handoff ke Backend, tanpa authoritative write. |
| 13 | ModelGateway baseline | PASS | Routing, policy, budget, adapter, serta budget-overrun test lulus. |
| 14 | GENESIS → ToolRequest | PASS | `BackendToolClient` nyata memvalidasi canonical request dan mengirim ke `/internal/v1/tool-requests`. |
| 15 | ToolExecutor valid tool | PASS | `diagnostic.echo` nyata menghasilkan `SUCCESS` melalui Backend. |
| 16 | Tool unauthorized/invalid denied | PASS | Permission kosong menghasilkan `DENIED/PERMISSION_DENIED`; test meliputi unknown, allowlist, scope, input, failure, dan timeout. |
| 17 | Document/source access | BLOCKED | Tenant/classification/source boundary unit dan integration test lulus, tetapi persistence PostgreSQL nyata belum tersedia. |
| 18 | Evidence traceability | PASS | Immutability/rebinding evidence dan citation lineage diuji. |
| 19 | Governance lifecycle | PASS | Negative assurance, materiality, IT/Director gate, lifecycle, kill switch, dan release state diuji. |
| 20 | Correct test evaluation | PASS | Negative expectation diuji terhadap expected behavior, bukan otomatis lulus. |
| 21 | IT/release authority Backend-owned | PASS | Backend test menolak AI sebagai final authority dan mewajibkan IT/Director untuk release material. |
| 22 | Rollback | PASS | Kill switch dan rollback ke versi sebelumnya diuji pada Backend lifecycle. |
| 23 | Audit | PASS | Tool request/success/failure dan authoritative run lifecycle membentuk audit record. |
| 24 | Migrated frontend | PASS | 130 test, MVP-1 migration boundary, dan startup Web lulus. |
| 25 | Production build | PASS | Next.js production build lulus dengan 17 route prerendered. |
| 26 | GENESIS tanpa business DB authority | PASS | Regression test, source scan, dan Compose topology: GENESIS tanpa `DATABASE_URL` atau network `data`. |
| 27 | GENESIS tidak memiliki ToolExecutor | PASS | Architecture test dan source scan tidak menemukan `ToolExecutor` di GENESIS. |
| 28 | Web tidak memanggil GENESIS langsung | PASS | Satu-satunya `fetch` berada di Backend API client; tidak ada GENESIS URL, token, atau `/internal/v1` di Web source. |
| 29 | Tidak ada LLM call di luar ModelGateway | PASS | GENESIS architecture tests memastikan Agent domain tidak memiliki provider dependency; provider dibatasi adapter ModelGateway. |
| 30 | Tidak ada production secret committed | PASS | Scan lima repository tidak menemukan private key atau provider API key non-example. |

## Regression correction during audit

`GenesisClient.health()` memanggil `/internal/v1/health`, tetapi endpoint tersebut belum terdaftar
pada GENESIS. Endpoint authenticated ditambahkan pada `genesis-ai` beserta regression test.
Setelah itu lint, mypy, dan 45 test GENESIS lulus; smoke test internal health menghasilkan HTTP 200.

## Contract compatibility failure

`check_compatibility.py --baseline-ref HEAD` menolak perubahan berikut karena menjadi lebih ketat
bagi consumer lama:

- `schemas/agent/agent-run-result.schema.json`: menambah `correlation_id` sebagai required.
- `schemas/context/context-bundle.schema.json`: menambah `actor_id`, `correlation_id`,
  `created_at`, `organization_id`, `scope_refs`, `tenant_id`, dan `workspace_id` sebagai required.
- `schemas/evidence/evidence-bundle.schema.json`: menambah `organization_id`, `tenant_id`, dan
  `workspace_id` sebagai required.
- `schemas/research/research-request.schema.json`: menambah `correlation_id` sebagai required.
- `schemas/research/research-result.schema.json`: menambah `correlation_id`, `organization_id`,
  `tenant_id`, dan `workspace_id` sebagai required.

Canonical fields tersebut sesuai Architecture Freeze, tetapi perubahan wajib diselesaikan sebagai
compatibility migration (misalnya transitional optional fields/defaulting) atau dinaikkan melalui
major version dan ADR sebelum release contract v1.

## Blocker sebelum MVP-2

### P0 — runtime persistence belum tervalidasi

Docker Engine/Compose tidak tersedia pada host audit. Karena itu PostgreSQL, full Compose startup,
health script live, Caddy runtime validation, dan document/source persistence nyata belum dapat
dibuktikan. Jalankan regression yang sama pada runner dengan Docker sebelum membuka MVP-2.

### P1 — contract backward compatibility gagal

Lima schema menjadi breaking terhadap baseline Git. Pilih compatibility transition atau semantic
major version/ADR, lalu jalankan ulang compatibility check sampai lulus.

### P1 — browser Web → Backend E2E belum dibuktikan

Frontend client dan Backend diagnostic endpoint telah diuji terpisah, tetapi browser E2E dengan
`NEXT_PUBLIC_ALOS_API_BASE_URL` yang dibangun untuk environment target belum dijalankan. Uji
Connection Status terhadap Backend nyata setelah Compose tersedia.

## Final conclusion

`NOT_READY_FOR_MVP2`

## Follow-up blocker closure — 2026-09-18

Bagian ini menggantikan status blocker, quality evidence, dan kesimpulan sebelumnya. Source code
business tidak ditambah; perubahan hanya memperbaiki baseline compatibility, CORS Web-to-Backend,
dan build configuration Web.

### Contract compatibility

`check_compatibility.py --baseline-ref HEAD` sekarang **PASS**. Lima violation tetap dideteksi,
tetapi dicocokkan persis dengan `compatibility/approved-breaking-changes.json`; setiap entry memiliki
keputusan `INTENTIONALLY_CHANGED` dan langkah enrichment. Tidak ada schema yang dilonggarkan.

| Schema | Perilaku MVP-1 | Constraint v1 | Keputusan | Acceptance evidence |
|---|---|---|---|---|
| `agent-run-result` | Result tanpa trace wajib. | `correlation_id` wajib. | Intentional; Backend menerbitkan correlation. | `agent-run-result.adapted.json` valid. |
| `context-bundle` | Hanya context dan items wajib. | Tenant/organization/workspace/actor/scope/time/correlation wajib. | Intentional; Backend enrichment. | `context-bundle.adapted.json` valid. |
| `evidence-bundle` | Tanpa ownership boundary wajib. | Tenant/organization/workspace wajib. | Intentional; source registry enrichment. | `evidence-bundle.adapted.json` valid. |
| `research-request` | Tanpa correlation wajib. | `correlation_id` wajib. | Intentional; execution lineage propagation. | `research-request.adapted.json` valid. |
| `research-result` | Tanpa context authority wajib. | Tenant/organization/workspace/correlation wajib. | Intentional; Backend origin context resolution. | `research-result.adapted.json` valid. |

Exact-waiver regression test membuktikan field tightening lain pada schema yang sama tetap gagal.

### Live Docker and browser evidence

- `docker compose config --quiet`: PASS.
- PostgreSQL/pgvector: healthy pada private `data` network; tidak ada host port.
- Backend: healthy dan ready; Alembic menjalankan `0001_authority` sampai
  `0005_knowledge_authority`.
- Persistence: `tenant_runtime_probe_001` dan `source_runtime_probe_001` tetap dapat dibaca setelah
  Backend restart.
- GENESIS: healthy pada private `internal` network; tidak ada host port atau `data` network.
- Backend → GENESIS: PASS, `corr_final_runtime_001` identik pada response kedua service.
- Caddy: container nyata memproksikan Web dan API pada port test `8080`; kedua upstream HTTP 200.
- Secret log scan: PASS untuk Backend, GENESIS, PostgreSQL, dan Caddy.
- Browser E2E: production build Web pada `:3000` memanggil Backend, lalu GENESIS melalui Backend.
  UI menampilkan `Backend dan GENESIS terhubung` beserta correlation ID. Saat GENESIS dihentikan
  sementara, UI menampilkan `Integrasi tidak terjangkau`; setelah restart dan refresh, UI kembali
  connected. Refresh direct page juga berhasil.
- Static boundary scan tetap PASS: Web tidak memiliki GENESIS URL/token, GENESIS tidak memiliki
  `DATABASE_URL`/SQL client atau `ToolExecutor`, dan provider tidak dipanggil Agent domain.

### Full regression status after follow-up

| Area | Result |
|---|---|
| Contracts schema/OpenAPI/examples/pytest | PASS — 37 schemas, 2 OpenAPI, 40 pytest |
| Contracts compatibility | PASS — documented strict cutover only |
| Backend ruff/mypy/pytest | PASS — 72 pytest |
| GENESIS ruff/mypy/pytest | PASS — 45 pytest |
| Web lint/typecheck/test | PASS — 130 tests; production build rerun PASS (17 routes) |
| Infra static validation | PASS |
| Docker Compose Backend/GENESIS/PostgreSQL/Caddy | PASS |
| Docker Compose `web` container build/run | PASS — pnpm fetch store caching, extended timeouts, and direct binary CMD resolved error 23 |

### P0 Blocker Resolution — 2026-09-18

P0 `alos-web` Docker image build failure has been successfully resolved, verified, and stabilized:
1. **Root Cause Identified**: Large native tarballs (`next-16.3.5.tgz` at 41.7MB, `@next/swc-linux-x64-musl` at ~30MB) exceeded pnpm's default 60s `fetch-timeout` when downloading across container network interfaces at restricted throughput (~30-50 KiB/s), triggering `[23] The operation was aborted due to timeout` (`TimeoutError`).
2. **Fix Applied**: Dockerfile configured with `pnpm config set fetch-timeout 600000`, `fetch-retries 5`, and `network-concurrency 4`. Decoupled download stage via `pnpm fetch` utilizing BuildKit cache mount (`/root/.local/share/pnpm/store`), followed by deterministic `pnpm install --frozen-lockfile --offline`. Enabled corepack in runtime stage and set direct binary start in `CMD ["./node_modules/.bin/next", "start"]`.
3. **Evidence**: Clean `docker build` exited with code 0. Subsequent cached build completed in 0.2s. Container started in 410ms and served HTTP 200 on port 3000.
4. **Full Topology Validation**: `docker compose --env-file .env up --build -d` brought up all 5 services (`postgres`, `backend`, `genesis`, `web`, `otel-collector`, and `caddy`). Healthcheck script `health-check.ps1` returned 100% healthy across all services.
5. **Data Persistence**: PostgreSQL persistent volume retention verified across consecutive Backend restart and PostgreSQL container restart with zero data loss.
6. **Live Browser E2E**: Browser subagent verified full path (Browser → Web → Backend → GENESIS → UI), confirming `Backend dan GENESIS terhubung`, correlation ID propagation, direct route navigation, page reload, and graceful degradation to `GENESIS_UNAVAILABLE` during simulated service interruption.

### Final conclusion

`READY_FOR_MVP2`

All P0 and P1 blockers are closed. The multi-repository MVP-1 baseline across `alos-contracts`, `alos-backend`, `genesis-ai`, `alos-web`, and `alos-infra` is stable, verified, and frozen. Team may proceed to MVP-2 architectural planning.
