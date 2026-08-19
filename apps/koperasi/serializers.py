from rest_framework import serializers

from .models import ProdukKoperasi


class ProdukKoperasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdukKoperasi
        fields = [
            "id", "nama_produk", "deskripsi", "harga", "foto",
            "status", "link_gform_pesan"
        ]
