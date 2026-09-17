# ADR-003: GENESIS sebagai AI Control Plane

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

AI orchestration membutuhkan otonomi runtime tanpa mengambil alih otoritas bisnis.

## Keputusan

GENESIS memiliki AI planning, orchestration, delegation, dan eksekusi assurance. GENESIS tidak memiliki data bisnis atau keputusan authoritative.

## Konsekuensi

GENESIS berkomunikasi melalui kontrak internal, ModelGateway, dan Backend ToolExecutor.
