from rest_framework import permissions


class IsVerifiedUser(permissions.BasePermission):
    """User harus login dan sudah verifikasi OTP (anggota ATAU admin)."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_verified
        )