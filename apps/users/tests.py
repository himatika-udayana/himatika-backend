from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import EmailVerificationToken
from .serializers import RegisterSerializer
from .services import build_verification_link, send_verification_email


class AuthEndpointsTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="Password123!",
            nama_lengkap="Test User",
            nim="2308541001",
            angkatan="2023",
            is_verified=True,
        )

    def test_refresh_endpoint_returns_new_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("auth-refresh"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_returns_password_error_for_registered_email(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "WrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Password salah.")

    def test_login_keeps_generic_error_for_unknown_email(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "unknown@example.com", "password": "WrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Email atau password salah.")

    def test_logout_endpoint_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            reverse("auth-logout"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Logout berhasil.")

        with self.assertRaises(TokenError):
            refresh.check_blacklist()

    def test_reset_password_consumes_reset_token(self):
        token_obj, raw_token = EmailVerificationToken.buat_token_baru(
            user=self.user,
            purpose=EmailVerificationToken.Purpose.RESET_PASSWORD,
            masa_berlaku_jam=1,
        )
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.post(
            reverse("auth-reset-password"),
            {
                "uid": uid,
                "token": raw_token,
                "new_password": "NewPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.is_used)

        reused_response = self.client.post(
            reverse("auth-reset-password"),
            {
                "uid": uid,
                "token": raw_token,
                "new_password": "AnotherPassword123!",
            },
            format="json",
        )
        self.assertEqual(reused_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_accepts_valid_registration_token(self):
        user = get_user_model().objects.create_user(
            email="unverified@example.com",
            password="Password123!",
            nama_lengkap="Unverified User",
            nim="2308541002",
            angkatan="2023",
            is_verified=False,
        )
        token_obj, raw_token = EmailVerificationToken.buat_token_baru(
            user=user,
            purpose=EmailVerificationToken.Purpose.REGISTER,
            masa_berlaku_jam=24,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.post(
            reverse("auth-verify-email"),
            {"uid": uid, "token": raw_token, "purpose": "register"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        user.refresh_from_db()
        token_obj.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(token_obj.is_used)

    @override_settings(RESET_PASSWORD_BASE_URL="http://localhost:5173/reset-password")
    def test_reset_password_link_uses_reset_page(self):
        link = build_verification_link(
            self.user,
            "raw-token",
            purpose=EmailVerificationToken.Purpose.RESET_PASSWORD,
        )

        self.assertTrue(link.startswith("http://localhost:5173/reset-password?"))
        self.assertIn("purpose=reset_password", link)

    @override_settings(RESET_PASSWORD_BASE_URL="http://localhost:5173/reset-password")
    def test_legacy_reset_get_redirects_to_frontend(self):
        response = self.client.get(
            reverse("auth-reset-password"),
            {"uid": "MQ", "token": "raw-token", "purpose": "reset_password"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "http://localhost:5173/reset-password?uid=MQ&token=raw-token&purpose=reset_password",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verification_email_contains_html_cta(self):
        link = "http://localhost:5173/verify-email?uid=MQ&token=raw-token&purpose=register"

        send_verification_email(self.user, link)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.alternatives[0][1], "text/html")
        self.assertIn('>VERIFIKASI</a>', email.alternatives[0][0])
        self.assertIn(link, email.body)

    @patch(
        "apps.users.views.send_verification_email",
        side_effect=OSError("SMTP unavailable"),
    )
    def test_register_returns_service_unavailable_when_email_fails(self, send_email):
        response = self.client.post(
            reverse("auth-register"),
            {
                "email": "new-user@example.com",
                "password": "StrongPassword123!",
                "nama_lengkap": "New User",
                "nim": "2308541003",
                "angkatan": "2023",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertFalse(
            get_user_model().objects.filter(email="new-user@example.com").exists()
        )
        send_email.assert_called_once()

    def test_register_serializer_rejects_expired_unverified_email(self):
        user = get_user_model().objects.create_user(
            email="expired@example.com",
            password="Password123!",
            nama_lengkap="Expired User",
            nim="2308541004",
            angkatan="2023",
            is_verified=False,
        )
        EmailVerificationToken.objects.create(
            user=user,
            purpose=EmailVerificationToken.Purpose.REGISTER,
            token_hash="invalid-hash",
            expired_at=timezone.now() - timedelta(hours=1),
        )

        serializer = RegisterSerializer(
            data={
                "email": "expired@example.com",
                "password": "StrongPassword123!",
                "nama_lengkap": "New User",
                "nim": "2308541005",
                "angkatan": "2023",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("Email sudah terdaftar", str(serializer.errors["email"]))

    def test_register_rejects_duplicate_name_and_nim(self):
        duplicate_name = RegisterSerializer(
            data={
                "email": "different@example.com",
                "password": "StrongPassword123!",
                "nama_lengkap": "Test User",
                "nim": "2308541005",
                "angkatan": "2023",
            }
        )
        self.assertFalse(duplicate_name.is_valid())
        self.assertIn("sudah digunakan", str(duplicate_name.errors["nama_lengkap"]))

        duplicate_nim = RegisterSerializer(
            data={
                "email": "different-two@example.com",
                "password": "StrongPassword123!",
                "nama_lengkap": "Different User",
                "nim": "2308541001",
                "angkatan": "2023",
            }
        )
        self.assertFalse(duplicate_nim.is_valid())
        self.assertIn("sudah terdaftar", str(duplicate_nim.errors["nim"]))
