from django.contrib import admin

from apps.core.admin import HanyaAdminMixin
from .models import (
    KategoriAspirasi,
    Semester,
    RamaSubmission,
    RamaAspirasi,
)


@admin.register(KategoriAspirasi)
class KategoriAspirasiAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "urutan",
        "nama_kategori",
        "deskripsi",
    )

    ordering = (
        "urutan",
    )

    search_fields = (
        "nama_kategori",
        "deskripsi",
    )


@admin.register(Semester)
class SemesterAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "tahun_ajaran",
        "jenis",
        "aktif",
    )

    list_filter = (
        "aktif",
        "jenis",
    )

    search_fields = (
        "tahun_ajaran",
    )

    ordering = (
        "-tahun_ajaran",
        "jenis",
    )


class RamaAspirasiInline(admin.StackedInline):
    model = RamaAspirasi

    extra = 0
    can_delete = False
    show_change_link = False

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "kategori",
                    "kepuasan",
                    "isi_aspirasi",
                )
            },
        ),
    )

    readonly_fields = (
        "kategori",
        "kepuasan",
        "isi_aspirasi",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RamaSubmission)
class RamaSubmissionAdmin(HanyaAdminMixin, admin.ModelAdmin):

    list_display = (
        "kode_respon",
        "semester",
        "tanggal_submit",
        "status_badge",
    )

    list_filter = (
        "semester",
        "status",
    )

    search_fields = (
        "token",
    )

    ordering = (
        "-tanggal_submit",
    )

    inlines = [
        RamaAspirasiInline,
    ]

    def get_fields(self, request, obj=None):
        fields = [
            "kode_respon",
            "semester",
            "tanggal_submit",
            "status",
        ]

        if request.user.is_superuser:
            fields.insert(1, "user")

        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly = [
            "kode_respon",
            "semester",
            "tanggal_submit",
            "status",
        ]

        if request.user.is_superuser:
            readonly.append("user")

        return readonly

    @admin.display(description="Kode Respon")
    def kode_respon(self, obj):
        return obj.kode_respon

    @admin.display(description="Status")
    def status_badge(self, obj):
        return obj.get_status_display()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False