from rest_framework import serializers

from .models import FAQ, Post, PostImage, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "nama",
            "slug",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = (
            "nomor",
            "gambar",
            "caption",
        )


class PostSerializer(serializers.ModelSerializer):
    publisher = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    tipe_display = serializers.CharField(
        source="get_tipe_display",
        read_only=True,
    )

    level_prestasi_display = serializers.CharField(
        source="get_level_prestasi_display",
        read_only=True,
    )

    kategori_mathpedia_display = serializers.CharField(
        source="get_kategori_mathpedia_display",
        read_only=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "tipe",
            "tipe_display",
            "judul",
            "slug",
            "ringkasan",
            "konten",
            "thumbnail",
            "penulis",
            "email_penulis",
            "ig_penulis",
            "publisher",
            "status",
            "tanggal_dibuat",
            "tanggal_publish",
            "tanggal_diubah",
            "tanggal_event",
            "lokasi_event",
            "link_formulir",
            "deadline_formulir",
            "level_prestasi",
            "level_prestasi_display",
            "kategori_mathpedia",
            "kategori_mathpedia_display",
            "tags",
            "images",
        )


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = (
            "id",
            "pertanyaan",
            "jawaban",
        )