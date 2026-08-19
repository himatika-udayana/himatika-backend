from django.contrib import admin

# Register your models here.
from .models import ProdukKoperasi
from apps.core.admin import HanyaAdminMixin

@admin.register(ProdukKoperasi)
class ProdukKoperasiAdmin(HanyaAdminMixin, admin.ModelAdmin):
    list_display = ("nama_produk", "harga", "status", "link_gform_pesan", "foto", "deskripsi")
    list_filter = ("status",)
    search_fields = ("nama_produk",)
    ordering = ("nama_produk",)