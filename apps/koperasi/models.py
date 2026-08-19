from django.db import models

from apps.core.storage_backends import CloudinaryImageStorage


class ProdukKoperasi(models.Model):
    class Status(models.TextChoices):
        TERSEDIA = 'tersedia', 'Tersedia'
        HABIS = 'habis', 'Habis'

    nama_produk = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    harga = models.DecimalField(max_digits=12, decimal_places=2)
    foto = models.ImageField(
        upload_to='koperasi/', storage=CloudinaryImageStorage(), blank=True, null=True
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TERSEDIA)
    link_gform_pesan = models.URLField(
        blank=True, help_text="Link Google Form untuk pemesanan produk ini"
    )

    class Meta:
        ordering = ['nama_produk']
        verbose_name = "Produk Koperasi"
        verbose_name_plural = "Produk Koperasi"

    def __str__(self):
        return self.nama_produk