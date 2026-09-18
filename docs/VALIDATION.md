# Validasi

Jalankan seluruh pemeriksaan dari root repository setelah memasang development dependency.

## JSON Schema

```bash
python scripts/validate_schemas.py
```

Perintah ini memvalidasi setiap schema terhadap meta-schema yang dideklarasikan, memastikan nilai `$id` kanonis unik, dan menolak referensi schema internal yang tidak ditemukan.

## OpenAPI

```bash
python scripts/validate_openapi.py
```

Perintah ini memvalidasi dokumen OpenAPI 3.1 publik dan internal beserta referensi schema eksternalnya.

## Contoh payload

```bash
python scripts/check_examples.py
```

Setiap contoh JSON harus mendeklarasikan `$schema` kanonis yang dikenal dan valid dengan pemeriksaan format aktif. Pemeriksaan ini mencakup `examples/`, contoh event, dan payload hasil adaptasi MVP-1 di `compatibility/fixtures/mvp1/`.

## Pengujian

```bash
python -m pytest
```

Pengujian mencakup validasi payload positif dan negatif, pemisahan otoritas ReviewPackage, validasi OpenAPI, validasi event, dan deteksi kompatibilitas.

## Generated TypeScript

```bash
python scripts/generate_typescript.py --check
```

Pemeriksaan ini memastikan public Factory type/client sama persis dengan hasil generator.
Jalankan `python scripts/generate_typescript.py` setelah contract Factory berubah. JSON Schema
dan OpenAPI tetap menjadi source of truth.

## Kompatibilitas terhadap revisi Git

```bash
python scripts/check_compatibility.py --baseline-ref <git-ref>
```

CI menjalankan perbandingan ini terhadap commit dasar pull request.
