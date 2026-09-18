# Migrasi Knowledge dan Research MVP-1

Sumber audit dikunci pada `andara-alos-ai/alos` branch `develop`, commit
`01416390287114a451a22e16ff14e493df43362f`. Pada snapshot tersebut, implementasi nyata
berada pada `services/platform/src/alos/documents/` dan `sources/`; tidak ada modul mandiri
`memory/`, `research/`, atau `evidence/`.

Kontrak lintas repository tetap dimiliki `alos-contracts`:

- `ContextBundle` membawa tenant, organisasi, workspace, actor, scope, klasifikasi, versi
  sumber, content hash, anchor, dan `evidence_id`.
- `EvidenceRef` dan `EvidenceBundle` mempertahankan lineage tenant/workspace serta korelasi.
- `ResearchRequest` membawa `correlation_id` dan dapat menerima `ContextBundle` yang sudah
  diotorisasi Backend.
- `ResearchResult`, `ResearchFinding`, dan `Recommendation` membedakan temuan berbukti dari
  rekomendasi non-authoritative.

Payload legacy yang hanya memakai `workspace_id`, path file lokal, atau hasil analisis tanpa
evidence lineage harus diadaptasi. Penambahan field wajib provenance merupakan breaking change
terhadap payload legacy tersebut, tetapi menjadi baseline wajib contract v1 sebelum dipakai
lintas repository.

Tidak ada logika penyimpanan, retrieval, ranking, atau reasoning di repository ini.
