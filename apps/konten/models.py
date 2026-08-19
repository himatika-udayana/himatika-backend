from django.utils import timezone

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from apps.core.storage_backends import CloudinaryImageStorage
from apps.users.models import User

class Tag(models.Model):
    nama = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["nama"]
        verbose_name = "Tag"
        verbose_name_plural = "Tag"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama)
            slug = base_slug
            counter = 1

            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.nama

class Post(models.Model):
    class Tipe(models.TextChoices):
        PENGUMUMAN = "pengumuman", "Pengumuman"
        OPEN_REQUIREMENT = "open-requirement", "Open Requirement"
        EVENT = "event", "Event"
        PRESTASI = "prestasi", "Prestasi"
        MATHPEDIA = "mathpedia", "Mathpedia"
    # Tipe
    tipe = models.CharField(max_length=20, choices=Tipe.choices, default=Tipe.PENGUMUMAN)

    # Konten
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    ringkasan = models.TextField(max_length=300, blank=True, null=True)
    konten = models.TextField()
    thumbnail = models.ImageField(
        upload_to='post/', storage=CloudinaryImageStorage(), blank=True, null=True
    )

    # Penulis Asli
    penulis = models.CharField(max_length=100)
    email_penulis = models.EmailField(max_length=100, blank=True, null=True)
    ig_penulis = models.CharField(max_length=100, blank=True, null=True)
    
    # Publisher
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='published_posts')

    # Status
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Waktu
    tanggal_dibuat = models.DateTimeField(auto_now_add=True)
    tanggal_publish = models.DateTimeField(null=True, blank=True)
    tanggal_diubah = models.DateTimeField(auto_now=True)

    # Khusus Event
    tanggal_event = models.DateField(null=True, blank=True)
    lokasi_event = models.CharField(max_length=255, null=True, blank=True)

    # Khusus Open Requirement
    link_formulir = models.URLField(max_length=255, null=True, blank=True)
    deadline_formulir = models.DateField(null=True, blank=True)

    # Khusus Prestasi
    class LevelPrestasi(models.TextChoices):
        INTERNASIONAL = 'internasional', 'Internasional'
        NASIONAL = 'nasional', 'Nasional'
        LOKAL = 'lokal', 'Lokal'
    level_prestasi = models.CharField(max_length=20, choices=LevelPrestasi.choices, null=True, blank=True)

    # Khusus Mathpedia
    class KategoriMathpedia(models.TextChoices):
        ALJABAR = "aljabar", "Aljabar"
        GEOMETRI = "geometri", "Geometri"
        KALKULUS = "kalkulus", "Kalkulus"
        ANALISIS = "analisis", "Analisis"
        MATEMATIKA_DISKRIT = "matematika-diskrit", "Matematika Diskrit"
        PELUANG = "peluang", "Peluang"
        STATISTIKA = "statistika", "Statistika"
        LAINNYA = "lainnya", "Lainnya"

    kategori_mathpedia = models.CharField(
        max_length=30,
        choices=KategoriMathpedia.choices,
        blank=True,
        null=True,
        help_text="hanya digunakan jika tipe mathpedia"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts"
    )

    class Meta:
        ordering = ['-status', '-tanggal_dibuat', '-tanggal_publish']
        indexes = [
            models.Index(fields=["tipe"]),
            models.Index(fields=["status"]),
            models.Index(fields=["tanggal_publish"]),
        ]

    def clean(self):
        super().clean()

        # EVENT
        if self.tipe == self.Tipe.EVENT:
            errors = {}

            if not self.tanggal_event:
                errors["tanggal_event"] = "Tanggal event wajib diisi."

            if not self.lokasi_event:
                errors["lokasi_event"] = "Lokasi event wajib diisi."

            if errors:
                raise ValidationError(errors)
        else:
            self.tanggal_event = None
            self.lokasi_event = None

        # OPEN REQUIREMENT
        if self.tipe == self.Tipe.OPEN_REQUIREMENT:
            errors = {}

            if not self.link_formulir:
                errors["link_formulir"] = "Link formulir wajib diisi."

            if not self.deadline_formulir:
                errors["deadline_formulir"] = "Deadline formulir wajib diisi."

            if errors:
                raise ValidationError(errors)
        else:
            self.link_formulir = None
            self.deadline_formulir = None

        # PRESTASI
        if self.tipe == self.Tipe.PRESTASI:
            if not self.level_prestasi:
                raise ValidationError({
                    "level_prestasi": "Level prestasi wajib dipilih."
                })
        else:
            self.level_prestasi = None

        # MATHPEDIA
        if self.tipe == self.Tipe.MATHPEDIA:
            if not self.kategori_mathpedia:
                raise ValidationError({
                    "kategori_mathpedia": "Kategori Mathpedia wajib dipilih."
                })
        else:
            self.kategori_mathpedia = None

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.status == self.Status.PUBLISHED and not self.tanggal_publish:
            self.tanggal_publish = timezone.now()
        elif self.status == self.Status.DRAFT:
            self.tanggal_publish = None

        if not self.slug:
            base_slug = slugify(self.judul)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.get_tipe_display()}] {self.judul}"
    
class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="images"
    )

    nomor = models.PositiveIntegerField()

    gambar = models.ImageField(
        upload_to="post/",
        storage=CloudinaryImageStorage(),
    )

    caption = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        ordering = ["nomor"]
        unique_together = ("post", "nomor")
        verbose_name = "Gambar Artikel"
        verbose_name_plural = "Gambar Artikel"

    def __str__(self):
        return f"{self.post.judul} - Gambar {self.nomor}"


class FAQ(models.Model):
    pertanyaan = models.CharField(max_length=255)
    jawaban = models.TextField()

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

    def __str__(self):
        return self.pertanyaan
