from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.core.models import SingletonModel
from apps.core.storage_backends import CloudinaryImageStorage


class Bidang(models.IntegerChoices):
    INTI = 1, "Inti"
    BPH = 2, "Badan Pengurus Harian"
    BIDANG_1 = 3, "Bidang I Pendidikan dan Penalaran"
    BIDANG_2 = 4, "Bidang II Minat dan Bakat"
    BIDANG_3 = 5, "Bidang III Kewirausahaan dan Kesejahteraan Mahasiswa"
    BIDANG_4 = 6, "Bidang IV Pengabdian Masyarakat"
    BIDANG_5 = 7, "Bidang V Komunikasi dan Informasi"


class Jabatan(models.IntegerChoices):
    KETUA = 1, "Ketua"
    WAKIL = 2, "Wakil Ketua"
    SEKRETARIS = 3, "Sekretaris"
    BENDAHARA = 4, "Bendahara"
    KABID = 5, "Koordinator Bidang"
    STAFF = 6, "Staff"




class PengaturanWebsite(SingletonModel):
    nama_website = models.CharField(max_length=100, default="HIMATIKA Universitas Udayana")
    statistik_1_label = models.CharField(max_length=100, default="Anggota Aktif")
    statistik_1_nilai = models.CharField(max_length=50, default="300+")
    statistik_2_label = models.CharField(max_length=100, default="Prestasi Diraih")
    statistik_2_nilai = models.CharField(max_length=50, default="50+")
    statistik_3_label = models.CharField(max_length=100, default="Program Kerja")
    statistik_3_nilai = models.CharField(max_length=50, default="20+")
    statistik_4_label = models.CharField(max_length=100, default="Berdiri Sejak")
    statistik_4_nilai = models.CharField(max_length=50, default="1998")
    alamat = models.TextField(blank=True)
    instagram_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    spotify_link = models.URLField(blank=True)
    youtube_link = models.URLField(blank=True)
    website_link = models.URLField(blank=True)
    email_kontak = models.EmailField(blank=True)
    no_hp = models.CharField(max_length=20, blank=True)
    whatsapp_pj_koperasi = models.CharField(
        max_length=20, blank=True, help_text="Nomor WA PJ untuk konfirmasi pesanan koperasi"
    )

    class Meta:
        verbose_name = "Pengaturan Website"
        verbose_name_plural = "Pengaturan Website"

    def __str__(self):
        return "Pengaturan Website"


class Profil(SingletonModel):
    sejarah = models.TextField(blank=True)
    visi = models.TextField(blank=True)
    periode_kepengurusan = models.CharField(
        max_length=9, blank=True, help_text="Contoh: 2023/2024"
    )
    logo = models.ImageField(
            upload_to="profil/", storage=CloudinaryImageStorage(), blank=True, null=True
        )

    class Meta:
        verbose_name = "Profil HIMATIKA"
        verbose_name_plural = "Profil HIMATIKA"

    def __str__(self):
        return "Profil HIMATIKA"

class FilosofiLogo(models.Model):
    profil = models.ForeignKey(
        "Profil",
        on_delete=models.CASCADE,
        related_name="filosofi",
        blank=True,
        null=True,
    )
    nama = models.CharField(max_length=100)
    deskripsi = models.TextField()

    class Meta:
        verbose_name = "Filosofi Logo"
        verbose_name_plural = "Filosofi Logo"

    def __str__(self):
        return self.nama


class Misi(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="misi")
    urutan = models.PositiveSmallIntegerField(help_text="Urutan misi (1, 2, 3, ...)")
    deskripsi = models.TextField()

    class Meta:
        verbose_name = "Misi"
        verbose_name_plural = "Misi"
        ordering = ["urutan"]

    def __str__(self):
        return self.deskripsi


class Timeline(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="timeline")
    tahun = models.PositiveIntegerField(help_text="Tahun kejadian")
    judul = models.CharField(max_length=200)
    deskripsi = models.TextField()

    class Meta:
        verbose_name = "Timeline"
        verbose_name_plural = "Timeline"
        ordering = ["-tahun"]

    def __str__(self):
        return f"{self.tahun} - {self.judul}"


class Pengurus(models.Model):
    nama = models.CharField(max_length=100)
    foto = models.ImageField(
        upload_to="pengurus/", storage=CloudinaryImageStorage(), blank=True, null=True
    )
    bidang = models.PositiveSmallIntegerField(
        choices=Bidang.choices, default=Bidang.INTI
    )
    jabatan = models.PositiveSmallIntegerField(
        choices=Jabatan.choices, default=Jabatan.STAFF
    )

    class Meta:
        ordering = ["bidang", "jabatan", "nama"]
        verbose_name = "Pengurus"
        verbose_name_plural = "Pengurus"

    def __str__(self):
        # periode sekarang diambil dari Profil (singleton), bukan field lokal
        return (
            f"{self.nama} - {self.get_jabatan_display()} ({self.get_bidang_display()})"
        )


class ProgramKerja(models.Model):
    nama_proker = models.CharField(max_length=200)
    deskripsi = models.TextField()
    foto = models.ImageField(
        upload_to="program-kerja/",
        storage=CloudinaryImageStorage(),
        blank=True,
        null=True,
    )
    bidang = models.PositiveSmallIntegerField(
        choices=Bidang.choices, default=Bidang.INTI
    )
    progres = models.PositiveIntegerField(
        default=0,
        help_text="Persentase progres (0-100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        ordering = ["progres"]
        verbose_name = "Program Kerja"
        verbose_name_plural = "Program Kerja"

    @property
    def status(self):
        if self.progres == 0:
            return "Rencana"
        elif self.progres == 100:
            return "Selesai"
        return "Berjalan"

    def __str__(self):
        return self.nama_proker
