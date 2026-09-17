# ADR-005: Batas Backend ToolExecutor

- Status: Diterima
- Tanggal: 2026-09-16

## Konteks

Akses langsung agent ke sistem bisnis akan melewati kebijakan dan kontrol audit yang berlaku.

## Keputusan

Agent menghasilkan `ToolRequest`; ALOS Backend memvalidasi context, permission, scope, dan argument, kemudian ToolExecutor menjalankan atau menolak aksi tersebut dan mengembalikan `ToolResult`.

## Konsekuensi

Agent tidak menyimpan credential database bisnis. Setiap aksi memiliki correlation dan dapat diaudit.
