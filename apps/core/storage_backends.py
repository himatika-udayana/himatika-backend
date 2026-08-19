"""
Storage backend Cloudinary — dipakai untuk semua ImageField (logo, foto pengurus,
thumbnail blog/post, foto produk koperasi, thumbnail mathpedia).

Arsip Soal TIDAK pakai storage ini — disimpan sebagai link Google Drive (URLField),
bukan file upload, jadi tidak butuh cloud storage backend sama sekali.
"""
from cloudinary_storage.storage import MediaCloudinaryStorage


class CloudinaryImageStorage(MediaCloudinaryStorage):
    pass