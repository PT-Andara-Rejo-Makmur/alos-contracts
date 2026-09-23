# Canonical Identity Foundation Baseline

Audit date: 2026-09-23

This document records the verified cross-repository baseline for the identity, workspace,
access, and integration foundation. It is architecture evidence, not a claim that Contracts
owns credentials, sessions, or the business database.

## Repository baseline

| Repository | Development HEAD | Development vs main | Latest development CI |
| --- | --- | --- | --- |
| alos-contracts | `a7e7c75be06f1c56e4b2e395b245e84c642c824d` | 1 commit ahead | PASS |
| alos-backend | `bc4453d5d87ddc7712ba55f0620d4854ef233552` | 8 commits ahead | PASS |
| genesis-ai | `c740b2aaa63775555451482c8ef421edd4cb9a79` | 28 commits ahead | PASS |
| alos-web | `f1edf944f0d25130d61e1d5516bfe1e8db4754e9` | 2 commits ahead | PASS |
| alos-infra | `a3258a27c8137e7870a5fe81ae3901b651a3cd22` | 2 commits ahead | PASS |

The checked-out repositories matched `origin/development` when this audit started. The
Contracts release file was `1.6.0`; public OpenAPI still declared `1.5.0`, while internal
OpenAPI declared `1.6.0`. Backend migration head was `0007_runtime_research`.

## Findings

### P0

- Backend production authentication instantiated `AuthService()` backed by process memory,
  despite `core.auth_accounts` and `core.auth_sessions` already existing.
- Public self-registration accepted tenant, organization, workspace, role, permission, scope,
  and data-scope grants supplied by the caller.
- Session tokens were deterministic hashes of account data and were neither persisted nor
  revocable.

### P1

- `auth_accounts.workspace_id` made one workspace part of permanent account identity.
- Backend exposed no authoritative `GET /api/v1/workspaces` or active-workspace selection API.
- Backend `whoami` returned one workspace while Web maintained duplicate `workspace_ids` and
  `division_codes` identity shapes.
- Web fabricated a workspace from `whoami.workspace_id` after a workspace API failure.
- Web destination resolution gave global roles precedence over the selected workspace.
- Public OpenAPI used `/v1` for runtime paths, declared opaque bearer tokens as JWT, and omitted
  implemented auth routes.
- The integration Compose stack omitted Web, so its smoke did not prove the HttpOnly BFF path.

### P2

- Web readiness marked shared modules READY even where no matching Backend route exists.
- Web CI checked out Contracts `main`; Backend, GENESIS, and integration CI used `development`.
- Runtime role vocabulary still mixed organizational titles (`DIRECTOR`, `IT_LEAD`,
  `DIVISION_*`, `QA_SECURITY`) with authority archetypes.

### P3

- Historical milestone names remain in compatibility fixtures and historical evidence. They
  are not runtime imports and should not be blindly renamed.

## Stabilization direction

Contracts will own transport projections and stable authority vocabulary. Backend will own
persistent accounts, sessions, actors, memberships, workspace validation, provisioning, and
authorization. Web will consume Backend projections through its same-origin BFF and will not
manufacture authority state. GENESIS remains an internal intelligence plane and requires no
identity authority. Infra will prove the complete Web-to-Backend-to-GENESIS path and negative
workspace isolation.

