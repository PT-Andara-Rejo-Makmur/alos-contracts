# Panduan Kontribusi

Perubahan kontrak memengaruhi beberapa repository dan memerlukan peninjauan yang terencana.

1. Baca Architecture Freeze dan tentukan schema yang menjadi pemilik kanonis definisi tersebut.
2. Jangan menduplikasi identifier, enum, atau object yang sudah tersedia melalui `$ref`.
3. Tambahkan atau perbarui contoh positif dan pengujian negatif untuk batasan yang berubah.
4. Jalankan semua perintah di `docs/VALIDATION.md`.
5. Jelaskan dampak kompatibilitas dan langkah migrasi di dalam pull request.
6. Perbarui `CHANGELOG.md` dan `VERSION` ketika menyiapkan rilis.

Perubahan breaking memerlukan versi mayor dan migrasi terkoordinasi pada seluruh konsumen. Jangan pernah menyertakan credential, data produksi, atau secret dalam schema, contoh, pengujian, maupun dokumentasi.
