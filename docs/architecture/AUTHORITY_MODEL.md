# Model Otoritas

ALOS Backend memiliki tenant access, kebijakan bisnis, mutasi data bisnis, ToolExecutor, transisi release, dan pencatatan keputusan manusia authoritative. GENESIS dapat melakukan planning, orchestration, delegation, research, dan menghasilkan artefak assurance, tetapi tidak dapat menyetujui pekerjaannya sendiri atau mengubah business state di luar ToolExecutor.

ModelGateway merupakan satu-satunya boundary akses model. Backend ToolExecutor merupakan satu-satunya boundary antara agent dan aksi bisnis. ExecutionContext membawa identity, authority, referensi permission, referensi scope, classification, budget, dan correlation—bukan credential.

Output AI review merupakan rekomendasi berbasis evidence. `DecisionRef` hanya mengizinkan jenis keputusan `IT` dan `DIRECTOR`, serta mewajibkan actor manusia/platform dan timestamp. ReviewPackage dapat tersedia sebelum salah satu keputusan dibuat; keberadaan AI recommendation tidak pernah menyatakan approval.
