# Aturan Dependency

1. Repository konsumen mereferensikan versi kontrak yang telah dirilis atau commit yang di-pin.
2. Konsumen tidak menyalin schema, enum, atau fragmen OpenAPI menjadi definisi kanonis lokal.
3. `alos-web` hanya bergantung pada surface OpenAPI publik.
4. `genesis-ai` bergantung pada kontrak internal, runtime, agent, skill, delegation, tool, evidence, research, dan review.
5. `alos-backend` mengimplementasikan otoritas publik dan boundary ToolExecutor internal.
6. `alos-infra` boleh memvalidasi konfigurasi terhadap kontrak, tetapi tidak boleh mengubah makna kontrak.
7. Ekstensi GIIVEPRO menyusun identifier dan context ALOS, bukan membuat model tenant atau otoritas paralel.
8. Artefak hasil generate, ketika diperkenalkan, merupakan output yang reproducible dan tidak pernah menjadi source of truth.
9. Rilis kontrak mengalir keluar; model spesifik implementasi tidak menjadi schema kanonis tanpa architecture review.
