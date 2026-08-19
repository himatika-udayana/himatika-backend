import uuid

from django.core.exceptions import ValidationError
from django.db import models


class KategoriAspirasi(models.Model):
    urutan = models.PositiveIntegerField(
        help_text="Urutan kategori aspirasi (1, 2, 3, ...)"
    )

    nama_kategori = models.CharField(max_length=100)

    deskripsi = models.TextField(blank=True)

    class Meta:
        ordering = ["urutan"]
        verbose_name = "Kategori Aspirasi"
        verbose_name_plural = "Kategori Aspirasi"

    def __str__(self):
        return self.nama_kategori


class Semester(models.Model):

    class Jenis(models.TextChoices):
        GANJIL = "ganjil", "Ganjil"
        GENAP = "genap", "Genap"

    tahun_ajaran = models.CharField(
        max_length=9,
        help_text="Contoh: 2025/2026",
    )

    jenis = models.CharField(
        max_length=10,
        choices=Jenis.choices,
    )

    aktif = models.BooleanField(
        default=False,
        help_text="Hanya boleh ada satu semester aktif.",
    )

    class Meta:
        ordering = ["-tahun_ajaran", "jenis"]
        verbose_name = "Semester"
        verbose_name_plural = "Semester"
        constraints = [
            models.UniqueConstraint(
                fields=["tahun_ajaran", "jenis"],
                name="unique_semester",
            ),
        ]

    def clean(self):
        if (
            self.aktif
            and Semester.objects.exclude(pk=self.pk).filter(aktif=True).exists()
        ):
            raise ValidationError(
                "Hanya boleh ada satu semester yang aktif."
            )

    def __str__(self):
        return f"{self.get_jenis_display()} {self.tahun_ajaran}"


class RamaSubmission(models.Model):

    class Status(models.TextChoices):
        TERSIMPAN = "tersimpan", "Tersimpan"
        TERKIRIM = "terkirim", "Terkirim ke Google Sheet"
        GAGAL = "gagal", "Gagal Sinkronisasi"

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Kode anonim responden.",
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="rama_submissions",
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    tanggal_submit = models.DateTimeField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TERSIMPAN,
    )

    class Meta:
        ordering = ["-tanggal_submit"]
        verbose_name = "Pengisian RAMA"
        verbose_name_plural = "Pengisian RAMA"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "semester"],
                name="unique_user_semester_submission",
            ),
        ]

        indexes = [
            models.Index(fields=["semester"]),
            models.Index(fields=["status"]),
            models.Index(fields=["tanggal_submit"]),
        ]

    @property
    def kode_respon(self):
        return str(self.token)[:8]

    def __str__(self):
        return f"{self.kode_respon} - {self.semester}"


class RamaAspirasi(models.Model):

    class Kepuasan(models.IntegerChoices):
        SANGAT_TIDAK_PUAS = 1, "Sangat Tidak Puas"
        TIDAK_PUAS = 2, "Tidak Puas"
        CUKUP = 3, "Cukup"
        PUAS = 4, "Puas"
        SANGAT_PUAS = 5, "Sangat Puas"

    submission = models.ForeignKey(
        RamaSubmission,
        on_delete=models.CASCADE,
        related_name="aspirasi",
    )

    kategori = models.ForeignKey(
        KategoriAspirasi,
        on_delete=models.CASCADE,
        related_name="aspirasi",
    )

    kepuasan = models.PositiveSmallIntegerField(
        choices=Kepuasan.choices,
    )

    isi_aspirasi = models.TextField()

    class Meta:
        verbose_name = "Aspirasi RAMA"
        verbose_name_plural = "Aspirasi RAMA"
        ordering = ["kategori__urutan"]

        constraints = [
            models.UniqueConstraint(
                fields=["submission", "kategori"],
                name="unique_submission_kategori",
            ),
        ]

        indexes = [
            models.Index(fields=["kategori"]),
        ]

    def __str__(self):
        return (
            f"{self.submission.kode_respon} - "
            f"{self.kategori.nama_kategori}"
        )