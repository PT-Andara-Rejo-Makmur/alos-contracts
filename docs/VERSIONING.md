# Versioning

Repository ini mengikuti Semantic Versioning: `MAJOR.MINOR.PATCH`.

- **MAJOR**: perubahan yang tidak kompatibel bagi konsumen, termasuk penghapusan schema/property/nilai enum, field wajib baru, perubahan makna, atau batasan validasi yang diperketat.
- **MINOR**: penambahan backward compatible seperti property opsional, schema baru, atau penambahan nilai enum apabila konsumen diwajibkan menerima nilai yang belum dikenalnya.
- **PATCH**: perbaikan dokumentasi, contoh, atau validasi yang tidak mengubah payload yang diterima.

Nilai `$id` schema mencantumkan lini kontrak mayor (`/v1/`). Lini baru yang tidak kompatibel menggunakan namespace URI baru seperti `/v2/`; lini lama yang masih didukung tetap tersedia selama migrasi. `VERSION`, `info.version` OpenAPI, tag rilis, dan `CHANGELOG.md` harus konsisten untuk setiap rilis yang dipublikasikan.

Jangan mengubah fungsi field yang sudah ada secara diam-diam. Tambahkan field baru atau publikasikan lini kontrak mayor baru beserta panduan migrasi.
