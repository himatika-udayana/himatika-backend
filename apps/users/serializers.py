from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    nama_lengkap = serializers.CharField(validators=[])
    nim = serializers.CharField(validators=[])
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "nama_lengkap",
            "nim",
            "angkatan",
        ]

        extra_kwargs = {
            "email": {
                "validators": [],
            },
        }

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email sudah terdaftar. Silakan gunakan email lain.")

        return value

    def validate(self, attrs):
        nama_lengkap = (attrs.get("nama_lengkap") or "").strip()
        nim = (attrs.get("nim") or "").strip()
        angkatan = (attrs.get("angkatan") or "").strip()

        if not nama_lengkap:
            raise serializers.ValidationError({
                "nama_lengkap": "Nama lengkap wajib diisi."
            })

        if User.objects.filter(nama_lengkap__iexact=nama_lengkap).exists():
            raise serializers.ValidationError({
                "nama_lengkap": "Nama lengkap sudah digunakan."
            })

        attrs["nama_lengkap"] = nama_lengkap
        attrs["nim"] = nim

        if not nim:
            raise serializers.ValidationError({
                "nim": "NIM wajib diisi."
            })

        if not angkatan:
            raise serializers.ValidationError({
                "angkatan": "Angkatan wajib diisi."
            })

        if not nim.isdigit() or len(nim) != 10:
            raise serializers.ValidationError({
                "nim": "NIM harus terdiri dari tepat 10 digit angka."
            })

        if User.objects.filter(nim=nim).exists():
            raise serializers.ValidationError({
                "nim": "NIM sudah terdaftar."
            })

        if nim[2:7] != "08541":
            raise serializers.ValidationError({
                "nim": "NIM bukan milik Program Studi Matematika FMIPA Universitas Udayana."
            })

        if not angkatan.isdigit() or len(angkatan) != 4:
            raise serializers.ValidationError({
                "angkatan": "Angkatan harus berupa tahun, misalnya 2024."
            })

        if nim[:2] != angkatan[-2:]:
            raise serializers.ValidationError({
                "nim": "Dua digit pertama NIM tidak sesuai dengan angkatan."
            })

        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email").strip().lower()

        User.objects.filter(
            email=email,
            is_verified=False,
        ).delete()

        password = validated_data.pop("password")

        user = User(
            email=email,
            **validated_data,
            is_verified=False,
        )

        user.set_password(password)
        user.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login JWT hanya diizinkan untuk akun yang sudah
    melakukan verifikasi email.
    """

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        user = User.objects.filter(email=email).first()
        if user and not user.check_password(attrs.get("password", "")):
            raise AuthenticationFailed("Password salah.")

        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            raise AuthenticationFailed("Email atau password salah.")

        if not self.user.is_verified:
            raise serializers.ValidationError(
                "Akun belum diverifikasi. Silakan cek email untuk melakukan verifikasi."
            )

        return data


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nama_lengkap",
            "nim",
            "angkatan",
            "is_verified",
        ]
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
