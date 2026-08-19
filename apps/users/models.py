import secrets
from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    nama_lengkap = models.CharField(
        max_length=100,
        blank=True,
    )

    nim = models.CharField(
        max_length=10,
        blank=True,
    )

    angkatan = models.CharField(
        max_length=4,
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True setelah email diverifikasi.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"
        constraints = [
            models.UniqueConstraint(
                fields=["nama_lengkap"],
                condition=~Q(nama_lengkap=""),
                name="unique_user_nama_lengkap",
            ),
            models.UniqueConstraint(
                fields=["nim"],
                condition=~Q(nim=""),
                name="unique_user_nim",
            ),
        ]

    def __str__(self):
        return self.email


class EmailVerificationToken(models.Model):
    """
    Menggantikan OTPCode — verifikasi sekarang lewat link (token acak panjang),
    bukan kode 6 digit yang diketik manual.
    """
    class Purpose(models.TextChoices):
        REGISTER = "register", "Registrasi"
        RESET_PASSWORD = "reset_password", "Reset Password"
        CHANGE_PASSWORD = "change_password", "Ganti Password"

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="verification_tokens"
    )
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.REGISTER)
    token_hash = models.CharField(max_length=255)  # hash, bukan token asli
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Token Verifikasi Email"
        verbose_name_plural = "Token Verifikasi Email"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "purpose"]),
            models.Index(fields=["expired_at"]),
        ]

    def __str__(self):
        return f"Token {self.user.email} ({self.get_purpose_display()})"

    @staticmethod
    def generate_raw_token() -> str:
        # 32 byte random, url-safe -> ~43 karakter. Jauh lebih sulit ditebak
        # daripada kode 6 digit, cocok karena dikirim via link bukan diketik manual.
        return secrets.token_urlsafe(32)

    @classmethod
    def buat_token_baru(cls, user, purpose=Purpose.REGISTER, masa_berlaku_jam=24):
        # hapus token aktif lama untuk purpose yang sama, sama seperti OTP dulu
        cls.objects.filter(user=user, purpose=purpose, is_used=False).delete()

        raw_token = cls.generate_raw_token()
        obj = cls.objects.create(
            user=user,
            purpose=purpose,
            token_hash=make_password(raw_token),
            expired_at=timezone.now() + timedelta(hours=masa_berlaku_jam),
        )
        return obj, raw_token

    @property
    def is_expired(self):
        return timezone.now() > self.expired_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired

    def verify(self, raw_token):
        return self.is_valid and check_password(raw_token, self.token_hash)

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])
