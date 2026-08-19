from django.contrib import admin, messages
from django.utils.html import format_html

from apps.core.admin import HanyaAdminMixin

from .forms import PostAdminForm
from .models import FAQ, Post, PostImage, Tag
from .services import MammothService


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = (
        "nomor",
        "gambar",
        "caption",
    )


@admin.register(Tag)
class TagAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "nama",
        "slug",
    )
    search_fields = (
        "nama",
        "slug",
    )
    readonly_fields = (
        "slug",
    )


@admin.register(Post)
class PostAdmin(HanyaAdminMixin, admin.ModelAdmin):
    form = PostAdminForm

    inlines = [PostImageInline]

    filter_horizontal = ("tags",)

    list_display = (
        "judul",
        "tipe",
        "penulis",
        "ringkasan",
        "publisher",
        "status",
        "tanggal_publish",
        "thumbnail_preview",
    )

    list_filter = (
        "tipe",
        "status",
        "tanggal_publish",
    )

    search_fields = (
        "judul",
        "penulis",
        "email_penulis",
        "ig_penulis",
    )

    readonly_fields = (
        "slug",
        "konten",
        "publisher",
        "tanggal_dibuat",
        "tanggal_diubah",
        "tanggal_publish",
    )

    fieldsets = (
        (
            "Informasi Umum",
            {
                "fields": (
                    "tipe",
                    "judul",
                    "slug",
                    "ringkasan",
                    "thumbnail",
                )
            },
        ),
        (
            "Penulis",
            {
                "fields": (
                    "penulis",
                    "email_penulis",
                    "ig_penulis",
                )
            },
        ),
        (
            "Mathpedia",
            {
                "fields": (
                    "kategori_mathpedia",
                    "tags",
                )
            },
        ),
        (
            "Event",
            {
                "fields": (
                    "tanggal_event",
                    "lokasi_event",
                )
            },
        ),
        (
            "Open Requirement",
            {
                "fields": (
                    "link_formulir",
                    "deadline_formulir",
                )
            },
        ),
        (
            "Prestasi",
            {
                "fields": (
                    "level_prestasi",
                )
            },
        ),
        (
            "Import DOCX",
            {
                "fields": (
                    "document",
                )
            },
        ),
        (
            "Publikasi",
            {
                "fields": (
                    "status",
                    "publisher",
                    "tanggal_dibuat",
                    "tanggal_diubah",
                    "tanggal_publish",
                )
            },
        ),
    )

    class Media:
        js = (
            "admin/js/post_admin.js",
        )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="120" style="border-radius:8px;">',
                obj.thumbnail.url,
            )
        return "-"

    thumbnail_preview.short_description = "Thumbnail"

    def save_model(self, request, obj, form, change):
        document = form.cleaned_data.get("document")

        if document:
            try:
                obj.konten = MammothService.convert_docx_to_html(document)
            except Exception as e:
                self.message_user(
                    request,
                    f"Gagal mengonversi DOCX: {e}",
                    level=messages.ERROR,
                )
                return

        if not obj.publisher:
            obj.publisher = request.user

        super().save_model(request, obj, form, change)


@admin.register(FAQ)
class FAQAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "pertanyaan",
        "jawaban",
    )

    search_fields = (
        "pertanyaan",
        "jawaban",
    )
