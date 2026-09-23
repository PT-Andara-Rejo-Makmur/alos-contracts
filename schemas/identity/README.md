# Batas identity

Folder ini memiliki projection transport kanonis untuk actor, workspace, membership/access,
principal terautentikasi, dan active workspace. Projection ini membawa hasil keputusan Backend;
ia tidak memberikan authority sendiri.

Credential, password hash, token hash, session repository, dan user database tetap concern privat
ALOS Backend dan tidak boleh ditambahkan ke Contracts. Gunakan `actor_id` kanonis dan jangan
membuat alias identity baru.
