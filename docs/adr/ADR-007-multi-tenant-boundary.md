# ADR-007: Batas multi-tenant

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

Kebocoran lintas tenant merupakan risiko platform yang tidak dapat diterima.

## Keputusan

ExecutionContext membawa tenant, organization, workspace, actor, permission, scope, classification, dan correlation kanonis pada setiap boundary eksekusi.

## Konsekuensi

Context yang tidak lengkap dianggap tidak valid. Implementasi harus memverifikasi context dan tidak hanya mempercayai pernyataan caller.
