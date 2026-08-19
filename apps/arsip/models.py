from django.db import models

from apps.users.models import User

class MataKuliah(models.Model):
    kode = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)

    class Meta:
        ordering = ["kode"]
        verbose_name = "Mata Kuliah"
        verbose_name_plural = "Mata Kuliah"

    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Arsip(models.Model):
    class Tipe(models.TextChoices):
        SOAL = "soal", "Arsip Soal"
        MATERI = "materi", "Materi Perkuliahan"

    class Semester(models.TextChoices):
        GANJIL = "ganjil", "Ganjil"
        GENAP = "genap", "Genap"

    tipe = models.CharField(
        max_length=20,
        choices=Tipe.choices,
    )

    judul = models.CharField(max_length=200)

    link_gdrive = models.URLField(
        help_text="Link Google Drive yang dapat diakses."
    )

    mata_kuliah = models.ForeignKey(
        MataKuliah,
        on_delete=models.PROTECT,
        related_name="arsip",
    )

    tahun = models.PositiveIntegerField()

    semester = models.CharField(
        max_length=10,
        choices=Semester.choices,
    )

    dosen = models.CharField(
        max_length=100,
        blank=True,
    )

    deskripsi = models.TextField(
        blank=True,
    )

    diunggah_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="arsip_kuliah",
    )

    tanggal_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-tahun", "-tanggal_upload"]
        verbose_name = "Arsip Soal & Materi"
        verbose_name_plural = "Arsip Soal & Materi"

        indexes = [
            models.Index(fields=["tipe"]),
            models.Index(fields=["mata_kuliah"]),
            models.Index(fields=["tahun"]),
            models.Index(fields=["semester"]),
        ]

    def __str__(self):
        return f"[{self.get_tipe_display()}] {self.judul}"