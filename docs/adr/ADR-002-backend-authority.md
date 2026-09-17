# ADR-002: Otoritas ALOS Backend

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

Kebijakan bisnis, data, dan approval membutuhkan satu boundary enforcement.

## Keputusan

ALOS Backend bersifat authoritative untuk business state, access policy, eksekusi tool, dan pencatatan keputusan manusia. Frontend hanya memanggil API publiknya.

## Konsekuensi

Backend memvalidasi ulang setiap request; output AI tidak pernah melewati business authorization.
