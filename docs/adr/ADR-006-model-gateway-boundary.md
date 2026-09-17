# ADR-006: Batas ModelGateway

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

Akses model yang tidak terkendali memecah kebijakan, batas biaya, kontrol keamanan, dan audit trail.

## Keputusan

Semua pemanggilan model melewati ModelGateway sesuai model policy dan execution budget yang dideklarasikan.

## Konsekuensi

Agent dan skill tidak pernah menyimpan credential provider atau memanggil provider secara langsung.
