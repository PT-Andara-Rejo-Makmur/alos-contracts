# Batas identity

Folder ini memiliki projection transport kanonis untuk actor, workspace, membership/access,
principal terautentikasi, dan active workspace. Projection ini membawa hasil keputusan Backend;
ia tidak memberikan authority sendiri.

Provisioning candidate projection hanya memuat fakta karyawan minimum yang telah difilter Backend
berdasarkan tenant, organisasi, status kerja, dan linkage actor.

Credential, password hash, activation token hash, session repository, dan account database tetap
concern privat ALOS Backend dan tidak boleh ditambahkan ke Contracts. Provisioning mengacu ke
employee yang sudah ada di HR, menerima tepat satu role workspace, dan tidak menerima password
atau permission/scope/data-scope pilihan client. Backend menentukan authority berdasarkan workspace,
role, dan policy organisasi. Gunakan identifier kanonis dan jangan membuat alias identity baru.

Role authorization aktif tepat `EXECUTIVE`, `DIVISION_LEAD`, `DIVISION_MEMBER`, dan `IT_ADMIN`.
Satu membership berlaku pada satu workspace dan membawa satu role utama; masa aktifnya dibatasi
`effective_at` dan `expires_at` bila tersedia.
