from django.core.exceptions import ValidationError
from django.db import models

from apps.users.models import User


class UserPoint(models.Model):
    """
    Total poin pengguna untuk leaderboard, di-cap ke SKOR TERBAIK per quiz_set
    (bukan akumulasi semua attempt) — supaya retry tidak menggembungkan poin.
    Selalu di-RECOMPUTE PENUH dari QuizAttempt setiap kali 1 attempt selesai,
    lihat services.update_user_point(). Jangan di-update manual/increment.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="point")
    total_poin = models.PositiveIntegerField(default=0)
    total_quiz = models.PositiveIntegerField(
        default=0, help_text="Jumlah quiz_set berbeda yang sudah diselesaikan"
    )
    total_benar = models.PositiveIntegerField(
        default=0, help_text="Total jawaban benar, dihitung dari attempt TERBAIK tiap quiz_set"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-total_poin"]
        verbose_name = "Poin Pengguna"
        verbose_name_plural = "Poin Pengguna"

    def __str__(self):
        return f"{self.user.username} ({self.total_poin} poin)"


class QuizSet(models.Model):
    class Level(models.TextChoices):
        MUDAH = "mudah", "Mudah"
        MENENGAH = "menengah", "Menengah"
        SULIT = "sulit", "Sulit"

    judul = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    topik = models.CharField(
        max_length=100, blank=True, help_text="Contoh: Kalkulus, Aljabar Linear"
    )
    level_kesulitan = models.CharField(max_length=20, choices=Level.choices, default=Level.MUDAH)
    dibuat_oleh = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="quiz_set_dibuat"
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["judul"]
        verbose_name = "Set Kuis"
        verbose_name_plural = "Set Kuis"

    def __str__(self):
        return self.judul

    @property
    def total_poin_maksimal(self):
        return self.soal.aggregate(total=models.Sum("poin"))["total"] or 0

    @property
    def jumlah_soal(self):
        return self.soal.count()


class QuizQuestion(models.Model):
    class Tipe(models.TextChoices):
        PILIHAN_GANDA = "pg", "Pilihan Ganda"
        ISIAN_SINGKAT = "isian", "Isian Singkat"

    class Jawaban(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"
        E = "E", "E"

    quiz_set = models.ForeignKey(QuizSet, on_delete=models.CASCADE, related_name="soal")
    urutan = models.PositiveIntegerField(default=1)
    tipe = models.CharField(max_length=10, choices=Tipe.choices, default=Tipe.PILIHAN_GANDA)
    teks_soal = models.TextField()
    poin = models.PositiveIntegerField(
        default=10, help_text="Poin yang diperoleh jika soal dijawab benar."
    )

    # === Pilihan Ganda ===
    pilihan_a = models.CharField(max_length=255, blank=True)
    pilihan_b = models.CharField(max_length=255, blank=True)
    pilihan_c = models.CharField(max_length=255, blank=True)
    pilihan_d = models.CharField(max_length=255, blank=True)
    pilihan_e = models.CharField(max_length=255, blank=True)
    jawaban_benar_pg = models.CharField(max_length=1, choices=Jawaban.choices, blank=True)

    # === Isian Singkat ===
    jawaban_benar_isian = models.CharField(
        max_length=255, blank=True, help_text="Tidak membedakan huruf besar-kecil."
    )

    # field 'penjelasan' SENGAJA DIHAPUS — tidak pernah dikirim ke frontend,
    # dan validasi jawaban cuma terjadi di backend (lihat cek_jawaban di bawah),
    # jadi menyimpannya tidak ada gunanya untuk alur saat ini.

    class Meta:
        ordering = ["urutan"]
        verbose_name = "Soal Kuis"
        verbose_name_plural = "Soal Kuis"

    def clean(self):
        if self.tipe == self.Tipe.PILIHAN_GANDA:
            if not all([
                self.pilihan_a, self.pilihan_b, self.pilihan_c,
                self.pilihan_d, self.pilihan_e, self.jawaban_benar_pg,
            ]):
                raise ValidationError(
                    "Semua pilihan dan jawaban benar wajib diisi untuk soal pilihan ganda."
                )
            self.jawaban_benar_isian = ""
        elif self.tipe == self.Tipe.ISIAN_SINGKAT:
            if not self.jawaban_benar_isian:
                raise ValidationError(
                    "Jawaban benar wajib diisi untuk soal isian singkat."
                )
            self.pilihan_a = ""
            self.pilihan_b = ""
            self.pilihan_c = ""
            self.pilihan_d = ""
            self.pilihan_e = ""
            self.jawaban_benar_pg = ""

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quiz_set.judul} - Soal {self.urutan}"

    def cek_jawaban(self, jawaban: str) -> bool:
        """
        SATU-SATUNYA tempat logic pengecekan jawaban boleh ada — dipanggil dari
        services.py. Sengaja jadi method model supaya nama field tidak bisa
        typo lagi di tempat lain (root cause bug sebelumnya).
        """
        jawaban_bersih = (jawaban or "").strip()
        if self.tipe == self.Tipe.PILIHAN_GANDA:
            return jawaban_bersih.upper() == self.jawaban_benar_pg.upper()
        return jawaban_bersih.lower() == self.jawaban_benar_isian.lower()


class QuizAttempt(models.Model):
    class Status(models.TextChoices):
        BERLANGSUNG = "berlangsung", "Berlangsung"
        SELESAI = "selesai", "Selesai"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz_set = models.ForeignKey(QuizSet, on_delete=models.CASCADE, related_name="attempts")
    skor = models.PositiveIntegerField(default=0, help_text="Nilai akhir dalam persen (0-100)")
    total_poin = models.PositiveIntegerField(
        default=0, help_text="Total poin yang didapat dari jawaban benar di attempt ini"
    )
    waktu_mulai = models.DateTimeField(auto_now_add=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BERLANGSUNG)

    class Meta:
        ordering = ["-waktu_mulai"]
        verbose_name = "Percobaan Kuis"
        verbose_name_plural = "Percobaan Kuis"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["quiz_set"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.quiz_set.judul} ({self.skor})"


class QuizAnswer(models.Model):
    """
    Model ini sebelumnya belum ikut di-paste, jadi field-nya saya definisikan
    berdasarkan cara services.py memakainya. Cek lagi nama field-nya kalau
    versi asli kamu beda.
    """
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="jawaban")
    question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name="jawaban_masuk"
    )
    jawaban_dipilih = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Jawaban Kuis"
        verbose_name_plural = "Jawaban Kuis"
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"], name="unique_jawaban_per_soal_per_attempt"
            )
        ]

    def __str__(self):
        return f"Attempt #{self.attempt_id} - Soal #{self.question_id}"