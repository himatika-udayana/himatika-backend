from rest_framework import serializers

from .models import FilosofiLogo, Misi, Pengurus, ProgramKerja, Profil, PengaturanWebsite, Timeline

class FilosofiSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilosofiLogo
        fields = ["id", "nama", "deskripsi"]

class MisiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Misi
        fields = ["id", "urutan", "deskripsi"]


class TimelineSerializer(serializers.ModelSerializer):
    year = serializers.IntegerField(source='tahun')
    title = serializers.CharField(source='judul')
    description = serializers.CharField(source='deskripsi')
    
    class Meta:
        model = Timeline
        fields = ["id", "year", "title", "description"]


class ProfilSerializer(serializers.ModelSerializer):
    misi = MisiSerializer(many=True, read_only=True)

    class Meta:
        model = Profil
        fields = ["id", "sejarah", "visi", "misi", "periode_kepengurusan", "logo"]


class PengurusSerializer(serializers.ModelSerializer):
    bidang = serializers.IntegerField()
    bidang_display = serializers.CharField(source="get_bidang_display", read_only=True)
    jabatan = serializers.IntegerField()
    jabatan_display = serializers.CharField(
        source="get_jabatan_display", read_only=True
    )

    class Meta:
        model = Pengurus
        fields = [
            "id",
            "nama",
            "foto",
            "bidang",
            "bidang_display",
            "jabatan",
            "jabatan_display",
        ]


class ProgramKerjaSerializer(serializers.ModelSerializer):
    bidang = serializers.IntegerField()
    bidang_display = serializers.CharField(source="get_bidang_display", read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ProgramKerja
        fields = [
            "id",
            "nama_proker",
            "deskripsi",
            "foto",
            "bidang",
            "bidang_display",
            "progres",
            "status",
        ]


class PengaturanWebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PengaturanWebsite
        fields = [
            "id",
            "nama_website",
            "statistik_1_label",
            "statistik_1_nilai",
            "statistik_2_label",
            "statistik_2_nilai",
            "statistik_3_label",
            "statistik_3_nilai",
            "statistik_4_label",
            "statistik_4_nilai",
            "alamat",
            "instagram_link",
            "facebook_link",
            "spotify_link",
            "youtube_link",
            "website_link",
            "email_kontak",
            "no_hp",
            "whatsapp_pj_koperasi",
        ]
