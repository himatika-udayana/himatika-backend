from django.db import transaction
from rest_framework import serializers

from .services import GoogleSheetService

from .models import (
    KategoriAspirasi,
    Semester,
    RamaSubmission,
    RamaAspirasi,
)


class SemesterSerializer(serializers.ModelSerializer):
    nama = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = (
            "id",
            "nama",
        )

    def get_nama(self, obj):
        return str(obj)


class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriAspirasi
        fields = (
            "id",
            "urutan",
            "nama_kategori",
            "deskripsi",
        )


class RamaAspirasiSerializer(serializers.ModelSerializer):
    kategori = serializers.CharField(
        source="kategori.nama_kategori",
        read_only=True,
    )

    kepuasan = serializers.CharField(
        source="get_kepuasan_display",
        read_only=True,
    )

    class Meta:
        model = RamaAspirasi
        fields = (
            "kategori",
            "kepuasan",
            "isi_aspirasi",
        )


class JawabanSerializer(serializers.Serializer):
    kategori = serializers.PrimaryKeyRelatedField(
        queryset=KategoriAspirasi.objects.all()
    )

    kepuasan = serializers.ChoiceField(
        choices=RamaAspirasi.Kepuasan.choices
    )

    isi_aspirasi = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


class RamaSubmissionSerializer(serializers.Serializer):
    jawaban = JawabanSerializer(many=True)

    def validate(self, attrs):
        semester = Semester.objects.filter(
            aktif=True
        ).first()

        if semester is None:
            raise serializers.ValidationError(
                "Belum ada semester yang sedang aktif."
            )

        user = self.context["request"].user

        if RamaSubmission.objects.filter(
            user=user,
            semester=semester,
        ).exists():
            raise serializers.ValidationError(
                "Kamu sudah mengisi RAMA pada semester ini."
            )

        kategori_db = set(
            KategoriAspirasi.objects.values_list(
                "id",
                flat=True,
            )
        )

        kategori_input = [
            item["kategori"].id
            for item in attrs["jawaban"]
        ]

        if len(kategori_input) != len(set(kategori_input)):
            raise serializers.ValidationError(
                "Kategori tidak boleh diisi lebih dari satu kali."
            )

        if set(kategori_input) != kategori_db:
            raise serializers.ValidationError(
                "Semua kategori wajib diisi tepat satu kali."
            )

        attrs["semester"] = semester
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        submission = RamaSubmission.objects.create(
            user=self.context["request"].user,
            semester=validated_data["semester"],
        )

        RamaAspirasi.objects.bulk_create([
            RamaAspirasi(
                submission=submission,
                kategori=item["kategori"],
                kepuasan=item["kepuasan"],
                isi_aspirasi=item["isi_aspirasi"],
            )
            for item in validated_data["jawaban"]
        ])

        transaction.on_commit(
            lambda: GoogleSheetService.simpan_submission(submission)
        )

        return submission


class RamaSubmissionDetailSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()

    status = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    jawaban = RamaAspirasiSerializer(
        source="aspirasi",
        many=True,
        read_only=True,
    )

    class Meta:
        model = RamaSubmission
        fields = (
            "semester",
            "tanggal_submit",
            "status",
            "jawaban",
        )


class RamaFormSerializer(serializers.Serializer):
    """
    Serializer untuk GET /api/rama

    Jika belum submit:
    {
        "sudah_submit": false,
        "semester": {...},
        "kategori": [...]
    }

    Jika sudah submit:
    {
        "sudah_submit": true,
        "submission": {...}
    }
    """

    sudah_submit = serializers.BooleanField()

    semester = SemesterSerializer(
        required=False,
    )

    kategori = KategoriSerializer(
        many=True,
        required=False,
    )

    submission = RamaSubmissionDetailSerializer(
        required=False,
    )