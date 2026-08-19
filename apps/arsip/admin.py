from django.contrib import admin
from django.utils.html import format_html

from apps.core.admin import HanyaAdminMixin

from .models import Arsip, MataKuliah


class MataKuliahAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = ("nama", "kode")
    search_fields = ("nama", "kode")


class ArsipAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "judul",
        "tipe",
        "mata_kuliah",
        "tahun",
        "semester",
        "dosen",
        "diunggah_oleh",
        "tanggal_upload",
        "link_preview",
    )

    list_filter = (
        "tipe",
        "mata_kuliah",
        "tahun",
        "semester",
    )

    search_fields = (
        "judul",
        "mata_kuliah",
        "dosen",
        "deskripsi",
    )

    ordering = (
        "-tahun",
        "-tanggal_upload",
    )

    readonly_fields = (
        "tanggal_upload",
    )

    fieldsets = (
        (
            "Informasi",
            {
                "fields": (
                    "tipe",
                    "judul",
                    "link_gdrive",
                    "deskripsi",
                )
            },
        ),
        (
            "Akademik",
            {
                "fields": (
                    "mata_kuliah",
                    "tahun",
                    "semester",
                    "dosen",
                )
            },
        ),
        (
            "Publikasi",
            {
                "fields": (
                    "diunggah_oleh",
                    "tanggal_upload",
                )
            },
        ),
    )

    def link_preview(self, obj):
        return format_html(
            '<a href="{}" target="_blank">Buka Google Drive</a>',
            obj.link_gdrive,
        )

    link_preview.short_description = "Dokumen"

    def save_model(self, request, obj, form, change):
        if not obj.diunggah_oleh:
            obj.diunggah_oleh = request.user
        super().save_model(request, obj, form, change)


admin.site.register(MataKuliah, MataKuliahAdmin)
admin.site.register(Arsip, ArsipAdmin)