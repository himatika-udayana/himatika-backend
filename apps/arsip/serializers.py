from rest_framework import serializers

from .models import Arsip


class ArsipSerializer(serializers.ModelSerializer):
    diunggah_oleh_nama = serializers.CharField(
        source="diunggah_oleh.username",
        read_only=True,
    )

    tipe_display = serializers.CharField(
        source="get_tipe_display",
        read_only=True,
    )

    semester_display = serializers.CharField(
        source="get_semester_display",
        read_only=True,
    )

    class Meta:
        model = Arsip
        fields = (
            "id",
            "tipe",
            "tipe_display",
            "judul",
            "link_gdrive",
            "mata_kuliah",
            "tahun",
            "semester",
            "semester_display",
            "dosen",
            "deskripsi",
            "diunggah_oleh",
            "diunggah_oleh_nama",
            "tanggal_upload",
        )

        read_only_fields = (
            "diunggah_oleh",
            "tanggal_upload",
        )