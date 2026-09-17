# Panduan Kontrak

## Aturan umum

Gunakan URI `$id` kanonis dan `$ref` ke definisi bersama, bukan menyalinnya. Payload transport harus tervalidasi sebelum melewati batas repository. Model internal yang disimpan boleh berbeda, tetapi adapter harus mempertahankan semantik kontrak. Setiap request harus sadar tenant, workspace, scope, dan correlation.

## ALOS Backend

Backend mengimplementasikan `openapi/public/alos-public-api.yaml`, memiliki otoritas bisnis dan data, memvalidasi request publik yang masuk, serta memetakan run request yang valid ke API internal ALOS–GENESIS. Backend mengimplementasikan ToolExecutor dan memvalidasi ulang setiap ToolRequest terhadap permission serta scope terbaru. Backend juga mencatat keputusan IT dan Director yang authoritative.

## GENESIS dan kapabilitas AI

GENESIS menggunakan API internal serta schema agent, skill, runtime, delegation, context, tool, evidence, research, dan review. Semua akses model dikirim melalui ModelGateway. Agent tidak pernah menggunakan credential database bisnis dan hanya dapat meminta aksi bisnis dengan menghasilkan ToolRequest. Turunan agent mempertahankan `root_run_id` dan `parent_run_id`.

Field AI review merupakan rekomendasi dan sinyal assurance. Field tersebut tidak boleh mengisi atau menyamar sebagai `it_decision` maupun `director_decision`.

## Frontend, ARA, dan GIIVEPRO

Client frontend menghasilkan atau menulis client hanya dari OpenAPI publik. Client tidak pernah memanggil GENESIS atau endpoint internal. ARA merupakan workspace manusia, sedangkan GIIVEPRO merupakan lapisan bisnis/produk di atas ALOS. Keduanya tidak menjadi otoritas terpisah.

## Menambahkan kontrak

Pilih domain pemilik yang paling sempit, gunakan kembali identifier kanonis, tetapkan `$id` unik pada `/v1/`, tolak field yang tidak dikenal kecuali extensibility memang disengaja, tambahkan contoh valid dan pengujian negatif, serta perbarui kontrak OpenAPI atau event ketika schema melintasi boundary tersebut.
