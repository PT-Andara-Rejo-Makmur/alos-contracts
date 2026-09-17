# ADR-008: Silsilah evidence dan keputusan

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

Assurance dan decision harus reproducible serta dapat diaudit.

## Keputusan

Evidence memiliki source, waktu pengambilan, URI, dan content hash kanonis. Decision memiliki identity, jenis otoritas, actor, outcome, dan timestamp kanonis. Correlation identifier menghubungkan seluruh rangkaian.

## Konsekuensi

Klaim yang tidak traceable tidak dapat memenuhi evidence review; decision tidak boleh disimpulkan dari output state.
