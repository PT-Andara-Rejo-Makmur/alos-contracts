# Architecture Freeze v1

Status: **Diterima dan dibekukan**

Mulai berlaku: 2026-09-16

1. Frontend hanya berkomunikasi dengan ALOS Backend dan tidak pernah berkomunikasi langsung dengan GENESIS.
2. ALOS Backend adalah platform authoritative.
3. GENESIS adalah AI Control Plane, bukan otoritas bisnis.
4. Agent tidak pernah mengakses database bisnis secara langsung.
5. Setiap aksi agent melewati `ToolRequest -> Backend ToolExecutor`.
6. Setiap pemanggilan model melewati ModelGateway.
7. GIIVEPRO berjalan di atas ALOS dan bukan otoritas platform terpisah.
8. Setiap proses harus sadar tenant dan scope.
9. Evidence dan decision harus traceable.
10. Agent, sub-agent, dan turunannya mempertahankan lineage run.
11. AI Review merupakan rekomendasi dan assurance, bukan approval authoritative.
12. IT dan Director memegang keputusan authoritative.
13. Output state dan release lifecycle merupakan kontrak yang berbeda.
14. CI mendeteksi perubahan kontrak yang breaking.
15. Schema bersifat kanonis di repository ini dan tidak diduplikasi di repository lain.
16. Desain bersifat capability-first; suatu kebutuhan tidak otomatis memerlukan agent.

Perubahan terhadap aturan ini memerlukan ADR pengganti, approval otoritas yang eksplisit, peninjauan kontrak mayor, dan pembaruan terkoordinasi pada seluruh repository konsumen.
