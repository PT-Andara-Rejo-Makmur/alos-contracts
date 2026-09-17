# Kompatibilitas

Backward compatibility berarti payload yang valid pada versi lama yang masih didukung tetap valid dan mempertahankan maknanya pada versi yang lebih baru.

Perubahan yang umumnya kompatibel meliputi property opsional, schema independen baru, penjelasan deskripsi, dan pelonggaran batasan. Perubahan yang berpotensi breaking meliputi penghapusan atau penggantian nama field, penambahan field wajib, penyempitan type/range/pattern, penghapusan anggota enum, perubahan semantik otoritas, atau penghapusan schema.

`scripts/check_compatibility.py` mendeteksi perubahan struktural breaking yang umum terhadap suatu revisi Git. Hasilnya sengaja konservatif, tetapi tidak dapat mendeteksi setiap perubahan semantik. Peninjauan manusia tetap diwajibkan untuk perubahan deskripsi, otoritas, keamanan, batas tenant, dan semantik lifecycle.

Konsumen hanya boleh mengabaikan property object opsional yang tidak dikenal jika schema mengizinkannya dan harus menangani evolusi enum sesuai strategi bahasa pemrogramannya. Sebagian besar kontrak kanonis menggunakan `additionalProperties: false`, sehingga penambahan memerlukan pembaruan kontrak minor dan koordinasi dengan konsumen.

Perubahan breaking memerlukan versi mayor, dokumentasi migrasi, pembaruan konsumen yang terkoordinasi, dan rencana rollout eksplisit. Jangan melewati CI dengan menduplikasi atau memindahkan schema.
