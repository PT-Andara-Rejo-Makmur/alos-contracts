# Kontrak ALOS

`alos-contracts` adalah sumber kebenaran komunikasi untuk ALOS (Andara Leaverage Operating System), GENESIS (AI Control Plane), ARA (Human AI Workspace), dan GIIVEPRO (kapabilitas bisnis/produk di atas ALOS). Repository ini hanya berisi spesifikasi berversi dan tidak menjalankan logika bisnis.

## Alasan repository ini dibuat

Kontrak bersama mencegah repository frontend, backend, AI, dan infrastruktur membuat payload yang saling tidak kompatibel. Perubahan kontrak ditinjau satu kali, divalidasi melalui CI, diberi versi secara semantik, dan digunakan oleh setiap repository implementasi.

## Konsumen

- `alos-backend` memiliki otoritas platform, implementasi API publik, data bisnis, ToolExecutor, dan keputusan manusia.
- `genesis-ai` menggunakan kontrak agent, skill, runtime, delegation, research, evidence, dan API internal sebagai AI Control Plane.
- `alos-web` hanya menggunakan kontrak API publik ALOS dan tidak boleh memanggil GENESIS secara langsung.
- `alos-infra` menggunakan metadata antarmuka untuk mengonfigurasi lingkungan tanpa mendefinisikan ulang payload.
- ARA dan GIIVEPRO menggunakan kapabilitas platform melalui ALOS Backend.

## Cakupan yang dimiliki repository ini

Dokumen OpenAPI, JSON Schema, event envelope, identifier dan status kanonis, contoh payload, pemeriksaan kompatibilitas, keputusan arsitektur, serta tooling validasi kontrak.

Repository ini **tidak** memiliki kode aplikasi, agent, eksekusi model, database, antrean, implementasi autentikasi, client hasil generate palsu, layanan bisnis, atau infrastruktur deployment.

## Prasyarat dan instalasi

Python 3.12 dan Git diperlukan.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Lihat [Instalasi](docs/INSTALLATION.md) untuk langkah spesifik setiap platform.

## Validasi dan pengujian

```bash
python scripts/validate_schemas.py
python scripts/validate_openapi.py
python scripts/check_examples.py
python -m pytest
```

Contoh payload mendeklarasikan kontraknya melalui `$schema`:

```json
{
  "$schema": "https://schemas.alos.dev/v1/agent/agent-run-request.schema.json",
  "run_id": "run_order_review_001",
  "root_run_id": "run_order_review_001"
}
```

Contoh lengkap yang valid tersedia di [`examples/agent/agent-run-request.json`](examples/agent/agent-run-request.json).

## Alur perubahan

1. Tentukan schema pemilik; jangan menyalin definisi bersama.
2. Perbarui schema, contoh, referensi OpenAPI, dan dokumentasi secara bersamaan.
3. Jalankan seluruh validasi dan pengujian secara lokal.
4. Klasifikasikan kompatibilitas serta perbarui `VERSION` dan `CHANGELOG.md` ketika melakukan rilis.
5. Buka pull request untuk owner yang diwajibkan. AI review bersifat rekomendasi; keputusan IT dan Director tetap authoritative.

Rilis menggunakan Semantic Versioning. Menghapus field atau nilai enum, menambah field wajib, memperketat batasan yang diterima, atau mengubah makna memerlukan versi mayor. CI membandingkan pull request dengan commit dasarnya dan menolak perubahan schema breaking, kecuali proses rilis secara sengaja menetapkan lini mayor baru.

## Dokumentasi

- [Architecture Freeze v1](docs/architecture/ARCHITECTURE_FREEZE_V1.md)
- [Topologi repository](docs/architecture/REPOSITORY_TOPOLOGY.md)
- [Model otoritas](docs/architecture/AUTHORITY_MODEL.md)
- [Aturan dependency](docs/architecture/DEPENDENCY_RULES.md)
- [Panduan kontrak](docs/CONTRACT_GUIDE.md)
- [Validasi](docs/VALIDATION.md)
- [Versioning](docs/VERSIONING.md)
- [Kompatibilitas](docs/COMPATIBILITY.md)
- [Struktur folder](docs/FOLDER_STRUCTURE.md)
- [Panduan kontribusi](CONTRIBUTING.md)

> `.github/CODEOWNERS` masih berisi placeholder owner dan harus diperbarui dengan tim atau pengguna GitHub yang sebenarnya sebelum branch protection mengandalkannya.
