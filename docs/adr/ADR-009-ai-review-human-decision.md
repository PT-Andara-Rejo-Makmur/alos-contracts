# ADR-009: AI review dan keputusan manusia

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

AI dapat mempercepat assurance, tetapi tidak dapat mengambil alih akuntabilitas organisasi.

## Keputusan

AI review dan recommendation bersifat rekomendasi. Keputusan IT dan Director disimpan sebagai record `DecisionRef` authoritative yang terpisah.

## Konsekuensi

ReviewPackage mempertahankan kedua lapisan secara eksplisit. AI recommendation tidak dapat memajukan approval authoritative dengan sendirinya.
