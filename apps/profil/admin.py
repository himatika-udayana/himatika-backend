from django.contrib import admin
from django.utils.html import format_html

from .models import FilosofiLogo, Misi, Profil, Pengurus, ProgramKerja, PengaturanWebsite, Timeline
from apps.core.admin import HanyaAdminMixin


class MisiInline(admin.TabularInline):
    model = Misi
    extra = 1
    fields = ("urutan", "deskripsi")
    ordering = ("urutan",)

class TimelineInline(admin.TabularInline):
    model = Timeline
    extra = 1
    fields = ("tahun", "judul", "deskripsi")
    ordering = ("-tahun",)

class FilosofiInline(admin.TabularInline):
    model = FilosofiLogo
    extra = 1
    fields = ("nama", "deskripsi")

@admin.register(Profil)
class ProfilAdmin(HanyaAdminMixin, admin.ModelAdmin):
    inlines = [MisiInline, TimelineInline, FilosofiInline]
    list_display = ("__str__", "periode_kepengurusan", "logo_preview")
    fields = ("periode_kepengurusan", "sejarah", "visi", "logo", "logo_preview")
    readonly_fields = ("logo_preview",)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 80px; border-radius: 4px;" />',
                obj.logo.url,
            )
        return "-"

    logo_preview.short_description = "Preview Logo"

    def has_add_permission(self, request):
        # Singleton: hanya boleh ada 1 baris. Kalau sudah ada, sembunyikan tombol "Add".
        return super().has_add_permission(request) and not Profil.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Satu-satunya row Profil tidak boleh dihapus dari admin, meski oleh admin/superuser.
        return False


@admin.register(Pengurus)
class PengurusAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = ("nama", "jabatan", "bidang", "foto_preview")
    list_filter = ("bidang", "jabatan")
    search_fields = ("nama",)
    ordering = ("bidang", "jabatan", "nama")
    fields = ("nama", "jabatan", "bidang", "foto", "foto_preview")
    readonly_fields = ("foto_preview",)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 60px; border-radius: 50%;" />',
                obj.foto.url,
            )
        return "-"

    foto_preview.short_description = "Preview Foto"


@admin.register(ProgramKerja)
class ProgramKerjaAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = ("nama_proker", "bidang", "progres", "status_display", "foto_preview")
    list_filter = ("bidang",)
    search_fields = ("nama_proker", "deskripsi")
    ordering = ("progres",)
    list_editable = ("progres",)
    fields = ("nama_proker", "deskripsi", "foto", "bidang", "progres", "foto_preview")
    readonly_fields = ("foto_preview",)

    @admin.display(description="Status")
    def status_display(self, obj):
        return obj.status

    @admin.display(description="Preview Foto")
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 60px; border-radius: 8px;" />',
                obj.foto.url,
            )
        return "-"


@admin.register(PengaturanWebsite)
class PengaturanWebsiteAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = (
        "nama_website",
        "alamat",
        "instagram_link",
        "facebook_link",
        "spotify_link",
        "youtube_link",
        "website_link",
        "email_kontak",
        "no_hp",
        "whatsapp_pj_koperasi",
    )
    fieldsets = (
        ("Identitas Website", {
            "fields": ("nama_website",),
        }),
        ("Statistik Home", {
            "fields": (
                ("statistik_1_label", "statistik_1_nilai"),
                ("statistik_2_label", "statistik_2_nilai"),
                ("statistik_3_label", "statistik_3_nilai"),
                ("statistik_4_label", "statistik_4_nilai"),
            ),
        }),
        ("Kontak", {
            "fields": (
                "alamat",
                "instagram_link",
                "facebook_link",
                "spotify_link",
                "youtube_link",
                "website_link",
                "email_kontak",
                "no_hp",
                "whatsapp_pj_koperasi",
            ),
        }),
    )
