from django.utils.decorators import method_decorator
from django.conf import settings
from django.db import IntegrityError
import logging
from django.shortcuts import redirect
from django_ratelimit.decorators import ratelimit
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.permissions import IsVerifiedUser
from .models import EmailVerificationToken, User
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ConfirmResetPasswordSerializer,
    ResetPasswordSerializer,
    UserMeSerializer,
)
from .services import (
    build_verification_link,
    decode_uid,
    send_verification_email,
)

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="login",
    )
    def login(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="refresh",
    )
    def refresh(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="logout",
    )
    def logout(self, request):
        serializer = TokenBlacklistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Logout berhasil."})

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="register",
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        # akun lama yang belum diverifikasi dianggap basi
        User.objects.filter(
            email=email,
            is_verified=False,
        ).delete()

        try:
            user = serializer.save()
        except IntegrityError:
            return Response(
                {
                    "detail": (
                        "Email, nama lengkap, atau NIM sudah digunakan. "
                        "Silakan gunakan data lain."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, raw_token = EmailVerificationToken.buat_token_baru(
            user=user,
            purpose=EmailVerificationToken.Purpose.REGISTER,
            masa_berlaku_jam=24,
        )

        link = build_verification_link(
            user,
            raw_token,
            purpose=EmailVerificationToken.Purpose.REGISTER,
        )

        try:
            send_verification_email(
                user,
                link,
                purpose=EmailVerificationToken.Purpose.REGISTER,
            )
        except Exception:
            logger.exception("Gagal mengirim email verifikasi ke %s", user.email)
            user.delete()
            return Response(
                {
                    "detail": (
                        "Registrasi belum selesai karena email verifikasi gagal dikirim. "
                        "Silakan coba lagi nanti."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "message": (
                    "Registrasi berhasil. "
                    "Silakan cek email untuk melakukan verifikasi."
                )
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get", "post"],
        permission_classes=[permissions.AllowAny],
        url_path="verify-email",
    )
    def verify_email(self, request):
        data = request.query_params if request.method == "GET" else request.data
        return self._process_verification(data)

    def _process_verification(self, data):
        uidb64 = data.get("uid")
        raw_token = data.get("token")
        purpose = data.get(
            "purpose",
            EmailVerificationToken.Purpose.REGISTER,
        )

        if not uidb64 or not raw_token:
            return Response(
                {"detail": "Parameter uid dan token wajib diisi."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = decode_uid(uidb64)
        if not user_id:
            return Response(
                {"detail": "Link verifikasi tidak valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Link verifikasi tidak valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if purpose == EmailVerificationToken.Purpose.REGISTER and user.is_verified:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Akun sudah terverifikasi sebelumnya.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )

        token_obj = (
            EmailVerificationToken.objects.filter(
                user=user,
                purpose=purpose,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not token_obj:
            return Response(
                {"detail": "Token verifikasi tidak ditemukan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if token_obj.is_expired:
            if purpose == EmailVerificationToken.Purpose.REGISTER:
                user.delete()

            return Response(
                {"detail": "Link verifikasi telah kedaluwarsa."},
                status=status.HTTP_410_GONE,
            )

        if not token_obj.verify(raw_token):
            return Response(
                {"detail": "Token verifikasi tidak valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_obj.mark_as_used()

        if purpose == EmailVerificationToken.Purpose.REGISTER:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Verifikasi berhasil.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )

        return Response({"message": "Token berhasil diverifikasi."})

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsVerifiedUser],
        url_path="change-password",
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"detail": "Password lama salah."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password berhasil diubah."})

    @action(
        detail=False,
        methods=["get", "post"],
        permission_classes=[permissions.AllowAny],
        url_path="reset-password",
    )
    @method_decorator(
        ratelimit(
            key="ip",
            rate="3/h",
            method="POST",
            block=False,
        )
    )
    def reset_password(self, request):
        if request.method == "GET":
            query_string = request.query_params.urlencode()
            reset_url = settings.RESET_PASSWORD_BASE_URL
            if query_string:
                reset_url = f"{reset_url}?{query_string}"
            return redirect(reset_url)

        if getattr(request, "limited", False):
            return Response(
                {
                    "detail": (
                        "Terlalu banyak permintaan reset password. " "Coba lagi nanti."
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = ConfirmResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = decode_uid(serializer.validated_data["uid"])
        if not user_id:
            return Response(
                {"detail": "Token reset password tidak valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Token reset password tidak valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_obj = (
            EmailVerificationToken.objects.filter(
                user=user,
                purpose=EmailVerificationToken.Purpose.RESET_PASSWORD,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )
        if not token_obj or not token_obj.verify(serializer.validated_data["token"]):
            return Response(
                {"detail": "Token reset password tidak valid atau kedaluwarsa."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        token_obj.mark_as_used()

        return Response({"message": "Password berhasil direset."})

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[permissions.AllowAny],
        url_path="forgot-password",
    )
    @method_decorator(
        ratelimit(key="ip", rate="3/h", method="POST", block=False)
    )
    def forgot_password(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"detail": "Terlalu banyak permintaan reset password. Coba lagi nanti."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response(
                {"detail": "Email tidak ditemukan."},
                status=status.HTTP_404_NOT_FOUND,
            )

        _, raw_token = EmailVerificationToken.buat_token_baru(
            user=user,
            purpose=EmailVerificationToken.Purpose.RESET_PASSWORD,
            masa_berlaku_jam=1,
        )
        link = build_verification_link(
            user,
            raw_token,
            purpose=EmailVerificationToken.Purpose.RESET_PASSWORD,
        )
        send_verification_email(user, link, purpose=EmailVerificationToken.Purpose.RESET_PASSWORD)

        return Response({"message": "Link reset password sudah dikirim ke email."})

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsVerifiedUser],
        url_path="me",
    )
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)
