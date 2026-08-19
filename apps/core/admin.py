from django.contrib import admin

# Register your models here.
class HanyaAdminMixin:
    """Defense-in-depth: selain is_staff, pastikan role juga 'admin'.

    Superuser (mis. hasil `createsuperuser`) selalu diizinkan, supaya
    tidak ter-lock out dari admin panel saat role belum di-set manual.
    """

    def _is_admin(self, request):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or getattr(user, "role", None) == "admin"
        )

    def has_module_permission(self, request):
        return self._is_admin(request)

    def has_view_permission(self, request, obj=None):
        return self._is_admin(request)

    def has_add_permission(self, request):
        return self._is_admin(request)

    def has_change_permission(self, request, obj=None):
        return self._is_admin(request)

    def has_delete_permission(self, request, obj=None):
        return self._is_admin(request)
