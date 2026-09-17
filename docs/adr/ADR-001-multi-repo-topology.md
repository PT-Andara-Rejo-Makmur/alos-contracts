# ADR-001: Topologi multi-repository

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

ALOS, GENESIS, frontend, dan infrastruktur memiliki boundary rilis dan otoritas yang berbeda.

## Keputusan

Pertahankan `alos-contracts`, `alos-backend`, `genesis-ai`, `alos-web`, dan `alos-infra` sebagai repository terpisah. Seluruh bentuk komunikasi berasal dari `alos-contracts`.

## Konsekuensi

Tim dapat merilis implementasi secara independen, tetapi rilis kontrak dan pemeriksaan kompatibilitas harus mendahului perubahan lintas boundary.
